import json
from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models.ai_cost_log import AICallLog
from app.models.ai_model_config import AIModelConfiguration, AIModelTypeEnum, AIProviderEnum
from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.models.story import Story
from app.models.user import User
from app.models.user_interview_response import UserInterviewResponse
from app.models.world import World


pytestmark = pytest.mark.integration


def _get_access_token(client, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_dashboard_and_model_catalog_endpoints_work_with_real_db(client, register_and_login, run_db):
    credentials, _ = register_and_login("catalogflow")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Catalog World",
            "description": "World for dashboard and model catalog tests",
            "short_description": "Catalog world",
            "is_free_chat_enabled": False,
        },
        headers=headers,
    )
    assert world_response.status_code == 201, world_response.text
    world_id = world_response.json()["data"]["id"]

    story_response = client.post(
        "/api/v1/stories/",
        json={
            "title": "Catalog Story",
            "short_description": "Story for dashboard tests",
            "world_id": world_id,
            "story_type": "advanced",
        },
        headers=headers,
    )
    assert story_response.status_code == 201, story_response.text
    story_id = story_response.json()["data"]["id"]

    character_response = client.post(
        f"/api/v1/worlds/{world_id}/characters",
        json={"name": "Catalog Hero", "description": "Character for summary counts"},
        headers=headers,
    )
    assert character_response.status_code == 201, character_response.text

    location_response = client.post(
        f"/api/v1/worlds/{world_id}/locations",
        json={"name": "Catalog City", "description": "Location for summary counts"},
        headers=headers,
    )
    assert location_response.status_code == 201, location_response.text

    lore_response = client.post(
        f"/api/v1/worlds/{world_id}/lore-items",
        json={
            "title": "Catalog Artifact",
            "description": "Lore for summary counts",
            "category": "ARTIFACT",
        },
        headers=headers,
    )
    assert lore_response.status_code == 201, lore_response.text

    def seed_models_and_logs(session):
        async def _inner():
            user = (
                await session.execute(select(User).where(User.username == credentials["username"]))
            ).scalar_one()

            generation_model = AIModelConfiguration(
                display_name="Integration GPT Model",
                model_name="gpt-integration",
                description="Generation model for integration coverage",
                provider=AIProviderEnum.OPENAI,
                model_type=AIModelTypeEnum.GENERATION,
                is_active=True,
                is_public_chat_default=True,
                max_tokens=4096,
                temperature=0.7,
                top_p=1.0,
                presence_penalty=0.0,
                frequency_penalty=0.0,
                is_json_mode=False,
                provider_cost_input_usd_pm=1.5,
                provider_cost_output_usd_pm=2.5,
                user_price_input_usd_pm=3.5,
                user_price_output_usd_pm=4.5,
            )
            embedding_model = AIModelConfiguration(
                display_name="Integration Embedding Model",
                model_name="embed-integration",
                description="Embedding model for llm-model coverage",
                provider=AIProviderEnum.OPENAI,
                model_type=AIModelTypeEnum.EMBEDDING,
                is_active=True,
                is_public_chat_default=False,
                max_tokens=2048,
                temperature=0.0,
                top_p=1.0,
                presence_penalty=0.0,
                frequency_penalty=0.0,
                is_json_mode=False,
                provider_cost_input_usd_pm=0.1,
                provider_cost_output_usd_pm=0.1,
                user_price_input_usd_pm=0.2,
                user_price_output_usd_pm=0.2,
            )
            session.add_all([generation_model, embedding_model])
            await session.flush()

            session.add(
                AICallLog(
                    user_id=user.id,
                    model_config_id=generation_model.id,
                    input_prompt="Summarize this scene.",
                    call_type="story_generation",
                    model_name=generation_model.model_name,
                    object_id=story_id,
                    prompt_tokens=120,
                    completion_tokens=80,
                    total_tokens=200,
                    calculated_cost_usd=Decimal("0.01250000"),
                    duration_ms=321,
                )
            )
            await session.commit()

        return _inner()

    run_db(seed_models_and_logs)

    dashboard_response = client.get("/api/v1/dashboard/summary", headers=headers)
    assert dashboard_response.status_code == 200, dashboard_response.text
    dashboard_body = dashboard_response.json()
    assert dashboard_body["success"] is True
    summary = dashboard_body["data"]["summary"]
    assert summary["total_worlds"] >= 1
    assert summary["total_stories"] >= 1
    assert summary["total_characters"] >= 1
    assert summary["total_locations"] >= 1
    assert summary["total_lore_items"] >= 1

    ai_models_response = client.get("/api/v1/ai-models/", headers=headers)
    assert ai_models_response.status_code == 200, ai_models_response.text
    ai_models_body = ai_models_response.json()
    assert ai_models_body["success"] is True
    ai_model_names = {item["display_name"] for item in ai_models_body["data"]}
    assert "Integration GPT Model" in ai_model_names
    assert "Integration Embedding Model" not in ai_model_names

    user_available_response = client.get("/api/v1/ai-models/user-available", headers=headers)
    assert user_available_response.status_code == 200, user_available_response.text
    user_available_body = user_available_response.json()
    assert user_available_body["success"] is True
    assert any(item["display_name"] == "Integration GPT Model" for item in user_available_body["data"])

    cost_logs_response = client.get("/api/v1/ai-models/cost-logs/recent?limit=5", headers=headers)
    assert cost_logs_response.status_code == 200, cost_logs_response.text
    cost_logs_body = cost_logs_response.json()
    assert cost_logs_body["success"] is True
    assert cost_logs_body["data"]["total_count"] >= 1
    assert any(log["call_type"] == "story_generation" for log in cost_logs_body["data"]["recent_logs"])

    llm_models_response = client.get("/api/v1/llm-models/")
    assert llm_models_response.status_code == 200, llm_models_response.text
    llm_models_body = llm_models_response.json()
    assert llm_models_body["success"] is True
    assert llm_models_body["data"]["total_count"] >= 2
    assert llm_models_body["data"]["active_count"] >= 2
    assert "OPENAI" in llm_models_body["data"]["providers"]
    assert any(model["display_name"] == "Integration Embedding Model" for model in llm_models_body["data"]["models"])

    def fetch_dashboard_state(session):
        async def _inner():
            return {
                "world_count": len((await session.execute(select(World))).scalars().all()),
                "story_count": len((await session.execute(select(Story))).scalars().all()),
                "character_count": len((await session.execute(select(Character))).scalars().all()),
                "location_count": len((await session.execute(select(Location))).scalars().all()),
                "lore_count": len((await session.execute(select(LoreItem))).scalars().all()),
            }

        return _inner()

    state = run_db(fetch_dashboard_state)
    assert state["world_count"] >= 1
    assert state["story_count"] >= 1
    assert state["character_count"] >= 1
    assert state["location_count"] >= 1
    assert state["lore_count"] >= 1


