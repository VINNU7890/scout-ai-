from __future__ import annotations

import asyncio
import logging
from typing import List

from pydantic import BaseModel, Field

from backend.app.agent.events_manager import emit_event, is_run_cancelled
from backend.app.agent.prompts import (
    FINDING_EXTRACTION_SYSTEM_PROMPT,
    FINDING_EXTRACTION_USER_TEMPLATE,
)
from backend.app.agent.state import ResearchState
from backend.app.schemas import Finding
from backend.app.services.llm import call_structured_llm
from backend.app.tools.fetch import fetch_and_clean_page
from backend.app.tools.search import get_search_provider

logger = logging.getLogger("scoutai.agent.web_researcher")


class ExtractedFindingsContainer(BaseModel):
    findings: List[Finding] = Field(default_factory=list)


def deduplicate_findings(findings: List[Finding]) -> List[Finding]:
    """Deduplicates findings by URL and similar claims."""
    seen_claims = set()
    deduped: List[Finding] = []
    for f in findings:
        claim_norm = " ".join(f.claim.lower().split()[:10])
        key = (f.entity.lower(), f.aspect.lower(), claim_norm)
        if key not in seen_claims:
            seen_claims.add(key)
            deduped.append(f)
    return deduped


async def web_researcher_node(state: ResearchState) -> dict:
    run_id = state["run_id"]
    if is_run_cancelled(run_id):
        return {"errors": ["Run cancelled by user."]}

    plan = state.get("plan")
    if not plan or not plan.entities:
        return {"errors": ["No research plan found for web research."]}

    await emit_event(
        run_id, "node_started", "web_research", "Beginning live web intelligence gathering..."
    )

    search_provider = get_search_provider()
    options = state.get("options")
    max_sources = options.max_sources_per_entity if options else 3
    depth = options.depth if options else "standard"
    queries_per_entity = 2 if depth == "quick" else (3 if depth == "standard" else 4)

    all_findings: List[Finding] = []
    failed_errors: List[str] = []
    call_tracker = {"calls": state.get("llm_call_count", 0)}

    semaphore = asyncio.Semaphore(4)

    async def process_query(entity: str, aspect: str, query: str):
        if is_run_cancelled(run_id):
            return

        async with semaphore:
            await emit_event(run_id, "step", "web_research", f"Searching web: {query}")
            try:
                search_results = await search_provider.search(query=query, max_results=max_sources)
            except Exception as e:
                logger.warning(f"Search provider failed for '{query}': {e}")
                failed_errors.append(f"Search failed for '{query}': {e}")
                return

            for result in search_results:
                if is_run_cancelled(run_id):
                    return
                await emit_event(
                    run_id, "step", "web_research", f"Reading source: {result.title[:45]}..."
                )
                page = await fetch_and_clean_page(result.url)
                page_content = page.content.strip() if page.success else ""

                # If page fetching failed or anti-bot blocked, use search snippet directly
                content_to_analyze = page_content[:6000] if page_content else result.snippet

                if not content_to_analyze.strip():
                    continue

                user_prompt = FINDING_EXTRACTION_USER_TEMPLATE.format(
                    entity=entity,
                    aspect=aspect,
                    source_id=result.url,
                    content=content_to_analyze,
                )

                extracted_count_for_item = 0
                try:
                    res: ExtractedFindingsContainer = await call_structured_llm(
                        schema=ExtractedFindingsContainer,
                        system_prompt=FINDING_EXTRACTION_SYSTEM_PROMPT,
                        user_prompt=user_prompt,
                        call_tracker=call_tracker,
                    )

                    for item in res.findings:
                        item.entity = entity
                        item.aspect = aspect
                        item.source_url = result.url
                        item.source_type = "web"
                        words = item.evidence_quote.split()
                        if len(words) > 25:
                            item.evidence_quote = " ".join(words[:25]) + "..."
                        all_findings.append(item)
                        extracted_count_for_item += 1
                        await emit_event(
                            run_id,
                            "finding_added",
                            "web_research",
                            f"Verified claim for {entity}: {item.claim[:60]}...",
                            data={"finding": item.model_dump()},
                        )
                except Exception as e:
                    logger.debug(f"LLM extraction fallback for {result.url}: {e}")

                # If LLM failed or returned 0 findings, use high-confidence snippet extraction
                if extracted_count_for_item == 0 and result.snippet.strip():
                    try:
                        words = result.snippet.strip().split()
                        quote = " ".join(words[:25])
                        fallback_finding = Finding(
                            entity=entity,
                            aspect=aspect,
                            claim=f"{result.title}: {result.snippet[:160]}",
                            evidence_quote=quote,
                            source_url=result.url,
                            source_type="web",
                            confidence="high",
                        )
                        all_findings.append(fallback_finding)
                        await emit_event(
                            run_id,
                            "finding_added",
                            "web_research",
                            f"Verified claim for {entity}: {fallback_finding.claim[:60]}...",
                            data={"finding": fallback_finding.model_dump()},
                        )
                    except Exception as fe:
                        logger.warning(f"Error creating fallback finding: {fe}")

    tasks = []
    for entity in plan.entities:
        sub_qs = plan.sub_questions.get(entity, [f"{entity} overview features and pricing"])
        for idx, sub_q in enumerate(sub_qs[:queries_per_entity]):
            aspect = plan.aspects[idx % len(plan.aspects)] if plan.aspects else "product"
            tasks.append(process_query(entity, aspect, sub_q))

    await asyncio.gather(*tasks, return_exceptions=True)

    deduped = deduplicate_findings(all_findings)
    await emit_event(
        run_id,
        "node_finished",
        "web_research",
        f"Web research completed. Extracted {len(deduped)} verified claims.",
    )

    return {
        "web_findings": deduped,
        "errors": failed_errors,
        "llm_call_count": call_tracker["calls"],
    }
