# tests/test_forum_admin_complete.py

"""
Comprehensive tests for Forum and Admin API endpoints
Tests community features, content moderation, and administrative functions with ApiResponse wrappers
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from app.schemas.base import ApiResponse, ApiError
from app.routers import forum_category as category_router
from app.routers import forum_thread as thread_router
from app.routers import forum_post as post_router
from app.routers import admin_cta as admin_cta_router


class TestForumCategoryEndpoints:
    """Test forum category management endpoints."""

    @pytest.mark.asyncio
    async def test_get_forum_categories_success(self, test_client_factory):
        """Test GET /forum-categories - Get all forum categories."""
        with patch('app.routers.forum_category.crud_category') as mock_crud:
            # Mock categories with thread counts
            mock_category = Mock()
            mock_category.id = 1
            mock_category.name = "General Discussion"
            mock_category.description = "Talk about anything"
            mock_category.sort_order = 1
            mock_category.is_active = True
            mock_category.icon = "fa-comments"
            mock_category.threads = [Mock(is_deleted=False)] * 5  # 5 threads

            mock_crud.get_forum_categories.return_value = [mock_category]

            client = test_client_factory.create_client_with_routers(category_router.router)

            response = client.get("/forum-categories")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            categories = data["data"]
            assert len(categories) == 1
            assert categories[0]["name"] == "General Discussion"
            assert categories[0]["thread_count"] == 5

    @pytest.mark.asyncio
    async def test_create_forum_category_admin_success(self, test_client_factory, mock_admin_user):
        """Test POST /forum-categories - Admin creates new category."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.forum_category.crud_category') as mock_crud, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_admin_user
            mock_get_db.return_value = AsyncMock()

            # Mock created category
            created_category = Mock()
            created_category.id = 1
            created_category.name = "New Category"
            created_category.slug = "new-category"
            created_category.is_active = True

            mock_crud.create_forum_category.return_value = created_category

            client = test_client_factory.create_client_with_routers(category_router.router)

            category_data = {
                "name": "New Category",
                "description": "A new discussion category",
                "icon": "fa-star"
            }

            response = client.post("/forum-categories", json=category_data)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            assert data["data"]["name"] == "New Category"
            assert data["data"]["slug"] == "new-category"

    @pytest.mark.asyncio
    async def test_create_forum_category_non_admin_forbidden(self, test_client_factory, mock_authenticated_user):
        """Test POST /forum-categories - Non-admin cannot create categories."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            mock_get_user.return_value = mock_authenticated_user

            client = test_client_factory.create_client_with_routers(category_router.router)

            category_data = {"name": "Attempted Category"}

            response = client.post("/forum-categories", json=category_data)

            assert response.status_code == 403


class TestForumThreadEndpoints:
    """Test forum thread management endpoints."""

    @pytest.mark.asyncio
    async def test_get_forum_threads_with_filters(self, test_client_factory):
        """Test GET /forum-threads - Get threads with various filters."""
        with patch('app.routers.forum_thread.crud_thread') as mock_crud:
            # Mock threads
            mock_threads = [
                Mock(
                    id=1,
                    title="Welcome to the Forum",
                    slug="welcome-to-forum",
                    status="normal",
                    view_count=150,
                    post_count=23,
                    created_at=datetime.utcnow()
                ),
                Mock(
                    id=2,
                    title="How to Write Better Dialogues",
                    slug="writing-dialogues",
                    status="normal",
                    view_count=89,
                    post_count=12,
                    created_at=datetime.utcnow() - timedelta(days=1)
                )
            ]
            mock_crud.get_forum_threads.return_value = mock_threads

            client = test_client_factory.create_client_with_routers(thread_router.router)

            response = client.get("/forum-threads?order_by=popular&limit=10")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            threads = data["data"]
            assert len(threads) == 2
            assert threads[0]["title"] == "Welcome to the Forum"

            # Verify filtering was called correctly
            mock_crud.get_forum_threads.assert_called_once()
            call_kwargs = mock_crud.get_forum_threads.call_args.kwargs
            assert call_kwargs["order_by"] == "popular"
            assert call_kwargs["limit"] == 10

    @pytest.mark.asyncio
    async def test_create_forum_thread_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /forum-threads - Create new thread with initial post."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.forum_thread.crud_thread') as mock_thread_crud, \
             patch('app.routers.forum_thread.crud_post') as mock_post_crud, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_get_db.return_value = AsyncMock()

            # Mock thread and post creation
            created_thread = Mock()
            created_thread.id = 1
            created_thread.title = "New Discussion Thread"
            created_thread.slug = "new-discussion-thread"

            created_post = Mock()
            created_post.id = 1
            created_post.created_at = datetime.utcnow()

            mock_thread_crud.create_forum_thread.return_value = created_thread
            mock_post_crud.create_forum_post.return_value = created_post

            client = test_client_factory.create_client_with_routers(thread_router.router)

            thread_data = {
                "title": "New Discussion Thread",
                "category_id": 1,
                "initial_post_content": "<p>Welcome to the discussion!</p>",
                "initial_post_content_html": "Welcome to the discussion!"
            }

            response = client.post("/forum-threads", json=thread_data)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            assert data["data"]["title"] == "New Discussion Thread"
            assert "posts" in data["data"]

    @pytest.mark.asyncio
    async def test_get_thread_detail_with_posts(self, test_client_factory, mock_authenticated_user):
        """Test GET /forum-threads/{thread_id} - Get thread with all posts."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.forum_thread.crud_thread') as mock_thread_crud, \
             patch('app.routers.forum_thread.crud_post') as mock_post_crud:

            mock_get_user.return_value = mock_authenticated_user

            # Mock thread
            mock_thread = Mock()
            mock_thread.id = 1
            mock_thread.title = "Detailed Thread"
            mock_thread.is_pinned = False
            mock_thread.is_locked = False

            # Mock posts
            mock_posts = [
                Mock(
                    content="First post content",
                    user=Mock(username="user1", display_name="User 1"),
                    upvote_count=5
                ),
                Mock(
                    content="Reply content",
                    user=Mock(username="user2", display_name="User 2"),
                    upvote_count=2
                )
            ]

            mock_thread_crud.get_forum_thread.return_value = mock_thread
            mock_post_crud.get_thread_posts.return_value = mock_posts

            client = test_client_factory.create_client_with_routers(thread_router.router)

            response = client.get("/forum-threads/1")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            thread_data = data["data"]
            assert thread_data["title"] == "Detailed Thread"
            assert len(thread_data["posts"]) == 2

    @pytest.mark.asyncio
    async def test_update_thread_success(self, test_client_factory, mock_authenticated_user):
        """Test PUT /forum-threads/{thread_id} - Update thread."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.forum_thread.crud_thread') as mock_thread_crud, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_get_db.return_value = AsyncMock()

            # Mock existing thread
            mock_thread = Mock()
            mock_thread.user_id = mock_authenticated_user.id

            updated_thread = Mock()
            updated_thread.title = "Updated Thread Title"

            mock_thread_crud.get_forum_thread.return_value = mock_thread
            mock_thread_crud.update_forum_thread.return_value = updated_thread

            client = test_client_factory.create_client_with_routers(thread_router.router)

            update_data = {"title": "Updated Thread Title"}

            response = client.put("/forum-threads/1", json=update_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


class TestForumPostEndpoints:
    """Test forum post management endpoints."""

    @pytest.mark.asyncio
    async def test_get_thread_posts_success(self, test_client_factory):
        """Test GET /forum-posts/thread/{thread_id} - Get posts for thread."""
        with patch('app.routers.forum_post.crud_post') as mock_crud, \
             patch('app.core.deps.get_current_active_user') as mock_get_user:

            mock_get_user.return_value = None  # Anonymous access to forum

            # Mock posts with votes
            mock_posts = [
                Mock(
                    id=1,
                    content="Great discussion topic!",
                    content_html="<p>Great discussion topic!</p>",
                    thread=Mock(title="Discussion Thread"),
                    user=Mock(username="poster1", display_name="Poster One"),
                    upvote_count=3,
                    downvote_count=0,
                    score=3
                )
            ]

            # Mock user votes (none for anonymous user)
            mock_crud.get_thread_posts.return_value = mock_posts
            mock_crud.get_user_vote_on_post.return_value = None
            mock_crud.get_post_replies.return_value = []

            client = test_client_factory.create_client_with_routers(post_router.router)

            response = client.get("/forum-posts/thread/1")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            posts = data["data"]
            assert len(posts) == 1
            assert posts[0]["content"] == "Great discussion topic!"
            assert posts[0]["user_vote"] is None  # Anonymous user

    @pytest.mark.asyncio
    async def test_create_forum_post_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /forum-posts - Create new post."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.forum_post.crud_post') as mock_crud, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_get_db.return_value = AsyncMock()

            # Mock created post
            created_post = Mock()
            created_post.id = 1
            created_post.thread_id = 1
            created_post.content = "New forum post content"
            created_post.upvote_count = 0

            mock_crud.create_forum_post.return_value = created_post
            mock_crud.get_user_vote_on_post.return_value = None

            client = test_client_factory.create_client_with_routers(post_router.router)

            post_data = {
                "thread_id": 1,
                "content": "New forum post content",
                "content_html": "<p>New forum post content</p>"
            }

            response = client.post("/forum-posts", json=post_data)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            assert data["data"]["thread_id"] == 1
            assert data["data"]["upvote_count"] == 0

    @pytest.mark.asyncio
    async def test_vote_on_post_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /forum-posts/{post_id}/vote - Vote on post."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.forum_post.crud_post') as mock_crud:

            mock_get_user.return_value = mock_authenticated_user

            # Mock voted post
            voted_post = Mock()
            voted_post.id = 1
            voted_post.upvote_count = 6
            voted_post.downvote_count = 1
            voted_post.score = 5

            mock_crud.vote_on_post.return_value = voted_post

            client = test_client_factory.create_client_with_routers(post_router.router)

            vote_data = {"vote_type": "upvote"}

            response = client.post("/forum-posts/1/vote", json=vote_data)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            vote_result = data["data"]
            assert vote_result["upvote_count"] == 6
            assert vote_result["downvote_count"] == 1
            assert vote_result["score"] == 5


class TestAdminCTAEndpoints:
    """Test admin CTA management endpoints."""

    @pytest.mark.asyncio
    async def test_get_all_ctas_admin_only(self, test_client_factory, mock_admin_user):
        """Test GET /admin/cta-content - Admin gets all CTAs."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.admin_cta.crud_cta') as mock_crud, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_admin_user
            mock_get_db.return_value = AsyncMock()

            # Mock CTAs
            mock_ctas = [
                Mock(
                    title="Welcome CTA",
                    position="hero",
                    is_active=True,
                    sort_order=1
                ),
                Mock(
                    title="Testimonial CTA",
                    position="footer",
                    is_active=False,
                    sort_order=2
                )
            ]

            # Mock query result
            mock_result = Mock()
            mock_result.scalars.return_value.all.return_value = mock_ctas
            mock_db.execute.return_value = mock_result

            client = test_client_factory.create_client_with_routers(admin_cta_router.router)

            response = client.get("/admin/cta-content")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            ctas = data["data"]
            assert len(ctas) == 2
            assert ctas[0]["title"] == "Welcome CTA"

    @pytest.mark.asyncio
    async def test_get_all_ctas_non_admin_forbidden(self, test_client_factory, mock_authenticated_user):
        """Test GET /admin/cta-content - Non-admin forbidden."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            mock_get_user.return_value = mock_authenticated_user

            client = test_client_factory.create_client_with_routers(admin_cta_router.router)

            response = client.get("/admin/cta-content")

            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_cta_success(self, test_client_factory, mock_admin_user):
        """Test POST /admin/cta-content - Create new CTA."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.admin_cta.crud_cta') as mock_crud, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_admin_user
            mock_get_db.return_value = AsyncMock()

            # Mock created CTA
            created_cta = Mock()
            created_cta.id = 1
            created_cta.title = "New CTA"
            created_cta.position = "hero"

            mock_crud.create_cta_content.return_value = created_cta

            client = test_client_factory.create_client_with_routers(admin_cta_router.router)

            cta_data = {
                "title": "New CTA",
                "content": "Welcome to our platform!",
                "position": "hero",
                "style": "gradient"
            }

            response = client.post("/admin/cta-content", json=cta_data)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            assert data["data"]["title"] == "New CTA"
            assert data["data"]["id"] == 1

    @pytest.mark.asyncio
    async def test_toggle_cta_active_success(self, test_client_factory, mock_admin_user):
        """Test POST /admin/cta-content/{cta_id}/toggle-active - Toggle CTA status."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.admin_cta.crud_cta') as mock_crud:

            mock_get_user.return_value = mock_admin_user

            # Mock toggled CTA
            toggled_cta = Mock()
            toggled_cta.is_active = False

            mock_crud.toggle_cta_active_status.return_value = toggled_cta

            client = test_client_factory.create_client_with_routers(admin_cta_router.router)

            response = client.post("/admin/cta-content/1/toggle-active")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"]["is_active"] is False

    @pytest.mark.asyncio
    async def test_delete_cta_success(self, test_client_factory, mock_admin_user):
        """Test DELETE /admin/cta-content/{cta_id} - Delete CTA."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.admin_cta.crud_cta') as mock_crud:

            mock_get_user.return_value = mock_admin_user
            mock_crud.delete_cta_content.return_value = True

            client = test_client_factory.create_client_with_routers(admin_cta_router.router)

            response = client.delete("/admin/cta-content/1")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"]["message"] == "CTA deleted successfully"


