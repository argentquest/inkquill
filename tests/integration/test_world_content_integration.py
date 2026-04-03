import pytest
from sqlalchemy import select

from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.models.story import Story


pytestmark = pytest.mark.integration


def test_world_content_crud_and_story_link_flow(client, register_and_login, run_db):
    register_and_login("contentflow")

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Content Flow World",
            "description": "World for content integration tests",
            "short_description": "Content flow world",
            "is_free_chat_enabled": False,
        },
    )
    assert world_response.status_code == 201, world_response.text
    world_id = world_response.json()["data"]["id"]

    character_response = client.post(
        f"/api/v1/worlds/{world_id}/characters/",
        json={
            "name": "Captain Rowan",
            "description": "A stubborn airship captain",
            "personality_traits": "determined, skeptical",
            "profession": "Captain",
        },
    )
    assert character_response.status_code == 201, character_response.text
    character_body = character_response.json()
    assert character_body["success"] is True
    character_id = character_body["data"]["id"]
    assert character_body["data"]["name"] == "Captain Rowan"

    location_response = client.post(
        f"/api/v1/worlds/{world_id}/locations/",
        json={
            "name": "Skyport Meridian",
            "description": "A busy floating port",
            "atmosphere": "crowded and electric",
            "scale": "CITY",
        },
    )
    assert location_response.status_code == 201, location_response.text
    location_body = location_response.json()
    assert location_body["success"] is True
    location_id = location_body["data"]["id"]

    lore_response = client.post(
        f"/api/v1/worlds/{world_id}/lore-items/",
        json={
            "title": "Storm Compass",
            "description": "An artifact that predicts sky fractures",
            "category": "ARTIFACT",
            "related_elements": "Captain Rowan, Skyport Meridian",
        },
    )
    assert lore_response.status_code == 201, lore_response.text
    lore_body = lore_response.json()
    assert lore_body["success"] is True
    lore_item_id = lore_body["data"]["id"]

    characters_list = client.get(f"/api/v1/worlds/{world_id}/characters/")
    assert characters_list.status_code == 200, characters_list.text
    assert any(item["id"] == character_id for item in characters_list.json()["data"])

    locations_list = client.get(f"/api/v1/worlds/{world_id}/locations/")
    assert locations_list.status_code == 200, locations_list.text
    assert any(item["id"] == location_id for item in locations_list.json()["data"])

    lore_list = client.get(f"/api/v1/worlds/{world_id}/lore-items/")
    assert lore_list.status_code == 200, lore_list.text
    assert any(item["id"] == lore_item_id for item in lore_list.json()["data"])

    character_get = client.get(f"/api/v1/characters/{character_id}")
    assert character_get.status_code == 200, character_get.text
    assert character_get.json()["data"]["name"] == "Captain Rowan"

    location_get = client.get(f"/api/v1/locations/{location_id}")
    assert location_get.status_code == 200, location_get.text
    assert location_get.json()["data"]["name"] == "Skyport Meridian"

    lore_get = client.get(f"/api/v1/lore-items/{lore_item_id}")
    assert lore_get.status_code == 200, lore_get.text
    assert lore_get.json()["data"]["title"] == "Storm Compass"

    character_update = client.put(
        f"/api/v1/characters/{character_id}",
        json={"short_backstory": "Raised by smugglers in the upper clouds."},
    )
    assert character_update.status_code == 200, character_update.text
    assert character_update.json()["data"]["short_backstory"] == "Raised by smugglers in the upper clouds."

    location_update = client.put(
        f"/api/v1/locations/{location_id}",
        json={"significance": "Primary trade hub for the frontier skylands."},
    )
    assert location_update.status_code == 200, location_update.text
    assert location_update.json()["data"]["significance"] == "Primary trade hub for the frontier skylands."

    lore_update = client.put(
        f"/api/v1/lore-items/{lore_item_id}",
        json={"importance_rating": 5},
    )
    assert lore_update.status_code == 200, lore_update.text
    assert lore_update.json()["data"]["importance_rating"] == 5

    character_context = client.get(f"/api/v1/characters/{character_id}/generated-context")
    assert character_context.status_code == 200, character_context.text
    assert "Captain Rowan" in character_context.json()["data"]["content"]

    location_context = client.get(f"/api/v1/locations/{location_id}/generated-context")
    assert location_context.status_code == 200, location_context.text
    assert "Skyport Meridian" in location_context.json()["data"]["content"]

    lore_context = client.get(f"/api/v1/lore-items/{lore_item_id}/generated-context")
    assert lore_context.status_code == 200, lore_context.text
    assert "Storm Compass" in lore_context.json()["data"]["content"]

    story_response = client.post(
        "/api/v1/stories/",
        json={
            "title": "Content Integration Story",
            "short_description": "Story for content linkage validation",
            "world_id": world_id,
            "story_type": "advanced",
        },
    )
    assert story_response.status_code == 201, story_response.text
    story_id = story_response.json()["data"]["id"]

    link_character = client.post(
        f"/api/v1/stories/{story_id}/characters/",
        json={"character_id": character_id, "role_in_story": "Protagonist"},
    )
    assert link_character.status_code == 201, link_character.text
    assert link_character.json()["success"] is True

    link_location = client.post(
        f"/api/v1/stories/{story_id}/locations/",
        json={"location_id": location_id, "significance_to_story": "Opening set piece"},
    )
    assert link_location.status_code == 201, link_location.text
    assert link_location.json()["success"] is True

    link_lore = client.post(
        f"/api/v1/stories/{story_id}/lore-items/",
        json={"lore_item_id": lore_item_id, "relevance_to_story": "Central mystery object"},
    )
    assert link_lore.status_code == 201, link_lore.text
    assert link_lore.json()["success"] is True

    story_characters = client.get(f"/api/v1/stories/{story_id}/characters/")
    assert story_characters.status_code == 200, story_characters.text
    assert story_characters.json()["data"][0]["role_in_story"] == "Protagonist"

    story_locations = client.get(f"/api/v1/stories/{story_id}/locations/")
    assert story_locations.status_code == 200, story_locations.text
    assert story_locations.json()["data"][0]["significance_to_story"] == "Opening set piece"

    story_lore = client.get(f"/api/v1/stories/{story_id}/lore-items/")
    assert story_lore.status_code == 200, story_lore.text
    assert story_lore.json()["data"][0]["relevance_to_story"] == "Central mystery object"

    def fetch_state(session):
        async def _inner():
            character = (
                await session.execute(select(Character).where(Character.id == character_id))
            ).scalar_one()
            location = (
                await session.execute(select(Location).where(Location.id == location_id))
            ).scalar_one()
            lore_item = (
                await session.execute(select(LoreItem).where(LoreItem.id == lore_item_id))
            ).scalar_one()
            story = (
                await session.execute(select(Story).where(Story.id == story_id))
            ).scalar_one()
            return {
                "character_world_id": character.world_id,
                "character_short_backstory": character.short_backstory,
                "location_world_id": location.world_id,
                "location_significance": location.significance,
                "lore_world_id": lore_item.world_id,
                "lore_importance": lore_item.importance_rating,
                "story_world_id": story.world_id,
            }

        return _inner()

    state = run_db(fetch_state)
    assert state["character_world_id"] == world_id
    assert state["character_short_backstory"] == "Raised by smugglers in the upper clouds."
    assert state["location_world_id"] == world_id
    assert state["location_significance"] == "Primary trade hub for the frontier skylands."
    assert state["lore_world_id"] == world_id
    assert state["lore_importance"] == 5
    assert state["story_world_id"] == world_id
