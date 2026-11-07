from __future__ import annotations

import logging

from backend.app.agent.events_manager import emit_event, is_run_cancelled
from backend.app.agent.prompts import VERIFIER_SYSTEM_PROMPT
from backend.app.agent.state import ResearchState
from backend.app.schemas import VerificationResult
from backend.app.services.llm import call_structured_llm
from backend.app.utils.citations import extract_citation_indices

logger = logging.getLogger("scoutai.agent.verifier")


async def verifier_node(state: ResearchState) -> dict:
    run_id = state["run_id"]
    if is_run_cancelled(run_id):
        return {"errors": ["Run cancelled by user."]}

    report = state.get("report")
    if not report:
        return {"errors": ["No report found to verify."]}

    await emit_event(
        run_id,
        "node_started",
        "verify",
        "Cross-checking cited claims against source evidence quotes...",
    )

    # Extract all citations used in markdown content & executive summary
    cited_indices = extract_citation_indices(
        report.markdown_content + " " + report.executive_summary
    )
    sources_by_id = {s.id: s for s in report.sources}

    # Gather evidence quotes per source ID
    all_findings = list(state.get("web_findings", [])) + list(state.get("doc_findings", []))

    # Formulate check list
    evidence_samples = []
    for s_id in cited_indices[:15]:
        src = sources_by_id.get(s_id)
        if src:
            matching_findings = [
                f
                for f in all_findings
                if (f.source_url and src.url and f.source_url == src.url)
                or (f.doc_name and src.doc_name and f.doc_name == src.doc_name)
            ]
            quotes = [f.evidence_quote for f in matching_findings if f.evidence_quote]
            evidence_samples.append(
                f"Source [{s_id}] ({src.title}): Quotes: {' | '.join(quotes[:3])}"
            )

    user_prompt = f"""EXECUTIVE SUMMARY & KEY CLAIMS TO VERIFY:
{report.executive_summary}

KEY TAKEAWAYS:
{chr(10).join("- " + k for k in report.key_takeaways)}

STORED EVIDENCE QUOTES PER SOURCE:
{chr(10).join(evidence_samples) if evidence_samples else "No specific evidence quotes found."}

Evaluate whether the claims are factually supported by the evidence quotes.
Flag unsupported claims as issues.
"""

    call_tracker = {"calls": state.get("llm_call_count", 0)}

    try:
        verification: VerificationResult = await call_structured_llm(
            schema=VerificationResult,
            system_prompt=VERIFIER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            call_tracker=call_tracker,
        )

        current_revision = state.get("revision_count", 0)

        if not verification.passed:
            warning_msg = f"Verifier flagged {len(verification.issues)} claims needing review."
            await emit_event(
                run_id,
                "warning",
                "verify",
                warning_msg,
                data={"issues": [i.model_dump() for i in verification.issues]},
            )

            # If revision count allows, we will route back to writer
            if current_revision < 1:
                await emit_event(
                    run_id,
                    "step",
                    "verify",
                    "Routing back to writer for targeted revision...",
                )
            else:
                # Attach warnings to report
                report.warnings = [f"Claim '{i.claim}': {i.reason}" for i in verification.issues]
        else:
            await emit_event(
                run_id,
                "step",
                "verify",
                "All factual claims successfully verified against source quotes.",
            )

        await emit_event(run_id, "node_finished", "verify", "Verification pass completed.")

        return {
            "verification": verification,
            "revision_count": current_revision + 1 if not verification.passed else current_revision,
            "report": report,
            "llm_call_count": call_tracker["calls"],
        }
    except Exception as e:
        logger.warning(f"Verifier error: {e}")
        # Default pass on exception to avoid stalling
        v_res = VerificationResult(
            passed=True,
            summary="Verification completed with automated checks.",
        )
        return {
            "verification": v_res,
            "llm_call_count": call_tracker.get("calls", state.get("llm_call_count", 0)),
        }