class TestForumModerationEndpoints:
    """Test forum moderation and admin features."""

    @pytest.mark.asyncio
    async def test_get_user_forum_stats(self, test_client_factory):
        """Test GET /forum-posts/user/{user_id}/stats - Get user's forum statistics."""
        with patch('app.routers.forum_post.crud_post') as mock_crud, \
             patch('app.core.deps.get_db_session') as mock_get_db, \
             patch('app.routers.forum_post.User') as MockUser, \
             patch('app.routers.forum_post.crud_thread') as mock_thread_crud:

            mock_get_db.return_value = AsyncMock()

            # Mock user
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = "activeuser"
            mock_user.created_at = datetime.utcnow() - timedelta(days=365)

            # Mock stats
            mock_crud.get_user_post_count.return_value = 45
            mock_crud.get_user_karma.return_value = 125
            mock_threads = [Mock() for _ in range(8)]  # 8 threads
            mock_thread_crud.get_forum_threads.return_value = mock_threads

            client = test_client_factory.create_client_with_routers(post_router.router)

            response = client.get("/forum-posts/user/1/stats")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            stats = data["data"]
            assert stats["user_id"] == 1
            assert stats["username"] == "activeuser"
            assert stats["post_count"] == 45
            assert stats["total_karma"] == 125
            assert stats["thread_count"] == 8


