"""Mock-based unit tests for users, prompt, world, and story-class routers."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock
import uuid

import pytest

from app.core.dependencies_shared import get_world_and_verify_ownership
from app.core.storage_deps import get_blob_service_client
from app.routers.prompt import router as prompt_router
from app.routers.story_class import router as story_class_router
from app.routers.users import router as users_router
from app.routers.world import router as world_router


pytestmark = pytest.mark.unit


def _user_obj(user_id: int = 1, is_admin: bool = False):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=user_id,
        username=f"user{user_id}",
        email=f"user{user_id}@example.com",
        display_name=f"User {user_id}",
        is_active=True,
        is_admin=is_admin,
        created_at=now,
        updated_at=now,
    )


def _prompt_obj(prompt_id: int = 1, owner_id: int = 1):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=prompt_id,
        title="Unit Prompt",
        prompt_content="Write this.",
        reason_to_use="Useful",
        comment=None,
        is_active=True,
        prompt_type="GENERAL",
        age_target="ALL_AGES",
        user_id=owner_id,
        last_updated_by_user_id=owner_id,
        created_at=now,
        updated_at=now,
    )


def _world_obj(world_id: int = 10, owner_id: int = 1):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=world_id,
        user_id=owner_id,
        name="Unit World",
        description="Unit world",
        short_description="Unit",
        is_free_chat_enabled=False,
        image_blob_path="worlds/unit.png",
        current_image_id=None,
        created_at=now,
        updated_at=now,
    )


def _story_obj(story_id: int = 1, world_id: int = 10, owner_id: int = 1):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=story_id,
        user_id=owner_id,
        world_id=world_id,
        title="Unit Story",
        short_description="Unit short",
        ai_summary=None,
        story_type="advanced",
        image_url=None,
        created_at=now,
        updated_at=now,
    )


def _story_class_obj(sc_id: int = 1, world_id: int = 10):
    now = datetime.now(timezone.utc)
    return SimpleNamespace(
        id=sc_id,
        name="Narrative",
        description="Narrative class",
        color="#336699",
        world_id=world_id,
        created_at=now,
        updated_at=now,
    )


def test_users_router_me_and_admin_paths(unit_client_factory, mock_admin_user, mock_db_session):
    """Users router supports self profile and admin-only user management paths."""
    client = unit_client_factory(users_router, router_prefix="/api/v1", user_override=mock_admin_user)
    mock_admin_user.updated_at = datetime.now(timezone.utc)
    target_user = _user_obj(2, is_admin=False)

    mock_scalar_result = MagicMock()
    mock_scalar_result.scalar.return_value = False
    mock_db_session.execute.return_value = mock_scalar_result

    with patch("app.routers.users.crud_user.get_user", new=AsyncMock(return_value=target_user)), patch(
        "app.routers.users.crud_user.get_users", new=AsyncMock(return_value=[target_user])
    ), patch("app.routers.users.crud_user.update_user", new=AsyncMock(return_value=target_user)):
        me_response = client.get("/api/v1/users/me")
        list_response = client.get("/api/v1/users/")
        toggle_response = client.patch("/api/v1/users/2/toggle-active")
        edit_response = client.patch("/api/v1/users/2/edit", json={"display_name": "Updated"})

    assert me_response.status_code == 200, me_response.text
    assert me_response.json()["success"] is True
    assert me_response.json()["data"]["id"] == mock_admin_user.id

    assert list_response.status_code == 200, list_response.text
    assert list_response.json()["data"][0]["id"] == 2

    assert toggle_response.status_code == 200, toggle_response.text
    assert toggle_response.json()["data"]["id"] == 2

    assert edit_response.status_code == 200, edit_response.text
    assert edit_response.json()["success"] is True


def test_users_router_updates_current_user_profile(unit_client_factory):
    """Users router supports current-user profile updates with duplicate checks."""
    client = unit_client_factory(users_router, router_prefix="/api/v1")
    current_user = _user_obj(1, is_admin=False)
    updated_user = _user_obj(1, is_admin=False)
    updated_user.display_name = "Updated User"
    updated_user.email = "updated@example.com"

    with patch("app.routers.users.crud_user.get_user_by_username", new=AsyncMock(return_value=None)), patch(
        "app.routers.users.crud_user.get_user_by_email", new=AsyncMock(return_value=None)
    ), patch("app.routers.users.crud_user.update_user", new=AsyncMock(return_value=updated_user)):
        response = client.put(
            "/api/v1/users/me",
            json={"display_name": "Updated User", "email": "updated@example.com"},
        )

    assert response.status_code == 200, response.text
    assert response.json()["success"] is True
    assert response.json()["data"]["display_name"] == "Updated User"


def test_prompt_router_core_endpoints(unit_client_factory):
    """Prompt router create/list/get/update/delete endpoints work with mocked CRUD."""
    client = unit_client_factory(prompt_router, router_prefix="/api/v1")
    prompt = _prompt_obj(prompt_id=7)

    with patch("app.routers.prompt.crud_prompt.create_prompt", new=AsyncMock(return_value=prompt)), patch(
        "app.routers.prompt.crud_prompt.get_prompts_by_type", new=AsyncMock(return_value=[prompt])
    ), patch("app.routers.prompt.crud_prompt.get_prompts_by_user", new=AsyncMock(return_value=[prompt])), patch(
        "app.routers.prompt.crud_prompt.get_shared_prompts", new=AsyncMock(return_value=[prompt])
    ), patch("app.routers.prompt.crud_prompt.get_prompt", new=AsyncMock(return_value=prompt)), patch(
        "app.routers.prompt.crud_prompt.update_prompt", new=AsyncMock(return_value=prompt)
    ), patch("app.routers.prompt.crud_prompt.delete_prompt", new=AsyncMock()):
        create_response = client.post(
            "/api/v1/prompts/",
            json={
                "title": "Unit Prompt",
                "prompt_content": "Write this.",
                "prompt_type": "GENERAL",
                "age_target": "ALL_AGES",
                "is_active": True,
            },
        )
        options_response = client.get("/api/v1/prompts/story-options")
        my_response = client.get("/api/v1/prompts/my-prompts")
        shared_response = client.get("/api/v1/prompts/shared")
        get_response = client.get("/api/v1/prompts/7")
        update_response = client.put("/api/v1/prompts/7", json={"title": "Updated"})
        delete_response = client.delete("/api/v1/prompts/7")

    assert create_response.status_code == 201, create_response.text
    assert create_response.json()["success"] is True
    assert create_response.json()["data"]["id"] == 7

    assert options_response.status_code == 200, options_response.text
    assert "genres" in options_response.json()["data"]

    assert my_response.status_code == 200, my_response.text
    assert shared_response.status_code == 200, shared_response.text
    assert get_response.status_code == 200, get_response.text
    assert update_response.status_code == 200, update_response.text
    assert delete_response.status_code == 204, delete_response.text


def test_story_class_router_crud_and_options(unit_client_factory):
    """Story-class router create/list/options/get/update/delete endpoints execute with mocked world ownership."""
    client = unit_client_factory(story_class_router, router_prefix="/api/v1")
    sc = _story_class_obj(sc_id=11, world_id=10)
    world = _world_obj(world_id=10)

    with patch("app.routers.story_class.crud_world.get_worlds_by_user", new=AsyncMock(return_value=[world])), patch(
        "app.routers.story_class.crud_world.get_world_for_user", new=AsyncMock(return_value=world)
    ), patch("app.routers.story_class.crud_story.get_story_for_user", new=AsyncMock(return_value=SimpleNamespace(world_id=10))), patch(
        "app.routers.story_class.crud_story_class.create_story_class", new=AsyncMock(return_value=sc)
    ), patch(
        "app.routers.story_class.crud_story_class.get_story_classes_by_world", new=AsyncMock(return_value=[sc])
    ), patch("app.routers.story_class.crud_story_class.get_story_class", new=AsyncMock(return_value=sc)), patch(
        "app.routers.story_class.crud_story_class.update_story_class", new=AsyncMock(return_value=sc)
    ), patch("app.routers.story_class.crud_story_class.delete_story_class", new=AsyncMock()):
        create_response = client.post(
            "/api/v1/story-classes/",
            json={"name": "Narrative", "description": "Narrative class", "color": "#336699"},
        )
        list_response = client.get("/api/v1/story-classes/")
        options_response = client.get("/api/v1/story-classes/options")
        get_response = client.get("/api/v1/story-classes/11")
        update_response = client.put("/api/v1/story-classes/11", json={"name": "Narrative+"})
        delete_response = client.delete("/api/v1/story-classes/11")

    assert create_response.status_code == 201, create_response.text
    assert list_response.status_code == 200, list_response.text
    assert options_response.status_code == 200, options_response.text
    assert get_response.status_code == 200, get_response.text
    assert update_response.status_code == 200, update_response.text
    assert delete_response.status_code == 204, delete_response.text


def test_world_router_crud_story_listing_and_image_paths(unit_client_factory):
    """World router create/list/get/update/delete/stories/images/set-current endpoints execute with mocked deps."""
    client = unit_client_factory(world_router, router_prefix="/api/v1")
    world = _world_obj(world_id=22, owner_id=1)
    image = SimpleNamespace(
        id=801,
        image_uuid=uuid.uuid4(),
        element_type="world",
        associated_element_id=22,
        blob_path="worlds/22.png",
        prompt="A unit world image",
        revised_prompt="A refined unit world image",
        created_at=datetime.now(timezone.utc),
    )

    async def _world_dep():
        return world

    class _BlobClient:
        url = "https://unit.local/generated/worlds/22.png"

        async def exists(self):
            return True

    class _StorageClient:
        def get_blob_client(self, container, blob):
            return _BlobClient()

    client.app.dependency_overrides[get_world_and_verify_ownership] = _world_dep
    client.app.dependency_overrides[get_blob_service_client] = lambda: _StorageClient()

    with patch("app.routers.world.crud_world.create_world", new=AsyncMock(return_value=world)), patch(
        "app.routers.world.crud_world.get_worlds_by_user", new=AsyncMock(return_value=[world])
    ), patch("app.routers.world.crud_world.update_world", new=AsyncMock(return_value=world)), patch(
        "app.routers.world.crud_story.get_stories_by_world_id",
        new=AsyncMock(side_effect=[[], [_story_obj(story_id=1, world_id=22)]]),
    ), patch("app.routers.world.crud_world.delete_world", new=AsyncMock()), patch(
        "app.routers.world.crud_generated_image.get_images_for_element", new=AsyncMock(return_value=[image])
    ), patch("app.routers.world.crud_generated_image.get_image", new=AsyncMock(return_value=image)):
        create_response = client.post(
            "/api/v1/worlds/",
            json={"name": "Unit World", "description": "Unit world", "short_description": "Unit"},
        )
        list_response = client.get("/api/v1/worlds/")
        single_response = client.get("/api/v1/worlds/22")
        update_response = client.put("/api/v1/worlds/22", json={"name": "Updated World"})
        delete_response = client.delete("/api/v1/worlds/22")
        stories_response = client.get("/api/v1/worlds/22/stories")
        images_response = client.get("/api/v1/worlds/22/images")
        set_image_response = client.post("/api/v1/worlds/22/set-current-image/801")

    assert create_response.status_code == 201, create_response.text
    assert list_response.status_code == 200, list_response.text
    assert single_response.status_code == 200, single_response.text
    assert update_response.status_code == 200, update_response.text
    assert delete_response.status_code == 204, delete_response.text
    assert stories_response.status_code == 200, stories_response.text
    assert images_response.status_code == 200, images_response.text
    assert set_image_response.status_code == 200, set_image_response.text
