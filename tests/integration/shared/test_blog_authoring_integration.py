"""Integration tests for blog authoring API flows (create, edit, publish, delete)."""

import pytest


pytestmark = pytest.mark.integration


def _get_access_token(client, username, password):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_create_blog_post_returns_201(client, register_and_login):
    """POST /api/blog/posts creates a new draft post and returns it wrapped."""
    credentials, _ = register_and_login("blog_author_test")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/blog/posts",
        headers=headers,
        json={
            "title": "Test Blog Post",
            "content": "This is the body of the test blog post.",
            "excerpt": "A short summary",
            "status": "draft",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["title"] == "Test Blog Post"
    assert body["data"]["status"] == "draft"
    assert body["data"]["id"] is not None


def test_get_author_posts_returns_only_authors_posts(client, register_and_login):
    """GET /api/blog/posts?author_id={id} returns only posts by that author."""
    credentials, _ = register_and_login("author_posts_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/blog/posts",
        headers=headers,
        json={"title": "My Post", "content": "Content", "excerpt": "Summary"},
    )
    assert create_response.status_code == 201, create_response.text
    post_id = create_response.json()["data"]["id"]

    get_response = client.get(f"/api/blog/posts?author_id={credentials['username']}", headers=headers)
    assert get_response.status_code == 200, get_response.text
    body = get_response.json()
    assert body["success"] is True
    assert any(p["id"] == post_id for p in body["data"])


def test_update_blog_post_modifies_fields(client, register_and_login):
    """PUT /api/blog/posts/{id} updates title and content and returns the updated post."""
    credentials, _ = register_and_login("update_post_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/blog/posts",
        headers=headers,
        json={"title": "Original Title", "content": "Original content"},
    )
    post_id = create_response.json()["data"]["id"]

    update_response = client.put(
        f"/api/blog/posts/{post_id}",
        headers=headers,
        json={"title": "Updated Title", "content": "Updated content"},
    )
    assert update_response.status_code == 200, update_response.text
    update_body = update_response.json()
    assert update_body["success"] is True
    assert update_body["data"]["title"] == "Updated Title"
    assert update_body["data"]["content"] == "Updated content"


def test_publish_blog_post_changes_status_to_published(client, register_and_login):
    """POST /api/blog/posts/{id}/publish sets status to published and returns the post."""
    credentials, _ = register_and_login("publish_post_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/blog/posts",
        headers=headers,
        json={"title": "Draft Post", "content": "Draft content"},
    )
    post_id = create_response.json()["data"]["id"]

    publish_response = client.post(f"/api/blog/posts/{post_id}/publish", headers=headers)
    assert publish_response.status_code == 200, publish_response.text
    publish_body = publish_response.json()
    assert publish_body["success"] is True
    assert publish_body["data"]["status"] == "published"
    assert publish_body["data"]["published_at"] is not None


def test_delete_blog_post_returns_204(client, register_and_login):
    """DELETE /api/blog/posts/{id} removes the post and returns 204."""
    credentials, _ = register_and_login("delete_post_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/blog/posts",
        headers=headers,
        json={"title": "To Delete", "content": "Delete me"},
    )
    post_id = create_response.json()["data"]["id"]

    delete_response = client.delete(f"/api/blog/posts/{post_id}", headers=headers)
    assert delete_response.status_code == 204, delete_response.text

    get_response = client.get(f"/api/blog/posts/{post_id}", headers=headers)
    assert get_response.status_code == 404, get_response.text


def test_blog_posts_search_returns_matching(client, register_and_login):
    """GET /api/blog/posts?search=term returns posts with matching title or content."""
    credentials, _ = register_and_login("search_post_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/blog/posts",
        headers=headers,
        json={"title": "Fantasy World Post", "content": "Magic and dragons"},
    )
    client.post(
        "/api/blog/posts",
        headers=headers,
        json={"title": "Sci-Fi Post", "content": "Space travel"},
    )

    search_response = client.get("/api/blog/posts?search=Fantasy", headers=headers)
    assert search_response.status_code == 200, search_response.text
    search_body = search_response.json()
    assert search_body["success"] is True
    assert len(search_body["data"]) >= 1


def test_get_blog_post_by_slug_returns_post(client, register_and_login):
    """GET /api/blog/posts/{slug} returns the post matching that URL slug."""
    credentials, _ = register_and_login("slug_post_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/blog/posts",
        headers=headers,
        json={"title": "My Slug Post", "content": "Content here"},
    )
    slug = create_response.json()["data"]["slug"]

    get_response = client.get(f"/api/blog/posts/{slug}", headers=headers)
    assert get_response.status_code == 200, get_response.text
    get_body = get_response.json()
    assert get_body["data"]["slug"] == slug


def test_unauthenticated_cannot_create_post(client):
    """POST /api/blog/posts without auth returns 401 or 403."""
    response = client.post(
        "/api/blog/posts",
        json={"title": "No Auth Post", "content": "Should fail"},
    )
    assert response.status_code in (401, 403), response.text


def test_full_blog_authoring_flow(client, register_and_login):
    """Create a post, verify it appears in the list, update it, publish it, then delete it."""
    credentials, _ = register_and_login("full_flow_author")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/blog/posts",
        headers=headers,
        json={"title": "Flow Test Post", "content": "Initial draft content", "excerpt": "Intro"},
    )
    assert create_response.status_code == 201, create_response.text
    post_id = create_response.json()["data"]["id"]

    list_response = client.get("/api/blog/posts", headers=headers)
    assert list_response.status_code == 200, list_response.text
    assert any(p["id"] == post_id for p in list_response.json()["data"])

    update_response = client.put(
        f"/api/blog/posts/{post_id}",
        headers=headers,
        json={"title": "Flow Test Post Updated"},
    )
    assert update_response.status_code == 200, update_response.text

    publish_response = client.post(f"/api/blog/posts/{post_id}/publish", headers=headers)
    assert publish_response.status_code == 200, publish_response.text
    assert publish_response.json()["data"]["status"] == "published"

    delete_response = client.delete(f"/api/blog/posts/{post_id}", headers=headers)
    assert delete_response.status_code == 204, delete_response.text