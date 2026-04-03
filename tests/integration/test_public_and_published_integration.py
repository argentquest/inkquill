import pytest
from sqlalchemy import select

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.published_story import PublishedStory
from app.models.story_comment import StoryComment
from app.models.story_rating import StoryRating


pytestmark = pytest.mark.integration


def _get_access_token(client, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


def test_public_world_chat_endpoints_with_mocked_ai(client, register_and_login, run_db, monkeypatch):
    credentials, _ = register_and_login("publicchat")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    auth_headers = {"Authorization": f"Bearer {token}"}

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Public Chat World",
            "description": "World used for public chat integration",
            "short_description": "Public chat world",
            "is_free_chat_enabled": True,
        },
    )
    assert world_response.status_code == 201, world_response.text
    world_id = world_response.json()["data"]["id"]

    client.post(
        f"/api/v1/worlds/{world_id}/characters/",
        json={"name": "Dockmaster Elian", "description": "Coordinates sky-port arrivals"},
    )
    client.post(
        f"/api/v1/worlds/{world_id}/locations/",
        json={"name": "Sky Port", "description": "Main gateway for floating ships", "scale": "BUILDING"},
    )
    client.post(
        f"/api/v1/worlds/{world_id}/lore-items/",
        json={"title": "Port Ledger", "description": "Tracks every vessel crossing the clouds", "category": "ARTIFACT"},
    )

    async def fake_generate_ai_response(self, **kwargs):
        full_context = {
            "user_message": kwargs["user_message"],
            "world_summary": "Public Chat World summary",
            "document_context": "No uploaded documents",
            "context_sources": [{"type": "world", "label": "Public Chat World"}],
            "conversation_history": "User: What is the Sky Port like?",
            "element_context": "",
            "timestamp": "2026-03-30T00:00:00Z",
        }
        stats = {
            "input_tokens": 14,
            "output_tokens": 22,
            "total_tokens": 36,
            "cost": 0.0,
            "model_name": "mock-public-chat",
            "duration_ms": 2,
        }
        return "The Sky Port is a crowded aerial harbor suspended above the trade winds.", None, full_context, stats

    monkeypatch.setattr(
        "app.services.world_chat_service.WorldChatService._generate_ai_response",
        fake_generate_ai_response,
    )

    samples_response = client.get("/api/v1/public/chat/samples")
    assert samples_response.status_code == 200, samples_response.text
    samples_body = samples_response.json()
    assert samples_body["success"] is True
    assert isinstance(samples_body["data"], list)

    public_worlds = client.get("/api/v1/public/worlds")
    assert public_worlds.status_code == 200, public_worlds.text
    worlds_body = public_worlds.json()
    assert worlds_body["success"] is True
    assert any(world["id"] == world_id for world in worlds_body["data"])

    public_world_detail = client.get(f"/api/v1/public/worlds/{world_id}")
    assert public_world_detail.status_code == 200, public_world_detail.text
    detail_body = public_world_detail.json()
    assert detail_body["success"] is True
    assert detail_body["data"]["world"]["name"] == "Public Chat World"
    assert len(detail_body["data"]["characters"]) == 1
    assert len(detail_body["data"]["locations"]) == 1
    assert len(detail_body["data"]["lore_items"]) == 1

    start_chat = client.post(
        f"/api/v1/public/worlds/{world_id}/chat",
        headers=auth_headers,
    )
    assert start_chat.status_code == 200, start_chat.text
    start_body = start_chat.json()
    assert start_body["success"] is True
    session_id = start_body["data"]["session_id"]
    assert start_body["data"]["world_name"] == "Public Chat World"
    assert start_body["data"]["remaining_balance"] >= 1.0

    send_message = client.post(
        f"/api/v1/public/chat/{session_id}/message",
        json={"content": "What is the Sky Port like?"},
        headers=auth_headers,
    )
    assert send_message.status_code == 200, send_message.text
    send_body = send_message.json()
    assert send_body["success"] is True
    assert "Sky Port" in send_body["data"]["ai_message"]["content"]
    assert send_body["data"]["call_stats"]["model_name"] == "mock-public-chat"

    list_messages = client.get(
        f"/api/v1/public/chat/{session_id}/messages",
        headers=auth_headers,
    )
    assert list_messages.status_code == 200, list_messages.text
    messages_body = list_messages.json()
    assert messages_body["success"] is True
    assert len(messages_body["data"]["messages"]) == 2

    def fetch_public_chat_state(session):
        async def _inner():
            chat_session = (
                await session.execute(select(ChatSession).where(ChatSession.id == session_id))
            ).scalar_one()
            messages = (
                await session.execute(
                    select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.id)
                )
            ).scalars().all()
            return {
                "world_id": chat_session.world_id,
                "user_id": chat_session.user_id,
                "message_roles": [message.role for message in messages],
                "assistant_content": messages[1].content,
            }

        return _inner()

    state = run_db(fetch_public_chat_state)
    assert state["world_id"] == world_id
    assert state["message_roles"] == ["user", "assistant"]
    assert "Sky Port" in state["assistant_content"]


