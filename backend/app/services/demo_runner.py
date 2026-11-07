from __future__ import annotations

import asyncio
import json
import logging

from sqlalchemy import select

from backend.app.agent.events_manager import emit_event, is_run_cancelled
from backend.app.db import SessionLocal
from backend.app.demo_fixture import DEMO_RUN_DATA
from backend.app.models import ResearchRun
from backend.app.schemas import (
    CompetitorProfile,
    Finding,
    GtmAction,
    Report,
    ResearchPlan,
    SourceItem,
    SWOTAnalysis,
    VerificationResult,
)

logger = logging.getLogger("scoutai.demo")


async def run_demo_simulation(run_id: str) -> None:
    """Simulates a realistic live research run from the demo fixture with timed SSE events."""
    logger.info(f"Starting demo simulation for run {run_id}")

    # Build Report object from demo data
    profiles = [CompetitorProfile(**p) for p in DEMO_RUN_DATA["profiles"]]
    sources = [SourceItem(**s) for s in DEMO_RUN_DATA["sources"]]
    findings = [Finding(**f) for f in DEMO_RUN_DATA["findings"]]
    plan = ResearchPlan(**DEMO_RUN_DATA["plan"])

    report = Report(
        title=DEMO_RUN_DATA["title"],
        executive_summary=DEMO_RUN_DATA["executive_summary"],
        key_takeaways=DEMO_RUN_DATA["key_takeaways"],
        comparison_table=DEMO_RUN_DATA["comparison_table"],
        profiles=profiles,
        swot=SWOTAnalysis(**DEMO_RUN_DATA["swot"]),
        gaps_and_opportunities=DEMO_RUN_DATA["gaps_and_opportunities"],
        recommended_gtm_actions=[GtmAction(**a) for a in DEMO_RUN_DATA["recommended_gtm_actions"]],
        methodology_and_limitations=DEMO_RUN_DATA["methodology_and_limitations"],
        sources=sources,
        verification=VerificationResult(**DEMO_RUN_DATA["verification"]),
    )

    from backend.app.agent.nodes.writer import generate_markdown_report

    report.markdown_content = generate_markdown_report(report, "BitDelta India")

    # Simulation timeline steps: (event, stage, message, delay, data)
    steps = [
        ("run_started", "init", "Research run initialized: Competitor & Market Brief", 0.4, None),
        (
            "node_started",
            "plan",
            "Analyzing research prompt and structuring entities...",
            0.6,
            None,
        ),
        (
            "step",
            "plan",
            "Identified 5 target entities (BitDelta India, CoinDCX, CoinSwitch, ZebPay, Mudrex) and 6 aspects",
            0.7,
            {"plan": plan.model_dump()},
        ),
        (
            "node_finished",
            "plan",
            "Research plan finalized with 20 targeted search sub-questions.",
            0.5,
            None,
        ),
        (
            "node_started",
            "web_research",
            "Beginning live web intelligence gathering across search engines...",
            0.6,
            None,
        ),
        (
            "step",
            "web_research",
            "Searching: BitDelta India platform features trading pairs derivatives",
            0.6,
            None,
        ),
        ("step", "web_research", "Reading page: bitdelta.com/en/about-us...", 0.5, None),
        (
            "finding_added",
            "web_research",
            "Verified claim for BitDelta India: Multi-asset trading with 400+ spot pairs...",
            0.5,
            {"finding": findings[0].model_dump()},
        ),
        (
            "step",
            "web_research",
            "Searching: FIU India registered reporting entities VDA registry",
            0.6,
            None,
        ),
        (
            "step",
            "web_research",
            "Reading page: fiuindia.gov.in/vda-compliance-registry...",
            0.5,
            None,
        ),
        (
            "finding_added",
            "web_research",
            "Verified claim for CoinDCX: Registered with FIU-IND & ISO 27001...",
            0.5,
            {"finding": findings[2].model_dump()},
        ),
        ("step", "web_research", "Reading page: coinswitch.co/pro-trading-deep-dive...", 0.5, None),
        (
            "finding_added",
            "web_research",
            "Verified claim for CoinSwitch: Order book aggregator across domestic venues...",
            0.5,
            {"finding": findings[3].model_dump()},
        ),
        (
            "step",
            "web_research",
            "Searching: Mudrex thematic crypto baskets Coin Sets licensing",
            0.6,
            None,
        ),
        (
            "finding_added",
            "web_research",
            "Verified claim for Mudrex: Thematic Coin Sets and EU VASP registration...",
            0.5,
            {"finding": findings[4].model_dump()},
        ),
        (
            "node_finished",
            "web_research",
            "Web research completed. Extracted 6 verified claims with evidence quotes.",
            0.5,
            None,
        ),
        (
            "node_started",
            "analyze",
            "Synthesizing competitive profiles and scoring aspects (1-5)...",
            0.6,
            None,
        ),
        (
            "step",
            "analyze",
            "Scoring BitDelta India: Product (4/5), Pricing (4/5), Compliance (3/5)...",
            0.5,
            None,
        ),
        (
            "step",
            "analyze",
            "Scoring CoinDCX & CoinSwitch: Compliance (5/5), GTM (5/5)...",
            0.5,
            None,
        ),
        ("node_finished", "analyze", "Strategic scoring completed for all 5 entities.", 0.5, None),
        (
            "node_started",
            "write",
            "Drafting executive brief, SWOT matrix, and GTM action plan...",
            0.6,
            None,
        ),
        (
            "report_ready",
            "write",
            "Executive report generated with comparison matrix and inline citations.",
            0.5,
            {"title": report.title},
        ),
        ("node_finished", "write", "Report drafting complete.", 0.4, None),
        (
            "node_started",
            "verify",
            "Cross-checking citations [1]-[6] against stored evidence quotes...",
            0.6,
            None,
        ),
        (
            "step",
            "verify",
            "All 6 citations verified with 100% quote fidelity. Zero hallucinations detected.",
            0.5,
            None,
        ),
        ("node_finished", "verify", "Verification pass completed successfully.", 0.4, None),
        (
            "run_completed",
            "done",
            "Competitive research brief is ready to review and export.",
            0.2,
            None,
        ),
    ]

    for event_type, stage, msg, delay, data in steps:
        if is_run_cancelled(run_id):
            logger.info(f"Demo run {run_id} cancelled.")
            await emit_event(run_id, "run_cancelled", stage, "Run cancelled by user.")
            with SessionLocal() as db:
                r_db = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
                if r_db:
                    r_db.status = "cancelled"
                    db.commit()
            return

        await asyncio.sleep(delay)
        await emit_event(run_id, event_type, stage, msg, data)

    # Persist final state in SQLite
    with SessionLocal() as db:
        run_record = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
        if run_record:
            run_record.status = "completed"
            run_record.title = report.title
            run_record.plan_json = json.dumps(plan.model_dump())
            run_record.report_json = json.dumps(report.model_dump())
            run_record.findings_json = json.dumps([f.model_dump() for f in findings])
            run_record.sources_json = json.dumps([s.model_dump() for s in sources])
            run_record.verification_json = json.dumps(DEMO_RUN_DATA["verification"])
            db.commit()
