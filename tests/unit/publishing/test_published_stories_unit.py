"""Mock-based unit tests for published stories router."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.core.deps import get_db_session
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


def _published_story(
    id: int = 1,
    story_id: int = 1,
    user_id: int = 1,
    title: str = "Test Story",
    average_rating: float | None = None,
):
    now = datetime.now(timezone.utc)
    mock = MagicMock()
    mock.id = id
    mock.story_id = story_id
    mock.user_id = user_id
    mock.title = title
    mock.description = "A test description."
    mock.published_url = "/published/test-story"
    mock.filename = "test-story.html"
    mock.word_count = 500
    mock.is_public = True
    mock.is_featured = False
    mock.view_count = 10
    mock.like_count = 2
    mock.comment_count = 1
    mock.average_rating = average_rating
    mock.published_at = now
    mock.updated_at = now
    mock.publisher = SimpleNamespace(username="testuser", display_name="Test User")
    mock.story = SimpleNamespace(title="Test Story", short_description="Test desc", world=None)
    return mock


class TestListPublishedStories:
    def test_list_returns_200_and_data_shape(self, unit_client_factory):
        client = unit_client_factory(published_stories_router)
        story = _published_story()
        mock_db = _sync_mock_db([story])
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.get("/published-stories/")
        assert response.status_code == 200
        body = response.json()
        assert body.get("success") is True
        assert "data" in body
        assert "stories" in body["data"]
        assert "total" in body["data"]

    def test_list_public_no_auth_required(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        mock_db = _sync_mock_db([])
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.get("/published-stories/")
        assert response.status_code == 200

    def test_list_respects_page_params(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        mock_db = _sync_mock_db([])
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.get("/published-stories/?page=2&per_page=10")
        assert response.status_code == 200

    def test_list_sorts_by_recent(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        mock_db = _sync_mock_db([])
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.get("/published-stories/?sort_by=recent")
        assert response.status_code == 200

    def test_list_sorts_by_popular(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        mock_db = _sync_mock_db([])
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.get("/published-stories/?sort_by=popular")
        assert response.status_code == 200

    def test_list_sorts_by_rating(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        mock_db = _sync_mock_db([])
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.get("/published-stories/?sort_by=rating")
        assert response.status_code == 200

    def test_list_filters_by_search(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        mock_db = _sync_mock_db([])
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.get("/published-stories/?search=magic")
        assert response.status_code == 200

    def test_list_filters_by_is_featured(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        mock_db = _sync_mock_db([])
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.get("/published-stories/?is_featured=true")
        assert response.status_code == 200

    def test_list_returns_stories_with_expected_fields(self, unit_client_factory):
        client = unit_client_factory(published_stories_router)
        story = _published_story(id=5, title="My Story", average_rating=4.5)
        mock_db = _sync_mock_db([story])
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.get("/published-stories/")
        assert response.status_code == 200
        body = response.json()
        stories = body["data"]["stories"]
        assert len(stories) == 1
        assert stories[0]["title"] == "My Story"
        assert stories[0]["average_rating"] == 4.5


class TestGetPublishedStory:
    def test_get_returns_200_and_detail_shape(self, unit_client_factory):
        client = unit_client_factory(published_stories_router)
        story = _published_story(id=3, title="Detail Story")
        mock_db = _sync_mock_db([story])
        # second execute for refreshed story after commit
        refreshed_result = MagicMock()
        refreshed_result.scalar_one.return_value = story
        call_count = [0]
        orig_execute = mock_db.execute

        async def _execute(q, **kwargs):
            call_count[0] += 1
            if call_count[0] >= 2:
                return refreshed_result
            return await orig_execute(q, **kwargs)

        mock_db.execute = _execute
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.get("/published-stories/3")
        assert response.status_code == 200
        body = response.json()
        assert body.get("success") is True
        assert "data" in body
        assert body["data"]["title"] == "Detail Story"

    def test_get_public_no_auth_required(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        story = _published_story(id=4)
        mock_db = _sync_mock_db([story])
        refreshed_result = MagicMock()
        refreshed_result.scalar_one.return_value = story
        call_count = [0]
        orig_execute = mock_db.execute

        async def _execute(q, **kwargs):
            call_count[0] += 1
            if call_count[0] >= 2:
                return refreshed_result
            return await orig_execute(q, **kwargs)

        mock_db.execute = _execute
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.get("/published-stories/4")
        assert response.status_code == 200

    def test_get_returns_404_for_missing(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        mock_db = _sync_mock_db([])
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.get("/published-stories/999")
        assert response.status_code == 404


class TestRatePublishedStory:
    def test_rate_creates_new_rating(self, unit_client_factory, mock_user):
        client = unit_client_factory(published_stories_router, user_override=mock_user)
        story = _published_story(id=2)
        mock_db = _sync_mock_db([story])
        rating_mock = MagicMock()
        rating_mock.id = 1
        rating_mock.published_story_id = 2
        rating_mock.user_id = mock_user.id
        rating_mock.rating = 5
        rating_mock.created_at = datetime.now(timezone.utc)
        rating_mock.updated_at = datetime.now(timezone.utc)
        rating_result = MagicMock()
        rating_result.scalar_one.return_value = rating_mock
        call_count = [0]
        orig_execute = mock_db.execute

        async def _execute(q, **kwargs):
            call_count[0] += 1
            if call_count[0] >= 3:
                return rating_result
            return await orig_execute(q, **kwargs)

        mock_db.execute = _execute
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.post(
            "/published-stories/2/rate",
            json={"published_story_id": 2, "rating": 5},
        )
        assert response.status_code in (200, 201)
        body = response.json()
        assert body.get("success") is True

    def test_rate_rejects_unauthenticated(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        # Force current_user to None since conftest defaults None to mock_user
        from app.core.deps import get_current_user
        client.app.dependency_overrides[get_current_user] = lambda: None
        story = _published_story(id=2)
        mock_db = _sync_mock_db([story])
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.post(
            "/published-stories/2/rate",
            json={"published_story_id": 2, "rating": 5},
        )
        assert response.status_code == 401


class TestCreateStoryComment:
    def test_create_comment_returns_success(self, unit_client_factory, mock_user):
        client = unit_client_factory(published_stories_router, user_override=mock_user)
        story = _published_story(id=6)
        mock_db = _sync_mock_db([story])
        commenter = SimpleNamespace(username="reader", display_name="A Reader")
        comment_mock = MagicMock()
        comment_mock.id = 1
        comment_mock.published_story_id = 6
        comment_mock.user_id = mock_user.id
        comment_mock.content = "Nice read!"
        comment_mock.parent_comment_id = None
        comment_mock.is_approved = True
        comment_mock.is_deleted = False
        comment_mock.created_at = datetime.now(timezone.utc)
        comment_mock.updated_at = datetime.now(timezone.utc)
        comment_mock.commenter = commenter
        comment_result = MagicMock()
        comment_result.scalar_one.return_value = comment_mock
        call_count = [0]
        orig_execute = mock_db.execute

        async def _execute(q, **kwargs):
            call_count[0] += 1
            if call_count[0] >= 2:
                return comment_result
            return await orig_execute(q, **kwargs)

        mock_db.execute = _execute
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.post(
            "/published-stories/6/comments",
            json={"published_story_id": 6, "content": "Nice read!"},
        )
        assert response.status_code in (200, 201)
        body = response.json()
        assert body.get("success") is True

    def test_create_comment_rejects_unauthenticated(self, unit_client_factory):
        client = unit_client_factory(published_stories_router, user_override=None)
        from app.core.deps import get_current_user
        client.app.dependency_overrides[get_current_user] = lambda: None
        story = _published_story(id=6)
        mock_db = _sync_mock_db([story])
        async def _db_gen():
            yield mock_db
        client.app.dependency_overrides[get_db_session] = _db_gen
        response = client.post(
            "/published-stories/6/comments",
            json={"published_story_id": 6, "content": "Nice read!"},
        )
        assert response.status_code == 401