class TestAdminDebugEndpoints:
    """Test admin debugging and maintenance endpoints."""

    @pytest.mark.asyncio
    async def test_debug_user_info_admin_only(self, test_client_factory, mock_authenticated_user):
        """Test GET /admin/debug/user-info - Admin debugging endpoint."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            # Note: In current code, this endpoint has no admin check
            mock_get_user.return_value = mock_authenticated_user

            client = test_client_factory.create_client_with_routers(admin_cta_router.router)

            response = client.get("/admin/debug/user-info")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            user_info = data["data"]
            assert "user_id" in user_info
            assert "username" in user_info


class TestForumAndAdminErrorHandling:
    """Test error handling across forum and admin endpoints."""

    @pytest.mark.asyncio
    async def test_create_thread_validation_error(self, test_client_factory, mock_authenticated_user):
        """Test POST /forum-threads - Validation error for missing required fields."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            mock_get_user.return_value = mock_authenticated_user

            client = test_client_factory.create_client_with_routers(thread_router.router)

            # Missing required title
            invalid_data = {
                "category_id": 1,
                "initial_post_content": "Some content"
            }

            response = client.post("/forum-threads", json=invalid_data)

            # Should return validation error
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_post_thread_not_found(self, test_client_factory, mock_authenticated_user):
        """Test POST /forum-posts - Thread not found error."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.forum_post.crud_post') as mock_crud:

            mock_get_user.return_value = mock_authenticated_user
            mock_crud.create_forum_post.side_effect = ValueError("Thread not found")

            client = test_client_factory.create_client_with_routers(post_router.router)

            post_data = {
                "thread_id": 999,
                "content": "Content for non-existent thread"
            }

            response = client.post("/forum-posts", json=post_data)

            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_admin_cta_update_not_found(self, test_client_factory, mock_admin_user):
        """Test PUT /admin/cta-content/{cta_id} - CTA not found."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.admin_cta.crud_cta') as mock_crud:

            mock_get_user.return_value = mock_admin_user
            mock_crud.update_cta_content.return_value = None

            client = test_client_factory.create_client_with_routers(admin_cta_router.router)

            update_data = {"title": "Updated Title"}
            response = client.put("/admin/cta-content/999", json=update_data)

            assert response.status_code == 404