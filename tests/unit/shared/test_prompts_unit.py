"""Mock-based unit tests for prompt router."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.routers.prompt import router as prompt_router
from app.models.prompt import Prompt, PromptTypeEnum, AgeTargetEnum


pytestmark = pytest.mark.unit


def _prompt(id=1, title="Test Prompt", prompt_type=PromptTypeEnum.GENERAL):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=id,
        title=title,
        prompt_content="Test prompt content",
        reason_to_use="Test reason",
        comment=None,
        is_active=True,
        prompt_type=prompt_type,
        age_target=AgeTargetEnum.ALL_AGES,
        user_id=1,
        created_at=now,
        updated_at=now
    )


def _serialize_prompt(prompt):
    return {
        "id": prompt.id,
        "title": prompt.title,
        "prompt_content": prompt.prompt_content,
        "reason_to_use": prompt.reason_to_use,
        "comment": prompt.comment,
        "is_active": prompt.is_active,
        "prompt_type": prompt.prompt_type.value if hasattr(prompt.prompt_type, "value") else str(prompt.prompt_type),
        "age_target": prompt.age_target.value if hasattr(prompt.age_target, "value") else str(prompt.age_target),
        "user_id": prompt.user_id,
        "created_at": None,
        "updated_at": None
    }


def test_list_my_prompts_returns_prompt_list(unit_client_factory, mock_db_session):
    """GET /prompts/my-prompts returns user's prompts wrapped in ApiResponse."""
    client = unit_client_factory(prompt_router, router_prefix="/api/v1")
    prompts = [_prompt(id=1, title="My Prompt 1"), _prompt(id=2, title="My Prompt 2")]

    with patch("app.routers.prompt.crud_prompt.get_prompts_by_user", new=AsyncMock(return_value=prompts)):
        response = client.get("/api/v1/prompts/my-prompts")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 2


def test_list_my_prompts_with_filter(unit_client_factory, mock_db_session):
    """GET /prompts/my-prompts?filter_prompt_type=GENERAL filters results."""
    client = unit_client_factory(prompt_router, router_prefix="/api/v1")
    prompts = [_prompt(id=1, title="General Prompt", prompt_type=PromptTypeEnum.GENERAL)]

    with patch("app.routers.prompt.crud_prompt.get_prompts_by_user", new=AsyncMock(return_value=prompts)):
        response = client.get("/api/v1/prompts/my-prompts?filter_prompt_type=GENERAL")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1


def test_list_shared_prompts_returns_prompts(unit_client_factory, mock_db_session):
    """GET /prompts/shared returns shared prompts wrapped in ApiResponse."""
    client = unit_client_factory(prompt_router, router_prefix="/api/v1")
    prompts = [_prompt(id=10, title="Shared Prompt", prompt_type=PromptTypeEnum.STORY)]

    with patch("app.routers.prompt.crud_prompt.get_shared_prompts", new=AsyncMock(return_value=prompts)):
        response = client.get("/api/v1/prompts/shared")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1


def test_create_prompt_returns_created_prompt(unit_client_factory, mock_db_session):
    """POST /prompts/ creates a new prompt and returns it wrapped."""
    client = unit_client_factory(prompt_router, router_prefix="/api/v1")
    created = _prompt(id=5, title="New Prompt")

    with patch("app.routers.prompt.crud_prompt.create_prompt", new=AsyncMock(return_value=created)):
        response = client.post(
            "/api/v1/prompts/",
            json={
                "title": "New Prompt",
                "prompt_content": "New content",
                "prompt_type": "GENERAL",
                "age_target": "ALL_AGES",
                "is_active": True
            }
        )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["title"] == "New Prompt"


def test_get_single_prompt_returns_prompt(unit_client_factory, mock_db_session):
    """GET /prompts/{id} returns the prompt if owned by user."""
    client = unit_client_factory(prompt_router, router_prefix="/api/v1")
    p = _prompt(id=7, title="Single Prompt")

    with patch("app.routers.prompt.crud_prompt.get_prompt", new=AsyncMock(return_value=p)):
        response = client.get("/api/v1/prompts/7")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["title"] == "Single Prompt"


def test_get_single_prompt_returns_404_when_not_found(unit_client_factory, mock_db_session):
    """GET /prompts/{id} returns 404 when prompt does not exist."""
    client = unit_client_factory(prompt_router, router_prefix="/api/v1")

    with patch("app.routers.prompt.crud_prompt.get_prompt", new=AsyncMock(return_value=None)):
        response = client.get("/api/v1/prompts/999")

    assert response.status_code == 404, response.text


def test_get_single_prompt_returns_403_when_not_owned(unit_client_factory, mock_db_session):
    """GET /prompts/{id} returns 403 when prompt belongs to another user."""
    client = unit_client_factory(prompt_router, router_prefix="/api/v1")
    p = _prompt(id=8, title="Other User Prompt")
    p.user_id = 999  # Different user

    with patch("app.routers.prompt.crud_prompt.get_prompt", new=AsyncMock(return_value=p)):
        response = client.get("/api/v1/prompts/8")

    assert response.status_code == 403, response.text


def test_delete_prompt_returns_204(unit_client_factory, mock_db_session):
    """DELETE /prompts/{id} returns 204 on successful deletion."""
    client = unit_client_factory(prompt_router, router_prefix="/api/v1")
    p = _prompt(id=9, title="To Delete")

    with patch("app.routers.prompt.crud_prompt.get_prompt", new=AsyncMock(return_value=p)), \
         patch("app.routers.prompt.crud_prompt.delete_prompt", new=AsyncMock()):
        response = client.delete("/api/v1/prompts/9")

    assert response.status_code == 204, response.text


def test_delete_prompt_returns_403_when_not_owned(unit_client_factory, mock_db_session):
    """DELETE /prompts/{id} returns 403 when user doesn't own the prompt."""
    client = unit_client_factory(prompt_router, router_prefix="/api/v1")
    p = _prompt(id=10, title="Not Mine")
    p.user_id = 999

    with patch("app.routers.prompt.crud_prompt.get_prompt", new=AsyncMock(return_value=p)):
        response = client.delete("/api/v1/prompts/10")

    assert response.status_code == 403, response.text


def test_get_story_options_returns_genres_tones_conflicts(unit_client_factory, mock_db_session):
    """GET /prompts/story-options returns genres, tones, and conflicts."""
    client = unit_client_factory(prompt_router, router_prefix="/api/v1")

    genres = [_prompt(id=1, title="Fantasy", prompt_type=PromptTypeEnum.STORY_GENRE)]
    tones = [_prompt(id=2, title="Dark", prompt_type=PromptTypeEnum.STORY_TONE)]
    conflicts = [_prompt(id=3, title="War", prompt_type=PromptTypeEnum.STORY_CONFLICT)]

    async def mock_get_by_type(db, prompt_type, is_active):
        if prompt_type == PromptTypeEnum.STORY_GENRE:
            return genres
        if prompt_type == PromptTypeEnum.STORY_TONE:
            return tones
        if prompt_type == PromptTypeEnum.STORY_CONFLICT:
            return conflicts
        return []

    with patch("app.routers.prompt.crud_prompt.get_prompts_by_type", new=mock_get_by_type):
        response = client.get("/api/v1/prompts/story-options")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]["genres"]) == 1
    assert len(body["data"]["tones"]) == 1
    assert len(body["data"]["conflicts"]) == 1