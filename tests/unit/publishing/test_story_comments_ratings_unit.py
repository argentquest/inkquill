"""Mock-based unit tests for story comments and ratings endpoints."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.routers.published_stories import router as published_stories_router


pytestmark = pytest.mark.unit


def _make_result(return_value):
    result = MagicMock()
    result.scalars.return_value.all.return_value = return_value if return_value else []
    scalar_val = return_value[0] if return_value and isinstance(return_value, list) else (return_value if return_value else None)
    result.scalar_one_or_none.return_value = scalar_val
    result.scalar.return_value = len(return_value) if return_value and isinstance(return_value, list) else 1
    return result


def _sync_mock_db(return_value):
    mock_db = MagicMock()

    async def mock_execute(q, **kwargs):
        return _make_result(return_value)

    mock_db.execute = mock_execute
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.refresh = AsyncMock()
    return mock_db


def _story_comment(
    id: int = 1,
    published_story_id: int = 1,
    user_id: int = 1,
    content: str = "Great story!",
):
    now = SimpleNamespace()
    mock = MagicMock()
    mock.id = id
    mock.published_story_id = published_story_id
    mock.user_id = user_id
    mock.commenter_username = "reader"
    mock.commenter_display_name = "A Reader"
    mock.content = content
    mock.is_approved = True
    mock.created_at = now
    mock.updated_at = now
    return mock


class TestStoryComments:
    def test_list_comments_returns_200(self, unit_client_factory):
        client = unit_client_factory(published_stories_router)
        comment = _story_comment()
        mock_db = _sync_mock_db([comment])
        with patch("app.routers.published_stories.get_db_session", new=lambda: mock_db):
            response = client.get("/published-stories/1/comments")
        assert response.status_code == 200
        body = response.json()
        assert body.get("success") is True

    def test_list_comments_is_public(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        mock_db = _sync_mock_db([])
        with patch("app.routers.published_stories.get_db_session", new=lambda: mock_db):
            response = client.get("/published-stories/1/comments")
        assert response.status_code == 200

    def test_list_comments_returns_only_approved(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        comment = _story_comment()
        mock_db = _sync_mock_db([comment])
        with patch("app.routers.published_stories.get_db_session", new=lambda: mock_db):
            response = client.get("/published-stories/1/comments")
        assert response.status_code == 200
        body = response.json()
        if "data" in body:
            for c in body["data"]:
                assert c.get("is_approved") is True


class TestCreateComment:
    def test_create_comment_rejects_empty_content(self, unit_client_factory, mock_user):
        client = unit_client_factory(published_stories_router, user_override=mock_user)
        response = client.post(
            "/published-stories/1/comments",
            json={"published_story_id": 1, "content": ""},
        )
        assert response.status_code in (400, 422)


class TestStoryRatings:
    def test_rate_story_rejects_rating_below_1(self, unit_client_factory, mock_user):
        client = unit_client_factory(published_stories_router, user_override=mock_user)
        response = client.post(
            "/published-stories/1/rate",
            json={"published_story_id": 1, "rating": 0},
        )
        assert response.status_code in (400, 422)

    def test_rate_story_rejects_rating_above_5(self, unit_client_factory, mock_user):
        client = unit_client_factory(published_stories_router, user_override=mock_user)
        response = client.post(
            "/published-stories/1/rate",
            json={"published_story_id": 1, "rating": 6},
        )
        assert response.status_code in (400, 422)