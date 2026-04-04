from pathlib import Path

import pytest
from sqlalchemy import select

from app.models.cta_content import CTAContent
from app.models.prompt import Prompt
from app.models.story_class import StoryClass
from app.models.social_share import SocialShare
from app.models.user import User
from app.models.user_activity import UserActivity


pytestmark = pytest.mark.integration


def _get_access_token(client, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_prompt_and_story_class_endpoints_work_with_real_db(client, register_and_login, run_db):
    credentials, _ = register_and_login("promptflow")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Prompt StoryClass World",
            "description": "World for prompt and story class integration tests",
            "short_description": "Prompt world",
            "is_free_chat_enabled": False,
        },
        headers=headers,
    )
    assert world_response.status_code == 201, world_response.text
    world_id = world_response.json()["data"]["id"]

    prompt_payloads = [
        {
            "title": "Epic Fantasy",
            "prompt_content": "Use epic fantasy framing.",
            "prompt_type": "STORY_GENRE",
            "age_target": "ALL_AGES",
        },
        {
            "title": "Hopeful",
            "prompt_content": "Use a hopeful tone.",
            "prompt_type": "STORY_TONE",
            "age_target": "ALL_AGES",
        },
        {
            "title": "Man vs Fate",
            "prompt_content": "Conflict against fate.",
            "prompt_type": "STORY_CONFLICT",
            "age_target": "ALL_AGES",
        },
        {
            "title": "Guardian",
            "prompt_content": "Character role prompt.",
            "prompt_type": "CHARACTER_ROLE",
            "age_target": "ALL_AGES",
        },
        {
            "title": "Painterly",
            "prompt_content": "Art style prompt.",
            "prompt_type": "IMAGE_STYLE",
            "age_target": "ALL_AGES",
        },
    ]

    created_prompt_ids = []
    for payload in prompt_payloads:
        response = client.post("/api/v1/prompts/", json=payload, headers=headers)
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["success"] is True
        created_prompt_ids.append(body["data"]["id"])

    my_prompts_response = client.get("/api/v1/prompts/my-prompts", headers=headers)
    assert my_prompts_response.status_code == 200, my_prompts_response.text
    my_prompts_body = my_prompts_response.json()
    assert my_prompts_body["success"] is True
    assert set(created_prompt_ids).issubset({item["id"] for item in my_prompts_body["data"]})

    story_options_response = client.get("/api/v1/prompts/story-options", headers=headers)
    assert story_options_response.status_code == 200, story_options_response.text
    story_options_body = story_options_response.json()
    assert story_options_body["success"] is True
    assert any(item["title"] == "Epic Fantasy" for item in story_options_body["data"]["genres"])
    assert any(item["title"] == "Hopeful" for item in story_options_body["data"]["tones"])
    assert any(item["title"] == "Man vs Fate" for item in story_options_body["data"]["conflicts"])

    character_roles_response = client.get("/api/v1/prompts/character-roles", headers=headers)
    assert character_roles_response.status_code == 200, character_roles_response.text
    assert any(item["title"] == "Guardian" for item in character_roles_response.json()["data"])

    art_styles_response = client.get("/api/v1/prompts/art-styles", headers=headers)
    assert art_styles_response.status_code == 200, art_styles_response.text
    assert any(item["title"] == "Painterly" for item in art_styles_response.json()["data"])

    prompt_id = created_prompt_ids[0]
    get_prompt_response = client.get(f"/api/v1/prompts/{prompt_id}", headers=headers)
    assert get_prompt_response.status_code == 200, get_prompt_response.text
    assert get_prompt_response.json()["data"]["title"] == "Epic Fantasy"

    update_prompt_response = client.put(
        f"/api/v1/prompts/{prompt_id}",
        json={"comment": "Updated in integration test"},
        headers=headers,
    )
    assert update_prompt_response.status_code == 200, update_prompt_response.text
    assert update_prompt_response.json()["data"]["comment"] == "Updated in integration test"

    story_class_response = client.post(
        f"/api/v1/story-classes/?world_id={world_id}",
        json={
            "name": "Action Beat",
            "description": "High-energy sequence",
            "color": "#12ABEF",
        },
        headers=headers,
    )
    assert story_class_response.status_code == 201, story_class_response.text
    story_class_body = story_class_response.json()
    assert story_class_body["success"] is True
    story_class_id = story_class_body["data"]["id"]

    list_story_classes = client.get(f"/api/v1/story-classes/?world_id={world_id}", headers=headers)
    assert list_story_classes.status_code == 200, list_story_classes.text
    list_story_classes_body = list_story_classes.json()
    assert list_story_classes_body["success"] is True
    assert any(item["id"] == story_class_id for item in list_story_classes_body["data"])

    options_response = client.get(f"/api/v1/story-classes/options?world_id={world_id}", headers=headers)
    assert options_response.status_code == 200, options_response.text
    options_body = options_response.json()
    assert options_body["success"] is True
    assert any(item["id"] == story_class_id for item in options_body["data"])

    get_story_class = client.get(f"/api/v1/story-classes/{story_class_id}", headers=headers)
    assert get_story_class.status_code == 200, get_story_class.text
    assert get_story_class.json()["data"]["name"] == "Action Beat"

    update_story_class = client.put(
        f"/api/v1/story-classes/{story_class_id}",
        json={"description": "Updated sequence description"},
        headers=headers,
    )
    assert update_story_class.status_code == 200, update_story_class.text
    assert update_story_class.json()["data"]["description"] == "Updated sequence description"

    delete_prompt = client.delete(f"/api/v1/prompts/{prompt_id}", headers=headers)
    assert delete_prompt.status_code == 204, delete_prompt.text

    delete_story_class = client.delete(f"/api/v1/story-classes/{story_class_id}", headers=headers)
    assert delete_story_class.status_code == 204, delete_story_class.text

    def fetch_prompt_and_story_class_state(session):
        async def _inner():
            prompt_count = len((await session.execute(select(Prompt))).scalars().all())
            story_class = (
                await session.execute(select(StoryClass).where(StoryClass.id == story_class_id))
            ).scalar_one_or_none()
            prompt = (
                await session.execute(select(Prompt).where(Prompt.id == prompt_id))
            ).scalar_one_or_none()
            return {
                "prompt_count": prompt_count,
                "story_class_missing": story_class is None,
                "prompt_missing": prompt is None,
            }

        return _inner()

    state = run_db(fetch_prompt_and_story_class_state)
    assert state["prompt_count"] >= 4
    assert state["story_class_missing"] is True
    assert state["prompt_missing"] is True


