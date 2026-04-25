"""Integration tests for family join flow, member management, and admin family operations."""
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.services.email_service import get_email_service

pytestmark = pytest.mark.integration


def _make_client(app_instance):
    """Create a fresh TestClient (new cookie jar = new session)."""
    return TestClient(app_instance, raise_server_exceptions=True)


def _register(client, prefix="member"):
    payload = {
        "username": f"{prefix}_{uuid4().hex[:8]}",
        "email": f"{prefix}_{uuid4().hex[:8]}@example.com",
        "password": "integration-pass-123",
        "display_name": f"{prefix.title()} User",
        "terms_accepted": True,
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 201, resp.text
    return payload, resp


def _get_join_code(client):
    """Trigger family creation and return the family join code via a patient."""
    resp = client.get("/api/v1/care-circle/family/patients")
    assert resp.status_code == 200
    patients = resp.json()["data"]
    assert len(patients) > 0, "Expected seed patients to exist"
    return patients[0]["joinCode"]


# ---------------------------------------------------------------------------
# Join flow
# ---------------------------------------------------------------------------

def test_join_request_with_valid_code(client, register_and_login, app_instance):
    """A registered user can submit a join request using a valid join code."""
    register_and_login("owner_join")
    join_code = _get_join_code(client)

    second_client = _make_client(app_instance)
    _register(second_client, "member_join")
    resp = second_client.post("/api/v1/care-circle/family/join", json={"join_code": join_code})
    assert resp.status_code == 201
    data = resp.json()["data"]
    assert data["status"] == "pending"
    assert "family_name" in data


def test_join_request_with_invalid_code(client, register_and_login):
    """A bad join code returns 400."""
    register_and_login("owner_bad_code")
    resp = client.post("/api/v1/care-circle/family/join", json={"join_code": "XXXXXX"})
    assert resp.status_code == 400


def test_duplicate_join_request_returns_400(client, register_and_login, app_instance):
    """Submitting a second pending request for the same family returns 400."""
    register_and_login("owner_dup")
    join_code = _get_join_code(client)

    second_client = _make_client(app_instance)
    _register(second_client, "member_dup")
    second_client.post("/api/v1/care-circle/family/join", json={"join_code": join_code})
    resp = second_client.post("/api/v1/care-circle/family/join", json={"join_code": join_code})
    assert resp.status_code == 400
    assert "pending" in resp.json()["detail"].lower()


def test_already_owner_join_request_returns_400(client, register_and_login):
    """The owner trying to join their own family returns 400."""
    register_and_login("owner_already")
    join_code = _get_join_code(client)
    resp = client.post("/api/v1/care-circle/family/join", json={"join_code": join_code})
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Owner: list and resolve join requests
# ---------------------------------------------------------------------------

def test_owner_can_list_join_requests(client, register_and_login, app_instance):
    register_and_login("owner_list")
    join_code = _get_join_code(client)

    second_client = _make_client(app_instance)
    _register(second_client, "req_list_member")
    second_client.post("/api/v1/care-circle/family/join", json={"join_code": join_code})

    resp = client.get("/api/v1/care-circle/family/join-requests")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "username" in data[0]


def test_owner_can_get_family_summary(client, register_and_login):
    register_and_login("owner_summary")
    join_code = _get_join_code(client)

    resp = client.get("/api/v1/care-circle/family/owner-summary")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["join_code"] == join_code
    assert data["active_member_count"] >= 1
    assert data["pending_request_count"] == 0


def test_owner_can_send_invite_email(client, register_and_login, app_instance):
    register_and_login("owner_invite")
    join_code = _get_join_code(client)

    class RecordingEmailService:
        def __init__(self):
            self.calls = []

        async def send_care_circle_invite_email(self, **kwargs):
            self.calls.append(kwargs)
            return True

    recorder = RecordingEmailService()
    app_instance.dependency_overrides[get_email_service] = lambda: recorder
    try:
        resp = client.post("/api/v1/care-circle/family/invite-email", json={"email": "invitee@example.com"})
    finally:
        app_instance.dependency_overrides.pop(get_email_service, None)

    assert resp.status_code == 201, resp.text
    data = resp.json()["data"]
    assert data["sent"] is True
    assert data["email"] == "invitee@example.com"
    assert data["join_code"] == join_code
    assert len(recorder.calls) == 1
    assert recorder.calls[0]["recipient_email"] == "invitee@example.com"
    assert recorder.calls[0]["join_code"] == join_code


def test_owner_can_approve_request(client, register_and_login, app_instance):
    register_and_login("owner_approve")
    join_code = _get_join_code(client)

    second_client = _make_client(app_instance)
    _register(second_client, "req_approve_member")
    second_client.post("/api/v1/care-circle/family/join", json={"join_code": join_code})

    requests = client.get("/api/v1/care-circle/family/join-requests").json()["data"]
    membership_id = requests[0]["id"]

    approve_resp = client.put(f"/api/v1/care-circle/family/join-requests/{membership_id}/approve")
    assert approve_resp.status_code == 200
    assert approve_resp.json()["data"]["status"] == "active"

    after = client.get("/api/v1/care-circle/family/join-requests").json()["data"]
    assert not any(r["id"] == membership_id for r in after)


def test_owner_can_reject_request(client, register_and_login, app_instance):
    register_and_login("owner_reject")
    join_code = _get_join_code(client)

    second_client = _make_client(app_instance)
    _register(second_client, "req_reject_member")
    second_client.post("/api/v1/care-circle/family/join", json={"join_code": join_code})

    requests = client.get("/api/v1/care-circle/family/join-requests").json()["data"]
    membership_id = requests[0]["id"]

    reject_resp = client.put(f"/api/v1/care-circle/family/join-requests/{membership_id}/reject")
    assert reject_resp.status_code == 200
    assert reject_resp.json()["data"]["status"] == "rejected"


def test_approve_nonexistent_request_returns_400(client, register_and_login):
    register_and_login("owner_ghost")
    _get_join_code(client)
    resp = client.put("/api/v1/care-circle/family/join-requests/999999/approve")
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# Owner: list and remove active members
# ---------------------------------------------------------------------------

def test_owner_can_list_members_after_approval(client, register_and_login, app_instance):
    register_and_login("owner_members")
    join_code = _get_join_code(client)

    second_client = _make_client(app_instance)
    _register(second_client, "active_member")
    second_client.post("/api/v1/care-circle/family/join", json={"join_code": join_code})

    requests = client.get("/api/v1/care-circle/family/join-requests").json()["data"]
    client.put(f"/api/v1/care-circle/family/join-requests/{requests[0]['id']}/approve")

    members_resp = client.get("/api/v1/care-circle/family/members")
    assert members_resp.status_code == 200
    members = members_resp.json()["data"]
    assert len(members) >= 1
    assert all("username" in m for m in members)


def test_owner_can_remove_member(client, register_and_login, app_instance):
    register_and_login("owner_remove")
    join_code = _get_join_code(client)

    second_client = _make_client(app_instance)
    _register(second_client, "remove_member")
    second_client.post("/api/v1/care-circle/family/join", json={"join_code": join_code})

    requests = client.get("/api/v1/care-circle/family/join-requests").json()["data"]
    membership_id = requests[0]["id"]
    client.put(f"/api/v1/care-circle/family/join-requests/{membership_id}/approve")

    remove_resp = client.delete(f"/api/v1/care-circle/family/members/{membership_id}")
    assert remove_resp.status_code == 200

    members = client.get("/api/v1/care-circle/family/members").json()["data"]
    assert not any(m["id"] == membership_id for m in members)


def test_empty_members_list_returns_empty(client, register_and_login):
    register_and_login("owner_empty")
    _get_join_code(client)
    resp = client.get("/api/v1/care-circle/family/members")
    assert resp.status_code == 200
    assert resp.json()["data"] == []


# ---------------------------------------------------------------------------
# is_family_owner flag
# ---------------------------------------------------------------------------

def test_owner_has_is_family_owner_true(client, register_and_login):
    register_and_login("flag_owner")
    _get_join_code(client)
    me = client.get("/api/v1/users/me").json()["data"]
    assert me["is_family_owner"] is True


def test_new_user_before_family_created_has_is_family_owner_false(client, register_and_login):
    register_and_login("flag_fresh")
    me = client.get("/api/v1/users/me").json()["data"]
    assert me["is_family_owner"] is False


# ---------------------------------------------------------------------------
# Admin: family management
# ---------------------------------------------------------------------------

def _register_admin(app_instance, run_db, prefix="admin_fam"):
    """Register a new user in a fresh client session and promote them to admin."""
    from sqlalchemy import select
    from app.models.user import User

    admin_client = _make_client(app_instance)
    payload, _ = _register(admin_client, prefix)
    username = payload["username"]

    async def promote(session):
        user = await session.scalar(select(User).where(User.username == username))
        user.is_admin = True
        await session.commit()

    run_db(promote)
    return admin_client


def test_admin_can_list_all_families(client, register_and_login, app_instance, run_db):
    register_and_login("admin_list_owner")
    _get_join_code(client)

    admin_client = _register_admin(app_instance, run_db, "admin_list")

    resp = admin_client.get("/api/v1/care-circle/admin/families")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all("name" in f for f in data)
    assert all("join_code" in f for f in data)


def test_non_admin_cannot_list_families(client, register_and_login):
    register_and_login("nonadmin_list")
    resp = client.get("/api/v1/care-circle/admin/families")
    assert resp.status_code == 403


def test_admin_can_disable_and_reenable_family(client, register_and_login, app_instance, run_db):
    register_and_login("disable_owner")
    join_code = _get_join_code(client)

    admin_client = _register_admin(app_instance, run_db, "admin_disable")
    families = admin_client.get("/api/v1/care-circle/admin/families").json()["data"]
    target = next((f for f in families if f["join_code"] == join_code), None)
    assert target is not None

    resp = admin_client.put(
        f"/api/v1/care-circle/admin/families/{target['id']}/disable",
        json={"disabled": True},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["is_disabled"] is True

    re_enable = admin_client.put(
        f"/api/v1/care-circle/admin/families/{target['id']}/disable",
        json={"disabled": False},
    )
    assert re_enable.status_code == 200
    assert re_enable.json()["data"]["is_disabled"] is False


def test_admin_can_delete_family(client, register_and_login, app_instance, run_db):
    register_and_login("delete_owner")
    join_code = _get_join_code(client)

    admin_client = _register_admin(app_instance, run_db, "admin_delete")
    families = admin_client.get("/api/v1/care-circle/admin/families").json()["data"]
    target = next((f for f in families if f["join_code"] == join_code), None)
    assert target is not None

    resp = admin_client.delete(f"/api/v1/care-circle/admin/families/{target['id']}")
    assert resp.status_code == 200

    after = admin_client.get("/api/v1/care-circle/admin/families").json()["data"]
    assert not any(f["id"] == target["id"] for f in after)


def test_disabled_family_blocks_join_requests(client, register_and_login, app_instance, run_db):
    register_and_login("disabled_join_owner")
    join_code = _get_join_code(client)

    admin_client = _register_admin(app_instance, run_db, "admin_block")
    families = admin_client.get("/api/v1/care-circle/admin/families").json()["data"]
    target = next((f for f in families if f["join_code"] == join_code), None)
    admin_client.put(
        f"/api/v1/care-circle/admin/families/{target['id']}/disable",
        json={"disabled": True},
    )

    member_client = _make_client(app_instance)
    _register(member_client, "blocked_member")
    resp = member_client.post("/api/v1/care-circle/family/join", json={"join_code": join_code})
    assert resp.status_code == 400
    assert "disabled" in resp.json()["detail"].lower()
