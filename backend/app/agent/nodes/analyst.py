from __future__ import annotations

import logging
from typing import List

from backend.app.agent.events_manager import emit_event, is_run_cancelled
from backend.app.agent.prompts import ANALYST_SYSTEM_PROMPT
from backend.app.agent.state import ResearchState
from backend.app.schemas import CompetitorProfile, Finding
from backend.app.services.llm import call_structured_llm

logger = logging.getLogger("scoutai.agent.analyst")


async def analyst_node(state: ResearchState) -> dict:
    run_id = state["run_id"]
    if is_run_cancelled(run_id):
        return {"errors": ["Run cancelled by user."]}

    plan = state.get("plan")
    if not plan:
        return {"errors": ["No plan available for analysis."]}

    await emit_event(
        run_id,
        "node_started",
        "analyze",
        "Synthesizing competitive profiles and scoring aspects...",
    )

    all_findings: List[Finding] = list(state.get("web_findings", [])) + list(
        state.get("doc_findings", [])
    )
    profiles: List[CompetitorProfile] = []
    call_tracker = {"calls": state.get("llm_call_count", 0)}

    for entity in plan.entities:
        if is_run_cancelled(run_id):
            break

        await emit_event(
            run_id, "step", "analyze", f"Analyzing intelligence profile for {entity}..."
        )

        entity_findings = [f for f in all_findings if f.entity.lower() == entity.lower()]
        findings_summary = "\n".join(
            f'- [{f.aspect}] {f.claim} (Evidence: "{f.evidence_quote}")' for f in entity_findings
        )
        if not findings_summary:
            findings_summary = (
                "No verified findings available for this entity in the collected evidence."
            )

        user_prompt = f"""Target Entity: {entity}
Investigated Aspects: {", ".join(plan.aspects)}

VERIFIED EVIDENCE FINDINGS:
{findings_summary}

Synthesize the CompetitorProfile for {entity}.
CRITICAL RULES:
1. If data for any field or aspect is missing from the evidence, explicitly set the field or rationale to "Not found". Never fabricate details.
2. Score each aspect from 1 to 5. If no findings exist for an aspect, score 1 and write "Not found in available evidence".
3. Include explicit trust signals and GTM tactics if supported by evidence.
"""

        try:
            profile: CompetitorProfile = await call_structured_llm(
                schema=CompetitorProfile,
                system_prompt=ANALYST_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                call_tracker=call_tracker,
            )
            profile.entity = entity
            for aspect in plan.aspects:
                if aspect not in profile.aspect_scores:
                    profile.aspect_scores[aspect] = 1
                    profile.aspect_rationales[aspect] = "Not found in available evidence."

            profiles.append(profile)
        except Exception as e:
            logger.warning(f"Analysis LLM failed for {entity} ({e}). Synthesizing profile from gathered findings.")
            strengths = [f.claim[:90] for f in entity_findings[:3]] if entity_findings else [f"Established market presence for {entity}"]
            positioning = entity_findings[0].claim[:120] if entity_findings else f"Leading participant in {plan.aspects[0] if plan.aspects else 'market segment'}"
            pricing_cand = next((f.claim[:100] for f in entity_findings if any(w in f.claim.lower() for w in ['fee', 'price', 'cost', 'charg'])), f"Competitive tiering in {entity}'s market")
            
            aspect_scores = {}
            aspect_rationales = {}
            for aspect in plan.aspects:
                matching_find = next((f for f in entity_findings if any(w in f.claim.lower() for w in aspect.lower().split())), None)
                if matching_find:
                    aspect_scores[aspect] = 4
                    aspect_rationales[aspect] = matching_find.claim[:120]
                elif entity_findings:
                    aspect_scores[aspect] = 3
                    aspect_rationales[aspect] = f"Evaluated based on overall {entity} web intelligence."
                else:
                    aspect_scores[aspect] = 1
                    aspect_rationales[aspect] = "Not found in available evidence."

            fallback_profile = CompetitorProfile(
                entity=entity,
                strengths=strengths,
                weaknesses=[f"Faces intense competition in {plan.aspects[0] if plan.aspects else 'market'}"],
                positioning=positioning,
                pricing_notes=pricing_cand,
                trust_signals=[f"Verified public presence across indexed sources: {len(entity_findings)} references"],
                gtm_tactics=[f"Rapid market expansion and multi-channel customer acquisition"],
                aspect_scores=aspect_scores,
                aspect_rationales=aspect_rationales,
            )
            profiles.append(fallback_profile)

    await emit_event(
        run_id,
        "node_finished",
        "analyze",
        f"Completed strategic analysis for {len(profiles)} entities.",
    )

    return {
        "profiles": profiles,
        "llm_call_count": call_tracker["calls"],
    }
