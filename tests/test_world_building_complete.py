# tests/test_world_building_complete.py

"""
Comprehensive tests for World Building API endpoints
Tests world CRUD, character, location, and lore item management with ApiResponse wrappers
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from app.schemas.base import ApiResponse, ApiError
from app.routers import world as world_router
from app.routers import character as character_router
from app.routers import location as location_router
from app.routers import lore_item as lore_item_router


class TestWorldCRUD:
    """Test world creation, reading, updating, and deletion."""

    @pytest.mark.asyncio
    async def test_get_user_worlds_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /worlds - Get user's worlds successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.world.crud_world') as mock_crud_world:

            mock_get_user.return_value = mock_authenticated_user

            # Mock world list
            mock_worlds = [
                Mock(
                    id=1,
                    name="Fantasy Kingdom",
                    description="A magical kingdom",
                    is_public=False
                ),
                Mock(
                    id=2,
                    name="Sci-Fi Universe",
                    description="Future technology world",
                    is_public=True
                )
            ]
            mock_crud_world.get_user_worlds.return_value = mock_worlds

            client = test_client_factory.create_client_with_routers(world_router.router)

            response = client.get("/worlds")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert len(data["data"]) == 2
            assert data["data"][0]["name"] == "Fantasy Kingdom"
            assert data["data"][1]["is_public"] is True

    @pytest.mark.asyncio
    async def test_create_world_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /worlds - Create new world successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.world.crud_world') as mock_crud_world, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock created world
            created_world = Mock()
            created_world.id = 1
            created_world.name = "New Fantasy World"
            created_world.description = "A new magical realm"
            created_world.is_public = False

            mock_crud_world.create_world.return_value = created_world

            client = test_client_factory.create_client_with_routers(world_router.router)

            world_data = {
                "name": "New Fantasy World",
                "description": "A new magical realm",
                "is_public": False
            }

            response = client.post("/worlds", json=world_data)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            assert data["data"]["name"] == "New Fantasy World"
            assert data["data"]["is_public"] is False

    @pytest.mark.asyncio
    async def test_get_world_detail_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /worlds/{world_id} - Get world details successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.world.crud_world') as mock_crud_world:

            mock_get_user.return_value = mock_authenticated_user

            # Mock detailed world
            mock_world = Mock()
            mock_world.id = 1
            mock_world.name = "Detailed World"
            mock_world.description = "Very detailed world"
            mock_world.is_public = True
            mock_world.user_id = mock_authenticated_user.id

            mock_crud_world.get_world.return_value = mock_world

            client = test_client_factory.create_client_with_routers(world_router.router)

            response = client.get("/worlds/1")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"]["name"] == "Detailed World"

    @pytest.mark.asyncio
    async def test_update_world_success(self, test_client_factory, mock_authenticated_user):
        """Test PUT /worlds/{world_id} - Update world successfully."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.world.crud_world') as mock_crud_world, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock existing world and updated world
            mock_world = Mock()
            mock_world.user_id = mock_authenticated_user.id

            updated_world = Mock()
            updated_world.id = 1
            updated_world.name = "Updated World Name"
            updated_world.description = "Updated description"

            mock_crud_world.get_world.return_value = mock_world
            mock_crud_world.update_world.return_value = updated_world

            client = test_client_factory.create_client_with_routers(world_router.router)

            update_data = {
                "name": "Updated World Name",
                "description": "Updated description"
            }

            response = client.put("/worlds/1", json=update_data)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"]["name"] == "Updated World Name"


