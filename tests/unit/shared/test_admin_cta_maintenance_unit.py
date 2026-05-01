"""Unit tests for admin CTA, maintenance, and impersonation routers."""

from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.routers.admin_cta import router as admin_cta_router
from app.routers.maintenance import router as maintenance_router
from app.routers.users import router as users_router


pytestmark = pytest.mark.unit


def _cta():
    return SimpleNamespace(
        id=7,
        title="Test CTA",
        subtitle="Test subtitle",
        position="home_hero",
        style="gradient",
        is_active=True,
        sort_order=0,
        primary_button_text="Get Started",
        primary_button_url="/signup",
        show_for_anonymous=True,
        show_for_authenticated=True,
    )


def _cta_dict():
    return {
        "id": 7,
        "title": "Test CTA",
        "subtitle": "Test subtitle",
        "position": "home_hero",
        "style": "gradient",
        "is_active": True,
        "sort_order": 0,
        "primary_button_text": "Get Started",
        "primary_button_url": "/signup",
        "show_for_anonymous": True,
        "show_for_authenticated": True,
    }


def test_admin_cta_get_all_returns_wrapped_list(unit_client_factory, mock_admin_user):
    """GET /admin/cta-content returns success=true with a list of CTA dicts."""
    client = unit_client_factory(admin_cta_router, router_prefix="/api/v1", user_override=mock_admin_user)

    with patch("app.routers.admin_cta.crud_cta.get_all_ctas", new=AsyncMock(return_value=[])):
        response = client.get("/api/v1/admin/cta-content?include_inactive=true")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)


def test_admin_cta_toggle_active_returns_is_active_and_message(unit_client_factory, mock_admin_user):
    """POST /admin/cta-content/{id}/toggle-active returns updated is_active flag."""
    client = unit_client_factory(admin_cta_router, router_prefix="/api/v1", user_override=mock_admin_user)

    cta = _cta()
    cta.is_active = False

    with patch("app.routers.admin_cta.crud_cta.toggle_cta_active_status", new=AsyncMock(return_value=cta)):
        response = client.post("/api/v1/admin/cta-content/7/toggle-active")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["is_active"] is False


def test_admin_cta_delete_returns_success(unit_client_factory, mock_admin_user):
    """DELETE /admin/cta-content/{id} returns success when CTA exists."""
    client = unit_client_factory(admin_cta_router, router_prefix="/api/v1", user_override=mock_admin_user)

    with patch("app.routers.admin_cta.crud_cta.delete_cta_content", new=AsyncMock(return_value=True)):
        response = client.delete("/api/v1/admin/cta-content/7")

    assert response.status_code == 200, response.text
    assert response.json()["success"] is True


def test_admin_cta_requires_admin_on_get(unit_client_factory, mock_user):
    """GET /admin/cta-content is rejected when user is not admin."""
    client = unit_client_factory(admin_cta_router, router_prefix="/api/v1", user_override=mock_user)

    response = client.get("/api/v1/admin/cta-content")

    assert response.status_code == 403, response.text


def test_admin_cta_requires_admin_on_toggle(unit_client_factory, mock_user):
    """POST /admin/cta-content/{id}/toggle-active is rejected when user is not admin."""
    client = unit_client_factory(admin_cta_router, router_prefix="/api/v1", user_override=mock_user)

    response = client.post("/api/v1/admin/cta-content/7/toggle-active")

    assert response.status_code == 403, response.text


def test_admin_cta_requires_admin_on_delete(unit_client_factory, mock_user):
    """DELETE /admin/cta-content/{id} is rejected when user is not admin."""
    client = unit_client_factory(admin_cta_router, router_prefix="/api/v1", user_override=mock_user)

    response = client.delete("/api/v1/admin/cta-content/7")

    assert response.status_code == 403, response.text


def test_maintenance_status_returns_enabled_flag(unit_client_factory, mock_admin_user):
    """GET /maintenance/status returns current maintenance state."""
    client = unit_client_factory(maintenance_router, router_prefix="/api/v1", user_override=mock_admin_user)

    with patch(
        "app.routers.maintenance.MaintenanceManager.get_maintenance_status",
        return_value={"enabled": True, "message": "Upgrade in progress", "estimated_end_time": None},
    ):
        response = client.get("/api/v1/maintenance/status")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["enabled"] is True


def test_maintenance_enable_requires_admin(unit_client_factory, mock_user):
    """POST /maintenance/enable is rejected when user is not admin."""
    client = unit_client_factory(maintenance_router, router_prefix="/api/v1", user_override=mock_user)

    response = client.post("/api/v1/maintenance/enable?message=Upgrade&duration_minutes=5")

    assert response.status_code == 403, response.text


def test_maintenance_enable_calls_set_maintenance_mode(unit_client_factory, mock_admin_user):
    """POST /maintenance/enable calls MaintenanceManager.set_maintenance_mode with correct args."""
    client = unit_client_factory(maintenance_router, router_prefix="/api/v1", user_override=mock_admin_user)

    with patch("app.routers.maintenance.MaintenanceManager.set_maintenance_mode") as set_mode_mock:
        response = client.post("/api/v1/maintenance/enable?message=Upgrade&duration_minutes=10")

    assert response.status_code == 200, response.text
    set_mode_mock.assert_called_once_with(enabled=True, message="Upgrade", duration_minutes=10)


def test_maintenance_disable_requires_admin(unit_client_factory, mock_user):
    """POST /maintenance/disable is rejected when user is not admin."""
    client = unit_client_factory(maintenance_router, router_prefix="/api/v1", user_override=mock_user)

    response = client.post("/api/v1/maintenance/disable")

    assert response.status_code == 403, response.text


def test_maintenance_disable_calls_set_maintenance_mode(unit_client_factory, mock_admin_user):
    """POST /maintenance/disable calls MaintenanceManager.set_maintenance_mode with enabled=False."""
    client = unit_client_factory(maintenance_router, router_prefix="/api/v1", user_override=mock_admin_user)

    with patch("app.routers.maintenance.MaintenanceManager.set_maintenance_mode") as set_mode_mock:
        response = client.post("/api/v1/maintenance/disable")

    assert response.status_code == 200, response.text
    set_mode_mock.assert_called_once_with(enabled=False)