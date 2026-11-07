from __future__ import annotations

import asyncio
import json
import logging
from typing import List, Optional

from pydantic import BaseModel
from sqlalchemy import select

from backend.app.agent.events_manager import (
    clear_run_cancellation,
    emit_event,
    is_run_cancelled,
    mark_run_cancelled,
)
from backend.app.agent.graph import compile_research_graph
from backend.app.agent.prompts import ASK_QA_SYSTEM_PROMPT
from backend.app.agent.state import ResearchState
from backend.app.config import get_settings
from backend.app.db import SessionLocal
from backend.app.models import ResearchRun
from backend.app.schemas import (
    AskQuestionResponse,
    Report,
    ResearchOptions,
    ResearchPlan,
    SourceItem,
    VerificationResult,
)
from backend.app.services.demo_runner import run_demo_simulation
from backend.app.services.llm import call_structured_llm

logger = logging.getLogger("scoutai.services.research")
settings = get_settings()

_research_tasks: dict[str, asyncio.Task] = {}


class AskAnswerSchema(BaseModel):
    answer: str
    cited_source_ids: List[int]
    follow_up_suggestions: List[str]


async def execute_research_run(run_id: str) -> None:
    """Executes the full research graph or demo simulation in background."""
    clear_run_cancellation(run_id)

    with SessionLocal() as db:
        run_record = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
        if not run_record:
            logger.error(f"Run {run_id} not found in database.")
            return

        query = run_record.query
        options_dict = json.loads(run_record.options_json) if run_record.options_json else {}
        options = ResearchOptions(**options_dict)
        document_ids = options_dict.get("document_ids", [])

        run_record.status = "planning"
        db.commit()

    # If demo mode is active, simulate run
    if settings.DEMO_MODE:
        try:
            await run_demo_simulation(run_id)
        except Exception as e:
            logger.exception(f"Demo simulation failed for {run_id}: {e}")
            with SessionLocal() as db:
                r = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
                if r:
                    r.status = "failed"
                    r.error_message = str(e)
                    db.commit()
            await emit_event(run_id, "error", "done", f"Demo simulation failed: {e}")
        return

    # Real LangGraph execution
    try:
        await emit_event(
            run_id, "run_started", "init", f"Initiating research investigation for: {query}"
        )

        graph = compile_research_graph()
        initial_state: ResearchState = {
            "run_id": run_id,
            "query": query,
            "options": options,
            "include_docs": options.include_docs,
            "document_ids": document_ids,
            "plan": None,
            "web_findings": [],
            "doc_findings": [],
            "profiles": [],
            "report": None,
            "verification": None,
            "revision_count": 0,
            "llm_call_count": 0,
            "errors": [],
        }

        final_state = await graph.ainvoke(initial_state)

        if is_run_cancelled(run_id):
            with SessionLocal() as db:
                r = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
                if r:
                    r.status = "cancelled"
                    db.commit()
            await emit_event(run_id, "run_cancelled", "done", "Research cancelled by user.")
            return

        report: Optional[Report] = final_state.get("report")
        plan: Optional[ResearchPlan] = final_state.get("plan")
        all_findings = list(final_state.get("web_findings", [])) + list(
            final_state.get("doc_findings", [])
        )
        verification: Optional[VerificationResult] = final_state.get("verification")
        errors = final_state.get("errors", [])

        with SessionLocal() as db:
            r = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
            if r:
                r.status = "completed"
                if report:
                    r.title = report.title
                    r.report_json = json.dumps(report.model_dump())
                    r.sources_json = json.dumps([s.model_dump() for s in report.sources])
                if plan:
                    r.plan_json = json.dumps(plan.model_dump())
                if all_findings:
                    r.findings_json = json.dumps([f.model_dump() for f in all_findings])
                if verification:
                    r.verification_json = json.dumps(verification.model_dump())
                if errors:
                    r.error_message = "; ".join(errors[:5])
                db.commit()

        await emit_event(
            run_id, "run_completed", "done", "Competitive research report compiled and verified."
        )

    except Exception as e:
        logger.exception(f"Research run {run_id} failed: {e}")
        with SessionLocal() as db:
            r = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
            if r:
                r.status = "failed"
                r.error_message = str(e)
                db.commit()
        await emit_event(run_id, "error", "done", f"Research run failed: {e}")
    finally:
        _research_tasks.pop(run_id, None)


def start_research_run(run_id: str) -> None:
    task = asyncio.create_task(execute_research_run(run_id))
    _research_tasks[run_id] = task


def cancel_research_run(run_id: str) -> bool:
    mark_run_cancelled(run_id)
    task = _research_tasks.get(run_id)
    if task and not task.done():
        task.cancel()
    with SessionLocal() as db:
        r = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
        if r:
            r.status = "cancelled"
            db.commit()
            return True
    return False


async def answer_followup_question(run_id: str, question: str) -> AskQuestionResponse:
    """Answers a grounded follow-up question over a completed report and findings."""
    with SessionLocal() as db:
        r = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
        if not r or not r.report_json:
            raise ValueError(f"Finished report not found for run {run_id}")

        report_dict = json.loads(r.report_json)
        sources_dict = json.loads(r.sources_json) if r.sources_json else []
        findings_dict = json.loads(r.findings_json) if r.findings_json else []

    sources = [SourceItem(**s) for s in sources_dict]
    sources_text = "\n".join(f"[{s.id}] {s.title} ({s.url or s.doc_name})" for s in sources)
    findings_text = "\n".join(
        f'- [{f.get("entity")}] {f.get("claim")} (Evidence: "{f.get("evidence_quote")}")'
        for f in findings_dict[:30]
    )

    user_prompt = f"""REPORT EXECUTIVE SUMMARY:
{report_dict.get("executive_summary")}

AVAILABLE SOURCES:
{sources_text}

VERIFIED FINDINGS:
{findings_text}

USER QUESTION:
{question}

Provide a grounded, cited answer conforming to the schema with 2-3 logical follow-up exploration suggestion chips.
"""

    try:
        res: AskAnswerSchema = await call_structured_llm(
            schema=AskAnswerSchema,
            system_prompt=ASK_QA_SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )
        cited_sources = [s for s in sources if s.id in res.cited_source_ids]
        return AskQuestionResponse(
            answer=res.answer,
            citations=cited_sources,
            follow_up_suggestions=res.follow_up_suggestions,
        )
    except Exception as e:
        logger.warning(f"Follow-up QA LLM call failed ({e}), returning fallback answer")
        return AskQuestionResponse(
            answer=f"Based on the intelligence report, {report_dict.get('title')}: {report_dict.get('executive_summary')}",
            citations=sources[:2],
            follow_up_suggestions=[
                "Compare fee tiers across all competitors",
                "What are the top regulatory risks identified?",
                "Which entity has the strongest go-to-market advantage?",
            ],
        )
