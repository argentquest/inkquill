"""Mock-based unit tests for basic story, interview, and world importer routes."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.models.job_status import JobStateEnum, JobTypeEnum
from app.routers.basic_stories import router as basic_stories_router
from app.routers.interview import router as interview_router
from app.routers.world_importer import router as world_importer_router


pytestmark = pytest.mark.unit


def test_basic_story_create_and_list_are_wrapped(unit_client_factory):
    """Basic story create/list endpoints should return `ApiResponse` wrappers."""
    client = unit_client_factory(basic_stories_router, router_prefix="/api/v1")

    story = SimpleNamespace(
        id=100,
        title="Unit Basic Story",
        short_description="unit desc",
        ai_summary=None,
        world_id=44,
        story_type="basic",
        story_genre=None,
        story_tone=None,
        primary_conflict_type=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        user_id=1,
    )
    first_act = SimpleNamespace(id=200)

    with patch("app.routers.basic_stories.story_service.create_basic_story", new=AsyncMock(return_value=(story, first_act))), patch(
        "app.routers.basic_stories.story_service.get_stories_by_type", new=AsyncMock(return_value=[story])
    ):
        create_response = client.post(
            "/api/v1/stories/basic/create",
            json={"title": "Unit Basic Story", "short_description": "unit desc"},
        )
        list_response = client.get("/api/v1/stories/basic/list")

    assert create_response.status_code == 200, create_response.text
    create_body = create_response.json()
    assert create_body["success"] is True
    assert create_body["data"]["id"] == 100
    assert create_body["data"]["first_act_id"] == 200
    assert "editor_url" in create_body["data"]

    assert list_response.status_code == 200, list_response.text
    list_body = list_response.json()
    assert list_body["success"] is True
    assert list_body["data"][0]["title"] == "Unit Basic Story"


def test_interview_submit_now_returns_api_response(unit_client_factory, mock_db_session, mock_user):
    """Interview submit endpoint should return wrapped `InterviewSubmissionResponse`."""
    client = unit_client_factory(interview_router)

    # No existing interview response
    mock_db_session.execute = AsyncMock(return_value=SimpleNamespace(scalar_one_or_none=lambda: None))

    async def _refresh_side_effect(obj):
        obj.id = 321
        obj.completed_at = datetime.now(timezone.utc)

    mock_db_session.refresh = AsyncMock(side_effect=_refresh_side_effect)

    with patch("app.routers.interview.validation_service.validate_response", return_value=None), patch(
        "app.routers.interview.validation_service.sanitize_response", side_effect=lambda payload: payload
    ):
        response = client.post(
            "/api/v1/interview/submit",
            json={
                "interview_id": "new_user_onboarding",
                "responses": {
                    "writing_experience": {
                        "question_id": "writing_experience",
                        "selected_values": ["write_for_fun"],
                        "answered_at": "2026-04-01T00:00:00Z",
                    }
                },
                "navigation": {"final_destination": "/ui/brainstorm"},
                "metadata": {"source": "unit"},
            },
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["success"] is True
    assert body["data"]["interview_id"] == 321


def test_world_importer_submit_and_status_are_wrapped(unit_client_factory):
    """World importer submission and status endpoints should return `ApiResponse` wrappers."""
    client = unit_client_factory(world_importer_router, router_prefix="/api/v1")

    job_row = SimpleNamespace(
        job_id="job-unit-1",
        job_type=JobTypeEnum.WORLD_IMPORT_FROM_TITLE,
        state=JobStateEnum.PENDING,
        status_message="Queued",
        result_message=None,
        world_id=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )

    with patch("app.routers.world_importer.crud_job_status.create_job", new=AsyncMock(return_value=None)), patch(
        "app.routers.world_importer.import_world_from_book_task", new=AsyncMock(return_value=None)
    ), patch("app.routers.world_importer.crud_job_status.get_job_by_job_id", new=AsyncMock(return_value=job_row)):
        submit_response = client.post(
            "/api/v1/worlds/import-from-book-title",
            json={"book_title": "Unit Book Title"},
        )
        job_status_response = client.get("/api/v1/worlds/import/job-status/job-unit-1")

    assert submit_response.status_code == 202, submit_response.text
    submit_body = submit_response.json()
    assert submit_body["success"] is True
    assert submit_body["data"]["job_id"]

    assert job_status_response.status_code == 200, job_status_response.text
    status_body = job_status_response.json()
    assert status_body["success"] is True
    assert status_body["data"]["job_id"] == "job-unit-1"
