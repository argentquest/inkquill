"""Integration tests for admin API flows and permission denial cases."""

from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models.user import User
from app.models.cta_content import CTAContent
from app.models.user_account import UserAccount
from app.models.user_transaction import UserTransaction, TransactionType


pytestmark = pytest.mark.integration


def _get_access_token(client, username: str, password: str) -> str:
    response = client.post(
        "/api/v1/auth/token",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["data"]["access_token"]


class TestAdminCTAIntegration:
    def test_admin_can_list_ctas(self, client, register_and_login, run_db):
        admin_creds, _ = register_and_login("actaadmin")
        admin_token = _get_access_token(client, admin_creds["username"], admin_creds["password"])
        headers = {"Authorization": f"Bearer {admin_token}"}

        def promote_admin(session):
            async def _inner():
                user = (
                    await session.execute(select(User).where(User.username == admin_creds["username"]))
                ).scalar_one()
                user.is_admin = True
                await session.commit()

            return _inner()

        run_db(promote_admin)

        response = client.get("/api/v1/admin/cta-content?include_inactive=true", headers=headers)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["success"] is True
        assert isinstance(body["data"], list)

    def test_non_admin_cannot_list_ctas(self, client, register_and_login):
        creds, _ = register_and_login("actauser")
        token = _get_access_token(client, creds["username"], creds["password"])
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/admin/cta-content?include_inactive=true", headers=headers)
        assert response.status_code == 403, response.text

    def test_non_admin_cannot_toggle_cta(self, client, register_and_login, run_db):
        user_creds, _ = register_and_login("ctatoggleuser")
        user_token = _get_access_token(client, user_creds["username"], user_creds["password"])
        headers = {"Authorization": f"Bearer {user_token}"}

        def seed_cta(session):
            async def _inner():
                cta = CTAContent(
                    title="Test CTA",
                    position="home_hero",
                    style="gradient",
                    is_active=True,
                )
                session.add(cta)
                await session.commit()
                await session.refresh(cta)
                return cta.id

            return _inner()

        cta_id = run_db(seed_cta)

        response = client.post(f"/api/v1/admin/cta-content/{cta_id}/toggle-active", headers=headers)
        assert response.status_code == 403, response.text

    def test_non_admin_cannot_delete_cta(self, client, register_and_login, run_db):
        user_creds, _ = register_and_login("ctadeleteuser")
        user_token = _get_access_token(client, user_creds["username"], user_creds["password"])
        headers = {"Authorization": f"Bearer {user_token}"}

        def seed_cta(session):
            async def _inner():
                cta = CTAContent(title="Delete CTA", position="footer", style="simple", is_active=True)
                session.add(cta)
                await session.commit()
                await session.refresh(cta)
                return cta.id

            return _inner()

        cta_id = run_db(seed_cta)

        response = client.delete(f"/api/v1/admin/cta-content/{cta_id}", headers=headers)
        assert response.status_code == 403, response.text


class TestAdminMaintenanceIntegration:
    def test_admin_can_enable_maintenance(self, client, register_and_login, run_db):
        admin_creds, _ = register_and_login("maintadmin")
        admin_token = _get_access_token(client, admin_creds["username"], admin_creds["password"])
        headers = {"Authorization": f"Bearer {admin_token}"}

        def promote_admin(session):
            async def _inner():
                user = (
                    await session.execute(select(User).where(User.username == admin_creds["username"]))
                ).scalar_one()
                user.is_admin = True
                await session.commit()

            return _inner()

        run_db(promote_admin)

        response = client.post(
            "/api/v1/maintenance/enable?message=Upgrade+in+progress&duration_minutes=15",
            headers=headers,
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["success"] is True

    def test_non_admin_cannot_enable_maintenance(self, client, register_and_login):
        creds, _ = register_and_login("maintuser")
        token = _get_access_token(client, creds["username"], creds["password"])
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            "/api/v1/maintenance/enable?message=Upgrade&duration_minutes=5",
            headers=headers,
        )
        assert response.status_code == 403, response.text

    def test_non_admin_cannot_disable_maintenance(self, client, register_and_login):
        creds, _ = register_and_login("maintuser2")
        token = _get_access_token(client, creds["username"], creds["password"])
        headers = {"Authorization": f"Bearer {token}"}

        response = client.post("/api/v1/maintenance/disable", headers=headers)
        assert response.status_code == 403, response.text

    def test_maintenance_status_is_public(self, client):
        response = client.get("/api/v1/maintenance/status")
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["success"] is True
        assert "enabled" in body["data"]


class TestAdminBillingIntegration:
    def test_admin_can_get_billing_dashboard(self, client, register_and_login, run_db):
        admin_creds, _ = register_and_login("billadmin")
        admin_token = _get_access_token(client, admin_creds["username"], admin_creds["password"])
        headers = {"Authorization": f"Bearer {admin_token}"}

        def promote_admin(session):
            async def _inner():
                user = (
                    await session.execute(select(User).where(User.username == admin_creds["username"]))
                ).scalar_one()
                user.is_admin = True
                await session.commit()

            return _inner()

        run_db(promote_admin)

        response = client.get("/api/v1/admin/billing/dashboard", headers=headers)
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["success"] is True

    def test_non_admin_cannot_get_billing_dashboard(self, client, register_and_login):
        creds, _ = register_and_login("billuser")
        token = _get_access_token(client, creds["username"], creds["password"])
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/v1/admin/billing/dashboard", headers=headers)
        assert response.status_code == 403, response.text

    def test_non_admin_cannot_adjust_credits(self, client, register_and_login, run_db):
        admin_creds, _ = register_and_login("billadmin2")
        user_creds, _ = register_and_login("billtarget")
        admin_token = _get_access_token(client, admin_creds["username"], admin_creds["password"])
        headers = {"Authorization": f"Bearer {admin_token}"}

        def setup(session):
            async def _inner():
                admin_user = (
                    await session.execute(select(User).where(User.username == admin_creds["username"]))
                ).scalar_one()
                admin_user.is_admin = True
                await session.commit()
                user = (
                    await session.execute(select(User).where(User.username == user_creds["username"]))
                ).scalar_one()
                return user.id

            return _inner()

        target_user_id = run_db(setup)

        user_token = _get_access_token(client, user_creds["username"], user_creds["password"])
        user_headers = {"Authorization": f"Bearer {user_token}"}

        response = client.post(
            "/api/v1/admin/billing/adjust-credits",
            json={"user_id": target_user_id, "amount": "50.0000", "description": "Test adjustment"},
            headers=user_headers,
        )
        assert response.status_code == 403, response.text


class TestAdminUsersIntegration:
    def test_admin_can_list_users(self, client, register_and_login, run_db):
        admin_creds, _ = register_and_login("usersadmin")
        admin_token = _get_access_token(client, admin_creds["username"], admin_creds["password"])
        headers = {"Authorization": f"Bearer {admin_token}"}

        def promote_admin(session):
            async def _inner():
                user = (
                    await session.execute(select(User).where(User.username == admin_creds["username"]))
                ).scalar_one()
                user.is_admin = True
                await session.commit()

            return _inner()

        run_db(promote_admin)

        response = client.get("/api/v1/users/?limit=100", headers=headers)
        assert response.status_code == 200, response.text

    def test_non_admin_cannot_toggle_user_active(self, client, register_and_login, run_db):
        admin_creds, _ = register_and_login("toggleadmin")
        user_creds, _ = register_and_login("toggletarget")
        admin_token = _get_access_token(client, admin_creds["username"], admin_creds["password"])
        headers = {"Authorization": f"Bearer {admin_token}"}

        def setup(session):
            async def _inner():
                admin_user = (
                    await session.execute(select(User).where(User.username == admin_creds["username"]))
                ).scalar_one()
                admin_user.is_admin = True
                await session.commit()
                user = (
                    await session.execute(select(User).where(User.username == user_creds["username"]))
                ).scalar_one()
                return user.id

            return _inner()

        target_user_id = run_db(setup)

        user_token = _get_access_token(client, user_creds["username"], user_creds["password"])
        user_headers = {"Authorization": f"Bearer {user_token}"}

        response = client.patch(f"/api/v1/users/{target_user_id}/toggle-active", headers=user_headers)
        assert response.status_code == 403, response.text