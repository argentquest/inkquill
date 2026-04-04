import pytest
from sqlalchemy import select

from app.models.world import World


pytestmark = pytest.mark.integration


def _get_access_token(client, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_world_builder_endpoints_with_mocked_generation(client, register_and_login, run_db, monkeypatch):
    credentials, _ = register_and_login("worldbuilder")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    auth_headers = {"Authorization": f"Bearer {token}"}

    questions_response = client.get("/api/v1/world-builder/questions", headers=auth_headers)
    assert questions_response.status_code == 200, questions_response.text
    questions_body = questions_response.json()
    assert questions_body["success"] is True
    questions = questions_body["data"]["questions"]
    assert len(questions) >= 2

    first_question = questions[0]
    second_question = questions[1]
    answers = {
        first_question["id"]: first_question["answers"][0]["id"],
        second_question["id"]: second_question["answers"][0]["id"],
    }

    single_question = client.get(
        f"/api/v1/world-builder/questions/{first_question['id']}",
        headers=auth_headers,
    )
    assert single_question.status_code == 200, single_question.text
    single_question_body = single_question.json()
    assert single_question_body["success"] is True
    assert single_question_body["data"]["id"] == first_question["id"]

    validation_response = client.post(
        "/api/v1/world-builder/validate",
        json={"answers": answers},
        headers=auth_headers,
    )
    assert validation_response.status_code == 200, validation_response.text
    validation_body = validation_response.json()
    assert validation_body["success"] is True
    assert validation_body["data"]["valid"] is True
    assert validation_body["data"]["answer_count"] == 2

    async def fake_generate_world_description(answers, user_id, db):
        return {
            "short_description": "A trade nexus built on floating terraces.",
            "description": "The world is a lattice of aerial markets linked by disciplined guild routes.",
            "visual_prompt": "Floating terraces connected by luminous trade bridges under layered clouds.",
        }

    monkeypatch.setattr(
        "app.routers.world_builder.world_builder_service.generate_world_description",
        fake_generate_world_description,
    )

    generate_response = client.post(
        "/api/v1/world-builder/generate",
        json={"answers": answers},
        headers=auth_headers,
    )
    assert generate_response.status_code == 200, generate_response.text
    generate_body = generate_response.json()
    assert generate_body["success"] is True
    assert generate_body["data"]["short_description"] == "A trade nexus built on floating terraces."
    assert len(generate_body["data"]["answer_summary"]) == 2

    create_response = client.post(
        "/api/v1/world-builder/create",
        json={"name": "Builder Created World", "answers": answers},
        headers=auth_headers,
    )
    assert create_response.status_code == 200, create_response.text
    create_body = create_response.json()
    assert create_body["success"] is True
    world_id = create_body["data"]["id"]
    assert create_body["data"]["name"] == "Builder Created World"
    assert create_body["data"]["short_description"] == "A trade nexus built on floating terraces."

    update_response = client.put(
        f"/api/v1/world-builder/worlds/{world_id}",
        json={"answers": answers},
        headers=auth_headers,
    )
    assert update_response.status_code == 200, update_response.text
    update_body = update_response.json()
    assert update_body["success"] is True
    assert update_body["data"]["id"] == world_id

    def fetch_world_builder_state(session):
        async def _inner():
            world = (
                await session.execute(select(World).where(World.id == world_id))
            ).scalar_one()
            return {
                "name": world.name,
                "short_description": world.short_description,
                "description": world.description,
                "image_prompt_definition": world.image_prompt_definition,
                "world_builder_data": world.world_builder_data,
            }

        return _inner()

    state = run_db(fetch_world_builder_state)
    assert state["name"] == "Builder Created World"
    assert state["short_description"] == "A trade nexus built on floating terraces."
    assert state["description"] == "The world is a lattice of aerial markets linked by disciplined guild routes."
    assert state["image_prompt_definition"] == "Floating terraces connected by luminous trade bridges under layered clouds."
    normalized_answers = {str(key): value for key, value in answers.items()}
    assert state["world_builder_data"]["answers"] == normalized_answers
