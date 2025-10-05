# tests/test_api_endpoints.py

"""
Comprehensive unit tests for all API endpoints from REACT_MIGRATION_ANALYSIS.MD
Tests follow the migration requirements for React SPA compatibility
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, patch

from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.base import ApiResponse, ApiError
from app.schemas import user as schema_user


class TestAuthTokenEndpoint:
    """Test the NEW bearer token authentication endpoint"""

    @pytest.mark.asyncio
    async def test_post_auth_token_success(self):
        """
        Test successful token login for API clients
        This endpoint is NEW for React SPA migration
        """
        # Test setup follows React auth requirements:
        # - Returns Bearer tokens vs HttpOnly cookies
        # - Enables client-side token management
        # - Supports refresh token rotation

        with patch('app.routers.auth.crud_user') as mock_crud_user, \
             patch('app.routers.auth.security') as mock_security, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            # Mock user lookup
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'testuser'
            mock_user.is_active = True
            mock_crud_user.get_user_by_username.return_value = mock_user

            # Mock password verification
            mock_security.verify_password.return_value = True

            # Mock token creation
            mock_tokens = Mock()
            mock_security.create_access_token_and_refresh_token.return_value = mock_tokens

            # Mock database session
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Create test client
            from fastapi import FastAPI
            from app.routers.auth import router

            app = FastAPI()
            app.include_router(router, prefix="/auth", tags=["authentication"])
            client = TestClient(app)

            # Test successful login
            response = client.post(
                "/auth/token",
                data={"username": "testuser", "password": "password123"}
            )

            # Verify endpoint structure - NEW for React migration
            assert response.status_code == 200
            data = response.json()
            assert "success" in data
            assert data["success"] is True  # Should use ApiResponse wrapper
            assert "data" in data

            # Verify token response structure for React clients
            token_data = data["data"]
            assert "access_token" in token_data
            assert "refresh_token" in token_data
            assert "token_type" in token_data
            assert token_data["token_type"] == "bearer"

            # Verify mocks were called correctly
            mock_crud_user.get_user_by_username.assert_called_once_with(mock_db, username="testuser")
            mock_security.verify_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_post_auth_token_invalid_credentials(self):
        """Test token login with invalid credentials"""
        with patch('app.routers.auth.crud_user') as mock_crud_user, \
             patch('app.routers.auth.security') as mock_security:

            # Mock user not found
            mock_crud_user.get_user_by_username.return_value = None

            from fastapi import FastAPI
            from app.routers.auth import router

            app = FastAPI()
            app.include_router(router, prefix="/auth", tags=["authentication"])
            client = TestClient(app)

            response = client.post(
                "/auth/token",
                data={"username": "invalid", "password": "wrong"}
            )

            # Should return 401 for invalid credentials
            assert response.status_code == 401
            assert "WWW-Authenticate" in response.headers

    @pytest.mark.asyncio
    async def test_post_auth_token_inactive_user(self):
        """Test token login with inactive user account"""
        with patch('app.routers.auth.crud_user') as mock_crud_user, \
             patch('app.routers.auth.security') as mock_security:

            # Mock inactive user
            mock_user = Mock()
            mock_user.is_active = False
            mock_crud_user.get_user_by_username.return_value = mock_user

            from fastapi import FastAPI
            from app.routers.auth import router

            app = FastAPI()
            app.include_router(router, prefix="/auth", tags=["authentication"])
            client = TestClient(app)

            response = client.post(
                "/auth/token",
                data={"username": "inactive", "password": "password123"}
            )

            # Should return 400 for inactive account
            assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_post_auth_token_response_format(self):
        """Test that token endpoint uses proper ApiResponse format for React"""
        with patch('app.routers.auth.crud_user') as mock_crud_user, \
             patch('app.routers.auth.security') as mock_security, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            # Mock successful authentication
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = 'testuser'
            mock_user.is_active = True
            mock_crud_user.get_user_by_username.return_value = mock_user
            mock_security.verify_password.return_value = True

            # Mock token response
            mock_tokens = schema_user.UserTokenWithDetails(
                access_token="access_token_123",
                refresh_token="refresh_token_456",
                token_type="bearer",
                expires_in=3600,
                user=schema_user.UserRead(
                    id=1,
                    username="testuser",
                    email="test@example.com"
                )
            )
            mock_security.create_access_token_and_refresh_token.return_value = mock_tokens

            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            from fastapi import FastAPI
            from app.routers.auth import router

            app = FastAPI()
            app.include_router(router, prefix="/auth", tags=["authentication"])
            client = TestClient(app)

            response = client.post(
                "/auth/token",
                data={"username": "testuser", "password": "password123"}
            )

            assert response.status_code == 200
            data = response.json()

            # Verify ApiResponse format required for React clients
            assert data["success"] is True
            assert "data" in data
            assert "errors" in data
            assert "meta" in data

            # Verify token data structure
            token_response = data["data"]
            assert token_response["access_token"] == "access_token_123"
            assert token_response["refresh_token"] == "refresh_token_456"
            assert token_response["token_type"] == "bearer"
            assert "user" in token_response


class TestAuthRefreshEndpoint:
    """Test the NEW token refresh endpoint"""

    @pytest.mark.asyncio
    async def test_post_auth_refresh_success(self):
        """Test successful token refresh"""
        with patch('app.routers.auth.refresh_token_crud') as mock_crud, \
             patch('app.routers.auth.crud_user') as mock_user_crud, \
             patch('app.routers.auth.security') as mock_security, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            # Mock valid refresh token
            mock_token = Mock()
            mock_token.user_id = 1
            mock_crud.get_valid.return_value = mock_token

            # Mock valid user
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = "testuser"
            mock_user.is_active = True
            mock_user_crud.get_user.return_value = mock_user

            # Mock new token creation
            mock_new_tokens = schema_user.UserToken(
                access_token="new_access_token",
                refresh_token="new_refresh_token",
                token_type="bearer",
                expires_in=3600
            )
            mock_security.create_access_token_and_refresh_token.return_value = mock_new_tokens

            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            from fastapi import FastAPI
            from app.routers.auth import router

            app = FastAPI()
            app.include_router(router, prefix="/auth", tags=["authentication"])
            client = TestClient(app)

            response = client.post(
                "/auth/refresh",
                data={"refresh_token": "valid_refresh_token"}
            )

            assert response.status_code == 200
            data = response.json()

            # Verify ApiResponse format
            assert data["success"] is True
            assert "data" in data

    @pytest.mark.asyncio
    async def test_post_auth_refresh_invalid_token(self):
        """Test refresh with invalid/expired token"""
        with patch('app.routers.auth.refresh_token_crud') as mock_crud:

            # Mock invalid refresh token
            mock_crud.get_valid.return_value = None

            from fastapi import FastAPI
            from app.routers.auth import router

            app = FastAPI()
            app.include_router(router, prefix="/auth", tags=["authentication"])
            client = TestClient(app)

            response = client.post(
                "/auth/refresh",
                data={"refresh_token": "invalid_token"}
            )

            # Should return 401 for invalid refresh token
            assert response.status_code == 401


class TestAuthWsTicketEndpoint:
    """Test WebSocket ticket generation"""

    @pytest.mark.asyncio
    async def test_get_auth_ws_ticket(self):
        """Test WebSocket ticket generation for real-time features"""
        with patch('app.routers.auth.security') as mock_security, \
             patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.username = "testuser"
            mock_get_user.return_value = mock_user

            # Mock ticket creation
            mock_security.create_access_token.return_value = "ws_ticket_123"

            from fastapi import FastAPI
            from app.routers.auth import router

            app = FastAPI()
            app.include_router(router, prefix="/auth", tags=["authentication"])
            client = TestClient(app)

            response = client.get("/auth/ws-ticket")

            assert response.status_code == 200
            data = response.json()
            assert "ticket" in data
            assert "expires_at" in data
            assert data["ticket"] == "ws_ticket_123"


class TestDashboardSummaryEndpoint:
    """Test the new dashboard summary endpoint for React"""

    @pytest.mark.asyncio
    async def test_get_dashboard_summary(self):
        """Test dashboard summary endpoint required for React homepage"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.dashboard.crud_world') as mock_world_crud, \
             patch('app.routers.dashboard.crud_story') as mock_story_crud, \
             patch('app.routers.dashboard.crud_character') as mock_character_crud, \
             patch('app.routers.dashboard.crud_location') as mock_location_crud, \
             patch('app.routers.dashboard.crud_lore_item') as mock_lore_crud:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock database results (counts)
            mock_world_crud.count_worlds_by_user.return_value = 5
            mock_story_crud.count_stories_by_user.return_value = 12
            mock_character_crud.count_characters_by_user.return_value = 45
            mock_location_crud.count_locations_by_user.return_value = 8
            mock_lore_crud.count_lore_items_by_user.return_value = 15

            from fastapi import FastAPI
            from app.routers.dashboard import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/dashboard", tags=["dashboard"])
            client = TestClient(app)

            response = client.get("/api/v1/dashboard/summary")

            assert response.status_code == 200
            data = response.json()

            # Verify ApiResponse format
            assert data["success"] is True
            assert "data" in data

            # Verify dashboard data structure
            dashboard = data["data"]
            assert dashboard["summary"]["total_worlds"] == 5
            assert dashboard["summary"]["total_stories"] == 12
            assert dashboard["summary"]["total_characters"] == 45
            assert dashboard["summary"]["total_locations"] == 8
            assert dashboard["summary"]["total_lore_items"] == 15


