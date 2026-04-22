import pytest
from datetime import date
import json
from pathlib import Path

from app.models.ai_model_config import AIProviderEnum
from app.services.care_circle.providers.daily_quote.provider import DailyQuoteProvider
from app.services.care_circle.session_assembler import (
    _extract_rendered_html,
    _get_family_owner_user_id,
    _log_provider_token_usage,
    _purge_obsolete_cached_provider_files,
    _normalize_job_id_for_logging,
    _normalize_provider_card,
    _resolve_ai_model_config_for_logging,
    get_newsletter_html_for_date,
)
from scripts.validate_care_circle_newsletter_uniqueness import (
    _build_report,
    _normalize_payload,
)


class _StubPatient:
    id = 1
    display_name = "Rose"
    preferences = {"city_for_weather": "Chicago, IL"}


def test_normalize_provider_card_strips_html_and_renderer_only_fields():
    title, body = _normalize_provider_card(
        {
            "data": {
                "title": "Daily Word Search",
                "instruction": "Find the hidden words.",
                "words": ["SPRING", "GARDEN"],
                "puzzle_content": "<table><tr><td>S</td></tr></table>",
            }
        }
    )

    assert title == "Daily Word Search"
    assert "Find the hidden words." in body
    assert "Words: SPRING; GARDEN" in body
    assert "<table>" not in body
    assert "puzzle_content" not in body


def test_extract_rendered_html_prefers_provider_template_output():
    rendered_html = _extract_rendered_html(
        {
            "data": {
                "title": "Daily Word Search",
                "instruction": "Find the hidden words.",
                "puzzle_content": "<table><tr><td>S</td></tr></table>",
            }
        }
    )

    assert rendered_html == "<table><tr><td>S</td></tr></table>"


def test_normalize_provider_card_avoids_raw_dict_dump_output():
    title, body = _normalize_provider_card(
        {
            "data": {
                "type": "odd_one_out",
                "title": "Which One Doesn't Belong?",
                "instruction": "Circle the word that doesn't fit with the others.",
                "items": ["APPLE", "BANANA", "CARROT", "PEAR"],
                "answer": "CARROT",
            }
        }
    )

    assert title == "Which One Doesn't Belong?"
    assert "Circle the word that doesn't fit with the others." in body
    assert "Items: APPLE; BANANA; CARROT; PEAR" in body
    assert "Answer: CARROT" in body
    assert "{'type':" not in body


@pytest.mark.asyncio
async def test_provider_execute_renders_default_template_html():
    provider = DailyQuoteProvider(
        patient_config={"fallback_quote": "Be kind.", "fallback_author": "Unknown"}
    )
    result = await provider.execute(_StubPatient())

    assert result["success"] is True
    rendered_html = result["data"]["rendered_html"]
    assert "Words of Wisdom" in rendered_html
    assert "section--daily_quote" in rendered_html
    assert "-" in rendered_html
    assert "<style>" in rendered_html


@pytest.mark.asyncio
async def test_get_family_owner_user_id_prefers_family_creator():
    patient = type("Patient", (), {"family_id": 10, "created_by_user_id": 77})()
    family = type("Family", (), {"created_by_user_id": 55})()

    class _DB:
        async def get(self, model, key):
            return family

    owner_user_id = await _get_family_owner_user_id(_DB(), patient)
    assert owner_user_id == 55


@pytest.mark.asyncio
async def test_resolve_ai_model_config_for_logging_creates_ad_hoc_config_when_missing():
    captured = {}

    class _DB:
        async def scalar(self, *args, **kwargs):
            return None

        def add(self, model):
            captured["model"] = model

        async def flush(self):
            captured["flushed"] = True
            captured["model"].id = 321

    config = await _resolve_ai_model_config_for_logging(
        _DB(), "grok-4-1-fast-non-reasoning"
    )

    assert config.id == 321
    assert config.model_name == "grok-4-1-fast-non-reasoning"
    assert config.provider == AIProviderEnum.OPENAI
    assert config.user_price_input_usd_pm == 0.60
    assert config.user_price_output_usd_pm == 0.60


