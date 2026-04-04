"""Mock-based unit tests for dashboard and model catalog routers."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.models.ai_model_config import AIModelTypeEnum, AIProviderEnum
from app.routers.ai_model_config import router as ai_model_router
from app.routers.dashboard import router as dashboard_router
from app.routers.llm_models import router as llm_models_router


pytestmark = pytest.mark.unit


def _scalar_result(value):
    return SimpleNamespace(scalar=lambda: value)


def test_dashboard_summary_counts_are_wrapped(unit_client_factory, mock_db_session):
    """`GET /api/v1/dashboard/summary` returns ApiResponse with summary counts."""
    client = unit_client_factory(dashboard_router)

    # world, story, character, location, lore counts in call order
    mock_db_session.execute = AsyncMock(
        side_effect=[
            _scalar_result(3),
            _scalar_result(7),
            _scalar_result(11),
            _scalar_result(13),
            _scalar_result(17),
        ]
    )

    response = client.get("/api/v1/dashboard/summary")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["summary"]["total_worlds"] == 3
    assert body["data"]["summary"]["total_stories"] == 7
    assert body["data"]["summary"]["total_characters"] == 11
    assert body["data"]["summary"]["total_locations"] == 13
    assert body["data"]["summary"]["total_lore_items"] == 17


def test_ai_model_config_list_and_user_available_are_wrapped(unit_client_factory):
    """`/api/v1/ai-models` endpoints return wrapped model rows."""
    client = unit_client_factory(ai_model_router, router_prefix="/api/v1")

    model = SimpleNamespace(
        id=1,
        display_name="Unit Test GPT",
        description="Unit generation model",
        model_name="gpt-unit",
        is_public_chat_default=True,
    )

    with patch("app.routers.ai_model_config.crud_ai_model_config.get_all_model_configs", new=AsyncMock(return_value=[model])):
        list_response = client.get("/api/v1/ai-models/")
        user_response = client.get("/api/v1/ai-models/user-available")

    assert list_response.status_code == 200, list_response.text
    assert list_response.json()["success"] is True
    assert list_response.json()["data"][0]["display_name"] == "Unit Test GPT"

    assert user_response.status_code == 200, user_response.text
    assert user_response.json()["success"] is True
    assert user_response.json()["data"][0]["model_name"] == "gpt-unit"


def test_ai_model_cost_logs_recent_returns_wrapped_summary(unit_client_factory, mock_db_session):
    """`GET /api/v1/ai-models/cost-logs/recent` returns wrapped log summary."""
    client = unit_client_factory(ai_model_router, router_prefix="/api/v1")

    log_row = SimpleNamespace(
        id=42,
        call_type="act_review",
        model_name="gpt-unit",
        prompt_tokens=100,
        completion_tokens=50,
        total_tokens=150,
        calculated_cost_usd=0.0123,
        duration_ms=210,
        object_id=77,
        created_at=datetime.now(timezone.utc),
    )

    mock_db_session.execute = AsyncMock(
        side_effect=[
            _scalar_result(1),
            SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: [log_row])),
        ]
    )

    response = client.get("/api/v1/ai-models/cost-logs/recent?limit=5")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total_count"] == 1
    assert body["data"]["act_review_count"] == 1
    assert body["data"]["recent_logs"][0]["id"] == 42


def test_llm_models_endpoint_returns_wrapped_catalog(unit_client_factory):
    """`GET /api/v1/llm-models/` returns wrapped LLM catalog response."""
    client = unit_client_factory(llm_models_router, router_prefix="/api/v1")

    model_rows = [
        SimpleNamespace(
            id=1,
            display_name="Unit GPT",
            model_name="gpt-unit",
            description="Unit model",
            provider=AIProviderEnum.OPENAI,
            model_type=AIModelTypeEnum.GENERATION,
            is_active=True,
            is_public_chat_default=True,
            max_tokens=4096,
            temperature=0.7,
            top_p=1.0,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            is_json_mode=False,
            provider_cost_input_usd_pm=1.0,
            provider_cost_output_usd_pm=2.0,
            user_price_input_usd_pm=3.0,
            user_price_output_usd_pm=4.0,
        )
    ]
    stats = {"total_count": 1, "active_count": 1, "providers": ["OPENAI"]}

    with patch("app.routers.llm_models.crud_llm_models.get_all_model_configurations", new=AsyncMock(return_value=model_rows)), patch(
        "app.routers.llm_models.crud_llm_models.get_model_statistics", new=AsyncMock(return_value=stats)
    ):
        response = client.get("/api/v1/llm-models/")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["total_count"] == 1
    assert body["data"]["models"][0]["display_name"] == "Unit GPT"
