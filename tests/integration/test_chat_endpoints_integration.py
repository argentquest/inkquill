from types import SimpleNamespace

import pytest
from sqlalchemy import select

from app.models.chat_message import ChatMessage
from app.models.chat_session import ChatSession
from app.models.story_chat_message import StoryChatMessage
from app.models.story_chat_session import StoryChatSession


pytestmark = pytest.mark.integration


def test_world_chat_endpoints_with_mocked_ai(client, register_and_login, run_db, monkeypatch):
    register_and_login("worldchat")

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Chat World",
            "description": "World used for chat integration",
            "short_description": "Chat world",
            "is_free_chat_enabled": True,
        },
    )
    assert world_response.status_code == 201, world_response.text
    world_id = world_response.json()["data"]["id"]

    client.post(
        f"/api/v1/worlds/{world_id}/characters/",
        json={"name": "Archivist Vale", "description": "Keeps the city records"},
    )
    client.post(
        f"/api/v1/worlds/{world_id}/locations/",
        json={"name": "Mirror Archive", "description": "Repository of mirrored histories", "scale": "BUILDING"},
    )
    client.post(
        f"/api/v1/worlds/{world_id}/lore-items/",
        json={"title": "Mirror Ledger", "description": "Records branching outcomes", "category": "ARTIFACT"},
    )

    async def fake_generate_ai_response(self, **kwargs):
        full_context = {
            "user_message": kwargs["user_message"],
            "world_summary": "Chat World summary",
            "document_context": "No documents",
            "context_sources": [{"type": "world", "label": "Chat World"}],
            "conversation_history": "User: Tell me about the archive",
            "element_context": "",
            "timestamp": "2026-03-30T00:00:00Z",
        }
        stats = {
            "input_tokens": 12,
            "output_tokens": 24,
            "total_tokens": 36,
            "cost": 0.0,
            "model_name": "mock-world-chat",
            "duration_ms": 1,
        }
        return "The Mirror Archive preserves branching city histories.", None, full_context, stats

    monkeypatch.setattr(
        "app.services.world_chat_service.WorldChatService._generate_ai_response",
        fake_generate_ai_response,
    )

    samples_response = client.get("/api/v1/world-chat/chat/samples")
    assert samples_response.status_code == 200, samples_response.text
    assert isinstance(samples_response.json()["data"], list)

    create_session = client.post(f"/api/v1/world-chat/sessions/{world_id}")
    assert create_session.status_code == 200, create_session.text
    create_body = create_session.json()
    assert create_body["success"] is True
    session_id = create_body["data"]["id"]

    list_sessions = client.get(f"/api/v1/world-chat/sessions/{world_id}")
    assert list_sessions.status_code == 200, list_sessions.text
    assert list_sessions.json()["data"]["total"] >= 1

    session_detail = client.get(f"/api/v1/world-chat/sessions/{world_id}/{session_id}")
    assert session_detail.status_code == 200, session_detail.text
    assert session_detail.json()["data"]["messages"] == []

    send_message = client.post(
        f"/api/v1/world-chat/sessions/{world_id}/{session_id}/messages",
        json={"message": "Tell me about the archive"},
    )
    assert send_message.status_code == 200, send_message.text
    send_body = send_message.json()
    assert send_body["success"] is True
    assert send_body["data"]["ai_response"]["content"] == "The Mirror Archive preserves branching city histories."

    session_after_message = client.get(f"/api/v1/world-chat/sessions/{world_id}/{session_id}")
    assert session_after_message.status_code == 200, session_after_message.text
    assert len(session_after_message.json()["data"]["messages"]) == 2

    world_context = client.get(f"/api/v1/world-chat/world-context/{world_id}")
    assert world_context.status_code == 200, world_context.text
    assert world_context.json()["data"]["world"]["name"] == "Chat World"
    assert len(world_context.json()["data"]["characters"]) == 1

    delete_session = client.delete(f"/api/v1/world-chat/sessions/{world_id}/{session_id}")
    assert delete_session.status_code == 200, delete_session.text
    assert delete_session.json()["data"]["message"] == "Chat session deleted successfully"

    def fetch_chat_state(session):
        async def _inner():
            remaining_session = (
                await session.execute(select(ChatSession).where(ChatSession.id == session_id))
            ).scalar_one_or_none()
            messages = (
                await session.execute(select(ChatMessage).where(ChatMessage.session_id == session_id))
            ).scalars().all()
            return {
                "remaining_session": remaining_session,
                "message_count": len(messages),
            }

        return _inner()

    state = run_db(fetch_chat_state)
    assert state["remaining_session"] is None
    assert state["message_count"] == 0