class TestBatchCharacterEndpoints:
    """Test batch character operations for React efficiency"""

    @pytest.mark.asyncio
    async def test_post_batch_characters_create(self):
        """Test batch character creation for React bulk operations"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.batch.Character') as mock_character_model, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            # Mock user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock character creation - simulate successful saves
            mock_db_instance1 = Mock()
            mock_db_instance1.id = 1
            mock_db_instance1.name = "Character 1"

            mock_db_instance2 = Mock()
            mock_db_instance2.id = 2
            mock_db_instance2.name = "Character 2"

            # Mock Character model constructor and save behavior
            def mock_character_constructor(**kwargs):
                mock_char = Mock()
                mock_char.id = len(mock_character_model.call_args_list) + 1
                mock_char.name = kwargs.get('name', f'Character {mock_char.id}')
                return mock_char

            mock_character_model.side_effect = mock_character_constructor

            # Mock database async operations
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            from fastapi import FastAPI
            from app.routers.batch import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/batch", tags=["batch-operations"])
            client = TestClient(app)

            # Test batch creation
            batch_data = [
                {
                    "world_id": 1,
                    "name": "Hero Character",
                    "backstory": "A brave hero"
                },
                {
                    "world_id": 1,
                    "name": "Villain Character",
                    "backstory": "A cunning villain"
                }
            ]

            response = client.post(
                "/api/v1/batch/characters",
                json=batch_data
            )

            assert response.status_code == 200
            data = response.json()

            # Verify batch response format
            assert data["success"] is True
            assert "data" in data

            batch_response = data["data"]
            assert "success_count" in batch_response
            assert "error_count" in batch_response
            assert "results" in batch_response

    @pytest.mark.asyncio
    async def test_get_batch_characters_retrieve(self):
        """Test batch character retrieval for React efficiency"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.batch.select') as mock_select, \
             patch('app.routers.batch.Character') as mock_character:

            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock database query and results
            mock_query = Mock()
            mock_select.return_value.where.return_value = mock_query

            mock_result = Mock()
            mock_session = Mock()
            mock_session.execute.return_value = mock_result

            # Mock characters found
            mock_chars = [
                Mock(name="Hero", id=1, description="Brave"),
                Mock(name="Villain", id=2, description="Cunning")
            ]
            mock_result.scalars.return_value.all.return_value = mock_chars

            from fastapi import FastAPI
            from app.routers.batch import router
            from app.core.deps import get_current_active_user_from_bearer_token

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/batch", tags=["batch-operations"])
            client = TestClient(app)

            response = client.get("/api/v1/batch/characters?character_ids=1,2")

            assert response.status_code == 200
            data = response.json()

            # Verify batch retrieval response
            assert data["success"] is True
            assert len(data["data"]) > 0


# Update task progress
# Completed: review-auth-token-new, review-auth-refresh-new, review-dashboard-summary
# Next: Continue with remaining auth endpoints