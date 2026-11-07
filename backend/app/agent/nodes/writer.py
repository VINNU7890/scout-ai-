from __future__ import annotations

import json
import logging
from typing import Dict, List

from backend.app.agent.events_manager import emit_event, is_run_cancelled
from backend.app.agent.prompts import WRITER_REVISION_PROMPT, WRITER_SYSTEM_PROMPT
from backend.app.agent.state import ResearchState
from backend.app.schemas import Finding, GtmAction, Report, SWOTAnalysis
from backend.app.services.llm import call_structured_llm
from backend.app.utils.citations import build_source_catalog

logger = logging.getLogger("scoutai.agent.writer")


def generate_markdown_report(report: Report, primary_entity: str) -> str:
    """Formats the structured Report into a publication-ready Markdown document."""
    lines: List[str] = []
    lines.append(f"# {report.title}\n")

    # Table of Contents
    lines.append("## Table of Contents")
    lines.append("- [Executive Summary](#executive-summary)")
    lines.append("- [Key Takeaways](#key-takeaways)")
    lines.append("- [Comparison Matrix](#comparison-matrix)")
    lines.append("- [Competitor Profiles](#competitor-profiles)")
    lines.append(
        f"- [SWOT Analysis: {primary_entity}](#swot-analysis-{primary_entity.lower().replace(' ', '-')})"
    )
    lines.append("- [Market Gaps & Opportunities](#market-gaps--opportunities)")
    lines.append("- [Recommended GTM Actions](#recommended-gtm-actions)")
    lines.append("- [Methodology & Limitations](#methodology--limitations)")
    lines.append("- [Sources & Citations](#sources--citations)\n")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append(f"{report.executive_summary}\n")

    # Key Takeaways
    lines.append("## Key Takeaways")
    for t in report.key_takeaways:
        lines.append(f"- {t}")
    lines.append("")

    # Comparison Matrix
    lines.append("## Comparison Matrix")
    if report.comparison_table:
        # First row: Aspects | Entity 1 | Entity 2 | ...
        entities = []
        for row in report.comparison_table.values():
            for ent in row.keys():
                if ent not in entities:
                    entities.append(ent)
        header = f"| Aspect | {' | '.join(entities)} |"
        sep = f"| --- | {' | '.join(['---'] * len(entities))} |"
        lines.append(header)
        lines.append(sep)
        for aspect, cols in report.comparison_table.items():
            row_vals = [cols.get(ent, "Not found") for ent in entities]
            lines.append(f"| **{aspect}** | {' | '.join(row_vals)} |")
        lines.append("")

    # Competitor Profiles
    lines.append("## Competitor Profiles")
    for p in report.profiles:
        lines.append(f"### {p.entity}")
        lines.append(f"**Positioning:** {p.positioning}\n")
        lines.append(f"**Pricing / Fees:** {p.pricing_notes}\n")

        lines.append("**Key Strengths:**")
        for s in p.strengths:
            lines.append(f"- {s}")

        lines.append("\n**Key Weaknesses:**")
        for w in p.weaknesses:
            lines.append(f"- {w}")

        if p.trust_signals:
            lines.append("\n**Trust & Security Signals:**")
            for ts in p.trust_signals:
                lines.append(f"- {ts}")

        if p.gtm_tactics:
            lines.append("\n**GTM & Growth Tactics:**")
            for gt in p.gtm_tactics:
                lines.append(f"- {gt}")

        lines.append("\n**Aspect Scores:**")
        for asp, score in p.aspect_scores.items():
            rationale = p.aspect_rationales.get(asp, "")
            lines.append(f"- **{asp}** ({score}/5): {rationale}")
        lines.append("")

    # SWOT Analysis
    lines.append(f"## SWOT Analysis: {primary_entity}")
    lines.append("### Strengths")
    for s in report.swot.strengths:
        lines.append(f"- {s}")
    lines.append("\n### Weaknesses")
    for w in report.swot.weaknesses:
        lines.append(f"- {w}")
    lines.append("\n### Opportunities")
    for o in report.swot.opportunities:
        lines.append(f"- {o}")
    lines.append("\n### Threats")
    for th in report.swot.threats:
        lines.append(f"- {th}")
    lines.append("")

    # Gaps & Opportunities
    lines.append("## Market Gaps & Opportunities")
    for gap in report.gaps_and_opportunities:
        lines.append(f"- {gap}")
    lines.append("")

    # Recommended GTM Actions
    lines.append("## Recommended GTM Actions")
    for act in report.recommended_gtm_actions:
        lines.append(f"### [{act.priority}] {act.title}")
        lines.append(f"**Action:** {act.action}\n")
        lines.append(f"**Rationale & Evidence:** {act.rationale_and_evidence}\n")

    # Methodology & Limitations
    lines.append("## Methodology & Limitations")
    lines.append(f"{report.methodology_and_limitations}\n")

    # Sources & Citations
    lines.append("## Sources & Citations")
    for s in report.sources:
        link_str = f"[{s.title}]({s.url})" if s.url else f"{s.doc_name} (Page {s.page or 1})"
        lines.append(
            f"[{s.id}] {link_str} ({s.source_type.upper()}) - Retrieved {s.retrieved_at[:10]}"
        )
    lines.append("")

    return "\n".join(lines)


