import pytest
from sqlalchemy import select

from app.models.act import Act
from app.models.published_story import PublishedStory
from app.models.scene import Scene
from app.models.story import Story
from app.models.world import World


pytestmark = pytest.mark.integration


def test_world_crud_flow_persists_data(client, register_and_login, run_db):
    payload, _ = register_and_login("worldflow")

    create_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Integration Test World",
            "description": "Initial world description",
            "short_description": "Short world description",
            "is_free_chat_enabled": False,
        },
    )
    assert create_response.status_code == 201, create_response.text
    create_body = create_response.json()
    assert create_body["success"] is True
    world_id = create_body["data"]["id"]

    list_response = client.get("/api/v1/worlds/")
    assert list_response.status_code == 200, list_response.text
    list_body = list_response.json()
    assert any(world["id"] == world_id for world in list_body["data"])

    get_response = client.get(f"/api/v1/worlds/{world_id}")
    assert get_response.status_code == 200, get_response.text
    assert get_response.json()["data"]["name"] == "Integration Test World"

    update_response = client.put(
        f"/api/v1/worlds/{world_id}",
        json={
            "description": "Updated world description",
            "short_description": "Updated short description",
            "is_free_chat_enabled": True,
        },
    )
    assert update_response.status_code == 200, update_response.text
    updated_body = update_response.json()
    assert updated_body["data"]["description"] == "Updated world description"
    assert updated_body["data"]["is_free_chat_enabled"] is True

    def fetch_world(session):
        async def _inner():
            world = (
                await session.execute(select(World).where(World.id == world_id))
            ).scalar_one()
            return {
                "user_id": world.user_id,
                "description": world.description,
                "is_free_chat_enabled": world.is_free_chat_enabled,
            }

        return _inner()

    world_state = run_db(fetch_world)
    assert world_state["description"] == "Updated world description"
    assert world_state["is_free_chat_enabled"] is True

    delete_response = client.delete(f"/api/v1/worlds/{world_id}")
    assert delete_response.status_code == 204, delete_response.text

    def world_exists(session):
        async def _inner():
            return (
                await session.execute(select(World).where(World.id == world_id))
            ).scalar_one_or_none()

        return _inner()

    assert run_db(world_exists) is None


def test_story_act_scene_publish_flow_uses_real_database(client, register_and_login, run_db, app_instance):
    register_and_login("storyflow")

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Story Flow World",
            "description": "World for story flow",
            "short_description": "Story flow short description",
            "is_free_chat_enabled": False,
        },
    )
    world_id = world_response.json()["data"]["id"]

    story_response = client.post(
        "/api/v1/stories/",
        json={
            "title": "Integration Story",
            "short_description": "Story for integration tests",
            "world_id": world_id,
            "story_type": "advanced",
        },
    )
    assert story_response.status_code == 201, story_response.text
    story_body = story_response.json()
    assert story_body["success"] is True
    story_id = story_body["data"]["id"]

    act_response = client.post(
        f"/api/v1/stories/{story_id}/acts/",
        json={
            "title": "Opening Act",
            "description": "<p>Act setup</p>",
            "act_number": 1,
            "act_summary": "Act summary",
        },
    )
    assert act_response.status_code == 201, act_response.text
    act_body = act_response.json()
    assert act_body["success"] is True
    act_id = act_body["data"]["id"]

    scene_response = client.post(
        f"/api/v1/acts/{act_id}/scenes/",
        json={
            "title": "First Scene",
            "summary": "Scene summary",
            "content": "<p>Scene content with enough text for publication.</p>",
            "scene_number": 10,
        },
    )
    assert scene_response.status_code == 201, scene_response.text
    scene_body = scene_response.json()
    assert scene_body["success"] is True
    scene_id = scene_body["data"]["id"]

    update_scene_response = client.put(
        f"/api/v1/scenes/{scene_id}",
        json={"content": "<p>Updated scene content for integration validation.</p>"},
    )
    assert update_scene_response.status_code == 200, update_scene_response.text
    assert update_scene_response.json()["data"]["content"] == "<p>Updated scene content for integration validation.</p>"

    acts_list_response = client.get(f"/api/v1/stories/{story_id}/acts/")
    assert acts_list_response.status_code == 200, acts_list_response.text
    assert acts_list_response.json()["data"][0]["id"] == act_id

    scenes_list_response = client.get(f"/api/v1/acts/{act_id}/scenes/")
    assert scenes_list_response.status_code == 200, scenes_list_response.text
    assert scenes_list_response.json()["data"][0]["id"] == scene_id

    publish_response = client.post(
        f"/api/v1/stories/{story_id}/publish",
        json={"visibility": "public", "description": "Published integration story"},
    )
    assert publish_response.status_code == 200, publish_response.text
    publish_body = publish_response.json()
    assert publish_body["success"] is True
    filename = publish_body["data"]["filename"]
    assert filename.endswith(".html")

    published_file = app_instance.state.test_storage_root / "uploads" / "published" / filename
    assert published_file.exists()
    assert "Integration Story" in published_file.read_text(encoding="utf-8")

    def fetch_story_graph(session):
        async def _inner():
            story = (
                await session.execute(select(Story).where(Story.id == story_id))
            ).scalar_one()
            act = (
                await session.execute(select(Act).where(Act.id == act_id))
            ).scalar_one()
            scene = (
                await session.execute(select(Scene).where(Scene.id == scene_id))
            ).scalar_one()
            published = (
                await session.execute(
                    select(PublishedStory).where(PublishedStory.story_id == story_id)
                )
            ).scalar_one()
            return {
                "story_world_id": story.world_id,
                "act_story_id": act.story_id,
                "scene_act_id": scene.act_id,
                "published_url": published.published_url,
                "published_title": published.title,
            }

        return _inner()

    graph = run_db(fetch_story_graph)
    assert graph["story_world_id"] == world_id
    assert graph["act_story_id"] == story_id
    assert graph["scene_act_id"] == act_id
    assert graph["published_url"].endswith(filename)
    assert graph["published_title"] == "Integration Story"