class TestCharacterManagement:
    """Test character creation, listing, and management within worlds."""

    @pytest.mark.asyncio
    async def test_get_world_characters_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /worlds/{world_id}/characters - Get characters for world."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.character.crud_character') as mock_crud_char:

            mock_get_user.return_value = mock_authenticated_user

            # Mock characters
            mock_chars = [
                Mock(
                    id=1,
                    name="Hero Character",
                    backstory="Born in a small village",
                    role="protagonist"
                ),
                Mock(
                    id=2,
                    name="Villain Character",
                    backstory="Corrupted by power",
                    role="antagonist"
                )
            ]
            mock_crud_char.get_characters_by_world.return_value = mock_chars

            client = test_client_factory.create_client_with_routers(character_router.router)

            response = client.get("/worlds/1/characters")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert len(data["data"]) == 2
            assert data["data"][0]["name"] == "Hero Character"
            assert data["data"][1]["role"] == "antagonist"

    @pytest.mark.asyncio
    async def test_create_character_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /characters - Create new character."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.character.crud_character') as mock_crud_char, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock world and character creation
            mock_world = Mock()
            mock_world.user_id = mock_authenticated_user.id

            created_char = Mock()
            created_char.id = 1
            created_char.name = "New Character"
            created_char.backstory = "A mysterious background"
            created_char.world_id = 1

            # Mock the CRUD functions
            with patch('app.routers.character.crud_world.get_world') as mock_get_world:
                mock_get_world.return_value = mock_world
                mock_crud_char.create_character.return_value = created_char

                client = test_client_factory.create_client_with_routers(character_router.router)

                char_data = {
                    "name": "New Character",
                    "backstory": "A mysterious background",
                    "world_id": 1
                }

                response = client.post("/characters", json=char_data)

                assert response.status_code == 201
                data = response.json()

                assert data["success"] is True
                assert data["data"]["name"] == "New Character"

    @pytest.mark.asyncio
    async def test_link_character_to_story_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /characters/{character_id}/link-to-story - Link character to story."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            client = test_client_factory.create_client_with_routers(character_router.router)

            link_data = {"story_id": 1}

            response = client.post("/characters/1/link-to-story", json=link_data)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True


class TestLocationManagement:
    """Test location creation, listing, and management within worlds."""

    @pytest.mark.asyncio
    async def test_get_world_locations_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /worlds/{world_id}/locations - Get locations for world."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.location.crud_location') as mock_crud_loc:

            mock_get_user.return_value = mock_authenticated_user

            # Mock locations
            mock_locations = [
                Mock(id=1, name="Castle", description="Big stone castle", importance="major"),
                Mock(id=2, name="Village", description="Small fishing village", importance="minor")
            ]
            mock_crud_loc.get_locations_by_world.return_value = mock_locations

            client = test_client_factory.create_client_with_routers(location_router.router)

            response = client.get("/worlds/1/locations")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert len(data["data"]) == 2
            assert data["data"][0]["importance"] == "major"

    @pytest.mark.asyncio
    async def test_create_location_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /locations - Create new location."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.location.crud_location') as mock_crud_loc, \
             patch('app.routers.location.crud_world') as mock_crud_world, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock world ownership
            mock_world = Mock()
            mock_world.user_id = mock_authenticated_user.id
            mock_crud_world.get_world.return_value = mock_world

            # Mock created location
            created_loc = Mock()
            created_loc.id = 1
            created_loc.name = "New Location"
            created_loc.description = "A mysterious place"
            mock_crud_loc.create_location.return_value = created_loc

            client = test_client_factory.create_client_with_routers(location_router.router)

            loc_data = {
                "name": "New Location",
                "description": "A mysterious place",
                "world_id": 1
            }

            response = client.post("/locations", json=loc_data)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            assert data["data"]["name"] == "New Location"


class TestLoreItemManagement:
    """Test lore item creation, listing, and management."""

    @pytest.mark.asyncio
    async def test_get_world_lore_items_success(self, test_client_factory, mock_authenticated_user):
        """Test GET /worlds/{world_id}/lore-items - Get lore items for world."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.lore_item.crud_lore_item') as mock_crud_lore:

            mock_get_user.return_value = mock_authenticated_user

            # Mock lore items
            mock_items = [
                Mock(id=1, name="Ancient Artifact", lore_type="artifact", importance="legendary"),
                Mock(id=2, name="Forgotten Language", lore_type="language", importance="historical")
            ]
            mock_crud_lore.get_lore_items_by_world.return_value = mock_items

            client = test_client_factory.create_client_with_routers(lore_item_router.router)

            response = client.get("/worlds/1/lore-items")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert len(data["data"]) == 2
            assert data["data"][0]["lore_type"] == "artifact"

    @pytest.mark.asyncio
    async def test_create_lore_item_success(self, test_client_factory, mock_authenticated_user):
        """Test POST /lore-items - Create new lore item."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.lore_item.crud_lore_item') as mock_crud_lore, \
             patch('app.routers.lore_item.crud_world') as mock_crud_world, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock world ownership
            mock_world = Mock()
            mock_world.user_id = mock_authenticated_user.id
            mock_crud_world.get_world.return_value = mock_world

            # Mock created lore item
            created_item = Mock()
            created_item.id = 1
            created_item.name = "Mysterious Rune"
            created_item.description = "An ancient magical symbol"
            mock_crud_lore.create_lore_item.return_value = created_item

            client = test_client_factory.create_client_with_routers(lore_item_router.router)

            item_data = {
                "name": "Mysterious Rune",
                "description": "An ancient magical symbol",
                "world_id": 1,
                "lore_type": "artifact"
            }

            response = client.post("/lore-items", json=item_data)

            assert response.status_code == 201
            data = response.json()

            assert data["success"] is True
            assert data["data"]["name"] == "Mysterious Rune"


