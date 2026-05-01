"""Mock-based unit tests for interview/onboarding router."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock
import json
from pathlib import Path

import pytest

from app.routers.interview import router as interview_router
from app.models.user_interview_response import UserInterviewResponse


pytestmark = pytest.mark.unit


def _user():
    return SimpleNamespace(id=1, username="unit_user", is_active=True)


def test_get_interview_questions_returns_questions_for_valid_interview(unit_client_factory):
    """GET /api/v1/interview/questions/new_user_onboarding returns question data."""
    client = unit_client_factory(interview_router)

    interview_file = Path(__file__).parent.parent.parent.parent / "app" / "data" / "interviews" / "new_user_onboarding.json"
    with open(interview_file, "r", encoding="utf-8") as f:
        expected_data = json.load(f)

    response = client.get("/api/v1/interview/questions/new_user_onboarding")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["interview_id"] == "new_user_onboarding"
    assert len(body["questions"]) >= 1


def test_get_interview_questions_returns_404_for_unknown_interview(unit_client_factory):
    """GET /api/v1/interview/questions/unknown returns 404."""
    client = unit_client_factory(interview_router)

    response = client.get("/api/v1/interview/questions/nonexistent_interview_id")
    assert response.status_code == 404, response.text


def test_get_interview_status_returns_completed_flag(unit_client_factory, mock_db_session):
    """GET /api/v1/interview/status/interview_id returns completed state."""
    client = unit_client_factory(interview_router)

    completed_at = datetime.now(timezone.utc)
    mock_response = SimpleNamespace(
        id=1,
        completed_at=completed_at,
        user_id=1,
        interview_id="new_user_onboarding",
        json_response="{}",
        get_response_data= lambda: {}
    )
    mock_db_session.execute = AsyncMock(
        return_value=SimpleNamespace(scalar_one_or_none=lambda: mock_response)
    )

    response = client.get("/api/v1/interview/status/new_user_onboarding")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["completed"] is True
    assert body["response_id"] == 1


def test_get_interview_status_returns_not_completed(unit_client_factory, mock_db_session):
    """When no prior response exists, status returns completed=false."""
    client = unit_client_factory(interview_router)
    mock_db_session.execute = AsyncMock(
        return_value=SimpleNamespace(scalar_one_or_none=lambda: None)
    )

    response = client.get("/api/v1/interview/status/new_user_onboarding")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["completed"] is False
    assert body["response_id"] is None


def test_get_user_interview_response_returns_404_when_not_found(unit_client_factory, mock_db_session):
    """GET /api/v1/interview/response/unknown returns 404."""
    client = unit_client_factory(interview_router)
    mock_db_session.execute = AsyncMock(
        return_value=SimpleNamespace(scalar_one_or_none=lambda: None)
    )

    response = client.get("/api/v1/interview/response/new_user_onboarding")
    assert response.status_code == 404, response.text


def _result(value):
    return SimpleNamespace(scalar_one_or_none=lambda: value)


def test_submit_interview_returns_400_for_malformed_payload(unit_client_factory, mock_db_session):
    """POST /api/v1/interview/submit with missing fields returns 422 validation error."""
    client = unit_client_factory(interview_router)

    response = client.post(
        "/api/v1/interview/submit",
        json={
            "interview_id": "new_user_onboarding",
            "responses": {"q1": "answer"},
        }
    )
    assert response.status_code == 422, response.text


def test_get_user_insights_returns_insights_payload(unit_client_factory, mock_db_session):
    """GET /api/v1/interview/user-insights returns has_completed_onboarding=true when onboarding is done."""
    client = unit_client_factory(interview_router)

    mock_insights = SimpleNamespace(
        id=1,
        user_id=1,
        interview_id="new_user_onboarding",
        completed_at=datetime.now(timezone.utc),
        json_response="{}",
        get_response_data=lambda: {},
        get_writing_experience=lambda: "beginner",
        get_selected_genres=lambda: ["fantasy"],
        get_help_needed=lambda: "worldbuilding",
        get_writing_stage=lambda: "planning",
        get_navigation_choice=lambda: "create_story",
        wants_brainstorming=lambda: False,
        get_story_summary=lambda: "A fantasy epic",
        get_navigation_destination=lambda: "/storytelling/stories"
    )
    mock_db_session.execute = AsyncMock(
        return_value=SimpleNamespace(scalar_one_or_none=lambda: mock_insights)
    )

    response = client.get("/api/v1/interview/user-insights")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["has_completed_onboarding"] is True