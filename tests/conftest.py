# tests/conftest.py

"""
Pytest configuration and shared fixtures for API endpoint testing.
Provides common setup for testing FastAPI endpoints with ApiResponse wrappers.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Generator
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.schemas.base import ApiResponse, ApiError
from app.models.user import User


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


def create_mock_story(user_id: int = 1):
    """Create a mock story for testing."""
    story = MagicMock()
    story.id = 1
    story.title = "Test Story"
    story.description = "A test story description"
    story.published = False
    story.user_id = user_id
    story.created_at = datetime.now()
    return story


def create_mock_world(user_id: int = 1):
    """Create a mock world for testing."""
    world = MagicMock()
    world.id = 1
    world.name = "Test World"
    world.description = "A test world description"
    world.user_id = user_id
    return world


def create_mock_character(world_id: int = 1):
    """Create a mock character for testing."""
    char = MagicMock()
    char.id = 1
    char.name = "Test Character"
    char.backstory = "A test character backstory"
    char.world_id = world_id
    return char


@pytest.fixture
def mock_authenticated_user() -> User:
    """Create a mock authenticated user for testing."""
    user = MagicMock(spec=User)
    user.id = 1
    user.username = "testuser"
    user.email = "test@example.com"
    user.is_active = True
    user.is_admin = False
    user.display_name = "Test User"
    user.created_at = datetime.utcnow()
    return user


@pytest.fixture
def mock_admin_user() -> User:
    """Create a mock admin user for testing."""
    user = MagicMock(spec=User)
    user.id = 2
    user.username = "admin"
    user.email = "admin@example.com"
    user.is_active = True
    user.is_admin = True
    user.display_name = "Admin User"
    user.created_at = datetime.utcnow()
    return user


@pytest.fixture
def api_response_success():
    """Standard success ApiResponse for testing."""
    return {
        "success": True,
        "data": {"message": "Operation successful"},
        "errors": None,
        "meta": None
    }


@pytest.fixture
def api_response_error():
    """Standard error ApiResponse for testing."""
    return {
        "success": False,
        "data": None,
        "errors": [{"code": "NOT_FOUND", "message": "Resource not found"}],
        "meta": None
    }


class TestClientFactory:
    """Factory for creating FastAPI test clients with router setup."""

    @staticmethod
    def create_client_with_routers(*routers) -> TestClient:
        """Create a test client with specified routers."""
        app = FastAPI(title="Test API", version="1.0.0")

        for router in routers:
            prefix = getattr(router, 'prefix', '')
            tags = getattr(router, 'tags', [])
            app.include_router(router, prefix=prefix, tags=tags)

        return TestClient(app)


@pytest.fixture
def test_client_factory():
    """Fixture providing test client factory."""
    return TestClientFactory()


def assert_api_response_format(response_data: dict, expected_success: bool = True):
    """
    Assert that response follows ApiResponse format.

    Args:
        response_data: The JSON response data
        expected_success: Whether the response should indicate success
    """
    assert isinstance(response_data, dict), "Response must be a dictionary"
    assert "success" in response_data, "Response must have 'success' field"
    assert "data" in response_data, "Response must have 'data' field"
    assert "errors" in response_data, "Response must have 'errors' field"
    assert "meta" in response_data, "Response must have 'meta' field"

    assert response_data["success"] is expected_success

    if expected_success:
        # Success response
        assert response_data["data"] is not None, "Success response must have data"
        assert response_data["errors"] is None or len(response_data["errors"] or []) == 0

    if not expected_success:
        # Error response
        assert response_data["errors"] is not None and len(response_data["errors"]) > 0


@pytest.fixture(autouse=True)
def mock_external_dependencies():
    """Mock external dependencies to avoid network calls during testing."""
    with pytest.MonkeyPatch().context() as m:
        # Mock Azure services
        m.setattr("app.core.azure_deps.get_blob_service_client", MagicMock())

        # Mock Semantic Kernel
        m.setattr("app.services.semantic_kernel_setup.get_kernel", MagicMock())

        yield m