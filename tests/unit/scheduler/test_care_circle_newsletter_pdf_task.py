from datetime import date
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.scheduler.tasks import care_circle_newsletter_pdf


@pytest.fixture
def local_tmp_dir():
    base = Path("tests/.tmp") / f"newsletter_pdf_task_{uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    yield base


@pytest.mark.asyncio
async def test_generate_daily_newsletter_pdfs_creates_pdf_paths(monkeypatch, local_tmp_dir):
    patient = SimpleNamespace(id=2, display_name="Denise Rivard")
    generated_paths = []

    async def fake_fetch_active_patients():
        return [patient]

    class _DB:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

    async def fake_get_newsletter_html_for_date(db, patient_id, for_date):
        return "<div>cached html</div>"

    async def fake_assemble_daily_patient_session(db, patient_id):
        return {"success": True}

    async def fake_generate_artifacts_for_patient_date(db, patient_id, for_date):
        base = local_tmp_dir / str(patient_id) / for_date.isoformat()
        base.mkdir(parents=True, exist_ok=True)
        pdf_path = base / "newsletter.pdf"
        html_path = base / "newsletter.html"
        pdf_path.write_bytes(b"%PDF-1.4")
        html_path.write_text("<html></html>", encoding="utf-8")
        generated_paths.append((pdf_path, html_path))
        return {
            "pdf_path": pdf_path,
            "html_path": html_path,
        }

    class _FakeDate(date):
        @classmethod
        def today(cls):
            return cls(2026, 4, 18)

    monkeypatch.setattr(care_circle_newsletter_pdf, "_fetch_active_patients", fake_fetch_active_patients)
    monkeypatch.setattr(care_circle_newsletter_pdf, "async_session_local", lambda: _DB())
    monkeypatch.setattr(care_circle_newsletter_pdf, "date", _FakeDate)
    monkeypatch.setattr(
        "app.services.care_circle.session_assembler.get_newsletter_html_for_date",
        fake_get_newsletter_html_for_date,
    )
    monkeypatch.setattr(
        "app.services.care_circle.session_assembler.assemble_daily_patient_session",
        fake_assemble_daily_patient_session,
    )
    monkeypatch.setattr(
        "app.services.care_circle.newsletter_pdf_service.newsletter_pdf_service.generate_artifacts_for_patient_date",
        fake_generate_artifacts_for_patient_date,
    )

    result = await care_circle_newsletter_pdf.generate_daily_newsletter_pdfs()

    assert result["success_count"] == 1
    assert result["failure_count"] == 0
    assert generated_paths[0][0].name == "newsletter.pdf"
    assert generated_paths[0][1].name == "newsletter.html"
    assert result["results"][0]["pdf_path"].endswith("newsletter.pdf")
    assert result["results"][0]["html_path"].endswith("newsletter.html")
