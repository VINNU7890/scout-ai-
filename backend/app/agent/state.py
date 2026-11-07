from __future__ import annotations

import operator
from typing import Annotated, List, Optional

from typing_extensions import TypedDict

from backend.app.schemas import (
    CompetitorProfile,
    Finding,
    Report,
    ResearchOptions,
    ResearchPlan,
    VerificationResult,
)


class ResearchState(TypedDict):
    run_id: str
    query: str
    options: ResearchOptions
    include_docs: bool
    document_ids: List[str]
    plan: Optional[ResearchPlan]
    web_findings: Annotated[List[Finding], operator.add]
    doc_findings: Annotated[List[Finding], operator.add]
    profiles: List[CompetitorProfile]
    report: Optional[Report]
    verification: Optional[VerificationResult]
    revision_count: int
    llm_call_count: int
    errors: Annotated[List[str], operator.add]
