from __future__ import annotations

import json

from fastapi import APIRouter, HTTPException, Query, Response, status
from sqlalchemy import select

from backend.app.db import SessionLocal
from backend.app.models import ResearchRun
from backend.app.schemas import Report
from backend.app.services.export_service import ExportService

router = APIRouter(prefix="/runs", tags=["export"])


@router.get("/{run_id}/export")
def export_report(run_id: str, format: str = Query("md", pattern="^(md|pdf|docx)$")) -> Response:
    with SessionLocal() as db:
        r = db.scalar(select(ResearchRun).where(ResearchRun.id == run_id))
        if not r or not r.report_json:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "not_found",
                        "message": f"Finished report not found for run '{run_id}'.",
                    }
                },
            )
        report = Report(**json.loads(r.report_json))

    safe_title = "".join(c for c in report.title if c.isalnum() or c in (" ", "_", "-")).rstrip()
    safe_filename = safe_title.replace(" ", "_")[:50] or f"scoutai_{run_id}"

    if format == "md":
        buffer = ExportService.to_markdown(report)
        media_type = "text/markdown; charset=utf-8"
        filename = f"{safe_filename}.md"
    elif format == "docx":
        buffer = ExportService.to_docx(report)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{safe_filename}.docx"
    elif format == "pdf":
        buffer = ExportService.to_pdf(report)
        media_type = "application/pdf"
        filename = f"{safe_filename}.pdf"
    else:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {"code": "invalid_format", "message": "Format must be md, pdf, or docx."}
            },
        )

    return Response(
        content=buffer.getvalue(),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
