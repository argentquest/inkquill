# /ai_rag_story_app/app/services/story_service.py

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models.story import Story
from app.models.world import World
from app.models.user import User
from app.models.act import Act
from app.schemas.story import StoryCreate, StoryUpdate
from app.crud import story as story_crud
from app.services.mixins import ShadowWorldMixin
from app.services.cost_tracker_service import log_ai_call, log_ai_streaming_call

logger = logging.getLogger(__name__)


class BasicStoryCreate:
    """Schema for Basic Story creation - minimal fields"""
    def __init__(self, title: str, short_description: Optional[str] = None):
        self.title = title
        self.short_description = short_description


class StoryService(ShadowWorldMixin):
    """
    Service for handling story operations with Basic/Advanced story support.
    Extends existing CRUD operations with story_type logic.
    """
    
    async def create_basic_story(
        self, 
        db: AsyncSession, 
        story_data: BasicStoryCreate, 
        user: User
    ) -> Story:
        """
        Create a Basic Story with shadow world and default first act.
        
        Args:
            db: Async database session
            story_data: Basic story creation data
            user: User creating the story
            
        Returns:
            Created story with shadow world and first act
            
        Raises:
            Exception: If shadow world creation fails
        """
        logger.info(f"Creating Basic Story '{story_data.title}' for user {user.id}")
        
        try:
            # Create shadow world directly with async session
            world_name = f"{story_data.title} World"
            shadow_world = World(
                name=world_name,
                description=f"Auto-generated world for the story '{story_data.title}'",
                short_description=f"World for {story_data.title}",
                user_id=user.id,
                is_shadow=True,  # Mark as shadow world
                is_free_chat_enabled=False
            )
            
            db.add(shadow_world)
            await db.flush()
            await db.refresh(shadow_world)
            
            # Create Basic Story
            story_create_data = StoryCreate(
                title=story_data.title,
                short_description=story_data.short_description,
                world_id=shadow_world.id,
                story_type='basic'  # Set as Basic Story
            )
            
            story = await story_crud.create_story(
                db=db, 
                story=story_create_data, 
                user_id=user.id
            )
            
            # Create first act automatically
            first_act = Act(
                title="Act 1",
                act_number=1,
                story_id=story.id,
                description=""  # Empty description, user will fill in editor
            )
            
            db.add(first_act)
            await db.flush()
            await db.refresh(first_act)
            
            logger.info(f"Basic Story '{story.title}' (ID: {story.id}) created with shadow world {shadow_world.id}")
            return story, first_act
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create Basic Story: {e}")
            raise
    
    async def upgrade_story_to_advanced(
        self, 
        db: AsyncSession, 
        story_id: int, 
        user_id: int,
        new_world_name: Optional[str] = None
    ) -> Story:
        """
        Upgrade a Basic Story to Advanced Story.
        
        Args:
            db: Async database session
            story_id: ID of story to upgrade
            user_id: User ID (for security)
            new_world_name: Optional new name for the revealed world
            
        Returns:
            Upgraded story
            
        Raises:
            ValueError: If story is not Basic or doesn't belong to user
        """
        logger.info(f"Upgrading story {story_id} to Advanced for user {user_id}")
        
        # Get story and verify it's Basic
        story = await story_crud.get_story_for_user(db, story_id, user_id)
        if not story:
            raise ValueError("Story not found or access denied")
            
        if story.story_type != 'basic':
            raise ValueError("Story is already Advanced")
        
        # Convert to sync session for world operations
        sync_db = Session(bind=db.bind.sync_engine)
        try:
            # Get the shadow world
            shadow_world = sync_db.query(World).filter(World.id == story.world_id).first()
            if not shadow_world:
                raise ValueError("Shadow world not found")
                
            # Reveal the shadow world
            self.reveal_shadow_world(
                db=sync_db, 
                world=shadow_world, 
                new_name=new_world_name
            )
            
            # Update story type to Advanced
            story_update = StoryUpdate(story_type='advanced')
            story = await story_crud.update_story(
                db=db, 
                story_id=story_id, 
                story_update=story_update, 
                user_id=user_id
            )
            
            logger.info(f"Story {story_id} upgraded to Advanced, world {shadow_world.id} revealed")
            return story
            
        except Exception as e:
            sync_db.rollback()
            logger.error(f"Failed to upgrade story: {e}")
            raise
        finally:
            sync_db.close()
    
    async def get_stories_by_type(
        self, 
        db: AsyncSession, 
        user_id: int, 
        story_type: Optional[str] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Story]:
        """
        Get stories filtered by type.
        
        Args:
            db: Async database session
            user_id: User ID
            story_type: Filter by 'basic', 'advanced', or None for all
            skip: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of stories
        """
        if story_type:
            # Use existing CRUD with additional filter
            # Note: This would need to be added to story_crud.py
            logger.debug(f"Fetching {story_type} stories for user {user_id}")
            # For now, get all and filter (inefficient, but works)
            all_stories = await story_crud.get_stories_by_user(db, user_id, skip=0, limit=1000)
            filtered_stories = [s for s in all_stories if s.story_type == story_type]
            return filtered_stories[skip:skip+limit]
        else:
            return await story_crud.get_stories_by_user(db, user_id, skip, limit)
    
    def is_basic_story(self, story: Story) -> bool:
        """Check if a story is a Basic Story"""
        return story.story_type == 'basic'
    
    def is_advanced_story(self, story: Story) -> bool:
        """Check if a story is an Advanced Story"""
        return story.story_type == 'advanced'
    
    def get_available_features(self, story: Story) -> dict:
        """
        Get available features for a story based on its type.
        
        Args:
            story: Story instance
            
        Returns:
            Dict of feature availability
        """
        if self.is_basic_story(story):
            return {
                'characters': False,
                'locations': False,
                'hierarchy_view': False,
                'world_detail': False,
                'world_chat': True,
                'lore_items': True,
                'acts': True,
                'scenes': True,
                'scene_character_associations': False,
                'scene_location_associations': False,
                'scene_lore_associations': False,
                'ai_summary_generation': True,  # Support AI summaries for story/act/scene
                'act_metadata_generation': False,  # No complex metadata, only summaries
                'scene_metadata_generation': False,  # No complex metadata, only summaries
                'publishing': True,  # Full publishing capabilities (same as Advanced)
                'ai_assistance': True,
                'upgrade_available': True
            }
        else:  # Advanced story
            return {
                'characters': True,
                'locations': True,
                'hierarchy_view': True,
                'world_detail': True,
                'world_chat': True,
                'lore_items': True,
                'acts': True,
                'scenes': True,
                'publishing': True,
                'ai_assistance': True,
                'upgrade_available': False
            }
    
    async def log_basic_story_ai_call(
        self,
        db: AsyncSession,
        user_id: int,
        model_config,  # AIModelConfiguration instance
        prompt_type: str,
        input_prompt: str,
        output_text: str,
        story_id: Optional[int] = None,
        duration_ms: Optional[int] = None
    ) -> Optional[int]:
        """
        Log an AI call for Basic Story operations with proper cost tracking.
        
        Args:
            db: Database session
            user_id: User making the call
            model_config: AI model configuration
            prompt_type: Type of Basic Story prompt used
            input_prompt: Full input sent to AI
            output_text: AI response
            story_id: Associated story ID
            duration_ms: Call duration
            
        Returns:
            Log ID if successful
        """
        try:
            call_type = f"basic_story_{prompt_type}"
            
            # Use streaming logger for Basic Story calls (most likely streaming)
            log_id = await log_ai_streaming_call(
                user_id=user_id,
                model_config=model_config,
                input_prompt=input_prompt,
                output_text=output_text,
                call_type=call_type,
                duration_ms=duration_ms,
                object_id=story_id,
                db=db
            )
            
            logger.info(f"Logged Basic Story AI call: {call_type} for user {user_id}, story {story_id}")
            return log_id
            
        except Exception as e:
            logger.error(f"Failed to log Basic Story AI call: {e}")
            return None
    
    def get_basic_story_prompt_variables(
        self, 
        story: Story, 
        content: str,
        assistance_type: str = "general",
        **kwargs
    ) -> dict:
        """
        Get variables for Basic Story AI prompts (context-free).
        
        Args:
            story: Story instance
            content: Current story content
            assistance_type: Type of assistance needed
            **kwargs: Additional variables
            
        Returns:
            Dict of prompt variables
        """
        base_variables = {
            'story_title': story.title,
            'story_content': content,
            'assistance_type': assistance_type
        }
        
        # Add any additional variables
        base_variables.update(kwargs)
        
        return base_variables
    
    def should_use_basic_story_prompts(self, story: Story) -> bool:
        """
        Determine if Basic Story prompts should be used.
        
        Args:
            story: Story instance
            
        Returns:
            True if Basic Story prompts should be used
        """
        return self.is_basic_story(story)
    
    def get_context_for_ai(self, story: Story) -> dict:
        """
        Get AI context based on story type.
        
        Args:
            story: Story instance
            
        Returns:
            Context dict for AI calls
        """
        if self.is_basic_story(story):
            # Basic Stories: No world context
            return {
                'story_type': 'basic',
                'world_context': None,
                'characters': [],
                'locations': [],
                'lore_items': [],
                'use_basic_prompts': True
            }
        else:
            # Advanced Stories: Full world context (would be loaded separately)
            return {
                'story_type': 'advanced', 
                'world_context': 'full',  # Placeholder - actual context loaded elsewhere
                'use_basic_prompts': False
            }
    
    async def upgrade_story_to_advanced(
        self, 
        db: AsyncSession, 
        story_id: int, 
        user: User,
        world_id: Optional[int] = None
    ) -> Story:
        """
        Upgrade a Basic Story to an Advanced Story.
        
        Args:
            db: Database session
            story_id: ID of the story to upgrade
            user: User performing the upgrade
            world_id: Optional world ID to associate with (if None, creates new world)
            
        Returns:
            Upgraded story
            
        Raises:
            ValueError: If story not found, already advanced, or user doesn't have access
        """
        # Get the story
        story = await story_crud.get_story_by_id(db, story_id, user.id)
        if not story:
            raise ValueError("Story not found or access denied")
        
        if story.story_type == 'advanced':
            raise ValueError("Story is already an Advanced Story")
        
        logger.info(f"Upgrading Basic Story {story_id} to Advanced for user {user.id}")
        
        # Handle world assignment
        if world_id:
            # Verify user owns the target world
            world = await db.get(World, world_id)
            if not world or world.owner_id != user.id:
                raise ValueError("Target world not found or access denied")
        else:
            # Create a new real world from the shadow world content
            shadow_world = story.world
            
            world = World(
                name=f"{story.title} World",
                description=f"World for the story '{story.title}', upgraded from Basic Story",
                owner_id=user.id,
                is_shadow=False  # This is a real world
            )
            
            db.add(world)
            await db.flush()  # Get the ID
        
        # Update the story
        story.story_type = 'advanced'
        story.world_id = world.id
        
        # The shadow world will be automatically cleaned up if not referenced elsewhere
        
        await db.commit()
        await db.refresh(story)
        
        logger.info(f"Successfully upgraded story {story_id} to Advanced Story with world {world.id}")
        return story


# Global service instance
story_service = StoryService()