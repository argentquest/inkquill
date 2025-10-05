# tests/test_users_crud_complete.py

"""
Comprehensive tests for User Management API endpoints
Tests all CRUD operations with ApiResponse wrappers for React SPA compatibility
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.schemas.base import ApiResponse, ApiError
from app.schemas import user as user_schemas
from app.routers.users import router


class TestUserProfileEndpoints:
    """Test user profile and account management endpoints."""

    @pytest.mark.asyncio
    async def test_get_current_user_profile_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /users/me - Get current user profile successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.users.crud_user') as mock_crud_user:

            # Setup mocks
            mock_get_user.return_value = mock_authenticated_user
            mock_crud_user.get_user.return_value = mock_authenticated_user

            client = test_client_factory.create_client_with_routers(router)

            # Make request
            response = client.get("/users/me")

            # Assert response
            assert response.status_code == 200
            data = response.json()

            # Verify ApiResponse format
            assert data["success"] is True
            assert "data" in data
            assert data["data"]["username"] == "testuser"
            assert data["data"]["email"] == "test@example.com"

            # Verify mocks were called
            mock_get_user.assert_called_once()
            mock_crud_user.get_user.assert_called_once_with(mock_authenticated_user.id)

    @pytest.mark.asyncio
    async def test_get_current_user_profile_unauthenticated(self, test_client_factory):
        """Test GET /users/me - Unauthenticated request."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            mock_get_user.return_value = None

            client = test_client_factory.create_client_with_routers(router)

            response = client.get("/users/me")
            assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, test_client_factory, mock_authenticated_user):
        """Test PUT /users/me - Update user profile successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.users.crud_user') as mock_crud_user, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            # Setup mocks
            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            updated_user = Mock()
            updated_user.username = "updateduser"
            updated_user.display_name = "Updated User"
            mock_crud_user.update_user.return_value = updated_user

            client = test_client_factory.create_client_with_routers(router)

            update_data = {
                "display_name": "Updated User"
            }

            response = client.put("/users/me", json=update_data)

            assert response.status_code == 200
            data = response.json()

            # Verify ApiResponse format
            assert data["success"] is True
            assert data["data"]["username"] == "updateduser"
            assert data["data"]["display_name"] == "Updated User"

            # Verify CRUD was called with correct data
            mock_crud_user.update_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_user_profile_validation_error(self, test_client_factory, mock_authenticated_user):
        """Test PUT /users/me - Validation error on update."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.users.crud_user') as mock_crud_user:

            mock_get_user.return_value = mock_authenticated_user
            mock_crud_user.update_user.return_value = None

            client = test_client_factory.create_client_with_routers(router)

            update_data = {"display_name": "Valid Name"}
            response = client.put("/users/me", json=update_data)

            assert response.status_code == 404
            data = response.json()

            # Should still return ApiResponse format even for 404
            # (Note: HTTP status codes are handled separately from response format)
            assert "success" in data

    @pytest.mark.asyncio
    async def test_get_all_users_admin_only(self, test_client_factory, mock_admin_user):
        """Test GET /users - Admin can list all users."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.users.crud_user') as mock_crud_user:

            mock_get_user.return_value = mock_admin_user

            # Mock user list
            mock_users = [
                Mock(id=1, username="user1", email="user1@test.com"),
                Mock(id=2, username="user2", email="user2@test.com")
            ]
            mock_crud_user.get_multi.return_value = mock_users

            client = test_client_factory.create_client_with_routers(router)

            response = client.get("/users")

            assert response.status_code == 200
            data = response.json()

            # Verify ApiResponse format
            assert data["success"] is True
            assert len(data["data"]) == 2
            assert data["data"][0]["username"] == "user1"

    @pytest.mark.asyncio
    async def test_get_all_users_non_admin_forbidden(self, test_client_factory, mock_authenticated_user):
        """Test GET /users - Non-admin cannot list users."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            mock_get_user.return_value = mock_authenticated_user

            client = test_client_factory.create_client_with_routers(router)

            response = client.get("/users")
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, test_client_factory, mock_admin_user):
        """Test GET /users/{user_id} - Admin can get specific user."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.users.crud_user') as mock_crud_user:

            mock_get_user.return_value = mock_admin_user

            target_user = Mock()
            target_user.id = 3
            target_user.username = "targetuser"
            target_user.email = "target@test.com"
            mock_crud_user.get_user.return_value = target_user

            client = test_client_factory.create_client_with_routers(router)

            response = client.get("/users/3")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"]["username"] == "targetuser"

            mock_crud_user.get_user.assert_called_once_with(3)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, test_client_factory, mock_admin_user):
        """Test GET /users/{user_id} - User not found."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.users.crud_user') as mock_crud_user:

            mock_get_user.return_value = mock_admin_user
            mock_crud_user.get_user.return_value = None

            client = test_client_factory.create_client_with_routers(router)

            response = client.get("/users/999")

            assert response.status_code == 404
            data = response.json()
            # HTTPExceptions result in error responses
            assert "success" in data