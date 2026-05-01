"""Integration tests for prompt library endpoints."""

import pytest


pytestmark = pytest.mark.integration


def _get_access_token(client, username, password):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_create_prompt_requires_auth(client):
    """POST /api/v1/prompts/ without auth returns 401."""
    response = client.post(
        "/api/v1/prompts/",
        json={"title": "Test", "prompt_content": "Content", "prompt_type": "GENERAL"},
    )
    assert response.status_code == 401, response.text


def test_create_prompt_returns_created_prompt(client, register_and_login):
    """POST /api/v1/prompts/ creates a prompt and returns it wrapped."""
    credentials, _ = register_and_login("prompt_creator")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/prompts/",
        headers=headers,
        json={
            "title": "Fantasy World Opener",
            "prompt_content": "Write a story opening set in a magical realm.",
            "prompt_type": "GENERAL",
            "age_target": "ALL_AGES",
            "is_active": True,
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["title"] == "Fantasy World Opener"
    assert body["data"]["id"] is not None


def test_list_my_prompts_returns_user_prompts(client, register_and_login):
    """GET /api/v1/prompts/my-prompts returns only the authenticated user's prompts."""
    credentials, _ = register_and_login("my_prompts_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/prompts/",
        headers=headers,
        json={"title": "My Prompt 1", "prompt_content": "Content 1", "prompt_type": "GENERAL"},
    )
    client.post(
        "/api/v1/prompts/",
        headers=headers,
        json={"title": "My Prompt 2", "prompt_content": "Content 2", "prompt_type": "STORY"},
    )

    response = client.get("/api/v1/prompts/my-prompts", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) >= 2
    assert all(p["title"].startswith("My Prompt") for p in body["data"])


def test_list_shared_prompts_returns_prompts(client, register_and_login):
    """GET /api/v1/prompts/shared returns shared prompts with is_active=True."""
    credentials, _ = register_and_login("shared_prompts_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/prompts/shared", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_get_single_prompt_returns_prompt(client, register_and_login):
    """GET /api/v1/prompts/{id} returns the prompt if it exists."""
    credentials, _ = register_and_login("get_single_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/v1/prompts/",
        headers=headers,
        json={"title": "Single Prompt", "prompt_content": "Content", "prompt_type": "GENERAL"},
    )
    prompt_id = create_response.json()["data"]["id"]

    response = client.get(f"/api/v1/prompts/{prompt_id}", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == prompt_id


def test_get_single_prompt_returns_404_for_nonexistent(client, register_and_login):
    """GET /api/v1/prompts/99999 returns 404 for a prompt that doesn't exist."""
    credentials, _ = register_and_login("nonexistent_prompt_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/prompts/99999", headers=headers)
    assert response.status_code == 404, response.text


def test_delete_prompt_returns_204(client, register_and_login):
    """DELETE /api/v1/prompts/{id} returns 204 on successful deletion."""
    credentials, _ = register_and_login("delete_prompt_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    create_response = client.post(
        "/api/v1/prompts/",
        headers=headers,
        json={"title": "To Delete", "prompt_content": "Content", "prompt_type": "GENERAL"},
    )
    prompt_id = create_response.json()["data"]["id"]

    delete_response = client.delete(f"/api/v1/prompts/{prompt_id}", headers=headers)
    assert delete_response.status_code == 204, delete_response.text

    get_response = client.get(f"/api/v1/prompts/{prompt_id}", headers=headers)
    assert get_response.status_code == 404, get_response.text


def test_get_story_options_returns_genres_tones_conflicts(client, register_and_login):
    """GET /api/v1/prompts/story-options returns genres, tones, and conflicts."""
    credentials, _ = register_and_login("story_options_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/prompts/story-options", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert "genres" in body["data"]
    assert "tones" in body["data"]
    assert "conflicts" in body["data"]