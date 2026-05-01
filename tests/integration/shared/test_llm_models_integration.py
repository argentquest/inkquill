"""Integration tests for AI model catalog endpoints."""

import pytest


pytestmark = pytest.mark.integration


def test_llm_models_returns_catalog(client):
    """GET /api/v1/llm-models/ returns the LLM model catalog with counts."""
    response = client.get("/api/v1/llm-models/")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert "models" in body["data"]
    assert "total_count" in body["data"]
    assert "active_count" in body["data"]
    assert "providers" in body["data"]
    assert isinstance(body["data"]["models"], list)


def test_llm_models_list_includes_model_details(client):
    """Each model in the catalog includes display_name, provider, model_type, and pricing."""
    response = client.get("/api/v1/llm-models/")
    assert response.status_code == 200, response.text
    body = response.json()
    models = body["data"]["models"]
    if len(models) > 0:
        model = models[0]
        assert "display_name" in model
        assert "model_name" in model
        assert "provider" in model
        assert "model_type" in model
        assert "max_tokens" in model
        assert "is_active" in model
        assert "user_price_input_usd_pm" in model
        assert "user_price_output_usd_pm" in model


def test_llm_models_shows_active_and_inactive(client):
    """Catalog separates active from inactive models."""
    response = client.get("/api/v1/llm-models/")
    assert response.status_code == 200, response.text
    body = response.json()
    models = body["data"]["models"]
    active_models = [m for m in models if m.get("is_active")]
    inactive_models = [m for m in models if not m.get("is_active")]
    assert body["data"]["active_count"] == len(active_models)
    assert body["data"]["total_count"] == len(models)