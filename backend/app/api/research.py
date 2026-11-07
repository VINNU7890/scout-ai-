from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import AsyncGenerator, List, Optional

from fastapi import APIRouter, Header, HTTPException, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy import delete, desc, select

from backend.app.agent.events_manager import register_run_listener, unregister_run_listener
from backend.app.db import SessionLocal
from backend.app.models import ResearchRun, RunEvent
from backend.app.schemas import (
    AskQuestionRequest,
    AskQuestionResponse,
    CreateRunRequest,
    Finding,
    Report,
    ResearchOptions,
    ResearchPlan,
    RunListItem,
    RunResponse,
    SourceItem,
    VerificationResult,
)
from backend.app.services.research_service import (
    answer_followup_question,
    cancel_research_run,
    start_research_run,
)
from backend.app.tools.rag import get_rag_store
from backend.app.utils.rate_limit import check_rate_limit

router = APIRouter(prefix="/runs", tags=["research"])
logger = logging.getLogger("scoutai.api.research")


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_run(request: Request, body: CreateRunRequest) -> dict:
    check_rate_limit(request)
    run_id = f"run_{uuid.uuid4().hex[:12]}"

    # Combine options
    options_payload = body.options.model_dump()
    options_payload["document_ids"] = body.document_ids

    with SessionLocal() as db:
        run_record = ResearchRun(
            id=run_id,
            query=body.query,
            title=f"Research: {body.query[:40]}...",
            status="queued",
            options_json=json.dumps(options_payload),
        )
        db.add(run_record)
        db.commit()

    start_research_run(run_id)
    return {"run_id": run_id}


@router.get("", response_model=List[RunListItem])
def list_runs() -> List[RunListItem]:
    with SessionLocal() as db:
        runs = db.scalars(select(ResearchRun).order_by(desc(ResearchRun.created_at))).all()
        return [
            RunListItem(
                id=r.id,
                query=r.query,
                title=r.title,
                status=r.status,
                created_at=r.created_at.isoformat(),
                updated_at=r.updated_at.isoformat(),
            )
            for r in runs
        ]


@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: str) -> RunResponse:
    with SessionLocal() as db:
        r = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
        if not r:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "not_found", "message": f"Run '{run_id}' not found."}},
            )

        options = ResearchOptions(**(json.loads(r.options_json) if r.options_json else {}))
        plan = ResearchPlan(**json.loads(r.plan_json)) if r.plan_json else None
        report = Report(**json.loads(r.report_json)) if r.report_json else None
        findings = [Finding(**f) for f in json.loads(r.findings_json)] if r.findings_json else []
        sources = [SourceItem(**s) for s in json.loads(r.sources_json)] if r.sources_json else []
        verification = (
            VerificationResult(**json.loads(r.verification_json)) if r.verification_json else None
        )

        return RunResponse(
            run_id=r.id,
            query=r.query,
            status=r.status,  # type: ignore
            options=options,
            plan=plan,
            report=report,
            findings=findings,
            sources=sources,
            verification=verification,
            error_message=r.error_message,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat(),
        )


@router.post("/{run_id}/cancel", response_model=dict)
def cancel_run(run_id: str) -> dict:
    cancelled = cancel_research_run(run_id)
    return {"success": cancelled, "run_id": run_id}


@router.delete("/{run_id}", response_model=dict)
def delete_run(run_id: str) -> dict:
    with SessionLocal() as db:
        r = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
        if not r:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "not_found", "message": f"Run '{run_id}' not found."}},
            )
        db.execute(delete(ResearchRun).where(ResearchRun.id == run_id))
        db.execute(delete(RunEvent).where(RunEvent.run_id == run_id))
        db.commit()

    # Clean up vector collections
    rag_store = get_rag_store()
    rag_store.delete_collection(run_id)
    return {"deleted": True, "run_id": run_id}


@router.get("/{run_id}/stream")
async def stream_run_events(
    run_id: str,
    last_event_id: Optional[str] = Header(None, alias="Last-Event-ID"),
    query_last_id: Optional[int] = Query(None, alias="last_id"),
) -> StreamingResponse:
    """Streams live Server-Sent Events (SSE) for the research run."""
    with SessionLocal() as db:
        run_record = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
        if not run_record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": {"code": "not_found", "message": f"Run '{run_id}' not found."}},
            )

    start_from_id = query_last_id
    if start_from_id is None and last_event_id and last_event_id.isdigit():
        start_from_id = int(last_event_id)

    async def event_generator() -> AsyncGenerator[str, None]:
        # Yield catch-up events from DB if reconnecting
        if start_from_id is not None:
            with SessionLocal() as db:
                past_events = db.scalars(
                    select(RunEvent)
                    .where(RunEvent.run_id == run_id, RunEvent.id > start_from_id)
                    .order_by(RunEvent.id.asc())
                ).all()
                for pe in past_events:
                    payload = {
                        "id": pe.id,
                        "run_id": pe.run_id,
                        "event": pe.event,
                        "stage": pe.stage,
                        "message": pe.message,
                        "data": json.loads(pe.data_json) if pe.data_json else None,
                        "timestamp": pe.timestamp.isoformat(),
                    }
                    yield f"id: {pe.id}\nevent: {pe.event}\ndata: {json.dumps(payload)}\n\n"

        # Check if already finished
        with SessionLocal() as db:
            cur = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
            if cur and cur.status in ("completed", "failed", "cancelled"):
                # Send terminal message and finish
                yield f"event: {cur.status}\ndata: {json.dumps({'status': cur.status})}\n\n"
                return

        queue = register_run_listener(run_id)
        try:
            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield event.to_sse()
                    if event.event in ("run_completed", "run_cancelled", "error"):
                        break
                except asyncio.TimeoutError:
                    # Keep-alive SSE comment
                    yield ": ping\n\n"
                    with SessionLocal() as db:
                        check = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
                        if check and check.status in ("completed", "failed", "cancelled"):
                            break
        finally:
            unregister_run_listener(run_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{run_id}/ask", response_model=AskQuestionResponse)
async def ask_question(run_id: str, body: AskQuestionRequest) -> AskQuestionResponse:
    try:
        return await answer_followup_question(run_id, body.question)
    except Exception as e:
        logger.warning(f"Error answering follow-up question for {run_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "ask_failed", "message": str(e)}},
        )
