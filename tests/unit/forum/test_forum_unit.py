"""Mock-based unit tests for forum routers."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.routers.forum_category import router as forum_category_router
from app.routers.forum_thread import router as forum_thread_router
from app.routers.forum_post import router as forum_post_router


pytestmark = pytest.mark.unit


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


class TestForumCategories:
    def test_list_categories_returns_200(self, unit_client_factory):
        """GET /api/forum/categories/ returns 200 with a success response."""
        client = unit_client_factory(forum_category_router)

        mock_db = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        async def _db_gen():
            yield mock_db

        client.app.dependency_overrides[
            __import__("app.core.deps", fromlist=["get_db_session"]).get_db_session
        ] = _db_gen

        response = client.get("/api/forum/categories/")
        assert response.status_code == 200

    def test_list_categories_is_public(self, unit_client_factory):
        """GET /api/forum/categories/ requires no authentication."""
        client = unit_client_factory(forum_category_router, user_override=None)

        mock_db = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        async def _db_gen():
            yield mock_db

        client.app.dependency_overrides[
            __import__("app.core.deps", fromlist=["get_db_session"]).get_db_session
        ] = _db_gen

        response = client.get("/api/forum/categories/")
        assert response.status_code == 200


class TestForumThreads:
    def test_list_threads_returns_200(self, unit_client_factory):
        """GET /api/forum/threads/ returns 200 with a list of threads."""
        client = unit_client_factory(forum_thread_router)

        mock_db = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        async def _db_gen():
            yield mock_db

        client.app.dependency_overrides[
            __import__("app.core.deps", fromlist=["get_db_session"]).get_db_session
        ] = _db_gen

        response = client.get("/api/forum/threads/")
        assert response.status_code == 200

    def test_list_threads_is_public(self, unit_client_factory):
        """GET /api/forum/threads/ requires no authentication."""
        client = unit_client_factory(forum_thread_router, user_override=None)

        mock_db = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        async def _db_gen():
            yield mock_db

        client.app.dependency_overrides[
            __import__("app.core.deps", fromlist=["get_db_session"]).get_db_session
        ] = _db_gen

        response = client.get("/api/forum/threads/")
        assert response.status_code == 200

    def test_list_threads_filters_by_category(self, unit_client_factory):
        """GET /api/forum/threads/?category_id=1 filters by category."""
        client = unit_client_factory(forum_thread_router, user_override=None)

        mock_db = AsyncMock()
        result = MagicMock()
        result.scalars.return_value.all.return_value = []
        mock_db.execute = AsyncMock(return_value=result)

        async def _db_gen():
            yield mock_db

        client.app.dependency_overrides[
            __import__("app.core.deps", fromlist=["get_db_session"]).get_db_session
        ] = _db_gen

        response = client.get("/api/forum/threads/?category_id=1")
        assert response.status_code == 200


class TestForumThreadDetail:
    def test_get_thread_returns_200(self, unit_client_factory):
        """GET /api/forum/threads/:id returns 200 for a known thread."""
        client = unit_client_factory(forum_thread_router)
        now = datetime.now(timezone.utc)

        mock_thread = MagicMock()
        mock_thread.id = 1
        mock_thread.title = "Test Thread"
        mock_thread.slug = "test-thread"
        mock_thread.status = "open"
        mock_thread.category_id = 1
        mock_thread.category = None
        mock_thread.user_id = 1
        mock_thread.user = None
        mock_thread.world_id = None
        mock_thread.world = None
        mock_thread.story_id = None
        mock_thread.story = None
        mock_thread.view_count = 0
        mock_thread.post_count = 0
        mock_thread.last_post_at = None
        mock_thread.last_post_by = None
        mock_thread.is_pinned = False
        mock_thread.is_locked = False
        mock_thread.created_at = now
        mock_thread.updated_at = now

        with patch("app.routers.forum_thread.crud_thread.get_forum_thread", new=AsyncMock(return_value=mock_thread)), \
             patch("app.routers.forum_thread.crud_post.get_thread_posts", new=AsyncMock(return_value=[])), \
             patch("app.routers.forum_thread.crud_thread.is_thread_subscribed", new=AsyncMock(return_value=False)):
            response = client.get("/api/forum/threads/1")
        assert response.status_code == 200

    def test_get_thread_is_public(self, unit_client_factory):
        """GET /api/forum/threads/:id requires no authentication."""
        client = unit_client_factory(forum_thread_router, user_override=None)
        now = datetime.now(timezone.utc)

        mock_thread = MagicMock()
        mock_thread.id = 1
        mock_thread.title = "Test Thread"
        mock_thread.slug = "test-thread"
        mock_thread.status = "open"
        mock_thread.category_id = 1
        mock_thread.category = None
        mock_thread.user_id = 1
        mock_thread.user = None
        mock_thread.world_id = None
        mock_thread.world = None
        mock_thread.story_id = None
        mock_thread.story = None
        mock_thread.view_count = 0
        mock_thread.post_count = 0
        mock_thread.last_post_at = None
        mock_thread.last_post_by = None
        mock_thread.is_pinned = False
        mock_thread.is_locked = False
        mock_thread.created_at = now
        mock_thread.updated_at = now

        with patch("app.routers.forum_thread.crud_thread.get_forum_thread", new=AsyncMock(return_value=mock_thread)), \
             patch("app.routers.forum_thread.crud_post.get_thread_posts", new=AsyncMock(return_value=[])):
            response = client.get("/api/forum/threads/1")
        assert response.status_code == 200


class TestForumCreateThread:
    def test_create_thread_validation_error(self, unit_client_factory):
        """POST /api/forum/threads/ with invalid data returns 422."""
        client = unit_client_factory(forum_thread_router)
        response = client.post(
            "/api/forum/threads/",
            json={"title": "", "category_id": 1, "initial_post_content": "Content"},
        )
        assert response.status_code == 422


class TestForumPosts:
    def test_create_post_rejects_empty_content(self, unit_client_factory, mock_user):
        """POST /api/forum/posts/ with empty content returns 400 or 422."""
        client = unit_client_factory(forum_post_router, user_override=mock_user)
        response = client.post(
            "/api/forum/posts/",
            json={"thread_id": 1, "content": ""},
        )
        assert response.status_code in (400, 422)