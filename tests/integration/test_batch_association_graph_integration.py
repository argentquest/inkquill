import pytest
from sqlalchemy import select

from app.models.location import LocationConnection
from app.models.story_associations import (
    StoryCharacterAssociation,
    StoryLocationAssociation,
    StoryLoreItemAssociation,
)


pytestmark = pytest.mark.integration


def _get_access_token(client, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_batch_endpoints_and_graph_relationships(client, register_and_login, run_db):
    credentials, _ = register_and_login("graphflow")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    auth_headers = {"Authorization": f"Bearer {token}"}

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Graph Flow World",
            "description": "World for graph and batch testing",
            "short_description": "Graph flow world",
            "is_free_chat_enabled": False,
        },
    )
    assert world_response.status_code == 201, world_response.text
    world_id = world_response.json()["data"]["id"]

    batch_characters = client.post(
        "/api/v1/batch/characters",
        headers=auth_headers,
        json=[
            {
                "world_id": world_id,
                "name": "Riven",
                "description": "A scout",
                "profession": "Scout",
            },
            {
                "world_id": world_id,
                "name": "Tallis",
                "description": "A diplomat",
                "profession": "Diplomat",
            },
        ],
    )
    assert batch_characters.status_code == 200, batch_characters.text
    batch_character_body = batch_characters.json()
    assert batch_character_body["success"] is True
    assert batch_character_body["data"]["success_count"] == 2
    character_ids = [item["id"] for item in batch_character_body["data"]["results"] if item["status"] == "created"]

    fetched_characters = client.get(
        "/api/v1/batch/characters",
        headers=auth_headers,
        params=[("character_ids", character_ids[0]), ("character_ids", character_ids[1])],
    )
    assert fetched_characters.status_code == 200, fetched_characters.text
    assert {item["name"] for item in fetched_characters.json()["data"]} == {"Riven", "Tallis"}

    batch_locations = client.post(
        "/api/v1/batch/locations",
        headers=auth_headers,
        json=[
            {
                "world_id": world_id,
                "name": "North Gate",
                "description": "The frozen city gate",
                "scale": "BUILDING",
            },
            {
                "world_id": world_id,
                "name": "Assembly Hall",
                "description": "Main council chamber",
                "scale": "ROOM",
            },
        ],
    )
    assert batch_locations.status_code == 200, batch_locations.text
    location_ids = [item["id"] for item in batch_locations.json()["data"]["results"] if item["status"] == "created"]

    fetched_locations = client.get(
        "/api/v1/batch/locations",
        headers=auth_headers,
        params=[("location_ids", location_ids[0]), ("location_ids", location_ids[1])],
    )
    assert fetched_locations.status_code == 200, fetched_locations.text
    assert {item["name"] for item in fetched_locations.json()["data"]} == {"North Gate", "Assembly Hall"}

    batch_lore = client.post(
        "/api/v1/batch/lore-items",
        headers=auth_headers,
        json=[
            {
                "world_id": world_id,
                "title": "Winter Pact",
                "description": "Ancient treaty",
                "category": "HISTORICAL_EVENT",
            },
            {
                "world_id": world_id,
                "title": "Signal Flame",
                "description": "A warning artifact",
                "category": "ARTIFACT",
            },
        ],
    )
    assert batch_lore.status_code == 200, batch_lore.text
    lore_ids = [item["id"] for item in batch_lore.json()["data"]["results"] if item["status"] == "created"]

    fetched_lore = client.get(
        "/api/v1/batch/lore-items",
        headers=auth_headers,
        params=[("lore_item_ids", lore_ids[0]), ("lore_item_ids", lore_ids[1])],
    )
    assert fetched_lore.status_code == 200, fetched_lore.text
    assert {item["title"] for item in fetched_lore.json()["data"]} == {"Winter Pact", "Signal Flame"}

    location_connection_create = client.post(
        f"/api/v1/worlds/{world_id}/location-connections/",
        json={
            "from_location_id": location_ids[0],
            "to_location_id": location_ids[1],
            "path_description": "A guarded stone corridor",
            "reverse_path_description": "Back toward the outer gate",
            "is_bidirectional": True,
            "dm_notes": "Used for emergency retreats",
        },
    )
    assert location_connection_create.status_code == 201, location_connection_create.text
    connection_body = location_connection_create.json()
    assert connection_body["success"] is True
    assert connection_body["data"]["from_location_id"] == location_ids[0]

    location_connections = client.get(f"/api/v1/worlds/{world_id}/location-connections/")
    assert location_connections.status_code == 200, location_connections.text
    assert len(location_connections.json()["data"]) == 1

    connections_for_location = client.get(
        f"/api/v1/worlds/{world_id}/location-connections/location/{location_ids[0]}"
    )
    assert connections_for_location.status_code == 200, connections_for_location.text
    assert connections_for_location.json()["data"][0]["to_location_id"] == location_ids[1]

    location_hierarchy = client.get(f"/api/v1/worlds/{world_id}/location-connections/hierarchy")
    assert location_hierarchy.status_code == 200, location_hierarchy.text
    assert location_hierarchy.json()["success"] is True

    location_connection_update = client.put(
        f"/api/v1/location-connections/{location_ids[0]}/{location_ids[1]}",
        json={"dm_notes": "Updated note for route graph"},
    )
    assert location_connection_update.status_code == 200, location_connection_update.text
    assert location_connection_update.json()["data"]["dm_notes"] == "Updated note for route graph"

    location_connection_get = client.get(
        f"/api/v1/location-connections/{location_ids[0]}/{location_ids[1]}"
    )
    assert location_connection_get.status_code == 200, location_connection_get.text
    assert location_connection_get.json()["data"]["path_description"] == "A guarded stone corridor"

    story_response = client.post(
        "/api/v1/stories/",
        json={
            "title": "Graph Story",
            "short_description": "Story for relationship graph testing",
            "world_id": world_id,
            "story_type": "advanced",
        },
    )
    assert story_response.status_code == 201, story_response.text
    story_id = story_response.json()["data"]["id"]

    act_response = client.post(
        f"/api/v1/stories/{story_id}/acts/",
        json={
            "title": "Signal Act",
            "description": "Act for association checks",
            "act_number": 1,
        },
    )
    assert act_response.status_code == 201, act_response.text
    act_id = act_response.json()["data"]["id"]

    scene_response = client.post(
        f"/api/v1/acts/{act_id}/scenes/",
        json={
            "title": "Assembly Scene",
            "summary": "Council meeting",
            "content": "Delegates argue over the signal flame.",
            "scene_number": 1,
        },
    )
    assert scene_response.status_code == 201, scene_response.text
    scene_id = scene_response.json()["data"]["id"]

    story_character_assoc = client.post(
        f"/api/v1/associations/story/{story_id}/character/{character_ids[0]}",
        json={
            "story_id": story_id,
            "character_id": character_ids[0],
            "roles": ["Protagonist"],
            "notes": "Primary viewpoint",
        },
    )
    assert story_character_assoc.status_code == 200, story_character_assoc.text
    assert story_character_assoc.json()["data"]["roles"] == ["protagonist"]

    story_location_assoc = client.post(
        f"/api/v1/associations/story/{story_id}/location/{location_ids[0]}",
        json={
            "story_id": story_id,
            "location_id": location_ids[0],
            "roles": ["Opening Location"],
            "notes": "First chapter set piece",
        },
    )
    assert story_location_assoc.status_code == 200, story_location_assoc.text

    story_lore_assoc = client.post(
        f"/api/v1/associations/story/{story_id}/lore_item/{lore_ids[0]}",
        json={
            "story_id": story_id,
            "lore_item_id": lore_ids[0],
            "roles": ["Core Mystery"],
            "notes": "Drives the main investigation",
        },
    )
    assert story_lore_assoc.status_code == 200, story_lore_assoc.text

    act_character_assoc = client.post(
        f"/api/v1/associations/act/{act_id}/character/{character_ids[1]}",
        json={
            "act_id": act_id,
            "character_id": character_ids[1],
            "roles": ["advisor"],
            "notes": "Secondary voice in the act",
        },
    )
    assert act_character_assoc.status_code == 200, act_character_assoc.text

    act_location_assoc = client.post(
        f"/api/v1/associations/act/{act_id}/location/{location_ids[1]}",
        json={
            "act_id": act_id,
            "location_id": location_ids[1],
            "roles": ["meeting place"],
            "notes": "Where the assembly gathers",
        },
    )
    assert act_location_assoc.status_code == 200, act_location_assoc.text

    act_lore_assoc = client.post(
        f"/api/v1/associations/act/{act_id}/lore_item/{lore_ids[1]}",
        json={
            "act_id": act_id,
            "lore_item_id": lore_ids[1],
            "roles": ["warning"],
            "notes": "Signals the approaching threat",
        },
    )
    assert act_lore_assoc.status_code == 200, act_lore_assoc.text

    roles_response = client.get("/api/v1/associations/roles/story/character")
    assert roles_response.status_code == 200, roles_response.text
    assert roles_response.json()["data"]["container_type"] == "story"

    story_characters = client.get(f"/api/v1/associations/story/{story_id}/characters")
    assert story_characters.status_code == 200, story_characters.text
    assert story_characters.json()["data"][0]["character_id"] == character_ids[0]

    single_association = client.get(
        f"/api/v1/associations/story/{story_id}/character/{character_ids[0]}"
    )
    assert single_association.status_code == 200, single_association.text
    assert single_association.json()["data"]["element_id"] == character_ids[0]

    association_update = client.put(
        f"/api/v1/associations/story/{story_id}/character/{character_ids[0]}",
        json={"roles": ["lead"], "notes": "Updated note"},
    )
    assert association_update.status_code == 200, association_update.text
    assert association_update.json()["data"]["roles"] == ["lead"]

    bulk_association = client.post(
        f"/api/v1/associations/bulk/scene/{scene_id}",
        json=[
            {"element_type": "character", "element_id": character_ids[0], "roles": ["present"]},
            {"element_type": "location", "element_id": location_ids[0], "roles": ["setting"]},
            {"element_type": "lore_item", "element_id": lore_ids[0], "roles": ["referenced"]},
        ],
    )
    assert bulk_association.status_code == 200, bulk_association.text
    assert len(bulk_association.json()["data"]["associations"]) == 3

    story_all_associations = client.get(f"/api/v1/associations/story/{story_id}/all")
    assert story_all_associations.status_code == 200, story_all_associations.text
    assert len(story_all_associations.json()["data"]["characters"]) == 1
    assert len(story_all_associations.json()["data"]["locations"]) == 1
    assert len(story_all_associations.json()["data"]["lore_items"]) == 1

    act_all_associations = client.get(f"/api/v1/associations/act/{act_id}/all")
    assert act_all_associations.status_code == 200, act_all_associations.text
    assert len(act_all_associations.json()["data"]["characters"]) == 1

    scene_all_associations = client.get(f"/api/v1/associations/scene/{scene_id}/all")
    assert scene_all_associations.status_code == 200, scene_all_associations.text
    assert len(scene_all_associations.json()["data"]["characters"]) == 1

    delete_single_association = client.delete(
        f"/api/v1/associations/story/{story_id}/character/{character_ids[0]}"
    )
    assert delete_single_association.status_code == 200, delete_single_association.text
    assert delete_single_association.json()["data"]["message"] == "Association deleted successfully"

    delete_generic_association = client.delete(
        f"/api/v1/associations/scene/{scene_id}/location/{location_ids[0]}"
    )
    assert delete_generic_association.status_code == 200, delete_generic_association.text
    assert delete_generic_association.json()["data"]["message"] == "Association removed successfully"

    delete_location_connection_response = client.delete(
        f"/api/v1/location-connections/{location_ids[0]}/{location_ids[1]}"
    )
    assert delete_location_connection_response.status_code == 204, delete_location_connection_response.text

    def fetch_graph_state(session):
        async def _inner():
            remaining_story_character = (
                await session.execute(
                    select(StoryCharacterAssociation).where(
                        StoryCharacterAssociation.story_id == story_id,
                        StoryCharacterAssociation.character_id == character_ids[0],
                    )
                )
            ).scalar_one_or_none()
            story_location = (
                await session.execute(
                    select(StoryLocationAssociation).where(
                        StoryLocationAssociation.story_id == story_id,
                        StoryLocationAssociation.location_id == location_ids[0],
                    )
                )
            ).scalar_one_or_none()
            story_lore = (
                await session.execute(
                    select(StoryLoreItemAssociation).where(
                        StoryLoreItemAssociation.story_id == story_id,
                        StoryLoreItemAssociation.lore_item_id == lore_ids[0],
                    )
                )
            ).scalar_one_or_none()
            remaining_connection = (
                await session.execute(
                    select(LocationConnection).where(
                        LocationConnection.from_location_id == location_ids[0],
                        LocationConnection.to_location_id == location_ids[1],
                    )
                )
            ).scalar_one_or_none()
            return {
                "remaining_story_character": remaining_story_character,
                "story_location_roles": story_location.roles if story_location else None,
                "story_lore_roles": story_lore.roles if story_lore else None,
                "remaining_connection": remaining_connection,
            }

        return _inner()

    state = run_db(fetch_graph_state)
    assert state["remaining_story_character"] is None
    assert state["story_location_roles"] == ["Opening Location"]
    assert state["story_lore_roles"] == ["Core Mystery"]
    assert state["remaining_connection"] is None
