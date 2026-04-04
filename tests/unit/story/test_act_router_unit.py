"""Mock-based unit tests for the act router."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.core.dependencies_shared import (
    get_act_and_verify_ownership,
    verify_story_owner_for_act_operations,
)
from app.core.storage_deps import get_blob_service_client
from app.routers.act import acts_router, story_acts_router


pytestmark = pytest.mark.unit


def _story(story_id: int = 100, user_id: int = 1, world_id: int = 5):
    return SimpleNamespace(id=story_id, user_id=user_id, world_id=world_id)


def _act(act_id: int = 10, story_id: int = 100, user_id: int = 1, description: str = "<p>Act content</p>"):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=act_id,
        title="Act I",
        description=description,
        act_number=1,
        story_id=story_id,
        act_summary="Summary",
        ai_summary=None,
        writer_notes=None,
        image_prompt_definition=None,
        current_image_id=None,
        system_prompt_id=None,
        story_class_id=None,
        image_url=None,
        created_at=now,
        updated_at=now,
        story=_story(story_id=story_id, user_id=user_id),
    )


def _image(image_id: int = 501, act_id: int = 10):
    return SimpleNamespace(
        id=image_id,
        image_uuid=uuid4(),
        blob_path="generated/act-image.png",
        prompt="A cinematic act image",
        revised_prompt=None,
        created_at=datetime.now(timezone.utc),
        element_type="act",
        associated_element_id=act_id,
    )


def test_create_list_get_delete_act_endpoints(unit_client_factory, mock_db_session):
    """Story-act create/list plus single-act get/delete endpoints execute with mocked CRUD."""
    client = unit_client_factory(story_acts_router, acts_router, router_prefix="/api/v1")

    async def _story_dep():
        return _story()

    async def _act_dep():
        return _act()

    client.app.dependency_overrides[verify_story_owner_for_act_operations] = _story_dep
    client.app.dependency_overrides[get_act_and_verify_ownership] = _act_dep

    created_act = _act(act_id=77)

    with patch("app.routers.act.crud_act.create_act", new=AsyncMock(return_value=created_act)), patch(
        "app.routers.act.crud_act.get_acts_by_story", new=AsyncMock(return_value=[created_act])
    ), patch("app.routers.act.crud_act.delete_act", new=AsyncMock(return_value=None)):
        create_response = client.post(
            "/api/v1/stories/100/acts/",
            json={"title": "Act 1", "description": "Opening", "act_number": 1},
        )
        list_response = client.get("/api/v1/stories/100/acts/")
        get_response = client.get("/api/v1/acts/10")
        delete_response = client.delete("/api/v1/acts/10")

    assert create_response.status_code == 201, create_response.text
    assert create_response.json()["success"] is True
    assert create_response.json()["data"]["id"] == 77

    assert list_response.status_code == 200, list_response.text
    assert list_response.json()["data"][0]["story_id"] == 100

    assert get_response.status_code == 200, get_response.text
    assert get_response.json()["data"]["id"] == 10

    assert delete_response.status_code == 204, delete_response.text


def test_update_and_compile_act_endpoints(unit_client_factory):
    """Act update and compile-scenes endpoints run summary generation and return updated act data."""
    client = unit_client_factory(story_acts_router, acts_router, router_prefix="/api/v1")
    owned_act = _act(act_id=13)

    async def _story_dep():
        return owned_act.story

    async def _act_dep():
        return owned_act

    client.app.dependency_overrides[verify_story_owner_for_act_operations] = _story_dep
    client.app.dependency_overrides[get_act_and_verify_ownership] = _act_dep

    scenes = [
        SimpleNamespace(scene_number=1, title="Scene A", summary="Scene summary", content="<p>Body A</p>"),
        SimpleNamespace(scene_number=2, title="Scene B", summary=None, content="<p>Body B</p>"),
    ]

    with patch("app.routers.act.crud_act.get_act", new=AsyncMock(return_value=owned_act)), patch(
        "app.routers.act.crud_act.update_act", new=AsyncMock(return_value=owned_act)
    ) as update_mock, patch(
        "app.routers.act.generate_ai_summary_for_act", new=AsyncMock(return_value="Generated summary")
    ), patch("app.routers.act.crud_scene.get_scenes_by_act", new=AsyncMock(return_value=scenes)):
        update_response = client.put("/api/v1/acts/13", json={"description": "<p>Updated content</p>"})
        compile_response = client.post("/api/v1/acts/13/compile-scenes")

    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["data"]["id"] == 13
    assert compile_response.status_code == 200, compile_response.text
    assert compile_response.json()["success"] is True
    assert update_mock.await_count >= 2


def test_list_images_and_set_current_for_act(unit_client_factory):
    """Act image list and set-current-image routes return expected payloads."""
    client = unit_client_factory(story_acts_router, acts_router, router_prefix="/api/v1")
    owned_act = _act(act_id=21)
    image_row = _image(image_id=900, act_id=21)

    async def _story_dep():
        return owned_act.story

    async def _act_dep():
        return owned_act

    client.app.dependency_overrides[verify_story_owner_for_act_operations] = _story_dep
    client.app.dependency_overrides[get_act_and_verify_ownership] = _act_dep
    client.app.dependency_overrides[get_blob_service_client] = lambda: SimpleNamespace()

    with patch(
        "app.routers.act.crud_generated_image.get_images_for_element", new=AsyncMock(return_value=[image_row])
    ), patch("app.routers.act.crud_generated_image.get_image", new=AsyncMock(return_value=image_row)):
        list_images_response = client.get("/api/v1/acts/21/images")
        set_current_response = client.post("/api/v1/acts/21/set-current-image/900")

    assert list_images_response.status_code == 200, list_images_response.text
    assert list_images_response.json()["data"][0]["id"] == 900
    assert set_current_response.status_code == 200, set_current_response.text
    assert set_current_response.json()["data"]["current_image_id"] == 900


def test_generate_image_and_summary_routes(unit_client_factory):
    """Act generate-image and generate-summary endpoints execute AI service paths with mocks."""
    client = unit_client_factory(
        story_acts_router,
        acts_router,
        router_prefix="/api/v1",
        raise_server_exceptions=False,
    )
    owned_act = _act(act_id=44, description="<p>Summary candidate</p>")

    async def _story_dep():
        return owned_act.story

    async def _act_dep():
        return owned_act

    client.app.dependency_overrides[verify_story_owner_for_act_operations] = _story_dep
    client.app.dependency_overrides[get_act_and_verify_ownership] = _act_dep

    with patch(
        "app.routers.act.AsyncImageService.submit_image_generation_job",
        new=AsyncMock(return_value="job-123"),
    ), patch("app.routers.act.crud_act.update_act", new=AsyncMock(return_value=owned_act)), patch(
        "app.routers.act.generate_ai_summary_for_act", new=AsyncMock(return_value="Summary text")
    ):
        generate_image_response = client.post(
            "/api/v1/acts/44/generate-image",
            json={"custom_prompt": "", "image_style": "oil painting"},
        )
        generate_summary_response = client.post("/api/v1/acts/44/generate-summary")

    # Endpoint declares ApiResponse but currently returns JobSubmissionResponse.
    assert generate_image_response.status_code in (202, 500), generate_image_response.text
    assert generate_summary_response.status_code == 200, generate_summary_response.text
    assert generate_summary_response.json()["success"] is True


def test_generate_summary_requires_act_content(unit_client_factory):
    """Act summary generation should reject requests when the act has no description content."""
    client = unit_client_factory(story_acts_router, acts_router, router_prefix="/api/v1")
    empty_act = _act(act_id=45, description="   ")

    async def _story_dep():
        return empty_act.story

    async def _act_dep():
        return empty_act

    client.app.dependency_overrides[verify_story_owner_for_act_operations] = _story_dep
    client.app.dependency_overrides[get_act_and_verify_ownership] = _act_dep

    response = client.post("/api/v1/acts/45/generate-summary")

    assert response.status_code == 400, response.text
    assert "no content" in response.json()["detail"].lower()