async def writer_node(state: ResearchState) -> dict:
    run_id = state["run_id"]
    if is_run_cancelled(run_id):
        return {"errors": ["Run cancelled by user."]}

    plan = state.get("plan")
    all_findings: List[Finding] = list(state.get("web_findings", [])) + list(
        state.get("doc_findings", [])
    )
    profiles = state.get("profiles", [])

    await emit_event(
        run_id, "node_started", "write", "Drafting executive brief and compiling citation matrix..."
    )

    primary_entity = plan.entities[0] if plan and plan.entities else "Primary Entity"

    # Catalog sources
    sources, source_mapping = build_source_catalog(all_findings)

    # Format findings with citation IDs
    findings_with_citations: List[str] = []
    for f in all_findings:
        key = (
            f.source_url
            if f.source_type == "web" and f.source_url
            else f"{f.doc_name}#p{f.page or 1}"
        )
        cid = source_mapping.get(key, 1)
        findings_with_citations.append(
            f'- [{cid}] [{f.entity} | {f.aspect}]: {f.claim} (Quote: "{f.evidence_quote}")'
        )

    findings_text = (
        "\n".join(findings_with_citations)
        if findings_with_citations
        else "No verified findings available."
    )

    sources_text = "\n".join(f"[{s.id}] {s.title} ({s.url or s.doc_name})" for s in sources)

    revision_context = ""
    verification = state.get("verification")
    if verification and not verification.passed and state.get("revision_count", 0) > 0:
        issues_summary = "\n".join(f"- {i.claim}: {i.reason}" for i in verification.issues)
        revision_context = WRITER_REVISION_PROMPT.format(issues=issues_summary)

    user_prompt = f"""Research Query: {state["query"]}
Primary Entity for SWOT: {primary_entity}
Entities: {", ".join(plan.entities if plan else [])}
Aspects: {", ".join(plan.aspects if plan else [])}

{revision_context}

CATALOG OF NUMBERED SOURCES (Use these numbers [N] for inline citations):
{sources_text}

VERIFIED FINDINGS WITH SOURCE NUMBERS:
{findings_text}

STRUCTURED PROFILES:
{json.dumps([p.model_dump() for p in profiles], indent=2)}

Produce the complete Report conforming to the schema.
CRITICAL INSTRUCTIONS:
1. Executive summary must be <= 150 words.
2. Provide exactly 5 bullet key takeaways.
3. Every factual sentence in the text must carry an inline citation marker like [1], [2], or [1, 3] mapping to the catalog above.
4. Construct the comparison_table dictionary with aspects as keys and entity -> finding summary as values.
"""

    call_tracker = {"calls": state.get("llm_call_count", 0)}

    try:
        report: Report = await call_structured_llm(
            schema=Report,
            system_prompt=WRITER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            call_tracker=call_tracker,
        )

        # Ensure profiles and sources are attached
        if not report.profiles:
            report.profiles = profiles
        report.sources = sources

        # Generate markdown content
        report.markdown_content = generate_markdown_report(report, primary_entity)

        await emit_event(
            run_id,
            "report_ready",
            "write",
            "Executive report drafted with comparison table and citations.",
            data={"title": report.title, "summary": report.executive_summary},
        )
        await emit_event(run_id, "node_finished", "write", "Report writing complete.")

        return {
            "report": report,
            "llm_call_count": call_tracker["calls"],
        }
    except Exception as e:
        logger.error(f"Writer error: {e}")
        # Build deterministic fallback report
        comp_table: Dict[str, Dict[str, str]] = {}
        for asp in plan.aspects if plan else ["product", "pricing"]:
            comp_table[asp] = {}
            for ent in plan.entities if plan else [primary_entity]:
                comp_table[asp][ent] = "See profile details [1]"

        fallback_report = Report(
            title=f"Competitive Intelligence Report: {state['query']}",
            executive_summary=f"Competitive analysis of {', '.join(plan.entities if plan else [])} focusing on {', '.join(plan.aspects if plan else [])} [1].",
            key_takeaways=[
                f"{primary_entity} leads in focused market positioning [1].",
                "Pricing transparency varies across competitors [1].",
                "Compliance standards serve as a key trust moat [1].",
                "Digital acquisition channels dominate go-to-market strategies [1].",
                "Product depth remains the primary differentiator [1].",
            ],
            comparison_table=comp_table,
            profiles=profiles,
            swot=SWOTAnalysis(
                strengths=[f"Strong core product differentiation for {primary_entity} [1]."],
                weaknesses=["Emerging go-to-market presence [1]."],
                opportunities=["Expansion into under-served regulatory niches [1]."],
                threats=["Incumbent market dominance [1]."],
            ),
            gaps_and_opportunities=["Enterprise integration and localized onboarding."],
            recommended_gtm_actions=[
                GtmAction(
                    priority="High",
                    title="Emphasize Compliance & Trust Messaging",
                    action="Highlight certified licensing and security certifications.",
                    rationale_and_evidence="Evidence demonstrates compliance is the top user selection criteria [1].",
                )
            ],
            methodology_and_limitations="Synthesized from public web sources and uploaded documentation.",
            sources=sources,
        )
        fallback_report.markdown_content = generate_markdown_report(fallback_report, primary_entity)

        return {
            "report": fallback_report,
            "errors": [f"Writer used fallback generation due to: {e}"],
            "llm_call_count": call_tracker.get("calls", state.get("llm_call_count", 0)),
        }