class TestWorldBuildingIntegration:
    """Test integration between world elements."""

    @pytest.mark.asyncio
    async def test_get_world_overview_with_elements(self, test_client_factory, mock_authenticated_user):
        """Test GET /worlds/{world_id} - World with all associated elements."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.world.crud_world') as mock_crud_world:

            mock_get_user.return_value = mock_authenticated_user

            # Mock world with stats
            mock_world = Mock()
            mock_world.id = 1
            mock_world.name = "Complete World"
            mock_world.description = "A world with many elements"
            mock_world.user_id = mock_authenticated_user.id
            mock_world.character_count = 5
            mock_world.location_count = 3
            mock_world.lore_item_count = 7

            mock_crud_world.get_world_with_stats.return_value = mock_world

            client = test_client_factory.create_client_with_routers(world_router.router)

            response = client.get("/worlds/1")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert "character_count" in data["data"]
            assert "location_count" in data["data"]

    @pytest.mark.asyncio
    async def test_public_worlds_discovery(self, test_client_factory, mock_authenticated_user):
        """Test GET /worlds/public - Discover public worlds."""
        with patch('app.routers.world.crud_world') as mock_crud_world:

            # Mock public worlds
            mock_worlds = [
                Mock(
                    id=1,
                    name="Public Fantasy World",
                    description="Creative fantasy setting",
                    is_public=True
                )
            ]
            mock_crud_world.get_public_worlds.return_value = mock_worlds

            client = test_client_factory.create_client_with_routers(world_router.router)

            response = client.get("/worlds/public")

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert len(data["data"]) == 1
            assert data["data"][0]["is_public"] is True


class TestBatchOperations:
    """Test batch operations for efficient bulk management."""

    @pytest.mark.asyncio
    async def test_batch_character_operations(self, test_client_factory, mock_authenticated_user):
        """Test POST /batch/characters - Batch character operations."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.batch.crud_character') as mock_crud_char, \
             patch('app.core.deps.get_db_session') as mock_get_db:

            mock_get_user.return_value = mock_authenticated_user
            mock_db = AsyncMock()
            mock_get_db.return_value = mock_db

            # Mock batch response
            mock_crud_char.batch_create_characters.return_value = {
                "success_count": 2,
                "error_count": 0,
                "results": [
                    {"id": 1, "name": "Character 1"},
                    {"id": 2, "name": "Character 2"}
                ]
            }

            from app.routers import batch
            client = test_client_factory.create_client_with_routers(batch.router)

            batch_data = [
                {"world_id": 1, "name": "Character 1", "backstory": "Background 1"},
                {"world_id": 1, "name": "Character 2", "backstory": "Background 2"}
            ]

            response = client.post("/batch/characters", json=batch_data)

            assert response.status_code == 200
            data = response.json()

            assert data["success"] is True
            assert data["data"]["success_count"] == 2
            assert data["data"]["error_count"] == 0


class TestWorldBuildingValidation:
    """Test validation and error handling for world building operations."""

    @pytest.mark.asyncio
    async def test_create_world_validation_required_fields(self, test_client_factory, mock_authenticated_user):
        """Test POST /worlds - Required field validation."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user:
            mock_get_user.return_value = mock_authenticated_user

            client = test_client_factory.create_client_with_routers(world_router.router)

            # Missing required name field
            invalid_data = {"description": "No name provided"}

            response = client.post("/worlds", json=invalid_data)

            # Should return 422 Unprocessable Entity for validation errors
            assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_character_world_not_found(self, test_client_factory, mock_authenticated_user):
        """Test POST /characters - World not found or not owned."""
        with patch('app.core.deps.get_current_active_user_from_bearer_token') as mock_get_user, \
             patch('app.routers.character.crud_world') as mock_crud_world:

            mock_get_user.return_value = mock_authenticated_user
            mock_crud_world.get_world.return_value = None  # World not found

            client = test_client_factory.create_client_with_routers(character_router.router)

            char_data = {
                "name": "Orphan Character",
                "world_id": 999  # Non-existent world
            }

            response = client.post("/characters", json=char_data)

            # Should return 404 for world not found
            assert response.status_code == 404