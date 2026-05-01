"""Mock-based unit tests for blog authoring router (create, list, update, publish, delete)."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.routers.blog import router as blog_router
from app.routers.blog_media import router as blog_media_router
from app.models.blog_post import BlogPostStatus


pytestmark = pytest.mark.unit


def _post(
    id=1,
    title="Test Post",
    slug="test-post",
    content="Post body content",
    excerpt="Test excerpt",
    status="draft",
    author_id=1,
):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=id,
        title=title,
        slug=slug,
        content=content,
        excerpt=excerpt,
        featured_image_url=None,
        status=status,
        author_id=author_id,
        view_count=0,
        like_count=0,
        comment_count=0,
        published_at=None,
        created_at=now,
        updated_at=now,
    )


def test_create_blog_post_returns_created_post(unit_client_factory, mock_db_session):
    """POST /api/blog/posts creates a post and returns it wrapped in ApiResponse."""
    client = unit_client_factory(blog_router)

    created = _post(id=5, title="New Post", slug="new-post")

    with patch("app.routers.blog.blog_service.create_post", new=AsyncMock(return_value=created)):
        response = client.post(
            "/api/blog/posts",
            json={
                "title": "New Post",
                "content": "Post body",
                "excerpt": "Test excerpt",
                "status": "draft",
            },
        )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["title"] == "New Post"
    assert body["data"]["status"] == "draft"


def test_get_blog_posts_returns_published_posts(unit_client_factory, mock_db_session):
    """GET /api/blog/posts returns published posts wrapped in ApiResponse."""
    client = unit_client_factory(blog_router)

    posts = [
        _post(id=1, title="Post One", status="published"),
        _post(id=2, title="Post Two", status="published"),
    ]

    with patch("app.routers.blog.blog_service.get_published_posts", new=AsyncMock(return_value=posts)):
        response = client.get("/api/blog/posts")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 2


def test_get_blog_posts_filters_by_author(unit_client_factory, mock_db_session):
    """GET /api/blog/posts?author_id=1 returns only posts by that author."""
    client = unit_client_factory(blog_router)

    posts = [_post(id=3, title="Author Post", author_id=1)]

    with patch("app.routers.blog.blog_service.get_published_posts", new=AsyncMock(return_value=posts)):
        response = client.get("/api/blog/posts?author_id=1")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert all(p["author_id"] == 1 for p in body["data"])


def test_get_blog_posts_filters_by_search(unit_client_factory, mock_db_session):
    """GET /api/blog/posts?search=term returns matching posts."""
    client = unit_client_factory(blog_router)

    posts = [_post(id=4, title="Searchable Post")]

    with patch("app.routers.blog.blog_service.get_published_posts", new=AsyncMock(return_value=posts)):
        response = client.get("/api/blog/posts?search=Searchable")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 1


def test_get_blog_post_by_slug_returns_post(unit_client_factory, mock_db_session):
    """GET /api/blog/posts/test-post returns the post with that slug."""
    client = unit_client_factory(blog_router)
    post = _post(id=1, title="Slug Post", slug="slug-post", status=BlogPostStatus.PUBLISHED)
    refreshed = _post(id=1, title="Slug Post", slug="slug-post", status=BlogPostStatus.PUBLISHED)

    with patch("app.routers.blog.blog_service.get_post_by_slug", new=AsyncMock(return_value=post)), \
         patch("app.routers.blog.blog_service.get_post_by_id", new=AsyncMock(return_value=refreshed)), \
         patch("app.services.blog_view_tracker.blog_view_tracker", new=MagicMock(track_view=AsyncMock())):
        response = client.get("/api/blog/posts/slug-post")

    assert response.status_code == 200, response.text


def test_get_blog_post_by_slug_returns_404_for_unknown_slug(unit_client_factory, mock_db_session):
    """GET /api/blog/posts/unknown returns 404."""
    client = unit_client_factory(blog_router)

    with patch("app.routers.blog.blog_service.get_post_by_slug", new=AsyncMock(return_value=None)):
        response = client.get("/api/blog/posts/nonexistent-slug")

    assert response.status_code == 404, response.text


def test_update_blog_post_returns_updated_post(unit_client_factory, mock_db_session):
    """PUT /api/blog/posts/1 updates and returns the post."""
    client = unit_client_factory(blog_router)
    updated = _post(id=1, title="Updated Title")

    with patch("app.routers.blog.blog_service.update_post", new=AsyncMock(return_value=updated)):
        response = client.put(
            "/api/blog/posts/1",
            json={"title": "Updated Title"},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["title"] == "Updated Title"


def test_publish_blog_post_returns_published_post(unit_client_factory, mock_db_session):
    """POST /api/blog/posts/1/publish sets status to published and returns post."""
    client = unit_client_factory(blog_router)
    published = _post(id=1, title="Published Post", status="published")

    with patch("app.routers.blog.blog_service.publish_post", new=AsyncMock(return_value=published)):
        response = client.post("/api/blog/posts/1/publish")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "published"


def test_delete_blog_post_returns_204(unit_client_factory, mock_db_session):
    """DELETE /api/blog/posts/1 returns 204 on success."""
    client = unit_client_factory(blog_router)

    with patch("app.routers.blog.blog_service.soft_delete_post", new=AsyncMock(return_value=True)):
        response = client.delete("/api/blog/posts/1")

    assert response.status_code == 204, response.text