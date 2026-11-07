from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ResearchOptions(BaseModel):
    depth: Literal["quick", "standard", "deep"] = Field(
        default="standard",
        description="Depth of research (quick=2 queries/entity, standard=4 queries, deep=6 queries)",
    )
    max_sources_per_entity: int = Field(
        default=5, description="Maximum sources to fetch and parse per competitor entity"
    )
    include_docs: bool = Field(
        default=True, description="Whether to retrieve and cite from uploaded user documents"
    )
    focus_areas: List[str] = Field(
        default_factory=lambda: [
            "product",
            "pricing/fees",
            "trust & security",
            "compliance",
            "target users",
            "marketing/gtm",
        ],
        description="Selected aspect focus areas for research",
    )


class Finding(BaseModel):
    entity: str = Field(description="Name of the company/product entity")
    aspect: str = Field(description="Aspect category, e.g. product, pricing/fees, compliance")
    claim: str = Field(description="Extracted factual finding/claim")
    evidence_quote: str = Field(
        description="Direct snippet from source text supporting the claim (<= 25 words)"
    )
    source_url: Optional[str] = Field(default=None, description="URL of the web source")
    doc_name: Optional[str] = Field(default=None, description="Filename of uploaded document")
    page: Optional[int] = Field(default=None, description="Page number if from document")
    source_type: Literal["web", "doc"] = Field(description="Type of source")
    retrieved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp when finding was extracted",
    )
    confidence: Literal["low", "med", "high"] = Field(
        default="high", description="Confidence score in the finding"
    )


class ResearchPlan(BaseModel):
    entities: List[str] = Field(description="Identified competitor entities (capped at 6)")
    aspects: List[str] = Field(description="Aspects to compare (capped at 8)")
    sub_questions: Dict[str, List[str]] = Field(
        description="2-4 search sub-questions mapped per entity"
    )
    assumptions: List[str] = Field(
        default_factory=list, description="Sensible assumptions recorded if query was vague"
    )


class CompetitorProfile(BaseModel):
    entity: str
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    positioning: str = Field(default="Not found")
    pricing_notes: str = Field(default="Not found")
    trust_signals: List[str] = Field(default_factory=list)
    gtm_tactics: List[str] = Field(default_factory=list)
    aspect_scores: Dict[str, int] = Field(
        default_factory=dict, description="1-5 integer score per aspect"
    )
    aspect_rationales: Dict[str, str] = Field(
        default_factory=dict, description="One-line rationale for each aspect score"
    )


class SourceItem(BaseModel):
    id: int = Field(description="Numeric index for inline citation, e.g. [1]")
    title: str
    url: Optional[str] = None
    doc_name: Optional[str] = None
    page: Optional[int] = None
    domain: Optional[str] = None
    source_type: Literal["web", "doc"]
    retrieved_at: str
    supported_claims: List[str] = Field(default_factory=list)


class GtmAction(BaseModel):
    priority: Literal["High", "Medium", "Low"]
    title: str
    action: str
    rationale_and_evidence: str


class SWOTAnalysis(BaseModel):
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    threats: List[str] = Field(default_factory=list)


class VerificationIssue(BaseModel):
    claim: str
    source_ref: str
    reason: str
    severity: Literal["warning", "unsupported"] = "unsupported"


class VerificationResult(BaseModel):
    passed: bool
    issues: List[VerificationIssue] = Field(default_factory=list)
    summary: str = ""


class Report(BaseModel):
    title: str
    executive_summary: str = Field(description="Executive Summary under 150 words")
    key_takeaways: List[str] = Field(description="5 bullet key takeaways")
    comparison_table: Dict[str, Dict[str, str]] = Field(
        description="aspects (rows) -> entities (columns) -> summary/finding"
    )
    profiles: List[CompetitorProfile]
    swot: SWOTAnalysis
    gaps_and_opportunities: List[str]
    recommended_gtm_actions: List[GtmAction]
    methodology_and_limitations: str
    sources: List[SourceItem]
    markdown_content: str = ""
    warnings: List[str] = Field(default_factory=list)


# API Request/Response Schemas


class CreateRunRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Research query or prompt")
    options: ResearchOptions = Field(default_factory=ResearchOptions)
    document_ids: List[str] = Field(
        default_factory=list, description="IDs of uploaded documents to include"
    )


class RunResponse(BaseModel):
    run_id: str
    query: str
    status: Literal[
        "queued",
        "planning",
        "researching",
        "analyzing",
        "writing",
        "verifying",
        "completed",
        "failed",
        "cancelled",
    ]
    options: ResearchOptions
    plan: Optional[ResearchPlan] = None
    report: Optional[Report] = None
    findings: List[Finding] = Field(default_factory=list)
    sources: List[SourceItem] = Field(default_factory=list)
    verification: Optional[VerificationResult] = None
    error_message: Optional[str] = None
    created_at: str
    updated_at: str


class RunListItem(BaseModel):
    id: str
    query: str
    title: str
    status: str
    created_at: str
    updated_at: str


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size_bytes: int
    chunk_count: int
    created_at: str


class AskQuestionRequest(BaseModel):
    question: str = Field(..., min_length=2)


class AskQuestionResponse(BaseModel):
    answer: str
    citations: List[SourceItem] = Field(default_factory=list)
    follow_up_suggestions: List[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str = "ok"
    gemini_configured: bool
    gemini_model: str
    search_provider: str
    demo_mode: bool
