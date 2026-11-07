from __future__ import annotations

import io

from docx import Document
from docx.shared import Pt, RGBColor
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from backend.app.schemas import Report


class ExportService:
    @staticmethod
    def to_markdown(report: Report) -> io.BytesIO:
        """Exports the report as a Markdown file buffer."""
        md_text = report.markdown_content or f"# {report.title}\n\n{report.executive_summary}"
        buffer = io.BytesIO()
        buffer.write(md_text.encode("utf-8"))
        buffer.seek(0)
        return buffer

    @staticmethod
    def to_docx(report: Report) -> io.BytesIO:
        """Exports the report as a polished Microsoft Word DOCX document."""
        doc = Document()

        # Styles
        title_p = doc.add_paragraph()
        title_run = title_p.add_run(report.title)
        title_run.font.size = Pt(24)
        title_run.font.bold = True
        title_run.font.color.rgb = RGBColor(99, 102, 241)  # Electric indigo

        # Executive Summary
        doc.add_heading("Executive Summary", level=1)
        doc.add_paragraph(report.executive_summary)

        # Key Takeaways
        doc.add_heading("Key Takeaways", level=1)
        for t in report.key_takeaways:
            doc.add_paragraph(t, style="List Bullet")

        # Comparison Table
        if report.comparison_table:
            doc.add_heading("Comparison Matrix", level=1)
            entities = []
            for row in report.comparison_table.values():
                for ent in row.keys():
                    if ent not in entities:
                        entities.append(ent)

            table = doc.add_table(rows=1 + len(report.comparison_table), cols=1 + len(entities))
            table.style = "Table Grid"

            # Header
            hdr_cells = table.rows[0].cells
            hdr_cells[0].text = "Aspect"
            for idx, ent in enumerate(entities):
                hdr_cells[idx + 1].text = ent

            # Rows
            for r_idx, (aspect, cols) in enumerate(report.comparison_table.items()):
                row_cells = table.rows[r_idx + 1].cells
                row_cells[0].text = aspect
                for c_idx, ent in enumerate(entities):
                    row_cells[c_idx + 1].text = cols.get(ent, "Not found")

        # Competitor Profiles
        doc.add_heading("Competitor Profiles", level=1)
        for p in report.profiles:
            doc.add_heading(p.entity, level=2)
            doc.add_paragraph(f"Positioning: {p.positioning}")
            doc.add_paragraph(f"Pricing: {p.pricing_notes}")

            if p.strengths:
                doc.add_paragraph("Strengths:", style="List Bullet")
                for s in p.strengths:
                    doc.add_paragraph(f"  • {s}")

            if p.weaknesses:
                doc.add_paragraph("Weaknesses:", style="List Bullet")
                for w in p.weaknesses:
                    doc.add_paragraph(f"  • {w}")

        # Recommended GTM Actions
        if report.recommended_gtm_actions:
            doc.add_heading("Recommended GTM Actions", level=1)
            for act in report.recommended_gtm_actions:
                p = doc.add_paragraph()
                p.add_run(f"[{act.priority}] {act.title}\n").bold = True
                p.add_run(f"Action: {act.action}\n")
                p.add_run(f"Evidence: {act.rationale_and_evidence}")

        # Sources
        if report.sources:
            doc.add_heading("Sources & Citations", level=1)
            for s in report.sources:
                doc.add_paragraph(
                    f"[{s.id}] {s.title} ({s.source_type.upper()}) - {s.url or s.doc_name}"
                )

        buffer = io.BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer

    @staticmethod
    def to_pdf(report: Report) -> io.BytesIO:
        """Exports the report as a publication-ready PDF document using ReportLab."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#4F46E5"),
            spaceAfter=12,
        )

        h1_style = ParagraphStyle(
            "H1",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1F2937"),
            spaceBefore=14,
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=14,
            textColor=colors.HexColor("#374151"),
            spaceAfter=6,
        )

        bullet_style = ParagraphStyle(
            "Bullet",
            parent=body_style,
            leftIndent=15,
            spaceAfter=3,
        )

        story = []

        # Title
        story.append(Paragraph(report.title, title_style))
        story.append(
            HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#6366F1"), spaceAfter=10)
        )

        # Executive Summary
        story.append(Paragraph("Executive Summary", h1_style))
        story.append(Paragraph(report.executive_summary, body_style))
        story.append(Spacer(1, 10))

        # Key Takeaways
        story.append(Paragraph("Key Takeaways", h1_style))
        for t in report.key_takeaways:
            story.append(Paragraph(f"• {t}", bullet_style))
        story.append(Spacer(1, 10))

        # Comparison Table
        if report.comparison_table:
            story.append(Paragraph("Comparison Matrix", h1_style))
            entities = []
            for row in report.comparison_table.values():
                for ent in row.keys():
                    if ent not in entities:
                        entities.append(ent)

            table_data = []
            header_row = ["Aspect"] + entities
            table_data.append([Paragraph(f"<b>{h}</b>", body_style) for h in header_row])

            for aspect, cols in list(report.comparison_table.items())[:8]:
                row_items = [Paragraph(f"<b>{aspect}</b>", body_style)]
                for ent in entities:
                    val = cols.get(ent, "Not found")
                    row_items.append(Paragraph(val[:120], body_style))
                table_data.append(row_items)

            # Auto fit widths
            total_width = 530
            col_width = total_width / len(header_row)
            col_widths = [col_width] * len(header_row)

            pdf_table = Table(table_data, colWidths=col_widths)
            pdf_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF2FF")),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D1D5DB")),
                    ]
                )
            )
            story.append(pdf_table)
            story.append(Spacer(1, 10))

        # Profiles
        story.append(Paragraph("Competitor Profiles", h1_style))
        for p in report.profiles[:4]:
            story.append(
                Paragraph(
                    f"<b>{p.entity}</b>",
                    ParagraphStyle("SubH", parent=h1_style, fontSize=11, spaceBefore=6),
                )
            )
            story.append(Paragraph(f"<b>Positioning:</b> {p.positioning}", body_style))
            story.append(Paragraph(f"<b>Pricing:</b> {p.pricing_notes}", body_style))
            if p.strengths:
                story.append(
                    Paragraph(f"<b>Strengths:</b> {', '.join(p.strengths[:3])}", body_style)
                )
            if p.weaknesses:
                story.append(
                    Paragraph(f"<b>Weaknesses:</b> {', '.join(p.weaknesses[:3])}", body_style)
                )
            story.append(Spacer(1, 4))

        # Sources
        if report.sources:
            story.append(Spacer(1, 10))
            story.append(Paragraph("Sources & Citations", h1_style))
            for s in report.sources[:15]:
                story.append(
                    Paragraph(
                        f"[{s.id}] {s.title} ({s.source_type.upper()}) - {s.url or s.doc_name}",
                        bullet_style,
                    )
                )

        doc.build(story)
        buffer.seek(0)
        return buffer
