from __future__ import annotations

import logging
from typing import List

from backend.app.agent.events_manager import emit_event, is_run_cancelled
from backend.app.agent.nodes.web_researcher import ExtractedFindingsContainer, deduplicate_findings
from backend.app.agent.prompts import (
    FINDING_EXTRACTION_SYSTEM_PROMPT,
    FINDING_EXTRACTION_USER_TEMPLATE,
)
from backend.app.agent.state import ResearchState
from backend.app.schemas import Finding
from backend.app.services.llm import call_structured_llm
from backend.app.tools.rag import get_rag_store

logger = logging.getLogger("scoutai.agent.doc_researcher")


async def doc_researcher_node(state: ResearchState) -> dict:
    run_id = state["run_id"]
    if is_run_cancelled(run_id):
        return {"errors": ["Run cancelled by user."]}

    include_docs = state.get("include_docs", True)
    document_ids = state.get("document_ids", [])
    plan = state.get("plan")

    if not include_docs or not document_ids or not plan:
        # Skip cleanly
        return {"doc_findings": []}

    await emit_event(
        run_id,
        "node_started",
        "doc_research",
        "Querying uploaded documents via RAG vector store...",
    )

    rag_store = get_rag_store()
    doc_findings: List[Finding] = []
    call_tracker = {"calls": state.get("llm_call_count", 0)}

    for entity in plan.entities:
        for aspect in plan.aspects[:3]:  # Top aspects
            if is_run_cancelled(run_id):
                break

            query_str = f"{entity} {aspect}"
            chunks = rag_store.query(collection_name=run_id, query_text=query_str, top_k=2)
            if not chunks:
                # Also check global document collection if indexed under doc_id
                for doc_id in document_ids:
                    sub_chunks = rag_store.query(
                        collection_name=doc_id, query_text=query_str, top_k=2
                    )
                    chunks.extend(sub_chunks)

            if not chunks:
                continue

            for chunk in chunks:
                await emit_event(
                    run_id,
                    "step",
                    "doc_research",
                    f"Reading document chunk: {chunk.doc_name} (Page {chunk.page})...",
                )

                user_prompt = FINDING_EXTRACTION_USER_TEMPLATE.format(
                    entity=entity,
                    aspect=aspect,
                    source_id=f"{chunk.doc_name} p.{chunk.page}",
                    content=chunk.content[:4000],
                )

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
                        item.doc_name = chunk.doc_name
                        item.page = chunk.page
                        item.source_type = "doc"
                        words = item.evidence_quote.split()
                        if len(words) > 25:
                            item.evidence_quote = " ".join(words[:25]) + "..."
                        doc_findings.append(item)
                        await emit_event(
                            run_id,
                            "finding_added",
                            "doc_research",
                            f"Verified claim from doc '{chunk.doc_name}': {item.claim[:60]}...",
                            data={"finding": item.model_dump()},
                        )
                except Exception as e:
                    logger.warning(f"Doc LLM extraction failed: {e}")

    deduped = deduplicate_findings(doc_findings)
    await emit_event(
        run_id,
        "node_finished",
        "doc_research",
        f"Document research completed with {len(deduped)} verified claims.",
    )

    return {
        "doc_findings": deduped,
        "llm_call_count": call_tracker["calls"],
    }
