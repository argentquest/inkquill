import pytest

from app.services.care_circle.session_assembler import _extract_rendered_html, _normalize_provider_card
from app.services.care_circle.providers.daily_quote.provider import DailyQuoteProvider


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
    provider = DailyQuoteProvider(patient_config={"fallback_quote": "Be kind.", "fallback_author": "Unknown"})
    result = await provider.execute(_StubPatient())

    assert result["success"] is True
    rendered_html = result["data"]["rendered_html"]
    assert "Words of Wisdom" in rendered_html
    assert "section--daily_quote" in rendered_html
    assert "—" in rendered_html or "-" in rendered_html
    assert "<style>" in rendered_html
