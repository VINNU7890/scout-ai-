import io
import json

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.db import SessionLocal, init_db
from backend.app.main import app
from backend.app.models import ResearchRun
from backend.app.schemas import Report, SWOTAnalysis


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert "search_provider" in data


@pytest.mark.asyncio
async def test_create_and_get_run():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Create
        create_resp = await client.post(
            "/api/runs",
            json={
                "query": "Compare BitDelta India with CoinDCX",
                "options": {"depth": "quick"},
                "document_ids": [],
            },
        )
        assert create_resp.status_code == 201
        run_id = create_resp.json()["run_id"]
        assert run_id.startswith("run_")

        # Get
        get_resp = await client.get(f"/api/runs/{run_id}")
        assert get_resp.status_code == 200
        run_data = get_resp.json()
        assert run_data["run_id"] == run_id
        assert "BitDelta" in run_data["query"]


@pytest.mark.asyncio
async def test_export_report_formats():
    import uuid

    run_id = f"test_export_{uuid.uuid4().hex[:8]}"
    dummy_report = Report(
        title="Export Test Brief",
        executive_summary="Executive summary for export testing [1].",
        key_takeaways=[
            "Takeaway 1 [1]",
            "Takeaway 2 [1]",
            "Takeaway 3 [1]",
            "Takeaway 4 [1]",
            "Takeaway 5 [1]",
        ],
        comparison_table={"Product": {"BitDelta": "Spot & Derivatives [1]"}},
        profiles=[],
        swot=SWOTAnalysis(
            strengths=["Test [1]"],
            weaknesses=["Test [1]"],
            opportunities=["Test [1]"],
            threats=["Test [1]"],
        ),
        gaps_and_opportunities=["Gap 1"],
        recommended_gtm_actions=[],
        methodology_and_limitations="Test methodology.",
        sources=[],
    )

    with SessionLocal() as db:
        run = ResearchRun(
            id=run_id,
            query="Test query",
            title="Export Test Brief",
            status="completed",
            report_json=json.dumps(dummy_report.model_dump()),
        )
        db.add(run)
        db.commit()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Markdown export
        md_resp = await client.get(f"/api/runs/{run_id}/export?format=md")
        assert md_resp.status_code == 200
        assert "text/markdown" in md_resp.headers["content-type"]
        assert len(md_resp.content) > 0

        # DOCX export
        docx_resp = await client.get(f"/api/runs/{run_id}/export?format=docx")
        assert docx_resp.status_code == 200
        assert "wordprocessingml" in docx_resp.headers["content-type"]
        assert len(docx_resp.content) > 100

        # PDF export
        pdf_resp = await client.get(f"/api/runs/{run_id}/export?format=pdf")
        assert pdf_resp.status_code == 200
        assert "application/pdf" in pdf_resp.headers["content-type"]
        assert len(pdf_resp.content) > 100
        assert pdf_resp.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_document_lifecycle():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Upload
        file_content = b"BitDelta compliance documentation: FIU-IND preliminary filings completed."
        files = {"file": ("test_compliance.txt", io.BytesIO(file_content), "text/plain")}
        upload_resp = await client.post("/api/documents", files=files)
        assert upload_resp.status_code == 201
        doc_data = upload_resp.json()
        doc_id = doc_data["id"]
        assert doc_data["filename"] == "test_compliance.txt"

        # List
        list_resp = await client.get("/api/documents")
        assert list_resp.status_code == 200
        docs = list_resp.json()
        assert any(d["id"] == doc_id for d in docs)

        # Delete
        del_resp = await client.delete(f"/api/documents/{doc_id}")
        assert del_resp.status_code == 200
        assert del_resp.json()["deleted"] is True
