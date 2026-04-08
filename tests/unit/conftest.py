"""Shared fixtures for isolated, mock-based unit tests."""

from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Callable
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.deps import (
    get_current_active_user,
    get_current_active_user_from_bearer_token,
    get_current_user,
    get_current_user_with_anonymous_support,
    get_current_user_from_bearer_token,
    get_db_session,
)


@pytest.fixture
def mock_user() -> SimpleNamespace:
    """Return a reusable authenticated user object for unit tests."""
    return SimpleNamespace(
        id=1,
        username="unit_user",
        email="unit@example.com",
        is_active=True,
        is_admin=False,
        bonus1=False,
        bonus2=False,
        bonus3=False,
        bonus4=False,
        bonus5=False,
        bonus6=False,
        bonus7=False,
        bonus8=False,
        bonus9=False,
        bonus10=False,
        interview_data=None,
        created_at=datetime.now(UTC),
    )


@pytest.fixture
def mock_admin_user(mock_user: SimpleNamespace) -> SimpleNamespace:
    """Return an admin user object for unit tests that need admin auth."""
    mock_user.is_admin = True
    return mock_user


@pytest.fixture
def mock_db_session() -> AsyncMock:
    """Return a mock async DB session."""
    db = AsyncMock()
    db.commit = AsyncMock()
    db.rollback = AsyncMock()
    db.refresh = AsyncMock()
    db.execute = AsyncMock()
    db.add = Mock()
    return db


@pytest.fixture
def unit_client_factory(
    mock_user: SimpleNamespace,
    mock_db_session: AsyncMock,
) -> Callable:
    """Create a TestClient with dependency overrides for unit tests."""

    def _create(
        *routers,
        router_prefix: str = "",
        user_override=None,
        raise_server_exceptions: bool = True,
    ) -> TestClient:
        app = FastAPI()

        for router in routers:
            app.include_router(router, prefix=router_prefix)

        active_user = user_override if user_override is not None else mock_user

        async def _db_override():
            yield mock_db_session

        app.dependency_overrides[get_db_session] = _db_override
        app.dependency_overrides[get_current_user] = lambda: active_user
        app.dependency_overrides[get_current_user_with_anonymous_support] = lambda: active_user
        app.dependency_overrides[get_current_active_user] = lambda: active_user
        app.dependency_overrides[get_current_user_from_bearer_token] = lambda: active_user
        app.dependency_overrides[get_current_active_user_from_bearer_token] = lambda: active_user

        return TestClient(app, raise_server_exceptions=raise_server_exceptions)

    return _create