def test_published_story_endpoints_persist_ratings_and_comments(client, register_and_login, run_db):
    credentials, _ = register_and_login("publishedflow")
    token = _get_access_token(client, credentials["username"], credentials["password"])
    auth_headers = {"Authorization": f"Bearer {token}"}

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Published Story World",
            "description": "World for published story integration",
            "short_description": "Published story world",
            "is_free_chat_enabled": False,
        },
    )
    world_id = world_response.json()["data"]["id"]

    story_response = client.post(
        "/api/v1/stories/",
        json={
            "title": "Published Integration Story",
            "short_description": "Story destined for the public catalog",
            "world_id": world_id,
            "story_type": "advanced",
        },
    )
    assert story_response.status_code == 201, story_response.text
    story_id = story_response.json()["data"]["id"]

    act_response = client.post(
        f"/api/v1/stories/{story_id}/acts/",
        json={"title": "Arrival", "description": "Opening act", "act_number": 1},
    )
    act_id = act_response.json()["data"]["id"]

    scene_response = client.post(
        f"/api/v1/acts/{act_id}/scenes/",
        json={
            "title": "Docking",
            "summary": "The ship arrives at the port",
            "content": "The vessel descended through silver cloud banks and locked into the sky-port berth.",
            "scene_number": 1,
        },
    )
    assert scene_response.status_code == 201, scene_response.text

    publish_response = client.post(
        f"/api/v1/stories/{story_id}/publish",
        json={"visibility": "public", "description": "Catalog description for integration tests"},
    )
    assert publish_response.status_code == 200, publish_response.text

    def fetch_published_story_id(session):
        async def _inner():
            published_story = (
                await session.execute(
                    select(PublishedStory).where(PublishedStory.story_id == story_id)
                )
            ).scalar_one()
            return published_story.id

        return _inner()

    published_story_id = run_db(fetch_published_story_id)

    list_response = client.get("/api/v1/published-stories/")
    assert list_response.status_code == 200, list_response.text
    list_body = list_response.json()
    assert list_body["success"] is True
    assert any(story["id"] == published_story_id for story in list_body["data"]["stories"])

    detail_response = client.get(
        f"/api/v1/published-stories/{published_story_id}",
        headers=auth_headers,
    )
    assert detail_response.status_code == 200, detail_response.text
    detail_body = detail_response.json()
    assert detail_body["success"] is True
    assert detail_body["data"]["title"] == "Published Integration Story"
    assert detail_body["data"]["story_title"] == "Published Integration Story"
    assert detail_body["data"]["has_user_rated"] is False

    rating_response = client.post(
        f"/api/v1/published-stories/{published_story_id}/rate",
        json={"published_story_id": published_story_id, "rating": 5},
        headers=auth_headers,
    )
    assert rating_response.status_code == 200, rating_response.text
    rating_body = rating_response.json()
    assert rating_body["success"] is True
    assert rating_body["data"]["rating"] == 5

    comment_response = client.post(
        f"/api/v1/published-stories/{published_story_id}/comments",
        json={"published_story_id": published_story_id, "content": "This scene lands cleanly and reads well."},
        headers=auth_headers,
    )
    assert comment_response.status_code == 200, comment_response.text
    comment_body = comment_response.json()
    assert comment_body["success"] is True
    assert comment_body["data"]["content"] == "This scene lands cleanly and reads well."

    comments_response = client.get(f"/api/v1/published-stories/{published_story_id}/comments")
    assert comments_response.status_code == 200, comments_response.text
    comments_body = comments_response.json()
    assert comments_body["success"] is True
    assert len(comments_body["data"]) == 1

    detail_after_rating = client.get(
        f"/api/v1/published-stories/{published_story_id}",
        headers=auth_headers,
    )
    assert detail_after_rating.status_code == 200, detail_after_rating.text
    detail_after_body = detail_after_rating.json()
    assert detail_after_body["data"]["has_user_rated"] is True
    assert detail_after_body["data"]["user_rating"] == 5

    def fetch_published_state(session):
        async def _inner():
            published_story = (
                await session.execute(select(PublishedStory).where(PublishedStory.id == published_story_id))
            ).scalar_one()
            rating = (
                await session.execute(select(StoryRating).where(StoryRating.published_story_id == published_story_id))
            ).scalar_one()
            comment = (
                await session.execute(select(StoryComment).where(StoryComment.published_story_id == published_story_id))
            ).scalar_one()
            return {
                "view_count": published_story.view_count,
                "average_rating": published_story.average_rating,
                "like_count": published_story.like_count,
                "comment_count": published_story.comment_count,
                "rating": rating.rating,
                "comment_content": comment.content,
            }

        return _inner()

    state = run_db(fetch_published_state)
    assert state["view_count"] >= 2
    assert state["average_rating"] == 5.0
    assert state["like_count"] == 1
    assert state["comment_count"] == 1
    assert state["rating"] == 5
    assert state["comment_content"] == "This scene lands cleanly and reads well."
