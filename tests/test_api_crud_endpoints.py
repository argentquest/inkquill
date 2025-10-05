# tests/test_api_crud_endpoints.py

"""
Comprehensive tests for CRUD endpoints across all API routers.
Tests standard REST operations: Create, Read, Update, Delete patterns.
Follows React migration requirements for ApiResponse format and Bearer auth.
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from fastapi import HTTPException, status
from fastapi.testclient import TestClient

from app.schemas.base import ApiResponse, ApiError


class TestUsersAPI:
    """Test User Management API endpoints"""

    @pytest.mark.asyncio
    async def test_get_user_profile(self):
        """Test GET /users/me - Get current user profile"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_user.username = "testuser"
            mock_user.email = "test@example.com"
            mock_user.is_active = True
            mock_user.created_at = datetime.now()
            mock_get_user.return_value = mock_user

            from fastapi import FastAPI
            from app.routers.users import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/users")
            client = TestClient(app)

            response = client.get("/api/v1/users/me")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["username"] == "testuser"
            assert data["data"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_list_users_admin_only(self):
        """Test GET /users/ - List all users (admin only)"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.user.user_crud.get_users') as mock_get_users:

            # Mock admin user
            mock_user = Mock()
            mock_user.is_admin = True
            mock_get_user.return_value = mock_user

            # Mock user list
            mock_users = [
                Mock(id=1, username="user1", email="user1@test.com"),
                Mock(id=2, username="user2", email="user2@test.com")
            ]
            mock_get_users.return_value = mock_users

            from fastapi import FastAPI
            from app.routers.users import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/users")
            client = TestClient(app)

            response = client.get("/api/v1/users/")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_get_user_by_id_forbidden_for_non_admin(self):
        """Test GET /users/{user_id} - Forbidden for non-admin users"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.user.user_crud.get') as mock_get_user_by_id:

            # Mock non-admin user
            mock_user = Mock()
            mock_user.is_admin = False
            mock_user.id = 1  # Different from requested user ID
            mock_get_user.return_value = mock_user

            from fastapi import FastAPI
            from app.routers.users import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/users")
            client = TestClient(app)

            response = client.get("/api/v1/users/2")  # Trying to access user ID 2

            # Should return 403 Forbidden
            assert response.status_code == 403


class TestWorldsAPI:
    """Test World Management API endpoints"""

    @pytest.mark.asyncio
    async def test_create_world(self):
        """Test POST /worlds/ - Create new world"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.world.world_crud.create') as mock_create_world, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock created world
            mock_world = Mock()
            mock_world.id = 1
            mock_world.name = "Test World"
            mock_world.description = "A test world"
            mock_create_world.return_value = mock_world

            # Mock database session
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            from fastapi import FastAPI
            from app.routers.world import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/worlds")
            client = TestClient(app)

            world_data = {
                "name": "Test World",
                "description": "A test world",
                "world_type": "fantasy"
            }

            response = client.post("/api/v1/worlds/", json=world_data)

            assert response.status_code == 200  # Or 201 depending on implementation
            data = response.json()
            assert data["success"] is True
            assert data["data"]["name"] == "Test World"

    @pytest.mark.asyncio
    async def test_list_user_worlds(self):
        """Test GET /worlds/ - List user's worlds"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.world.world_crud.get_worlds_by_user') as mock_get_worlds:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock user's worlds
            mock_worlds = [
                Mock(id=1, name="World 1", description="First world"),
                Mock(id=2, name="World 2", description="Second world")
            ]
            mock_get_worlds.return_value = mock_worlds

            from fastapi import FastAPI
            from app.routers.world import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/worlds")
            client = TestClient(app)

            response = client.get("/api/v1/worlds/")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 2

    @pytest.mark.asyncio
    async def test_get_world_details(self):
        """Test GET /worlds/{world_id} - Get single world"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.world.world_crud.get') as mock_get_world:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock world
            mock_world = Mock()
            mock_world.id = 1
            mock_world.name = "Test World"
            mock_world.user_id = 1  # Same user owns the world
            mock_get_world.return_value = mock_world

            from fastapi import FastAPI
            from app.routers.world import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/worlds")
            client = TestClient(app)

            response = client.get("/api/v1/worlds/1")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["name"] == "Test World"

    @pytest.mark.asyncio
    async def test_update_world(self):
        """Test PUT /worlds/{world_id} - Update world"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.world.world_crud.update') as mock_update_world, \
             patch('app.crud.world.world_crud.get') as mock_get_world:

            # Mock authenticated user and world ownership
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            mock_world = Mock()
            mock_world.user_id = 1  # User owns the world
            mock_get_world.return_value = mock_world

            mock_updated_world = Mock()
            mock_updated_world.name = "Updated World Name"
            mock_updated_world.description = "Updated description"
            mock_update_world.return_value = mock_updated_world

            from fastapi import FastAPI
            from app.routers.world import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/worlds")
            client = TestClient(app)

            update_data = {
                "name": "Updated World Name",
                "description": "Updated description"
            }

            response = client.put("/api/v1/worlds/1", json=update_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["name"] == "Updated World Name"


class TestStoriesAPI:
    """Test Story Management API endpoints"""

    @pytest.mark.asyncio
    async def test_create_story(self):
        """Test POST /stories/ - Create new story"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.story.story_crud.create') as mock_create_story:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock created story
            mock_story = Mock()
            mock_story.id = 1
            mock_story.title = "Test Story"
            mock_story.description = "A test story"
            mock_create_story.return_value = mock_story

            from fastapi import FastAPI
            from app.routers.story import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/stories")
            client = TestClient(app)

            story_data = {
                "title": "Test Story",
                "description": "A test story",
                "world_id": 1,
                "story_type": "advanced"
            }

            response = client.post("/api/v1/stories/", json=story_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["title"] == "Test Story"

    @pytest.mark.asyncio
    async def test_get_story_with_authorization(self):
        """Test GET /stories/{story_id} with proper authorization"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.story.story_crud.get') as mock_get_story, \
             patch('app.crud.world.world_crud.get') as mock_get_world:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock story owned by user
            mock_story = Mock()
            mock_story.id = 1
            mock_story.title = "Test Story"
            mock_story.user_id = 1  # User owns the story
            mock_get_story.return_value = mock_story

            # Mock world access (needed for story access check)
            mock_world = Mock()
            mock_world.user_id = 1  # User owns the world too
            mock_get_world.return_value = mock_world

            from fastapi import FastAPI
            from app.routers.story import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/stories")
            client = TestClient(app)

            response = client.get("/api/v1/stories/1")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["title"] == "Test Story"


class TestActsAPI:
    """Test Act Management API endpoints"""

    @pytest.mark.asyncio
    async def test_create_act_for_story(self):
        """Test POST /stories/{story_id}/acts/ - Create act for story"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.act.act_crud.create') as mock_create_act, \
             patch('app.crud.story.story_crud.get') as mock_get_story:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock story ownership
            mock_story = Mock()
            mock_story.id = 1
            mock_story.user_id = 1  # User owns the story
            mock_get_story.return_value = mock_story

            # Mock created act
            mock_act = Mock()
            mock_act.id = 1
            mock_act.title = "Test Act 1"
            mock_act.act_summary = "First act summary"
            mock_create_act.return_value = mock_act

            from fastapi import FastAPI
            from app.routers.act import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/stories")
            client = TestClient(app)

            act_data = {
                "title": "Test Act 1",
                "act_summary": "First act summary",
                "act_number": 1
            }

            response = client.post("/api/v1/stories/1/acts/", json=act_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["title"] == "Test Act 1"


class TestScenesAPI:
    """Test Scene Management API endpoints"""

    @pytest.mark.asyncio
    async def test_create_scene_for_act(self):
        """Test POST /acts/{act_id}/scenes/ - Create scene for act"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.scene.scene_crud.create') as mock_create_scene, \
             patch('app.crud.act.act_crud.get') as mock_get_act, \
             patch('app.crud.story.story_crud.get') as mock_get_story:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock story ownership chain
            mock_story = Mock()
            mock_story.user_id = 1
            mock_get_story.return_value = mock_story

            mock_act = Mock()
            mock_act.id = 1
            mock_act.story_id = 1  # Act belongs to story
            mock_get_act.return_value = mock_act

            # Mock created scene
            mock_scene = Mock()
            mock_scene.id = 1
            mock_scene.title = "Test Scene 1"
            mock_scene.content = "Scene content"
            mock_create_scene.return_value = mock_scene

            from fastapi import FastAPI
            from app.routers.scene import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/acts")
            client = TestClient(app)

            scene_data = {
                "title": "Test Scene 1",
                "content": "Scene content",
                "scene_number": 1
            }

            response = client.post("/api/v1/acts/1/scenes/", json=scene_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["title"] == "Test Scene 1"


class TestCharacterCRUD:
    """Test Character CRUD operations"""

    @pytest.mark.asyncio
    async def test_get_character_by_id(self):
        """Test GET /characters/{character_id} - Get single character"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.character.character_crud.get') as mock_get_character:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock character owned by user
            mock_character = Mock()
            mock_character.id = 1
            mock_character.name = "Test Character"
            mock_character.user_id = 1  # User owns the character
            mock_get_character.return_value = mock_character

            from fastapi import FastAPI
            from app.routers.character import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/characters")
            client = TestClient(app)

            response = client.get("/api/v1/characters/1")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["name"] == "Test Character"

    @pytest.mark.asyncio
    async def test_update_character(self):
        """Test PUT /characters/{character_id} - Update character"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.character.character_crud.update') as mock_update_character, \
             patch('app.crud.character.character_crud.get') as mock_get_character:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock character ownership
            mock_character = Mock()
            mock_character.user_id = 1
            mock_get_character.return_value = mock_character

            # Mock updated character
            mock_updated_character = Mock()
            mock_updated_character.name = "Updated Character Name"
            mock_updated_character.backstory = "Updated backstory"
            mock_update_character.return_value = mock_updated_character

            from fastapi import FastAPI
            from app.routers.character import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/characters")
            client = TestClient(app)

            update_data = {
                "name": "Updated Character Name",
                "backstory": "Updated backstory"
            }

            response = client.put("/api/v1/characters/1", json=update_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["name"] == "Updated Character Name"


class TestLocationCRUD:
    """Test Location CRUD operations"""

    @pytest.mark.asyncio
    async def test_get_location_details(self):
        """Test GET /locations/{location_id} - Get single location"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.location.location_crud.get') as mock_get_location:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock location owned by user
            mock_location = Mock()
            mock_location.id = 1
            mock_location.name = "Test Location"
            mock_location.user_id = 1
            mock_location.description = "A test location"
            mock_get_location.return_value = mock_location

            from fastapi import FastAPI
            from app.routers.location import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/locations")
            client = TestClient(app)

            response = client.get("/api/v1/locations/1")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["name"] == "Test Location"


class TestLoreItemCRUD:
    """Test Lore Item CRUD operations"""

    @pytest.mark.asyncio
    async def test_create_lore_item_for_world(self):
        """Test POST /worlds/{world_id}/lore-items/ - Create lore item for world"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.lore_item.lore_item_crud.create') as mock_create_lore_item, \
             patch('app.crud.world.world_crud.get') as mock_get_world:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock world ownership
            mock_world = Mock()
            mock_world.user_id = 1
            mock_get_world.return_value = mock_world

            # Mock created lore item
            mock_lore_item = Mock()
            mock_lore_item.id = 1
            mock_lore_item.name = "Ancient Artifact"
            mock_lore_item.description = "A powerful magical artifact"
            mock_create_lore_item.return_value = mock_lore_item

            from fastapi import FastAPI
            from app.routers.lore_item import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/worlds")
            client = TestClient(app)

            lore_item_data = {
                "name": "Ancient Artifact",
                "description": "A powerful magical artifact",
                "type": "artifact",
                "rarity": "legendary"
            }

            response = client.post("/api/v1/worlds/1/lore-items/", json=lore_item_data)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["data"]["name"] == "Ancient Artifact"


class TestAIEndpoints:
    """Test AI-powered endpoints"""

    @pytest.mark.asyncio
    async def test_world_chat_create_session(self):
        """Test POST /world-chat/sessions/{world_id} - Create chat session"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.world_chat.world_chat_crud.create_session') as mock_create_session, \
             patch('app.crud.world.world_crud.get') as mock_get_world:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock world ownership
            mock_world = Mock()
            mock_world.user_id = 1
            mock_get_world.return_value = mock_world

            # Mock created session
            mock_session = Mock()
            mock_session.id = 1
            mock_session.session_name = "New Chat Session"
            mock_create_session.return_value = mock_session

            # This would require the world_chat router - for now, testing basic structure
            # In a real implementation, this would be a full integration test


class TestDocumentAPIs:
    """Test Document Management endpoints"""

    @pytest.mark.asyncio
    async def test_list_user_documents(self):
        """Test GET /documents/ - List user's documents"""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.crud.document.document_crud.get_user_documents') as mock_get_documents:

            # Mock authenticated user
            mock_user = Mock()
            mock_user.id = 1
            mock_get_user.return_value = mock_user

            # Mock documents
            mock_documents = [
                Mock(id=1, filename="world_doc.pdf", uploaded_at=datetime.now()),
                Mock(id=2, filename="story_notes.txt", uploaded_at=datetime.now())
            ]
            mock_get_documents.return_value = mock_documents

            from fastapi import FastAPI
            from app.routers.document_upload import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/documents")
            client = TestClient(app)

            response = client.get("/api/v1/documents/")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) == 2


class TestPublishingAPIs:
    """Test Publishing and Sharing endpoints"""

    @pytest.mark.asyncio
    async def test_list_published_stories(self):
        """Test GET /published-stories/ - List public stories"""
        with patch('app.crud.published_story.published_story_crud.get_published_stories') as mock_get_published:

            # Mock published stories
            mock_stories = [
                Mock(id=1, title="Published Story 1", is_public=True),
                Mock(id=2, title="Published Story 2", is_public=True)
            ]
            mock_get_published.return_value = mock_stories

            from fastapi import FastAPI
            from app.routers.published_stories import router

            app = FastAPI()
            app.include_router(router, prefix="/api/v1/published-stories")
            client = TestClient(app)

            response = client.get("/api/v1/published-stories/")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert len(data["data"]) >= 0  # Public endpoint, can return empty