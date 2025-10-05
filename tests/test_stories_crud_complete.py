# tests/test_stories_crud_complete.py

"""
Comprehensive tests for Story Management API endpoints
Tests all story CRUD operations with ApiResponse wrappers for React SPA compatibility
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.schemas.base import ApiResponse, ApiError
from app.schemas import story as story_schemas
from app.routers import story as story_router


class TestStoryListEndpoints:
    """Test story listing and discovery endpoints."""

    @pytest.mark.asyncio
    async def test_get_user_stories_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /stories - Get user's stories successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story.crud_story') as mock_crud_story:

            # Setup mocks
            mock_get_user.return_value = mock_authenticated_user

            # Mock story list
            mock_stories = [
                Mock(
                    id=1,
                    title="Story 1",
                    description="Description 1",
                    published=False,
                    created_at=datetime.utcnow()
                ),
                Mock(
                    id=2,
                    title="Story 2",
                    description="Description 2",
                    published=True,
                    created_at=datetime.utcnow()
                )
            ]
            mock_crud_story.get_user_stories.return_value = mock_stories

            client = test_client_factory.create_client_with_routers(story_router.router)

            response = client.get("/stories")

            assert response.status_code == 200
            data = response.json()

            # Verify ApiResponse format
            assert data["success"] is True
            assert "data" in data
            assert len(data["data"]) == 2
            assert data["data"][0]["title"] == "Story 1"
            assert data["data"][1]["published"] is True

    @pytest.mark.asyncio
    async def test_get_user_stories_empty_list(self, test_client_factory, mock_authenticated_user):
        """Test GET /stories - Empty story list."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story.crud_story') as mock_crud_story:

            mock_get_user.return_value = mock_authenticated_user
            mock_crud_story.get_user_stories.return_value = []

            client = test_client_factory.create_client_with_routers(story_router.router)

            response = client.get("/stories")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"] == []

    @pytest.mark.asyncio
    async def test_get_stories_with_pagination(self, test_client_factory, mock_authenticated_user):
        """Test GET /stories - Pagination parameters."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story.crud_story') as mock_crud_story:

            mock_get_user.return_value = mock_authenticated_user
            mock_crud_story.get_user_stories.return_value = [Mock(id=1, title="Story 1")]

            client = test_client_factory.create_client_with_routers(story_router.router)

            response = client.get("/stories?skip=10&limit=5")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            # Verify pagination parameters were passed to CRUD function
            mock_crud_story.get_user_stories.assert_called_once()
            call_args = mock_crud_story.get_user_stories.call_args
            assert call_args[1]["skip"] == 10
            assert call_args[1]["limit"] == 5


class TestStoryDetailEndpoints:
    """Test individual story CRUD operations."""

    @pytest.mark.asyncio
    async def test_get_story_detail_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /stories/{story_id} - Get story details successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story.crud_story') as mock_crud_story:

            mock_get_user.return_value = mock_authenticated_user

            # Mock story with full details
            mock_story = Mock()
            mock_story.id = 1
            mock_story.title = "Test Story"
            mock_story.description = "Story description"
            mock_story.published = False
            mock_story.created_at = datetime.utcnow()
            mock_story.updated_at = datetime.utcnow()
            mock_story.user_id = mock_authenticated_user.id

            mock_crud_story.get_story.return_value = mock_story

            client = test_client_factory.create_client_with_routers(story_router.router)

            response = client.get("/stories/1")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"]["title"] == "Test Story"
            assert data["data"]["id"] == 1

    @pytest.mark.asyncio
    async def test_get_story_detail_not_found(self, test_client_factory, mock_authenticated_user):
        """Test GET /stories/{story_id} - Story not found."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story.crud_story') as mock_crud_story:

            mock_get_user.return_value = mock_authenticated_user
            mock_crud_story.get_story.return_value = None

            client = test_client_factory.create_client_with_routers(story_router.router)

            response = client.get("/stories/999")

            # Should return 404 with ApiResponse format (error responses handled by exceptions)
            assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_story_detail_forbidden(self, test_client_factory, mock_authenticated_user):
        """Test GET /stories/{story_id} - User not authorized."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story.crud_story') as mock_crud_story:

            mock_get_user.return_value = mock_authenticated_user

            # Mock story belonging to different user
            mock_story = Mock()
            mock_story.user_id = 999  # Different user ID

            mock_crud_story.get_story.return_value = mock_story

            client = test_client_factory.create_client_with_routers(story_router.router)

            response = client.get("/stories/1")

            # Should return 403 Forbidden
            assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_story_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /stories - Create new story successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story.crud_story') as mock_crud_story, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            # Setup mocks
            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock created story
            created_story = Mock()
            created_story.id = 1
            created_story.title = "New Story"
            created_story.description = "New description"
            created_story.published = False
            created_story.user_id = mock_authenticated_user.id

            mock_crud_story.create_story.return_value = created_story

            client = test_client_factory.create_client_with_routers(story_router.router)

            story_data = {
                "title": "New Story",
                "description": "New description",
                "published": False
            }

            response = client.post("/stories", json=story_data)

            assert response.status_code == 201  # Created
            data = response.json()

            # Verify ApiResponse format
            assert data["success"] is True
            assert data["data"]["title"] == "New Story"
            assert data["data"]["id"] == 1

    @pytest.mark.asyncio
    async def test_update_story_success(self, test_client_factory, mock_authenticated_user):
        """Test PUT /stories/{story_id} - Update story successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story.crud_story') as mock_crud_story, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock existing story
            existing_story = Mock()
            existing_story.id = 1
            existing_story.user_id = mock_authenticated_user.id

            # Mock updated story
            updated_story = Mock()
            updated_story.id = 1
            updated_story.title = "Updated Title"
            updated_story.description = "Updated description"

            mock_crud_story.get_story.return_value = existing_story
            mock_crud_story.update_story.return_value = updated_story

            client = test_client_factory.create_client_with_routers(story_router.router)

            update_data = {
                "title": "Updated Title",
                "description": "Updated description"
            }

            response = client.put("/stories/1", json=update_data)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"]["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_delete_story_success(self, test_client_factory, mock_authenticated_user):
        """Test DELETE /stories/{story_id} - Delete story successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story.crud_story') as mock_crud_story, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock story belonging to user
            mock_story = Mock()
            mock_story.id = 1
            mock_story.user_id = mock_authenticated_user.id

            mock_crud_story.get_story.return_value = mock_story
            mock_crud_story.delete_story.return_value = True

            client = test_client_factory.create_client_with_routers(story_router.router)

            response = client.delete("/stories/1")

            assert response.status_code == 204  # No Content

    @pytest.mark.asyncio
    async def test_publish_story_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /stories/{story_id}/publish - Publish story."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story.crud_story') as mock_crud_story, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock story and updated story
            mock_story = Mock()
            mock_story.id = 1
            mock_story.user_id = mock_authenticated_user.id

            published_story = Mock()
            published_story.id = 1
            published_story.published = True

            mock_crud_story.get_story.return_value = mock_story
            mock_crud_story.update_story.return_value = published_story

            client = test_client_factory.create_client_with_routers(story_router.router)

            response = client.post("/stories/1/publish")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"]["published"] is True


class TestStorySearchEndpoints:
    """Test story search and discovery functionality."""

    @pytest.mark.asyncio
    async def test_search_stories_success(self, test_client_factory):
        """Test GET /stories/search - Search published stories."""
        with patch('app.routers.story.crud_story') as mock_crud_story:
            # Mock search results
            mock_stories = [
                Mock(
                    id=1,
                    title="Fantasy Adventure",
                    description="A magical tale",
                    published=True,
                    view_count=100
                )
            ]
            mock_crud_story.search_stories.return_value = mock_stories

            client = test_client_factory.create_client_with_routers(story_router.router)

            response = client.get("/stories/search?q=fantasy")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["title"] == "Fantasy Adventure"

    @pytest.mark.asyncio
    async def test_get_published_stories(self, test_client_factory):
        """Test GET /stories/published - Get published stories for non-authenticated users."""
        with patch('app.routers.story.crud_story') as mock_crud_story:
            # Mock published stories
            mock_stories = [
                Mock(id=1, title="Published Story", published=True)
            ]
            mock_crud_story.get_published_stories.return_value = mock_stories

            client = test_client_factory.create_client_with_routers(story_router.router)

            response = client.get("/stories/published")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True


class TestStoryValidation:
    """Test input validation and error handling."""

    @pytest.mark.asyncio
    async def test_create_story_validation_error(self, test_client_factory, mock_authenticated_user):
        """Test POST /stories - Validation error for missing required fields."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            mock_get_user.return_value = mock_authenticated_user

            client = test_client_factory.create_client_with_routers(story_router.router)

            # Missing required title
            invalid_data = {
                "description": "Just a description"
            }

            response = client.post("/stories", json=invalid_data)

            # Should return validation error
            assert response.status_code == 422  # Unprocessable Entity

    @pytest.mark.asyncio
    async def test_update_story_not_found(self, test_client_factory, mock_authenticated_user):
        """Test PUT /stories/{story_id} - Story not found."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.story.crud_story') as mock_crud_story:

            mock_get_user.return_value = mock_authenticated_user
            mock_crud_story.get_story.return_value = None

            client = test_client_factory.create_client_with_routers(story_router.router)

            update_data = {"title": "New Title"}
            response = client.put("/stories/999", json=update_data)

            assert response.status_code == 404