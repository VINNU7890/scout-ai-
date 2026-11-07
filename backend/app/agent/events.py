from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

EventType = Literal[
    "run_started",
    "node_started",
    "step",
    "finding_added",
    "node_finished",
    "warning",
    "error",
    "report_ready",
    "run_completed",
    "run_cancelled",
]


class AgentEvent(BaseModel):
    id: int = Field(default=0, description="Sequential event ID for Last-Event-ID reconnection")
    run_id: str
    event: EventType
    stage: str = Field(
        default="init",
        description="plan | web_research | doc_research | analyze | write | verify | done",
    )
    message: str = Field(description="Human readable progress message")
    data: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional payload (e.g. finding, report summary)"
    )
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_sse(self) -> str:
        """Formats the event into standard SSE line block."""
        import json

        payload = self.model_dump()
        return f"id: {self.id}\nevent: {self.event}\ndata: {json.dumps(payload)}\n\n"