def test_admin_cta_and_maintenance_endpoints_work_for_admins(client, register_and_login, run_db, tmp_path, monkeypatch):
    credentials, _ = register_and_login("adminops")

    def promote_admin(session):
        async def _inner():
            user = (
                await session.execute(select(User).where(User.username == credentials["username"]))
            ).scalar_one()
            user.is_admin = True
            await session.commit()

        return _inner()

    run_db(promote_admin)

    from app.core import maintenance as maintenance_module

    monkeypatch.setattr(
        maintenance_module,
        "MAINTENANCE_FILE_PATH",
        Path(tmp_path) / "maintenance_status.json",
    )

    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    create_cta_response = client.post(
        "/api/v1/admin/cta-content",
        json={
            "title": "Start Writing",
            "subtitle": "Build your next world",
            "position": "HOME_SIDEBAR_TOP",
            "style": "gradient",
            "features": [{"icon": "fas fa-book", "text": "Outline faster"}],
            "primary_button_text": "Create World",
            "primary_button_url": "/ui/worlds/new",
        },
        headers=headers,
    )
    assert create_cta_response.status_code == 201, create_cta_response.text
    create_cta_body = create_cta_response.json()
    assert create_cta_body["success"] is True
    cta_id = create_cta_body["data"]["id"]

    list_ctas_response = client.get("/api/v1/admin/cta-content?include_inactive=true", headers=headers)
    assert list_ctas_response.status_code == 200, list_ctas_response.text
    list_ctas_body = list_ctas_response.json()
    assert list_ctas_body["success"] is True
    assert any(item["id"] == cta_id for item in list_ctas_body["data"])

    get_cta_response = client.get(f"/api/v1/admin/cta-content/{cta_id}", headers=headers)
    assert get_cta_response.status_code == 200, get_cta_response.text
    assert get_cta_response.json()["data"]["title"] == "Start Writing"

    update_cta_response = client.put(
        f"/api/v1/admin/cta-content/{cta_id}",
        json={"subtitle": "Build your next world faster"},
        headers=headers,
    )
    assert update_cta_response.status_code == 200, update_cta_response.text
    assert update_cta_response.json()["success"] is True

    toggle_cta_response = client.post(f"/api/v1/admin/cta-content/{cta_id}/toggle-active", headers=headers)
    assert toggle_cta_response.status_code == 200, toggle_cta_response.text
    assert toggle_cta_response.json()["data"]["is_active"] is False

    debug_user_response = client.get("/api/v1/admin/debug/user-info", headers=headers)
    assert debug_user_response.status_code == 200, debug_user_response.text
    assert debug_user_response.json()["data"]["is_admin"] is True

    create_default_response = client.post("/api/v1/admin/cta-content/create-default", headers=headers)
    assert create_default_response.status_code == 200, create_default_response.text
    assert create_default_response.json()["success"] is True

    maintenance_status = client.get("/api/v1/maintenance/status")
    assert maintenance_status.status_code == 200, maintenance_status.text
    assert maintenance_status.json()["success"] is True
    assert maintenance_status.json()["data"]["enabled"] is False

    enable_maintenance = client.post(
        "/api/v1/maintenance/enable",
        params={"message": "Planned maintenance", "duration_minutes": 15},
        headers=headers,
    )
    assert enable_maintenance.status_code == 200, enable_maintenance.text
    assert enable_maintenance.json()["data"]["status"] == "Maintenance mode enabled"

    maintenance_status_after = client.get("/api/v1/maintenance/status")
    assert maintenance_status_after.status_code == 200, maintenance_status_after.text
    assert maintenance_status_after.json()["data"]["enabled"] is True

    disable_maintenance = client.post("/api/v1/maintenance/disable", headers=headers)
    assert disable_maintenance.status_code == 200, disable_maintenance.text
    assert disable_maintenance.json()["data"]["status"] == "Maintenance mode disabled"

    delete_cta_response = client.delete(f"/api/v1/admin/cta-content/{cta_id}", headers=headers)
    assert delete_cta_response.status_code == 200, delete_cta_response.text
    assert delete_cta_response.json()["success"] is True

    def fetch_admin_state(session):
        async def _inner():
            ctas = (await session.execute(select(CTAContent))).scalars().all()
            return {
                "remaining_titles": [cta.title for cta in ctas],
            }

        return _inner()

    state = run_db(fetch_admin_state)
    assert "Start Writing" not in state["remaining_titles"]
    assert any(title == "Start Your Story Today!" for title in state["remaining_titles"])


