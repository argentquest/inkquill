"""Integration tests for chatbot session and message API flows."""
import pytest

pytestmark = pytest.mark.integration


def test_session_list_returns_ordered_by_updated_at(client, register_and_login):
    """GET /api/v1/chatbot/sessions returns sessions ordered by updated_at desc."""
    register_and_login("chatbot_order")
    client.post("/api/v1/chatbot/sessions", json={"title": "First"})
    import time; time.sleep(0.01)
    client.post("/api/v1/chatbot/sessions", json={"title": "Second"})

    resp = client.get("/api/v1/chatbot/sessions")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 2
    assert data[0]["title"] == "Second"
    assert data[1]["title"] == "First"


def test_send_message_increments_session_updated_at(client, register_and_login):
    """Sending a message updates the session's updated_at."""
    register_and_login("chatbot_updated_at")
    session = client.post("/api/v1/chatbot/sessions", json={"title": "Update test"}).json()["data"]
    session_id = session["id"]
    before = session["updated_at"]

    import time; time.sleep(0.01)
    client.post(f"/api/v1/chatbot/sessions/{session_id}/messages", json={"message": "Hello"})
    updated = client.get(f"/api/v1/chatbot/sessions/{session_id}").json()["data"]
    after = updated["updated_at"]

    assert after != before


def test_delete_nonexistent_session_returns_404(client, register_and_login):
    """DELETE /api/v1/chatbot/sessions/:id returns 404 for missing session."""
    register_and_login("chatbot_del_missing")
    resp = client.delete("/api/v1/chatbot/sessions/999999")
    assert resp.status_code == 404


def test_rename_session_empty_title_returns_422(client, register_and_login):
    """PUT /api/v1/chatbot/sessions/:id with empty title returns 422."""
    register_and_login("chatbot_rename_empty")
    session_id = client.post("/api/v1/chatbot/sessions", json={"title": "Test"}).json()["data"]["id"]
    resp = client.put(f"/api/v1/chatbot/sessions/{session_id}", json={"title": ""})
    assert resp.status_code == 422


def test_get_session_returns_messages_with_cost_data(client, register_and_login):
    """GET /api/v1/chatbot/sessions/:id returns messages with token/cost fields."""
    register_and_login("chatbot_cost_fields")
    session_id = client.post("/api/v1/chatbot/sessions", json={"title": "Cost test"}).json()["data"]["id"]

    client.post(f"/api/v1/chatbot/sessions/{session_id}/messages", json={"message": "Hello AI"})
    resp = client.get(f"/api/v1/chatbot/sessions/{session_id}")
    data = resp.json()["data"]

    assert "messages" in data
    assert len(data["messages"]) == 2
    ai_msg = data["messages"][1]
    assert ai_msg["role"] == "assistant"
    assert ai_msg["content"]
    assert ai_msg["input_tokens"] is not None
    assert ai_msg["output_tokens"] is not None
    assert ai_msg["cost_usd"] is not None
    assert ai_msg["model_name"] is not None


def test_session_isolation_user_a_cannot_see_user_b_sessions(client):
    """User A's sessions are not visible to User B."""
    client.post("/api/v1/auth/register", json={
        "username": "chatbot_user_a", "email": "usera@test.com", "password": "Test1234!"
    })
    client.post("/api/v1/chatbot/sessions", json={"title": "User A session"})

    client.post("/api/v1/auth/register", json={
        "username": "chatbot_user_b", "email": "userb@test.com", "password": "Test1234!"
    })
    resp = client.get("/api/v1/chatbot/sessions")
    assert resp.status_code == 200
    sessions = resp.json()["data"]
    titles = [s["title"] for s in sessions]
    assert "User A session" not in titles