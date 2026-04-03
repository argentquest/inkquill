"""Mock-based unit tests for auth router endpoints."""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.routers.auth import router


pytestmark = pytest.mark.unit


def test_token_endpoint_success_returns_api_response(unit_client_factory):
    """`POST /api/v1/auth/token` returns wrapped bearer tokens."""
    client = unit_client_factory(router, router_prefix="/api/v1")

    user = SimpleNamespace(
        id=10,
        username="token_user",
        hashed_password="hashed",
        is_active=True,
    )

    refresh_row = SimpleNamespace(token="refresh_token_value")

    with patch("app.routers.auth.crud_user.get_user_by_username", new=AsyncMock(return_value=user)), patch(
        "app.routers.auth.security.verify_password", return_value=True
    ), patch("app.routers.auth.security.create_access_token", return_value="access_token_value"), patch(
        "app.crud.refresh_token.refresh_token_crud.create", new=AsyncMock(return_value=refresh_row)
    ):
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "token_user", "password": "password123"},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"] == "access_token_value"
    assert body["data"]["refresh_token"] == "refresh_token_value"
    assert body["data"]["token_type"] == "bearer"


def test_token_endpoint_rejects_invalid_credentials(unit_client_factory):
    """`POST /api/v1/auth/token` returns 401 for bad credentials."""
    client = unit_client_factory(router, router_prefix="/api/v1")

    with patch("app.routers.auth.crud_user.get_user_by_username", new=AsyncMock(return_value=None)):
        response = client.post(
            "/api/v1/auth/token",
            data={"username": "bad_user", "password": "bad_password"},
        )

    assert response.status_code == 401


def test_refresh_endpoint_success(unit_client_factory):
    """`POST /api/v1/auth/refresh` returns a new wrapped access token."""
    client = unit_client_factory(router, router_prefix="/api/v1")

    refresh_row = SimpleNamespace(
        token="valid_refresh_token",
        user_id=10,
        is_active=True,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        is_expired=False,
    )
    user = SimpleNamespace(id=10, username="token_user", is_active=True)

    with patch("app.crud.refresh_token.refresh_token_crud.get_by_token", new=AsyncMock(return_value=refresh_row)), patch(
        "app.crud.refresh_token.refresh_token_crud.update_last_used", new=AsyncMock(return_value=refresh_row)
    ), patch("app.routers.auth.crud_user.get_user", new=AsyncMock(return_value=user)), patch(
        "app.routers.auth.security.create_access_token", return_value="new_access_token_value"
    ):
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "valid_refresh_token"},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["access_token"] == "new_access_token_value"
    assert body["data"]["token_type"] == "bearer"


def test_refresh_endpoint_rejects_unknown_token(unit_client_factory):
    """`POST /api/v1/auth/refresh` returns 401 for unknown token."""
    client = unit_client_factory(router, router_prefix="/api/v1")

    with patch("app.crud.refresh_token.refresh_token_crud.get_by_token", new=AsyncMock(return_value=None)):
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "missing_token"},
        )

    assert response.status_code == 401