def test_story_chat_session_endpoints_with_mocked_stream(client, register_and_login, run_db, monkeypatch):
    register_and_login("storychat")

    world_response = client.post(
        "/api/v1/worlds/",
        json={
            "name": "Story Chat World",
            "description": "World for story chat integration",
            "short_description": "Story chat world",
            "is_free_chat_enabled": False,
        },
    )
    assert world_response.status_code == 201, world_response.text
    world_id = world_response.json()["data"]["id"]

    story_response = client.post(
        "/api/v1/stories/",
        json={
            "title": "Story Chat Story",
            "short_description": "Story used for story chat",
            "world_id": world_id,
            "story_type": "advanced",
        },
    )
    assert story_response.status_code == 201, story_response.text
    story_id = story_response.json()["data"]["id"]

    act_response = client.post(
        f"/api/v1/stories/{story_id}/acts/",
        json={"title": "Act One", "description": "Opening act", "act_number": 1},
    )
    assert act_response.status_code == 201, act_response.text
    act_id = act_response.json()["data"]["id"]

    scene_response = client.post(
        f"/api/v1/acts/{act_id}/scenes/",
        json={
            "title": "First Exchange",
            "summary": "Opening exchange",
            "content": "The protagonist discovers a coded ledger.",
            "scene_number": 1,
        },
    )
    assert scene_response.status_code == 201, scene_response.text

    async def fake_story_send_message(self, story_id, session_id, user_id, request):
        user_message = StoryChatMessage(
            session_id=session_id,
            role="user",
            content=request.message,
            target_element=request.target_element,
            target_element_id=request.target_element_id,
        )
        self.db.add(user_message)
        await self.db.flush()

        ai_message = StoryChatMessage(
            session_id=session_id,
            role="assistant",
            content="Focus the next revision on the ledger reveal.",
            full_context={"mode": "mock"},
            story_context={"story_id": story_id},
        )
        self.db.add(ai_message)
        await self.db.commit()

        yield "Focus the next revision on the ledger reveal."

    monkeypatch.setattr(
        "app.services.story_chat_service.StoryChatService.send_message",
        fake_story_send_message,
    )

    create_session = client.post(
        f"/api/v1/story-chat/stories/{story_id}/sessions",
        json={"title": "Revision Session", "description": "Discuss act pacing", "focus_area": "plot"},
    )
    assert create_session.status_code == 200, create_session.text
    session_body = create_session.json()
    assert session_body["success"] is True
    session_id = session_body["data"]["id"]

    list_sessions = client.get(f"/api/v1/story-chat/stories/{story_id}/sessions")
    assert list_sessions.status_code == 200, list_sessions.text
    assert list_sessions.json()["data"][0]["id"] == session_id

    session_detail = client.get(f"/api/v1/story-chat/stories/{story_id}/sessions/{session_id}")
    assert session_detail.status_code == 200, session_detail.text
    assert session_detail.json()["data"]["messages"] == []

    send_ws_ticket = client.get("/api/v1/auth/ws-ticket")
    assert send_ws_ticket.status_code == 200, send_ws_ticket.text
    assert send_ws_ticket.json()["data"]["ticket"]

    with client.websocket_connect(
        f"/api/v1/story-chat/ws/stories/{story_id}/sessions/{session_id}/chat?ticket="
        f"{send_ws_ticket.json()['data']['ticket']}"
    ) as websocket:
        session_info = websocket.receive_json()
        assert session_info["type"] == "session_info"
        websocket.send_json({"type": "send_message", "content": "How should I improve act one?"})
        response_start = websocket.receive_json()
        text_chunk = websocket.receive_json()
        response_complete = websocket.receive_json()
        assert response_start["type"] == "response_start"
        assert text_chunk["type"] == "text_chunk"
        assert "ledger reveal" in text_chunk["content"]
        assert response_complete["type"] == "response_complete"

    session_after_chat = client.get(f"/api/v1/story-chat/stories/{story_id}/sessions/{session_id}")
    assert session_after_chat.status_code == 200, session_after_chat.text
    assert len(session_after_chat.json()["data"]["messages"]) == 2

    delete_session = client.delete(f"/api/v1/story-chat/stories/{story_id}/sessions/{session_id}")
    assert delete_session.status_code == 200, delete_session.text
    assert delete_session.json()["data"]["message"] == "Session deleted successfully"

    def fetch_story_chat_state(session):
        async def _inner():
            remaining_session = (
                await session.execute(select(StoryChatSession).where(StoryChatSession.id == session_id))
            ).scalar_one_or_none()
            messages = (
                await session.execute(
                    select(StoryChatMessage).where(StoryChatMessage.session_id == session_id)
                )
            ).scalars().all()
            return {
                "remaining_session": remaining_session,
                "message_count": len(messages),
            }

        return _inner()

    state = run_db(fetch_story_chat_state)
    assert state["remaining_session"] is None
    assert state["message_count"] == 0
