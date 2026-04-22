from datetime import date
import json
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.services.care_circle import provider_cache
from app.services.care_circle.newsletter_pdf_service import newsletter_pdf_service


class _ScalarResult:
    def __init__(self, items):
        self._items = items

    def scalars(self):
        return self

    def all(self):
        return self._items


@pytest.fixture
def local_tmp_dir():
    base = Path("tests/.tmp") / f"newsletter_pdf_service_{uuid4().hex}"
    base.mkdir(parents=True, exist_ok=True)
    yield base


@pytest.mark.asyncio
async def test_generate_newsletter_pdf_for_patient_date_writes_pdf(local_tmp_dir, monkeypatch):
    patient_id = 2
    for_date = date(2026, 4, 18)
    cache_dir = local_tmp_dir / str(patient_id) / for_date.isoformat()
    cache_dir.mkdir(parents=True)
    (cache_dir / "newsletter_header.json").write_text(
        json.dumps(
            {
                "data": {
                    "title": "Daily Newsletter",
                    "text": "Welcome back today.",
                }
            }
        ),
        encoding="utf-8",
    )
    (cache_dir / "animal_friend.json").write_text(
        json.dumps(
            {
                "data": {
                    "title": "Animal Friend",
                    "description": "A friendly dog is here to brighten the day.",
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(provider_cache, "CACHE_ROOT", local_tmp_dir)

    class _DB:
        async def get(self, model, key):
            return SimpleNamespace(id=patient_id, display_name="Denise Rivard")

        async def execute(self, statement):
            return _ScalarResult(
                [
                    SimpleNamespace(provider_key="newsletter_header", display_order=0),
                    SimpleNamespace(provider_key="animal_friend", display_order=10),
                ]
            )

    async def fake_get_newsletter_html_for_date(db, patient_id_arg, for_date_arg):
        assert patient_id_arg == patient_id
        assert for_date_arg == for_date
        return "<div class='section'><h2>Hello</h2><p>Rendered newsletter html</p></div>"

    monkeypatch.setattr(
        "app.services.care_circle.newsletter_pdf_service.get_newsletter_html_for_date",
        fake_get_newsletter_html_for_date,
    )

    async def fake_render_pdf_with_playwright(html_path, pdf_path):
        pdf_path.write_bytes(b"%PDF-1.4")

    monkeypatch.setattr(
        newsletter_pdf_service,
        "_render_pdf_with_playwright",
        fake_render_pdf_with_playwright,
    )

    artifacts = await newsletter_pdf_service.generate_artifacts_for_patient_date(_DB(), patient_id, for_date)
    pdf_path = artifacts["pdf_path"]
    html_path = artifacts["html_path"]

    assert pdf_path == cache_dir / "newsletter.pdf"
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
    assert html_path == cache_dir / "newsletter.html"
    assert html_path.exists()
    assert "Rendered newsletter html" in html_path.read_text(encoding="utf-8")
