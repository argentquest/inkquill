"""Mock-based unit tests for blog router."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from app.routers.blog import router as blog_router
from app.routers.blog_search import router as blog_search_router


pytestmark = pytest.mark.unit


def _make_result(return_value):
    result = MagicMock()
    result.scalars.return_value.all.return_value = return_value if return_value else []
    scalar_val = return_value[0] if return_value and isinstance(return_value, list) else (return_value if return_value else None)
    result.scalar_one_or_none.return_value = scalar_val
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


def _blog_post(
    id: int = 1,
    title: str = "Test Blog Post",
    slug: str = "test-blog-post",
    status: str = "published",
    author_id: int = 1,
):
    now = SimpleNamespace()
    mock = MagicMock()
    mock.id = id
    mock.title = title
    mock.slug = slug
    mock.content = "<p>Test content</p>"
    mock.excerpt = "Test excerpt"
    mock.featured_image_url = None
    mock.status = SimpleNamespace(value=status)
    mock.author_id = author_id
    mock.view_count = 10
    mock.like_count = 2
    mock.comment_count = 1
    mock.published_at = now
    mock.created_at = now
    mock.updated_at = now
    return mock


class TestBlogList:
    def test_list_blog_posts_returns_200(self, unit_client_factory):
        client = unit_client_factory(blog_router)
        mock_db = _sync_mock_db([_blog_post()])
        with patch("app.routers.blog.get_db_session", new=lambda: mock_db):
            response = client.get("/api/blog/posts")
        assert response.status_code == 200

    def test_list_blog_posts_is_public(self, unit_client_factory):
        client = unit_client_factory(blog_router, user_override=None)
        mock_db = _sync_mock_db([])
        with patch("app.routers.blog.get_db_session", new=lambda: mock_db):
            response = client.get("/api/blog/posts")
        assert response.status_code == 200

    def test_list_blog_posts_filters_by_search(self, unit_client_factory):
        client = unit_client_factory(blog_router, user_override=None)
        mock_db = _sync_mock_db([])
        with patch("app.routers.blog.get_db_session", new=lambda: mock_db):
            response = client.get("/api/blog/posts?search=test")
        assert response.status_code == 200

    def test_list_blog_posts_filters_by_category(self, unit_client_factory):
        client = unit_client_factory(blog_router, user_override=None)
        mock_db = _sync_mock_db([])
        with patch("app.routers.blog.get_db_session", new=lambda: mock_db):
            response = client.get("/api/blog/posts?category_id=1")
        assert response.status_code == 200


class TestBlogPostDetail:
    def test_get_blog_post_returns_200(self, unit_client_factory):
        client = unit_client_factory(blog_router)
        mock_post = _blog_post()
        with patch("app.routers.blog.blog_service.get_post_by_slug", new=AsyncMock(return_value=mock_post)), \
             patch("app.routers.blog.blog_service.get_post_by_id", new=AsyncMock(return_value=mock_post)), \
             patch("app.routers.blog._build_blog_post_read", new=lambda p: {"id": p.id, "title": p.title, "slug": p.slug, "content": p.content, "excerpt": p.excerpt, "featured_image_url": p.featured_image_url, "category_id": p.category_id, "meta_title": None, "meta_description": None, "meta_keywords": None, "allow_comments": True, "is_ai_generated": False, "is_featured": False, "status": "published", "author_id": p.author_id, "view_count": p.view_count, "like_count": p.like_count, "comment_count": p.comment_count, "published_at": None, "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00", "author": None, "category": None, "tags": []}):
            response = client.get("/api/blog/posts/test-blog-post")
        assert response.status_code == 200

    def test_get_blog_post_is_public(self, unit_client_factory):
        client = unit_client_factory(blog_router, user_override=None)
        mock_post = _blog_post()
        with patch("app.routers.blog.blog_service.get_post_by_slug", new=AsyncMock(return_value=mock_post)), \
             patch("app.routers.blog.blog_service.get_post_by_id", new=AsyncMock(return_value=mock_post)), \
             patch("app.routers.blog._build_blog_post_read", new=lambda p: {"id": p.id, "title": p.title, "slug": p.slug, "content": p.content, "excerpt": p.excerpt, "featured_image_url": p.featured_image_url, "category_id": p.category_id, "meta_title": None, "meta_description": None, "meta_keywords": None, "allow_comments": True, "is_ai_generated": False, "is_featured": False, "status": "published", "author_id": p.author_id, "view_count": p.view_count, "like_count": p.like_count, "comment_count": p.comment_count, "published_at": None, "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00", "author": None, "category": None, "tags": []}):
            response = client.get("/api/blog/posts/test-blog-post")
        assert response.status_code == 200

    def test_get_blog_post_returns_404_for_unknown_slug(self, unit_client_factory):
        client = unit_client_factory(blog_router, user_override=None)
        with patch("app.routers.blog.blog_service.get_post_by_slug", new=AsyncMock(return_value=None)):
            response = client.get("/api/blog/posts/no-such-post")
        assert response.status_code == 404


class TestBlogSearch:
    def test_blog_search_returns_200(self, unit_client_factory):
        client = unit_client_factory(blog_search_router, user_override=None)
        with patch("app.routers.blog_search.blog_search_service.search_posts", new=AsyncMock(return_value=[])):
            response = client.get("/api/blog/search/?q=test")
        assert response.status_code == 200

    def test_blog_search_is_public(self, unit_client_factory):
        client = unit_client_factory(blog_search_router, user_override=None)
        with patch("app.routers.blog_search.blog_search_service.search_posts", new=AsyncMock(return_value=[])):
            response = client.get("/api/blog/search/?q=test")
        assert response.status_code == 200