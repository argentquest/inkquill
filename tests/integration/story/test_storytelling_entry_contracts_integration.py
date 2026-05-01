"""Integration tests for the story and world list API contracts used by the storytelling boundary entry routes."""
import pytest

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Auth enforcement
# ---------------------------------------------------------------------------

def test_stories_list_requires_auth(client):
    """Unauthenticated GET /api/v1/stories/ returns 401."""
    resp = client.get("/api/v1/stories/")
    assert resp.status_code in {401, 403}, resp.text


def test_worlds_list_requires_auth(client):
    """Unauthenticated GET /api/v1/worlds/ returns 401."""
    resp = client.get("/api/v1/worlds/")
    assert resp.status_code in {401, 403}, resp.text


# ---------------------------------------------------------------------------
# Empty list for a new user
# ---------------------------------------------------------------------------

def test_new_user_has_empty_stories_list(client, register_and_login):
    """A newly registered user has no stories and receives an empty list."""
    register_and_login("st_empty_stories")
    resp = client.get("/api/v1/stories/")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []


def test_new_user_has_empty_worlds_list(client, register_and_login):
    """A newly registered user has no worlds and receives an empty list."""
    register_and_login("st_empty_worlds")
    resp = client.get("/api/v1/worlds/")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["success"] is True
    assert body["data"] == []


# ---------------------------------------------------------------------------
# List shape after creation
# ---------------------------------------------------------------------------

def test_created_world_appears_in_worlds_list(client, register_and_login):
    """A world created by the user appears in the worlds list with expected fields."""
    register_and_login("st_world_list")
    create_resp = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Aethoria",
            "short_description": "A realm of floating islands.",
            "is_free_chat_enabled": False,
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    world_id = create_resp.json()["data"]["id"]

    list_resp = client.get("/api/v1/worlds/")
    assert list_resp.status_code == 200, list_resp.text
    worlds = list_resp.json()["data"]
    assert any(w["id"] == world_id for w in worlds)
    match = next(w for w in worlds if w["id"] == world_id)
    assert match["name"] == "Aethoria"
    assert "created_at" in match
    assert "updated_at" in match


def test_created_story_appears_in_stories_list(client, register_and_login):
    """A story created by the user appears in the stories list with expected fields."""
    register_and_login("st_story_list")
    world_resp = client.post(
        "/api/v1/worlds/",
        json={"name": "Story World", "is_free_chat_enabled": False},
    )
    assert world_resp.status_code == 201, world_resp.text
    world_id = world_resp.json()["data"]["id"]

    story_resp = client.post(
        "/api/v1/stories/",
        json={
            "title": "The Silver Compass",
            "short_description": "An explorer finds a map.",
            "story_genre": "Fantasy Adventure",
            "story_type": "advanced",
            "world_id": world_id,
        },
    )
    assert story_resp.status_code == 201, story_resp.text
    story_id = story_resp.json()["data"]["id"]

    list_resp = client.get("/api/v1/stories/")
    assert list_resp.status_code == 200, list_resp.text
    stories = list_resp.json()["data"]
    assert any(s["id"] == story_id for s in stories)
    match = next(s for s in stories if s["id"] == story_id)
    assert match["title"] == "The Silver Compass"
    assert match["story_genre"] == "Fantasy Adventure"
    assert "created_at" in match
    assert "updated_at" in match


# ---------------------------------------------------------------------------
# User isolation
# ---------------------------------------------------------------------------

def test_stories_list_is_scoped_to_current_user(client, register_and_login, app_instance):
    """Stories created by user A are not visible in user B's list."""
    from fastapi.testclient import TestClient
    from uuid import uuid4

    register_and_login("st_iso_a")
    world_resp = client.post(
        "/api/v1/worlds/",
        json={"name": "User A World", "is_free_chat_enabled": False},
    )
    world_id = world_resp.json()["data"]["id"]
    story_resp = client.post(
        "/api/v1/stories/",
        json={"title": "User A Story", "story_type": "advanced", "world_id": world_id},
    )
    a_story_id = story_resp.json()["data"]["id"]

    b_client = TestClient(app_instance, raise_server_exceptions=True)
    suffix = uuid4().hex[:8]
    b_client.post("/api/v1/auth/register", json={
        "username": f"st_iso_b_{suffix}",
        "email": f"st_iso_b_{suffix}@example.com",
        "password": "integration-pass-123",
        "display_name": "Iso B",
        "terms_accepted": True,
    })
    b_list = b_client.get("/api/v1/stories/")
    assert b_list.status_code == 200
    assert not any(s["id"] == a_story_id for s in b_list.json()["data"])
