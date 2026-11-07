from typing import Any, Type

import pytest
from pydantic import BaseModel

import backend.app.agent.nodes.web_researcher as web_module
from backend.app.agent.graph import compile_research_graph
from backend.app.agent.nodes.web_researcher import ExtractedFindingsContainer
from backend.app.agent.state import ResearchState
from backend.app.schemas import (
    CompetitorProfile,
    Finding,
    GtmAction,
    Report,
    ResearchOptions,
    ResearchPlan,
    SourceItem,
    SWOTAnalysis,
    VerificationIssue,
    VerificationResult,
)
from backend.app.services.llm import set_mock_llm
from backend.app.tools.fetch import FetchedPage


@pytest.mark.asyncio
async def test_full_agent_graph_with_fake_llm_and_verifier_loop(monkeypatch):
    verification_call_count = 0

    # Mock page fetcher to avoid external requests
    async def fake_fetch(url, client=None):
        return FetchedPage(
            url=url,
            title="Fake Source",
            content="BitDelta features multi-asset trading engine with copy trading and multi-sig security.",
            success=True,
        )

    monkeypatch.setattr(web_module, "fetch_and_clean_page", fake_fetch)

    # Fake Search Provider
    class FakeSearchProvider:
        async def search(self, query: str, max_results: int = 5):
            from backend.app.tools.search import SearchResult

            return [
                SearchResult(
                    title="BitDelta Official",
                    url="https://bitdelta.com/about",
                    snippet="BitDelta trading platform features and security",
                )
            ]

    monkeypatch.setattr(web_module, "get_search_provider", lambda: FakeSearchProvider())

    def fake_llm_handler(schema: Type[BaseModel], system_prompt: str, user_prompt: str) -> Any:
        nonlocal verification_call_count

        if schema == ResearchPlan:
            return ResearchPlan(
                entities=["BitDelta", "CompetitorX"],
                aspects=["product", "compliance"],
                sub_questions={
                    "BitDelta": ["BitDelta product features"],
                    "CompetitorX": ["CompetitorX product features"],
                },
                assumptions=["Test assumption"],
            )

        elif schema == ExtractedFindingsContainer:
            return ExtractedFindingsContainer(
                findings=[
                    Finding(
                        entity="BitDelta",
                        aspect="product",
                        claim="BitDelta features multi-asset trading engine with copy trading.",
                        evidence_quote="multi-asset trading engine with copy trading",
                        source_url="https://bitdelta.com/about",
                        source_type="web",
                        confidence="high",
                    )
                ]
            )

        elif schema == CompetitorProfile:
            # Check entity in user prompt
            if "CompetitorX" in user_prompt:
                return CompetitorProfile(
                    entity="CompetitorX",
                    strengths=["Not found"],
                    weaknesses=["Not found"],
                    positioning="Not found",
                    pricing_notes="Not found",
                    trust_signals=[],
                    gtm_tactics=[],
                    aspect_scores={"product": 1, "compliance": 1},
                    aspect_rationales={
                        "product": "Not found in available evidence.",
                        "compliance": "Not found in available evidence.",
                    },
                )
            return CompetitorProfile(
                entity="BitDelta",
                strengths=["Multi-asset engine", "Copy trading"],
                weaknesses=["Emerging brand"],
                positioning="Pro-retail derivatives exchange",
                pricing_notes="0.10% maker/taker",
                trust_signals=["Multi-sig cold storage"],
                gtm_tactics=["Trading competitions"],
                aspect_scores={"product": 5, "compliance": 4},
                aspect_rationales={
                    "product": "Robust multi-asset engine.",
                    "compliance": "Active licensing filings.",
                },
            )

        elif schema == Report:
            return Report(
                title="Test Competitive Report",
                executive_summary="BitDelta leads in product breadth [1]. Unverified fabricated claim about zero fees everywhere [1].",
                key_takeaways=[
                    "BitDelta has 400+ pairs [1].",
                    "Copy trading provides differentiation [1].",
                    "CompetitorX data was not found [1].",
                    "Security is anchored in multi-sig custody [1].",
                    "GTM centers on active traders [1].",
                ],
                comparison_table={
                    "product": {"BitDelta": "Derivatives & Spot", "CompetitorX": "Not found"}
                },
                profiles=[],
                swot=SWOTAnalysis(
                    strengths=["Product diversity [1]"],
                    weaknesses=["Brand recognition [1]"],
                    opportunities=["Market expansion [1]"],
                    threats=["Regulatory changes [1]"],
                ),
                gaps_and_opportunities=["Copy trading whitespace"],
                recommended_gtm_actions=[
                    GtmAction(
                        priority="High",
                        title="Focus on derivatives",
                        action="Highlight copy trading engine",
                        rationale_and_evidence="Evidence proves product breadth [1]",
                    )
                ],
                methodology_and_limitations="Automated synthesis with citations.",
                sources=[
                    SourceItem(
                        id=1,
                        title="BitDelta Official",
                        url="https://bitdelta.com/about",
                        domain="bitdelta.com",
                        source_type="web",
                        retrieved_at="2026-11-05T00:00:00Z",
                        supported_claims=["Multi-asset trading engine"],
                    )
                ],
            )

        elif schema == VerificationResult:
            verification_call_count += 1
            # FIRST CALL: Fail deliberately with an unsupported claim issue to test the verifier loop!
            if verification_call_count == 1:
                return VerificationResult(
                    passed=False,
                    issues=[
                        VerificationIssue(
                            claim="Unverified fabricated claim about zero fees everywhere",
                            source_ref="[1]",
                            reason="Evidence quote does not substantiate zero fees everywhere.",
                            severity="unsupported",
                        )
                    ],
                    summary="Deliberately unsupported claim detected by verifier.",
                )
            # SECOND CALL (after writer revises): Pass
            return VerificationResult(
                passed=True,
                issues=[],
                summary="All claims substantiated.",
            )

        return schema()

    set_mock_llm(fake_llm_handler)

    try:
        graph = compile_research_graph()
        initial_state: ResearchState = {
            "run_id": "test_agent_run_001",
            "query": "Compare BitDelta and CompetitorX",
            "options": ResearchOptions(depth="quick", max_sources_per_entity=1, include_docs=False),
            "include_docs": False,
            "document_ids": [],
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

        # Assertions
        # 1. Verifier loop triggered: verification was called twice, revision_count >= 1
        assert verification_call_count >= 2, (
            f"Expected verifier to be called at least twice, got {verification_call_count}"
        )
        assert final_state["revision_count"] >= 1

        # 2. Findings carry sources
        findings = final_state["web_findings"]
        assert len(findings) > 0
        for f in findings:
            assert f.source_url == "https://bitdelta.com/about"
            assert f.source_type == "web"
            assert len(f.evidence_quote.split()) <= 25

        # 3. Report exists with profiles
        report = final_state["report"]
        assert report is not None
        assert len(report.profiles) == 2

        # 4. "Not found" is used for missing competitor data rather than fabricated info
        comp_x_profile = next(p for p in report.profiles if p.entity == "CompetitorX")
        assert comp_x_profile.positioning == "Not found"
        assert comp_x_profile.pricing_notes == "Not found"
        assert comp_x_profile.aspect_scores["product"] == 1
        assert "Not found" in comp_x_profile.aspect_rationales["product"]

    finally:
        set_mock_llm(None)