def test_basic_story_interview_welcome_and_importer_endpoints(client, register_and_login, run_db, monkeypatch):
    credentials, _ = register_and_login("extrasurface")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    import app.routers.world_importer as importer_router
    import app.routers.basic_stories as basic_stories_router

    async def fake_import_world_from_book_task(*args, **kwargs):
        return None

    async def fake_create_world_from_document_task(*args, **kwargs):
        return None

    class FakePdfExportService:
        async def export_story_to_pdf(self, *args, **kwargs):
            return b"%PDF-1.4 integration pdf"

    monkeypatch.setattr(importer_router, "import_world_from_book_task", fake_import_world_from_book_task)
    monkeypatch.setattr(
        importer_router,
        "create_world_and_extract_elements_from_document_task",
        fake_create_world_from_document_task,
    )
    monkeypatch.setattr(basic_stories_router, "pdf_export_service", FakePdfExportService(), raising=False)

    create_basic_story = client.post(
        "/api/v1/stories/basic/create",
        json={
            "title": "Integration Basic Story",
            "short_description": "A lightweight story flow",
        },
        headers=headers,
    )
    assert create_basic_story.status_code == 200, create_basic_story.text
    create_basic_story_body = create_basic_story.json()
    assert create_basic_story_body["success"] is True
    basic_story = create_basic_story_body["data"]
    story_id = basic_story["id"]
    assert basic_story["story_type"] == "basic"
    assert basic_story["first_act_id"] is not None
    assert "editor_url" in basic_story

    get_basic_story = client.get(f"/api/v1/stories/basic/{story_id}", headers=headers)
    assert get_basic_story.status_code == 200, get_basic_story.text
    assert get_basic_story.json()["success"] is True
    assert get_basic_story.json()["data"]["title"] == "Integration Basic Story"

    update_basic_story = client.put(
        f"/api/v1/stories/basic/{story_id}",
        json={
            "title": "Updated Basic Story",
            "short_description": "Updated lightweight story",
            "content": "<p>Basic story content for export.</p>",
        },
        headers=headers,
    )
    assert update_basic_story.status_code == 200, update_basic_story.text
    assert update_basic_story.json()["success"] is True
    assert update_basic_story.json()["data"]["title"] == "Updated Basic Story"

    list_basic_stories = client.get("/api/v1/stories/basic/list", headers=headers)
    assert list_basic_stories.status_code == 200, list_basic_stories.text
    list_basic_stories_body = list_basic_stories.json()
    assert list_basic_stories_body["success"] is True
    assert any(item["id"] == story_id for item in list_basic_stories_body["data"])

    feature_response = client.get(f"/api/v1/stories/basic/{story_id}/features", headers=headers)
    assert feature_response.status_code == 200, feature_response.text
    feature_body = feature_response.json()
    assert feature_body["success"] is True
    assert feature_body["data"]["story_id"] == story_id
    assert feature_body["data"]["story_type"] == "basic"

    export_response = client.post(
        f"/api/v1/stories/basic/{story_id}/export-pdf",
        json={"title": "Updated Basic Story", "content": "<p>Export me</p>"},
        headers=headers,
    )
    assert export_response.status_code == 200, export_response.text
    assert export_response.headers["content-type"] == "application/pdf"

    questions_response = client.get("/api/v1/interview/questions/new_user_onboarding")
    assert questions_response.status_code == 200, questions_response.text
    assert questions_response.json()["interview_id"] == "new_user_onboarding"

    submit_response = client.post(
        "/api/v1/interview/submit",
        json={
            "interview_id": "new_user_onboarding",
            "responses": {
                "writing_experience": {
                    "question_id": "writing_experience",
                    "selected_values": ["write_for_fun"],
                    "answered_at": "2026-04-01T00:00:00Z",
                },
                "genre_preferences": {
                    "question_id": "genre_preferences",
                    "selected_values": ["fantasy", "adventure"],
                    "answered_at": "2026-04-01T00:00:10Z",
                },
                "help_needed": {
                    "question_id": "help_needed",
                    "selected_values": ["brainstorming", "characters"],
                    "answered_at": "2026-04-01T00:00:20Z",
                },
                "writing_stage": {
                    "question_id": "writing_stage",
                    "selected_values": ["beginning_ideas"],
                    "answered_at": "2026-04-01T00:00:30Z",
                },
                "next_step": {
                    "question_id": "next_step",
                    "selected_values": ["world_first"],
                    "answered_at": "2026-04-01T00:00:40Z",
                },
                "brainstorming_popup": {
                    "question_id": "brainstorming_popup",
                    "selected_values": ["yes_brainstorm"],
                    "answered_at": "2026-04-01T00:00:50Z",
                },
            },
            "navigation": {
                "final_destination": "/ui/brainstorm",
                "from_question_5": "/ui/worlds/new",
            },
            "metadata": {"source": "integration-test"},
        },
        headers=headers,
    )
    assert submit_response.status_code == 200, submit_response.text
    submit_body = submit_response.json()
    assert submit_body["success"] is True
    response_id = submit_body["data"]["interview_id"]

    interview_status = client.get("/api/v1/interview/status/new_user_onboarding", headers=headers)
    assert interview_status.status_code == 200, interview_status.text
    assert interview_status.json()["completed"] is True
    assert interview_status.json()["response_id"] == response_id

    interview_response = client.get("/api/v1/interview/response/new_user_onboarding", headers=headers)
    assert interview_response.status_code == 200, interview_response.text
    assert interview_response.json()["id"] == response_id
    assert interview_response.json()["response_data"]["navigation"]["final_destination"] == "/ui/brainstorm"

    user_insights = client.get("/api/v1/interview/user-insights", headers=headers)
    assert user_insights.status_code == 200, user_insights.text
    assert user_insights.json()["has_completed_onboarding"] is True
    assert "fantasy" in user_insights.json()["insights"]["preferred_genres"]

    def seed_story_brainstorm_session(session):
        async def _inner():
            user = (
                await session.execute(select(User).where(User.username == credentials["username"]))
            ).scalar_one()
            session.add(
                UserInterviewResponse(
                    user_id=user.id,
                    interview_id="story_brainstorm",
                    json_response=json.dumps(
                        {
                            "responses": {
                                "genre_selection": {"selected_values": ["fantasy"]},
                                "story_tone": {"selected_values": ["epic_grand"]},
                            },
                            "navigation": {"final_destination": "/ui/story-wizard"},
                        }
                    ),
                )
            )
            await session.commit()

        return _inner()

    run_db(seed_story_brainstorm_session)

    brainstorm_sessions = client.get("/api/v1/interview/story-brainstorm/sessions", headers=headers)
    assert brainstorm_sessions.status_code == 200, brainstorm_sessions.text
    assert brainstorm_sessions.json()["total_sessions"] >= 1
    assert brainstorm_sessions.json()["sessions"][0]["response_data"]["navigation"]["final_destination"] == "/ui/story-wizard"

    bonus_status = client.get("/ui/welcome-interview/api/bonus-status", headers=headers)
    assert bonus_status.status_code == 200, bonus_status.text
    assert bonus_status.json()["success"] is True
    assert bonus_status.json()["data"]["bonus2"] is False

    claim_bonus = client.post(
        "/ui/welcome-interview/api/claim-bonus",
        json={"bonus_number": 2},
        headers=headers,
    )
    assert claim_bonus.status_code == 200, claim_bonus.text
    claim_bonus_body = claim_bonus.json()
    assert claim_bonus_body["success"] is True
    assert claim_bonus_body["data"]["success"] is True
    assert claim_bonus_body["data"]["coins_awarded"] == 500

    claim_bonus_again = client.post(
        "/ui/welcome-interview/api/claim-bonus",
        json={"bonus_number": 2},
        headers=headers,
    )
    assert claim_bonus_again.status_code == 200, claim_bonus_again.text
    assert claim_bonus_again.json()["data"]["already_claimed"] is True

    import_from_title = client.post(
        "/api/v1/worlds/import-from-book-title",
        json={"book_title": "The Archive of Integration"},
        headers=headers,
    )
    assert import_from_title.status_code == 202, import_from_title.text
    import_from_title_body = import_from_title.json()
    assert import_from_title_body["success"] is True
    title_job_id = import_from_title_body["data"]["job_id"]

    import_from_document = client.post(
        "/api/v1/worlds/import/create-from-document",
        data={"world_name": "Document Integration World"},
        files={"file": ("integration.txt", b"World source material", "text/plain")},
        headers=headers,
    )
    assert import_from_document.status_code == 202, import_from_document.text
    import_from_document_body = import_from_document.json()
    assert import_from_document_body["success"] is True
    document_job_id = import_from_document_body["data"]["job_id"]

    title_job_status = client.get(f"/api/v1/worlds/import/job-status/{title_job_id}", headers=headers)
    assert title_job_status.status_code == 200, title_job_status.text
    assert title_job_status.json()["success"] is True
    assert title_job_status.json()["data"]["job_id"] == title_job_id

    document_job_status = client.get(f"/api/v1/worlds/import/job-status/{document_job_id}", headers=headers)
    assert document_job_status.status_code == 200, document_job_status.text
    assert document_job_status.json()["success"] is True
    assert document_job_status.json()["data"]["job_id"] == document_job_id
