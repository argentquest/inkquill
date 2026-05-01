"""Integration tests for interview/onboarding endpoints."""

import pytest


pytestmark = pytest.mark.integration


def _get_access_token(client, username, password):
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_get_interview_questions_requires_auth(client):
    """GET /api/v1/interview/questions/new_user_onboarding without auth returns 401."""
    response = client.get("/api/v1/interview/questions/new_user_onboarding")
    assert response.status_code == 401, response.text


def test_get_interview_questions_returns_questions_for_onboarding(client, register_and_login):
    """GET /api/v1/interview/questions/new_user_onboarding returns interview structure."""
    credentials, _ = register_and_login("onboarding_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/interview/questions/new_user_onboarding", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["interview_id"] == "new_user_onboarding"
    assert "questions" in body
    assert len(body["questions"]) >= 1
    assert all("question" in q for q in body["questions"])
    assert all("id" in q for q in body["questions"])


def test_get_interview_questions_returns_404_for_unknown_interview(client, register_and_login):
    """GET /api/v1/interview/questions/nonexistent returns 404."""
    credentials, _ = register_and_login("onboarding_user2")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/interview/questions/nonexistent_interview", headers=headers)
    assert response.status_code == 404, response.text


def test_get_interview_status_returns_not_completed_initially(client, register_and_login):
    """GET /api/v1/interview/status/new_user_onboarding for new user returns completed=false."""
    credentials, _ = register_and_login("status_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/interview/status/new_user_onboarding", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["completed"] is False
    assert body["response_id"] is None


def test_submit_interview_creates_response(client, register_and_login):
    """POST /api/v1/interview/submit saves responses and returns success."""
    credentials, _ = register_and_login("submit_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post(
        "/api/v1/interview/submit",
        headers=headers,
        json={
            "interview_id": "new_user_onboarding",
            "responses": {
                "q1": "Fantasy is my favorite genre",
                "q2": "I write for fun and sharing"
            },
            "navigation": {},
            "metadata": {}
        }
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["success"] is True
    assert body["data"]["interview_id"] is not None


def test_submit_then_get_status_shows_completed(client, register_and_login):
    """After submitting, status returns completed=true with a response_id."""
    credentials, _ = register_and_login("completed_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    submit_response = client.post(
        "/api/v1/interview/submit",
        headers=headers,
        json={
            "interview_id": "new_user_onboarding",
            "responses": {"q1": "answer"},
            "navigation": {},
            "metadata": {}
        }
    )
    assert submit_response.status_code == 200, submit_response.text

    status_response = client.get("/api/v1/interview/status/new_user_onboarding", headers=headers)
    assert status_response.status_code == 200, status_response.text
    status_body = status_response.json()
    assert status_body["completed"] is True
    assert status_body["response_id"] is not None


def test_get_user_interview_response_returns_submitted_answers(client, register_and_login):
    """GET /api/v1/interview/response/new_user_onboarding returns submitted responses."""
    credentials, _ = register_and_login("response_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/interview/submit",
        headers=headers,
        json={
            "interview_id": "new_user_onboarding",
            "responses": {"q1": "My answer"},
            "navigation": {},
            "metadata": {}
        }
    )

    response = client.get("/api/v1/interview/response/new_user_onboarding", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["interview_id"] == "new_user_onboarding"
    assert "response_data" in body


def test_get_user_insights_after_onboarding_completion(client, register_and_login):
    """GET /api/v1/interview/user-insights returns has_completed_onboarding=true after submit."""
    credentials, _ = register_and_login("insights_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    client.post(
        "/api/v1/interview/submit",
        headers=headers,
        json={
            "interview_id": "new_user_onboarding",
            "responses": {"q1": "Fantasy writer"},
            "navigation": {},
            "metadata": {}
        }
    )

    insights_response = client.get("/api/v1/interview/user-insights", headers=headers)
    assert insights_response.status_code == 200, insights_response.text
    insights_body = insights_response.json()
    assert insights_body["has_completed_onboarding"] is True


def test_retake_interview_updates_existing_response(client, register_and_login):
    """Submitting again updates the prior response instead of creating a duplicate."""
    credentials, _ = register_and_login("retake_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    first_submit = client.post(
        "/api/v1/interview/submit",
        headers=headers,
        json={
            "interview_id": "new_user_onboarding",
            "responses": {"q1": "First answer"},
            "navigation": {},
            "metadata": {}
        }
    )
    assert first_submit.status_code == 200, first_submit.text
    first_id = first_submit.json()["data"]["interview_id"]

    second_submit = client.post(
        "/api/v1/interview/submit",
        headers=headers,
        json={
            "interview_id": "new_user_onboarding",
            "responses": {"q1": "Updated answer"},
            "navigation": {},
            "metadata": {}
        }
    )
    assert second_submit.status_code == 200, second_submit.text
    assert "retake" in second_submit.json()["data"]["message"].lower() or "updated" in second_submit.json()["data"]["message"].lower()

    status_body = client.get("/api/v1/interview/status/new_user_onboarding", headers=headers).json()
    assert status_body["completed"] is True


def test_story_brainstorm_allows_multiple_sessions(client, register_and_login):
    """story_brainstorm interview can be submitted multiple times (multiple sessions)."""
    credentials, _ = register_and_login("brainstorm_user")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    for i in range(2):
        response = client.post(
            "/api/v1/interview/submit",
            headers=headers,
            json={
                "interview_id": "story_brainstorm",
                "responses": {"q1": f"Brainstorm session {i+1}"},
                "navigation": {},
                "metadata": {}
            }
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["success"] is True
        assert "created" in response.json()["data"]["message"].lower()