@pytest.mark.asyncio
async def test_log_provider_token_usage_maps_to_family_owner_and_passes_job_id(
    monkeypatch,
):
    patient = type(
        "Patient",
        (),
        {"id": 20, "family_id": 10, "created_by_user_id": 77},
    )()
    family = type("Family", (), {"created_by_user_id": 55})()

    class _DB:
        async def get(self, model, key):
            return family

        async def scalar(self, *args, **kwargs):
            return None

        def add(self, model):
            model.id = 654

        async def flush(self):
            return None

    captured = {}

    async def fake_log_ai_call(**kwargs):
        captured.update(kwargs)
        return 123

    monkeypatch.setattr(
        "app.services.care_circle.session_assembler.log_ai_call",
        fake_log_ai_call,
    )
    async def fake_normalize_job_id_for_logging(db, job_id):
        return job_id

    monkeypatch.setattr(
        "app.services.care_circle.session_assembler._normalize_job_id_for_logging",
        fake_normalize_job_id_for_logging,
    )

    await _log_provider_token_usage(
        _DB(),
        patient,
        "memory_lane_photo",
        {
            "prompt_tokens": 100,
            "completion_tokens": 40,
            "total_tokens": 140,
            "model": "grok-4-1-fast-non-reasoning",
        },
        512.4,
        job_id="job-123",
    )

    assert captured["user_id"] == 55
    assert captured["call_type"] == "care_circle_provider"
    assert captured["object_id"] == 20
    assert captured["job_id"] == "job-123"
    assert captured["duration_ms"] == 512
    assert captured["input_prompt"] == "Care Circle provider: memory_lane_photo"
    assert captured["usage"]["total_tokens"] == 140
    assert captured["model_config"].model_name == "grok-4-1-fast-non-reasoning"
    assert captured["db"].__class__.__name__ == "_DB"


@pytest.mark.asyncio
async def test_normalize_job_id_for_logging_drops_missing_job_id():
    class _DB:
        async def scalar(self, *args, **kwargs):
            return None

    result = await _normalize_job_id_for_logging(_DB(), "missing-job")
    assert result is None


def test_purge_obsolete_cached_provider_files_removes_mimi_eunice(monkeypatch):
    class _FakePath:
        def __init__(self, name):
            self.name = name
            self.deleted = False

        def unlink(self):
            self.deleted = True

    obsolete = _FakePath("comic_mimi_eunice.json")
    keep = _FakePath("comic_wuffle.json")

    class _FakeDir:
        def __truediv__(self, other):
            return self

        def exists(self):
            return True

        def glob(self, pattern):
            assert pattern == "comic_mimi_eunice*"
            return [obsolete]

    class _FakeRoot:
        def __truediv__(self, other):
            return self

        def exists(self):
            return True

    monkeypatch.setattr(
        "app.services.care_circle.session_assembler.CACHE_ROOT",
        _FakeDir(),
    )

    _purge_obsolete_cached_provider_files(2, date(2026, 4, 21))

    assert obsolete.deleted is True
    assert keep.deleted is False


@pytest.mark.asyncio
async def test_get_newsletter_html_for_date_skips_obsolete_provider_files(monkeypatch):
    base = Path("tests/.tmp") / "obsolete_cache_html"
    cache_dir = base / "2" / "2026-04-21"
    cache_dir.mkdir(parents=True, exist_ok=True)
    (cache_dir / "comic_mimi_eunice.json").write_text(
        json.dumps({"data": {"rendered_html": "<div>obsolete</div>"}}),
        encoding="utf-8",
    )
    (cache_dir / "comic_wuffle.json").write_text(
        json.dumps({"data": {"rendered_html": "<div>wuffle</div>"}}),
        encoding="utf-8",
    )

    monkeypatch.setattr(
        "app.services.care_circle.session_assembler.CACHE_ROOT",
        base,
    )

    class _Result:
        def scalars(self):
            return self

        def all(self):
            return []

    class _DB:
        async def execute(self, *args, **kwargs):
            return _Result()

    html = await get_newsletter_html_for_date(_DB(), 2, date(2026, 4, 21))

    assert "wuffle" in html
    assert "obsolete" not in html


def test_uniqueness_normalization_strips_volatile_fields_and_prefers_remote_image():
    payload = {
        "title": "Sunny Garden",
        "rendered_html": "<div>html</div>",
        "generated_at": "April 21",
        "image_url": "/api/v1/care-circle/cached-image/20/2026-04-21/gallery_image.jpg",
        "image_url_remote": "https://images.example/gallery.jpg",
        "items": [
            {
                "caption": "A garden path",
                "thumb": "/api/v1/care-circle/cached-image/20/2026-04-21/thumb.jpg",
            }
        ],
    }

    normalized = _normalize_payload(payload)

    assert "rendered_html" not in normalized
    assert "generated_at" not in normalized
    assert normalized["image_url"] == "https://images.example/gallery.jpg"
    assert normalized["items"][0]["thumb"].endswith("/<date>/thumb.jpg")


def test_uniqueness_report_includes_duplicate_findings():
    patient = type("Patient", (), {"id": 20, "display_name": "June Carter"})()
    report = _build_report(
        [patient],
        [date(2026, 4, 21), date(2026, 4, 22), date(2026, 4, 23)],
        [
            type(
                "Finding",
                (),
                {
                    "patient_id": 20,
                    "patient_name": "June Carter",
                    "provider_key": "word_scramble",
                    "dates": ["2026-04-21", "2026-04-22"],
                },
            )()
        ],
    )

    assert "Patient 20 - June Carter" in report
    assert "`word_scramble` produced the same normalized output on: 2026-04-21, 2026-04-22" in report
