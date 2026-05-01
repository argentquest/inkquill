"""Integration tests for publishing, forum, and blog API contracts used by Sprint 09 routes."""
import pytest

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Published stories — public list
# ---------------------------------------------------------------------------

def test_published_stories_list_is_public(client):
    """Unauthenticated GET /api/v1/published-stories/ returns 200 with list shape."""
    resp = client.get("/api/v1/published-stories/")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    data = body["data"]
    assert "stories" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert isinstance(data["stories"], list)


def test_published_stories_list_only_returns_public_stories(client, register_and_login):
    """Published stories list only exposes is_public=True stories."""
    register_and_login("pub_list_check")
    resp = client.get("/api/v1/published-stories/")
    assert resp.status_code == 200, resp.text
    stories = resp.json()["data"]["stories"]
    for story in stories:
        assert story.get("is_public") is True


def test_published_story_detail_is_public(client, register_and_login):
    """GET /api/v1/published-stories/:id with an invalid id returns 404, not 401."""
    resp = client.get("/api/v1/published-stories/999999")
    assert resp.status_code == 404, resp.text


# ---------------------------------------------------------------------------
# Published stories — rating requires auth
# ---------------------------------------------------------------------------

def test_rate_story_requires_auth(client):
    """Unauthenticated POST /api/v1/published-stories/:id/rate returns 401 or 403."""
    resp = client.post("/api/v1/published-stories/1/rate", json={"rating": 5})
    assert resp.status_code in {401, 403}, resp.text


# ---------------------------------------------------------------------------
# Published stories — comments are public
# ---------------------------------------------------------------------------

def test_story_comments_endpoint_is_public(client):
    """GET /api/v1/published-stories/:id/comments returns 200 (empty) for a nonexistent story."""
    resp = client.get("/api/v1/published-stories/999999/comments")
    # Either 200 with empty list or 404 for unknown story — both are acceptable
    assert resp.status_code in {200, 404}, resp.text


# ---------------------------------------------------------------------------
# Forum — categories are public
# ---------------------------------------------------------------------------

def test_forum_categories_are_public(client):
    """Unauthenticated GET /api/forum/categories/ returns 200 with list."""
    resp = client.get("/api/forum/categories/")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


# ---------------------------------------------------------------------------
# Forum — threads are public
# ---------------------------------------------------------------------------

def test_forum_threads_are_public(client):
    """Unauthenticated GET /api/forum/threads/ returns 200 with list."""
    resp = client.get("/api/forum/threads/")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_forum_thread_detail_404_for_unknown(client):
    """GET /api/forum/threads/:id returns 404 for unknown thread."""
    resp = client.get("/api/forum/threads/999999")
    assert resp.status_code == 404, resp.text


# ---------------------------------------------------------------------------
# Blog — posts are public
# ---------------------------------------------------------------------------

def test_blog_posts_are_public(client):
    """Unauthenticated GET /api/blog/posts returns 200 with list."""
    resp = client.get("/api/blog/posts")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_blog_post_by_slug_404_for_unknown(client):
    """GET /api/blog/posts/:slug returns 404 for unknown slug."""
    resp = client.get("/api/blog/posts/this-slug-does-not-exist-xyz")
    assert resp.status_code == 404, resp.text


# ---------------------------------------------------------------------------
# Blog — search is public
# ---------------------------------------------------------------------------

def test_blog_search_requires_query(client):
    """GET /api/blog/search/ without q returns 422."""
    resp = client.get("/api/blog/search/")
    assert resp.status_code == 422, resp.text


def test_blog_search_is_public(client):
    """Unauthenticated GET /api/blog/search/?q=test returns 200."""
    resp = client.get("/api/blog/search/?q=test")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


# ---------------------------------------------------------------------------
# Forum — thread creation requires auth
# ---------------------------------------------------------------------------

def test_create_forum_thread_requires_auth(client):
    """Unauthenticated POST /api/forum/threads/ returns 401 or 403."""
    resp = client.post("/api/forum/threads/", json={
        "title": "Unauthorized thread",
        "category_id": 1,
        "initial_post_content": "This should not be created.",
    })
    assert resp.status_code in {401, 403}, resp.text


def test_create_forum_thread_authenticated(client, register_and_login):
    """Authenticated user can create a forum thread and initial post."""
    # Ensure a category exists first; create one if needed.
    cats_resp = client.get("/api/forum/categories/")
    assert cats_resp.status_code == 200
    categories = cats_resp.json()["data"]

    if not categories:
        # Create a category as admin is unavailable in integration — skip
        pytest.skip("No forum categories available in test database")

    cat_id = categories[0]["id"]
    register_and_login("forum_create")

    resp = client.post("/api/forum/threads/", json={
        "title": "Integration test thread",
        "category_id": cat_id,
        "initial_post_content": "This is the opening post.",
    })
    assert resp.status_code in {200, 201}, resp.text
    body = resp.json()
    assert body["success"] is True
    thread = body["data"]
    assert thread["title"] == "Integration test thread"
    assert isinstance(thread["posts"], list)
    assert len(thread["posts"]) >= 1
    assert thread["posts"][0]["content"] == "This is the opening post."


# ---------------------------------------------------------------------------
# Forum — post/reply creation requires auth
# ---------------------------------------------------------------------------

def test_create_forum_post_requires_auth(client):
    """Unauthenticated POST /api/forum/posts/ returns 401 or 403."""
    resp = client.post("/api/forum/posts/", json={
        "thread_id": 1,
        "content": "Unauthorized reply.",
    })
    assert resp.status_code in {401, 403}, resp.text


def test_create_forum_reply_authenticated(client, register_and_login):
    """Authenticated user can post a reply to an existing thread."""
    cats_resp = client.get("/api/forum/categories/")
    categories = cats_resp.json().get("data", [])
    if not categories:
        pytest.skip("No forum categories available in test database")

    register_and_login("forum_reply")
    cat_id = categories[0]["id"]

    thread_resp = client.post("/api/forum/threads/", json={
        "title": "Thread for reply test",
        "category_id": cat_id,
        "initial_post_content": "Opening post.",
    })
    assert thread_resp.status_code in {200, 201}, thread_resp.text
    thread_id = thread_resp.json()["data"]["id"]

    reply_resp = client.post("/api/forum/posts/", json={
        "thread_id": thread_id,
        "content": "This is a test reply.",
    })
    assert reply_resp.status_code in {200, 201}, reply_resp.text
    body = reply_resp.json()
    assert body["success"] is True
    post = body["data"]
    assert post["content"] == "This is a test reply."
    assert post["thread_id"] == thread_id
