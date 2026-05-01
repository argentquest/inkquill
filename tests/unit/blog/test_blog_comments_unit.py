"""Mock-based unit tests for blog comment endpoints."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.routers.blog_comments import router as blog_comments_router


pytestmark = pytest.mark.unit


def _comment(id=1, content="Test comment", post_id=1, author_id=1, like_count=2):
    now = datetime.now(timezone.utc)
    mock = MagicMock()
    mock.id = id
    mock.content = content
    mock.author_id = author_id
    mock.post_id = post_id
    mock.parent_comment_id = None
    mock.status = MagicMock()
    mock.status.value = "approved"
    mock.like_count = like_count
    mock.reply_count = 0
    mock.is_author_reply = False
    mock.created_at = now
    mock.updated_at = now
    mock.author = SimpleNamespace(
        id=author_id,
        username="commenter",
        display_name="Commenter",
        profile_picture_url=None,
    )
    mock._manual_replies = []
    return mock


def _post(id=1, title="Test Post", allow_comments=True, author_id=1):
    now = datetime.now(timezone.utc)
    mock = MagicMock()
    mock.id = id
    mock.title = title
    mock.allow_comments = allow_comments
    mock.author_id = author_id
    mock.created_at = now
    mock.updated_at = now
    return mock


class TestCreateBlogComment:
    def test_create_comment_returns_201(self, unit_client_factory, mock_user):
        """POST /api/blog/posts/1/comments creates a comment."""
        client = unit_client_factory(blog_comments_router, user_override=mock_user)
        post = _post(id=1)
        comment = _comment(id=5, content="Great post!")

        with patch("app.services.blog_service.blog_service.get_post_by_id", new=AsyncMock(return_value=post)), \
             patch("app.services.blog_comment_service.blog_comment_service.create_comment", new=AsyncMock(return_value=comment)):
            response = client.post(
                "/api/blog/posts/1/comments",
                json={"content": "Great post!", "parent_comment_id": None},
            )
        assert response.status_code == 201
        body = response.json()
        assert body.get("success") is True
        assert body["data"]["content"] == "Great post!"

    def test_create_comment_rejects_when_comments_disabled(self, unit_client_factory, mock_user):
        """POST /api/blog/posts/1/comments returns 403 when comments are disabled."""
        client = unit_client_factory(blog_comments_router, user_override=mock_user)
        post = _post(id=1, allow_comments=False)

        with patch("app.services.blog_service.blog_service.get_post_by_id", new=AsyncMock(return_value=post)):
            response = client.post(
                "/api/blog/posts/1/comments",
                json={"content": "Great post!", "parent_comment_id": None},
            )
        assert response.status_code == 403

    def test_create_comment_rejects_missing_post(self, unit_client_factory, mock_user):
        """POST /api/blog/posts/999/comments returns 404 for unknown post."""
        client = unit_client_factory(blog_comments_router, user_override=mock_user)

        with patch("app.services.blog_service.blog_service.get_post_by_id", new=AsyncMock(return_value=None)):
            response = client.post(
                "/api/blog/posts/999/comments",
                json={"content": "Great post!", "parent_comment_id": None},
            )
        assert response.status_code == 404


class TestListBlogComments:
    def test_list_comments_returns_200(self, unit_client_factory):
        """GET /api/blog/posts/1/comments returns comment list."""
        client = unit_client_factory(blog_comments_router, user_override=None)
        comment = _comment(id=1, content="Nice read")

        with patch("app.services.blog_comment_service.blog_comment_service.get_post_comments", new=AsyncMock(return_value=[comment])):
            response = client.get("/api/blog/posts/1/comments")
        assert response.status_code == 200
        body = response.json()
        assert body.get("success") is True
        assert isinstance(body["data"], list)
        assert len(body["data"]) == 1
        assert body["data"][0]["content"] == "Nice read"

    def test_list_comments_is_public(self, unit_client_factory):
        """GET /api/blog/posts/1/comments requires no auth."""
        client = unit_client_factory(blog_comments_router, user_override=None)

        with patch("app.services.blog_comment_service.blog_comment_service.get_post_comments", new=AsyncMock(return_value=[])):
            response = client.get("/api/blog/posts/1/comments")
        assert response.status_code == 200


class TestUpdateBlogComment:
    def test_update_comment_returns_200(self, unit_client_factory, mock_user):
        """PUT /api/blog/comments/1 updates the comment."""
        client = unit_client_factory(blog_comments_router, user_override=mock_user)
        comment = _comment(id=1, content="Updated text")

        with patch("app.services.blog_comment_service.blog_comment_service.get_comment", new=AsyncMock(return_value=comment)), \
             patch("app.services.blog_comment_service.blog_comment_service.update_comment", new=AsyncMock(return_value=comment)):
            response = client.put(
                "/api/blog/comments/1",
                json={"content": "Updated text"},
            )
        assert response.status_code == 200
        body = response.json()
        assert body.get("success") is True


class TestDeleteBlogComment:
    def test_delete_comment_returns_204(self, unit_client_factory, mock_user):
        """DELETE /api/blog/comments/1 returns 204."""
        client = unit_client_factory(blog_comments_router, user_override=mock_user)
        comment = _comment(id=1, author_id=mock_user.id)
        post = _post(id=1, author_id=mock_user.id)

        with patch("app.services.blog_comment_service.blog_comment_service.get_comment", new=AsyncMock(return_value=comment)), \
             patch("app.services.blog_service.blog_service.get_post_by_id", new=AsyncMock(return_value=post)), \
             patch("app.services.blog_comment_service.blog_comment_service.delete_comment", new=AsyncMock(return_value=True)):
            response = client.delete("/api/blog/comments/1")
        assert response.status_code == 204


class TestLikeBlogComment:
    def test_like_comment_returns_200(self, unit_client_factory, mock_user):
        """POST /api/blog/comments/1/like increments like count."""
        client = unit_client_factory(blog_comments_router, user_override=mock_user)
        comment = _comment(id=1, like_count=3)

        with patch("app.services.blog_comment_service.blog_comment_service.get_comment", new=AsyncMock(return_value=comment)):
            response = client.post("/api/blog/comments/1/like")
        assert response.status_code == 200
        body = response.json()
        assert body.get("success") is True
