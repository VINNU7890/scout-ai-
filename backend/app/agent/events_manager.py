from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, List, Optional

from backend.app.agent.events import AgentEvent, EventType
from backend.app.db import SessionLocal
from backend.app.models import RunEvent

logger = logging.getLogger("scoutai.events")

# Global in-memory broadcast queues per run_id
_run_queues: Dict[str, List[asyncio.Queue[AgentEvent]]] = {}
_run_counter: Dict[str, int] = {}
_run_cancellation: Dict[str, bool] = {}


def register_run_listener(run_id: str) -> asyncio.Queue[AgentEvent]:
    queue: asyncio.Queue[AgentEvent] = asyncio.Queue()
    if run_id not in _run_queues:
        _run_queues[run_id] = []
    _run_queues[run_id].append(queue)
    return queue


def unregister_run_listener(run_id: str, queue: asyncio.Queue[AgentEvent]) -> None:
    if run_id in _run_queues:
        if queue in _run_queues[run_id]:
            _run_queues[run_id].remove(queue)
        if not _run_queues[run_id]:
            _run_queues.pop(run_id, None)


def mark_run_cancelled(run_id: str) -> None:
    _run_cancellation[run_id] = True


def is_run_cancelled(run_id: str) -> bool:
    return _run_cancellation.get(run_id, False)


def clear_run_cancellation(run_id: str) -> None:
    _run_cancellation.pop(run_id, None)


async def emit_event(
    run_id: str,
    event: EventType,
    stage: str,
    message: str,
    data: Optional[dict] = None,
) -> AgentEvent:
    """Emits an event to all active SSE listeners and persists it to SQLite."""
    current_count = _run_counter.get(run_id, 0) + 1
    _run_counter[run_id] = current_count

    agent_event = AgentEvent(
        id=current_count,
        run_id=run_id,
        event=event,
        stage=stage,
        message=message,
        data=data,
    )

    # Persist in SQLite
    try:
        with SessionLocal() as db:
            db_event = RunEvent(
                run_id=run_id,
                event=event,
                stage=stage,
                message=message,
                data_json=json.dumps(data) if data is not None else None,
            )
            db.add(db_event)
            db.commit()
            agent_event.id = db_event.id
    except Exception as e:
        logger.warning(f"Could not persist event for run {run_id}: {e}")

    # Push to SSE queues
    listeners = _run_queues.get(run_id, [])
    for q in list(listeners):
        await q.put(agent_event)

    return agent_event
