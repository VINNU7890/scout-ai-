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
            # Verify aspect scores exist for all plan aspects
            for aspect in plan.aspects:
                if aspect not in profile.aspect_scores:
                    profile.aspect_scores[aspect] = 1
                    profile.aspect_rationales[aspect] = "Not found in available evidence."

            profiles.append(profile)
        except Exception as e:
            logger.warning(f"Analysis failed for {entity}: {e}")
            # Fallback profile strictly with "Not found"
            fallback_profile = CompetitorProfile(
                entity=entity,
                strengths=["Not found"],
                weaknesses=["Not found"],
                positioning="Not found",
                pricing_notes="Not found",
                trust_signals=["Not found"],
                gtm_tactics=["Not found"],
                aspect_scores={aspect: 1 for aspect in plan.aspects},
                aspect_rationales={
                    aspect: "Not found in available evidence." for aspect in plan.aspects
                },
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
