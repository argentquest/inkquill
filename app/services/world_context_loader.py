# /ai_rag_story_app/app/services/world_context_loader.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Dict, List, Any, Optional
import logging

from azure.storage.blob.aio import BlobServiceClient
from app.core.config import settings
from app.models.world import World
from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.models.story import Story
from app.models.act import Act
from app.models.scene import Scene
from app.schemas.chat import WorldContextData

logger = logging.getLogger(__name__)


class WorldContextLoader:
    """Service for loading complete world context data for chat interactions"""
    
    def __init__(self, db: AsyncSession, blob_service_client: Optional[BlobServiceClient] = None):
        self.db = db
        self.blob_service_client = blob_service_client
    
    async def load_full_world_context(self, world_id: int, user_id: int, public_chat: bool = False) -> Optional[WorldContextData]:
        """Load all world data including associated stories, acts, and scenes"""
        try:
            # Load world with all relationships including images
            query = select(World).options(
                selectinload(World.characters).selectinload(Character.current_image),
                selectinload(World.locations).selectinload(Location.current_image),
                selectinload(World.lore_items).selectinload(LoreItem.current_image),
                selectinload(World.stories).selectinload(Story.current_image),
                selectinload(World.story_classes),
                selectinload(World.current_image)
            ).where(World.id == world_id)
            
            # For public chat, allow any world with free chat enabled
            # For regular chat, only allow user's own worlds
            if public_chat:
                query = query.where(World.is_free_chat_enabled == True)
            else:
                query = query.where(World.user_id == user_id)
                
            world_result = await self.db.execute(query)
            world = world_result.scalar_one_or_none()
            
            if not world:
                if public_chat:
                    logger.warning(f"World {world_id} not found or not enabled for public chat")
                else:
                    logger.warning(f"World {world_id} not found for user {user_id}")
                return None
            
            # Load stories with their acts and scenes
            stories_result = await self.db.execute(
                select(Story)
                .options(
                    selectinload(Story.acts).selectinload(Act.scenes)
                )
                .where(Story.world_id == world_id)
                .where(Story.user_id == user_id)
            )
            stories = stories_result.scalars().all()
            
            # Extract acts and scenes
            acts = []
            scenes = []
            for story in stories:
                acts.extend(story.acts)
                for act in story.acts:
                    scenes.extend(act.scenes)
            
            # Convert to serializable format with image URLs
            context_data = WorldContextData(
                world=await self._serialize_world(world),
                characters=[await self._serialize_character(char) for char in world.characters],
                locations=[await self._serialize_location(loc) for loc in world.locations],
                lore_items=[await self._serialize_lore_item(lore) for lore in world.lore_items],
                stories=[await self._serialize_story(story) for story in stories],
                acts=[self._serialize_act(act) for act in acts],
                scenes=[self._serialize_scene(scene) for scene in scenes]
            )
            
            logger.info(f"Loaded world context for world {world_id}: "
                       f"{len(context_data.characters)} characters, "
                       f"{len(context_data.locations)} locations, "
                       f"{len(context_data.lore_items)} lore items, "
                       f"{len(context_data.stories)} stories, "
                       f"{len(context_data.acts)} acts, "
                       f"{len(context_data.scenes)} scenes")
            
            return context_data
            
        except Exception as e:
            logger.error(f"Error loading world context for world {world_id}: {str(e)}")
            raise
    
    async def _serialize_world(self, world: World) -> Dict[str, Any]:
        """Convert World model to serializable dict"""
        image_url = None
        if self.blob_service_client:
            path_to_check = world.current_image.blob_path if world.current_image else world.image_blob_path
            image_url = await self._check_and_get_image_url(path_to_check)
        
        return {
            "id": world.id,
            "name": world.name,
            "description": world.description,
            "user_id": world.user_id,
            "image_url": image_url,
            "created_at": world.created_at.isoformat() if world.created_at else None,
            "updated_at": world.updated_at.isoformat() if world.updated_at else None
        }
    
    async def _serialize_character(self, character: Character) -> Dict[str, Any]:
        """Convert Character model to serializable dict"""
        image_url = None
        if self.blob_service_client:
            path_to_check = character.current_image.blob_path if character.current_image else character.image_blob_path
            image_url = await self._check_and_get_image_url(path_to_check)
        
        return {
            "id": character.id,
            "name": character.name,
            "description": character.description,
            "personality_traits": character.personality_traits,
            "backstory": character.backstory,
            "placement_note": character.placement_note,
            "current_location_id": character.current_location_id,
            "image_url": image_url,
            "created_at": character.created_at.isoformat() if character.created_at else None,
            "updated_at": character.updated_at.isoformat() if character.updated_at else None
        }
    
    async def _serialize_location(self, location: Location) -> Dict[str, Any]:
        """Convert Location model to serializable dict"""
        image_url = None
        if self.blob_service_client:
            path_to_check = location.current_image.blob_path if location.current_image else location.image_blob_path
            image_url = await self._check_and_get_image_url(path_to_check)
        
        return {
            "id": location.id,
            "name": location.name,
            "description": location.description,
            "atmosphere": location.atmosphere,
            "significance": location.significance,
            "scale": location.scale.value if location.scale else None,
            "parent_location_id": location.parent_location_id,
            "map_x": location.map_x,
            "map_y": location.map_y,
            "map_z": location.map_z,
            "image_url": image_url,
            "created_at": location.created_at.isoformat() if location.created_at else None,
            "updated_at": location.updated_at.isoformat() if location.updated_at else None
        }
    
    async def _serialize_lore_item(self, lore: LoreItem) -> Dict[str, Any]:
        """Convert LoreItem model to serializable dict"""
        image_url = None
        if self.blob_service_client:
            path_to_check = lore.current_image.blob_path if lore.current_image else lore.image_blob_path
            image_url = await self._check_and_get_image_url(path_to_check)
        
        return {
            "id": lore.id,
            "title": lore.title,
            "description": lore.description,
            "category": lore.category.value if lore.category else None,
            "current_location_id": lore.current_location_id,
            "placement_note": lore.placement_note,
            "image_url": image_url,
            "created_at": lore.created_at.isoformat() if lore.created_at else None,
            "updated_at": lore.updated_at.isoformat() if lore.updated_at else None
        }
    
    async def _serialize_story(self, story: Story) -> Dict[str, Any]:
        """Convert Story model to serializable dict"""
        image_url = None
        if self.blob_service_client:
            path_to_check = story.current_image.blob_path if story.current_image else story.image_blob_path
            image_url = await self._check_and_get_image_url(path_to_check)
        
        return {
            "id": story.id,
            "title": story.title,
            "short_description": story.short_description,
            "world_id": story.world_id,
            "user_id": story.user_id,
            "image_url": image_url,
            "created_at": story.created_at.isoformat() if story.created_at else None,
            "updated_at": story.updated_at.isoformat() if story.updated_at else None
        }
    
    def _serialize_act(self, act: Act) -> Dict[str, Any]:
        """Convert Act model to serializable dict"""
        return {
            "id": act.id,
            "story_id": act.story_id,
            "act_number": act.act_number,
            "title": act.title,
            "description": act.description,
            "act_summary": act.act_summary,
            "writer_notes": act.writer_notes,
            "system_prompt_id": act.system_prompt_id,
            "story_class_id": act.story_class_id,
            "created_at": act.created_at.isoformat() if act.created_at else None,
            "updated_at": act.updated_at.isoformat() if act.updated_at else None
        }
    
    def _serialize_scene(self, scene: Scene) -> Dict[str, Any]:
        """Convert Scene model to serializable dict"""
        return {
            "id": scene.id,
            "act_id": scene.act_id,
            "scene_number": scene.scene_number,
            "title": scene.title,
            "summary": scene.summary,
            "content": scene.content,
            "characters_present": scene.characters_present,
            "plot_points": scene.plot_points,
            "mood": scene.mood,
            "story_class_id": scene.story_class_id,
            "current_image_id": scene.current_image_id,
            "created_at": scene.created_at.isoformat() if scene.created_at else None,
            "updated_at": scene.updated_at.isoformat() if scene.updated_at else None
        }
    
    async def get_element_by_id(self, element_type: str, element_id: int, world_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific element by type and ID"""
        try:
            if element_type == "character":
                result = await self.db.execute(
                    select(Character)
                    .where(Character.id == element_id)
                    .where(Character.world_id == world_id)
                )
                element = result.scalar_one_or_none()
                return self._serialize_character(element) if element else None
                
            elif element_type == "location":
                result = await self.db.execute(
                    select(Location)
                    .where(Location.id == element_id)
                    .where(Location.world_id == world_id)
                )
                element = result.scalar_one_or_none()
                return self._serialize_location(element) if element else None
                
            elif element_type == "lore_item":
                result = await self.db.execute(
                    select(LoreItem)
                    .where(LoreItem.id == element_id)
                    .where(LoreItem.world_id == world_id)
                )
                element = result.scalar_one_or_none()
                return self._serialize_lore_item(element) if element else None
                
            elif element_type == "story":
                result = await self.db.execute(
                    select(Story)
                    .where(Story.id == element_id)
                    .where(Story.world_id == world_id)
                )
                element = result.scalar_one_or_none()
                return self._serialize_story(element) if element else None
                
            elif element_type == "act":
                result = await self.db.execute(
                    select(Act)
                    .options(selectinload(Act.story))
                    .where(Act.id == element_id)
                )
                element = result.scalar_one_or_none()
                if element and element.story.world_id == world_id:
                    return self._serialize_act(element)
                return None
                
            elif element_type == "scene":
                result = await self.db.execute(
                    select(Scene)
                    .options(selectinload(Scene.act).selectinload(Act.story))
                    .where(Scene.id == element_id)
                )
                element = result.scalar_one_or_none()
                if element and element.act.story.world_id == world_id:
                    return self._serialize_scene(element)
                return None
                
            else:
                logger.warning(f"Unknown element type: {element_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting element {element_type}:{element_id}: {str(e)}")
            return None
    
    async def _check_and_get_image_url(self, blob_path: Optional[str]) -> Optional[str]:
        """Check if blob exists and return public URL"""
        if not blob_path or not self.blob_service_client:
            return None
        try:
            container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
            blob_client = self.blob_service_client.get_blob_client(container=container_name, blob=blob_path)
            if await blob_client.exists():
                return blob_client.url
        except Exception as e:
            logger.warning(f"Could not check for blob '{blob_path}' due to error: {e}")
        return None