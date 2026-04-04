import pytest
from sqlalchemy import select

from app.core.security import get_password_hash
from app.models.refresh_token import RefreshToken
from app.models.user import User


pytestmark = pytest.mark.integration


def test_cookie_login_works_for_seeded_admin_and_new_user(client, make_user_payload, run_db):
    admin_password = "password123"

    def ensure_seeded_admin_can_login(session):
        async def _inner():
            admin = (
                await session.execute(select(User).where(User.username == "admin"))
            ).scalar_one()
            admin.is_admin = True
            admin.is_active = True
            admin.hashed_password = get_password_hash(admin_password)
            await session.commit()

        return _inner()

    run_db(ensure_seeded_admin_can_login)

    client.cookies.clear()
    admin_login_response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": admin_password},
    )
    assert admin_login_response.status_code == 200, admin_login_response.text
    assert "access_token" in admin_login_response.cookies

    admin_me_response = client.get("/api/v1/users/me")
    assert admin_me_response.status_code == 200, admin_me_response.text
    admin_body = admin_me_response.json()
    assert admin_body["success"] is True
    assert admin_body["data"]["username"] == "admin"
    assert admin_body["data"]["is_admin"] is True

    new_user_payload = make_user_payload("loginflow")
    register_response = client.post("/api/v1/auth/register", json=new_user_payload)
    assert register_response.status_code == 201, register_response.text

    client.cookies.clear()
    new_user_login_response = client.post(
        "/api/v1/auth/login",
        data={
            "username": new_user_payload["username"],
            "password": new_user_payload["password"],
        },
    )
    assert new_user_login_response.status_code == 200, new_user_login_response.text
    assert "access_token" in new_user_login_response.cookies

    new_user_me_response = client.get("/api/v1/users/me")
    assert new_user_me_response.status_code == 200, new_user_me_response.text
    new_user_body = new_user_me_response.json()
    assert new_user_body["success"] is True
    assert new_user_body["data"]["username"] == new_user_payload["username"]
    assert new_user_body["data"]["email"] == new_user_payload["email"]
    assert new_user_body["data"]["is_admin"] is False


def test_register_token_refresh_and_read_current_user(client, register_and_login, run_db):
    payload, register_response = register_and_login("authflow")
    body = register_response.json()

    assert body["success"] is True
    assert body["data"]["username"] == payload["username"]
    assert "access_token" in register_response.cookies

    me_response = client.get("/api/v1/users/me")
    assert me_response.status_code == 200, me_response.text
    me_body = me_response.json()
    assert me_body["success"] is True
    assert me_body["data"]["username"] == payload["username"]
    assert me_body["data"]["email"] == payload["email"]

    token_response = client.post(
        "/api/v1/auth/token",
        data={"username": payload["username"], "password": payload["password"]},
    )
    assert token_response.status_code == 200, token_response.text
    token_body = token_response.json()
    assert token_body["success"] is True
    assert token_body["data"]["access_token"]
    assert token_body["data"]["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token_body["data"]["refresh_token"]},
    )
    assert refresh_response.status_code == 200, refresh_response.text
    refresh_body = refresh_response.json()
    assert refresh_body["success"] is True
    assert refresh_body["data"]["access_token"]

    bearer_me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token_body['data']['access_token']}"},
    )
    assert bearer_me_response.status_code == 200, bearer_me_response.text
    assert bearer_me_response.json()["data"]["username"] == payload["username"]

    def fetch_user_state(session):
        async def _inner():
            user = (
                await session.execute(select(User).where(User.username == payload["username"]))
            ).scalar_one()
            refresh_tokens = (
                await session.execute(
                    select(RefreshToken).where(RefreshToken.user_id == user.id)
                )
            ).scalars().all()
            return {
                "user_id": user.id,
                "is_active": user.is_active,
                "auth_provider": user.auth_provider,
                "refresh_token_count": len(refresh_tokens),
            }

        return _inner()

    state = run_db(fetch_user_state)
    assert state["is_active"] is True
    assert state["auth_provider"] == "local"
    assert state["refresh_token_count"] >= 1


def test_admin_can_list_all_users(client, register_and_login, run_db):
    admin_payload, _ = register_and_login("adminuser")
    user_payload, _ = register_and_login("regularuser")

    def promote_admin(session):
        async def _inner():
            admin = (
                await session.execute(select(User).where(User.username == admin_payload["username"]))
            ).scalar_one()
            admin.is_admin = True
            await session.commit()

        return _inner()

    run_db(promote_admin)

    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": admin_payload["username"], "password": admin_payload["password"]},
    )
    token = login_response.json()["data"]["access_token"]

    users_response = client.get(
        "/api/v1/users/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert users_response.status_code == 200, users_response.text
    users_body = users_response.json()
    assert users_body["success"] is True
    usernames = {user["username"] for user in users_body["data"]}
    assert admin_payload["username"] in usernames
    assert user_payload["username"] in usernames


def test_user_can_update_current_profile(client, register_and_login, run_db):
    payload, _ = register_and_login("profileflow")

    update_response = client.put(
        "/api/v1/users/me",
        json={
            "display_name": "Profile Flow Writer",
            "email": "profileflow.updated@example.com",
        },
    )
    assert update_response.status_code == 200, update_response.text
    update_body = update_response.json()
    assert update_body["success"] is True
    assert update_body["data"]["display_name"] == "Profile Flow Writer"
    assert update_body["data"]["email"] == "profileflow.updated@example.com"

    me_response = client.get("/api/v1/users/me")
    assert me_response.status_code == 200, me_response.text
    assert me_response.json()["data"]["display_name"] == "Profile Flow Writer"
    assert me_response.json()["data"]["email"] == "profileflow.updated@example.com"

    def fetch_user_state(session):
        async def _inner():
            user = (
                await session.execute(select(User).where(User.username == payload["username"]))
            ).scalar_one()
            return {
                "display_name": user.display_name,
                "email": user.email,
            }

        return _inner()

    state = run_db(fetch_user_state)
    assert state["display_name"] == "Profile Flow Writer"
    assert state["email"] == "profileflow.updated@example.com"
