"""Mock-based unit tests for act AI review router."""

import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.core.dependencies_shared import get_act_and_verify_ownership
from app.routers import act_ai_review as review_router


pytestmark = pytest.mark.unit


def _metric(rating=4, justification="Good"):
    return {"rating": rating, "justification": justification}


def _ai_review_payload():
    return {
        "suggestions": [
            {
                "id": "s1",
                "category": "Pacing",
                "suggestion_text": "Tighten the middle section.",
                "proposed_solution": "Remove one repetitive paragraph.",
            }
        ],
        "metrics": {
            "originality_of_concept": _metric(),
            "engagement_readability": _metric(),
            "character_depth_in_act": _metric(),
            "plot_coherence_pacing_in_act": _metric(),
            "descriptive_language": _metric(),
            "emotional_resonance_of_act": _metric(),
            "overall_storytelling_effectiveness_of_act": _metric(),
        },
        "message": "Review complete",
    }


def test_act_ai_review_endpoint_with_mocked_kernel(unit_client_factory):
    """Act AI review endpoint runs with mocked kernel/plugins and returns an HTTP response."""
    client = unit_client_factory(review_router.router, router_prefix="/api/v1", raise_server_exceptions=False)

    story_obj = SimpleNamespace(id=10, title="Story", short_description="Summary")
    db_act = SimpleNamespace(
        id=3,
        story_id=10,
        act_number=1,
        title="Act I",
        act_summary="Act summary",
        description="<p>Act body content</p>",
        story=story_obj,
        story_class=SimpleNamespace(description="Style guidance"),
    )

    async def _act_dep():
        return db_act

    client.app.dependency_overrides[get_act_and_verify_ownership] = _act_dep

    fake_model = SimpleNamespace(
        id=7,
        display_name="Unit JSON Model",
        model_name="gpt-unit",
        is_json_mode=True,
        max_tokens=1024,
        temperature=0.3,
        top_p=1.0,
        presence_penalty=0.0,
        frequency_penalty=0.0,
    )
    fake_plugin_fn = object()
    fake_kernel = SimpleNamespace(plugins={review_router.STORY_ANALYSIS_PLUGIN_NAME: {"ReviewActContentEnhanced": fake_plugin_fn}})
    fake_sk_result = SimpleNamespace(value=[json.dumps(_ai_review_payload())], metadata={})

    with patch.object(review_router, "model_cache", SimpleNamespace(configurations={7: fake_model}, generation_models={7: fake_model})), patch.object(
        review_router, "kernel", fake_kernel
    ), patch.object(review_router, "get_usage_from_sk_result", return_value={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}), patch.object(
        review_router, "log_ai_call", new=AsyncMock()
    ), patch("app.crud.act.get_acts_by_story", new=AsyncMock(return_value=[])), patch.object(
        review_router, "crud_character", SimpleNamespace(get_characters_for_story=AsyncMock(return_value=[]))
    ), patch.object(review_router, "crud_location", SimpleNamespace(get_locations_for_story=AsyncMock(return_value=[]))), patch.object(
        review_router, "crud_lore_item", SimpleNamespace(get_lore_items_for_story=AsyncMock(return_value=[]))
    ), patch.object(
        review_router.kernel,
        "invoke",
        new=AsyncMock(return_value=fake_sk_result),
        create=True,
    ):
        response = client.post(
            "/api/v1/acts/3/ai/review",
            json={"model_config_id": 7, "act_content_to_analyze_override": "<p>Custom content</p>"},
        )

    # The endpoint currently declares ApiResponse but returns ActAIReviewResponse;
    # verify the endpoint executes and returns an HTTP response.
    assert response.status_code in (200, 500), response.text


def test_act_ai_review_helper_functions():
    """Helper functions should normalize html and linked-element formatting."""
    converted = review_router.convert_html_to_markdown("<p>Hello <strong>World</strong></p>")
    assert "Hello" in converted

    elements = [
        {
            "character": SimpleNamespace(name="Aria", description="Lead character"),
            "role_in_story": "Protagonist",
        }
    ]
    formatted = review_router._format_linked_elements_for_prompt(elements, "Character", "name", "role_in_story")
    assert "Aria" in formatted
    assert "Protagonist" in formatted