def test_social_and_bot_analytics_endpoints_use_real_db_and_mockable_flows(client, register_and_login, run_db):
    credentials, _ = register_and_login("socialflow")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    headers = {"Authorization": f"Bearer {token}"}

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Social Preview World",
            "description": "World for social preview tests",
            "short_description": "Social world",
            "is_free_chat_enabled": False,
        },
        headers=headers,
    )
    assert world_response.status_code == 201, world_response.text
    world_id = world_response.json()["data"]["id"]

    story_response = client.post(
        "/api/v1/stories/",
        json={
            "title": "Social Preview Story",
            "short_description": "Story for social preview tests",
            "world_id": world_id,
            "story_type": "advanced",
        },
        headers=headers,
    )
    assert story_response.status_code == 201, story_response.text
    story_id = story_response.json()["data"]["id"]

    def seed_user_activity(session):
        async def _inner():
            user = (
                await session.execute(select(User).where(User.username == credentials["username"]))
            ).scalar_one()
            session.add_all(
                [
                    UserActivity(
                        user_id=user.id,
                        action_type="api_call",
                        action_category="analytics",
                        endpoint="/api/v1/worlds/",
                        method="GET",
                        status_code=200,
                        ip_address="127.0.0.1",
                        user_agent="Mozilla/5.0",
                        request_data={"referrer": "http://example.com"},
                    ),
                    UserActivity(
                        user_id=None,
                        action_type="api_call",
                        action_category="analytics",
                        endpoint="/api/v1/social/preview/story/1.jpg",
                        method="GET",
                        status_code=200,
                        ip_address="127.0.0.2",
                        user_agent="facebookexternalhit/1.1",
                        request_data={"referrer": "http://facebook.com"},
                    ),
                ]
            )
            await session.commit()

        return _inner()

    run_db(seed_user_activity)

    platforms_response = client.get("/api/v1/social/share/platforms")
    assert platforms_response.status_code == 200, platforms_response.text
    assert platforms_response.json()["success"] is True
    assert any(item["id"] == "facebook" for item in platforms_response.json()["data"]["platforms"])

    config_response = client.get("/api/v1/social/share/config")
    assert config_response.status_code == 200, config_response.text
    assert config_response.json()["success"] is True
    assert "published_story" in config_response.json()["data"]["supported_content_types"]

    share_url_response = client.post(
        "/api/v1/social/share/url",
        params={
            "url": "http://testserver/published/story",
            "title": "Share This Story",
            "description": "A shared story",
            "hashtags": "#inkandquill",
        },
        json={"content_type": "published_story", "content_id": "1", "platform": "facebook"},
        headers=headers,
    )
    assert share_url_response.status_code == 200, share_url_response.text
    share_url_body = share_url_response.json()
    assert share_url_body["success"] is True
    assert "facebook.com" in share_url_body["data"]["share_url"]

    track_share_response = client.post(
        "/api/v1/social/share/track",
        json={
            "content_type": "published_story",
            "content_id": str(story_id),
            "content_title": "Social Preview Story",
            "content_url": "http://testserver/published/story",
            "platform": "facebook",
            "shared_text": "Read this story",
            "shared_hashtags": "#inkandquill",
        },
        headers=headers,
    )
    assert track_share_response.status_code == 200, track_share_response.text
    track_share_body = track_share_response.json()
    assert track_share_body["success"] is True
    assert track_share_body["data"]["coin_awarded"] is True

    daily_stats_response = client.get("/api/v1/social/share/stats/daily", headers=headers)
    assert daily_stats_response.status_code == 200, daily_stats_response.text
    daily_stats_body = daily_stats_response.json()
    assert daily_stats_body["success"] is True
    assert daily_stats_body["data"]["total_shares"] >= 1

    analytics_response = client.get("/api/v1/social/share/analytics", headers=headers)
    assert analytics_response.status_code == 200, analytics_response.text
    analytics_body = analytics_response.json()
    assert analytics_body["success"] is True
    assert analytics_body["data"]["total_shares"] >= 1

    preview_story_response = client.get(f"/api/v1/social/preview/story/{story_id}.jpg")
    assert preview_story_response.status_code == 200, preview_story_response.text
    assert preview_story_response.headers["content-type"] == "image/jpeg"

    preview_world_response = client.get(f"/api/v1/social/preview/world/{world_id}.jpg")
    assert preview_world_response.status_code == 200, preview_world_response.text
    assert preview_world_response.headers["content-type"] == "image/jpeg"

    composite_response = client.get(
        "/api/v1/social/composite-image/test-image.jpg",
        params={
            "title": "Composite",
            "description": "Fallback composite generation",
            "image_type": "Story",
            "owner": credentials["username"],
            "date": "2026-03-31",
            "original_url": "http://does-not-resolve.invalid/image.jpg",
        },
    )
    assert composite_response.status_code == 200, composite_response.text
    assert composite_response.headers["content-type"] == "image/jpeg"

    test_composite_response = client.get("/api/v1/social/test-composite")
    assert test_composite_response.status_code == 200, test_composite_response.text
    assert "Composite image generation system operational" in test_composite_response.json()["message"]

    debug_share_response = client.get(
        "/api/v1/social/debug-facebook-share",
        params={"title": "Story Share", "description": "Debug share"},
    )
    assert debug_share_response.status_code == 200, debug_share_response.text
    assert "facebook_share_url" in debug_share_response.json()["debug_info"]

    bot_detection_response = client.get("/api/v1/analytics/bot-detection-test")
    assert bot_detection_response.status_code == 200, bot_detection_response.text
    assert bot_detection_response.json()["success"] is True

    activity_stats_response = client.get("/api/v1/analytics/activity-stats")
    assert activity_stats_response.status_code == 200, activity_stats_response.text
    activity_stats_body = activity_stats_response.json()
    assert activity_stats_body["success"] is True
    assert activity_stats_body["data"]["total_activity_count"] >= 2
    assert any(
        item["endpoint"] == "/api/v1/worlds/" for item in activity_stats_body["data"]["top_endpoints"]
    )

    recent_activity_response = client.get("/api/v1/analytics/recent-activity?limit=100")
    assert recent_activity_response.status_code == 200, recent_activity_response.text
    recent_activity_body = recent_activity_response.json()
    assert recent_activity_body["success"] is True
    assert recent_activity_body["data"]["total_returned"] >= 2
    assert any(
        item["likely_bot"] is True and "facebook" in item["user_agent"].lower()
        for item in recent_activity_body["data"]["activities"]
    )

    def fetch_social_state(session):
        async def _inner():
            shares = (await session.execute(select(SocialShare))).scalars().all()
            activities = (await session.execute(select(UserActivity))).scalars().all()
            return {
                "share_count": len(shares),
                "activity_count": len(activities),
            }

        return _inner()

    state = run_db(fetch_social_state)
    assert state["share_count"] >= 1
    assert state["activity_count"] >= 2
