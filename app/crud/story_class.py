"""Database CRUD helpers for story class."""

# /story_app/app/crud/story_class.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from typing import List, Optional
import logging

from app.models.story_class import StoryClass
from app.schemas.story_class import StoryClassCreate, StoryClassUpdate

logger = logging.getLogger(__name__)


async def create_story_class(db: AsyncSession, story_class_in: StoryClassCreate, world_id: int) -> StoryClass:
    """Create a new story class for a world."""
    story_class_data = story_class_in.model_dump()
    logger.info(f"Creating story class for world_id: {world_id} with data: {story_class_data}")
    
    db_story_class = StoryClass(**story_class_data, world_id=world_id)
    db.add(db_story_class)
    await db.flush()
    await db.refresh(db_story_class)
    
    logger.info(f"Story class ID: {db_story_class.id} created for world_id: {world_id}")
    return db_story_class


async def get_story_class(db: AsyncSession, story_class_id: int) -> Optional[StoryClass]:
    """Get a story class by ID."""
    logger.debug(f"Fetching story class with ID: {story_class_id}")
    result = await db.execute(select(StoryClass).filter(StoryClass.id == story_class_id))
    return result.scalars().first()


async def get_story_class_for_world(db: AsyncSession, story_class_id: int, world_id: int) -> Optional[StoryClass]:
    """Get a story class by ID for a specific world."""
    logger.debug(f"Fetching story class ID: {story_class_id} for world ID: {world_id}")
    result = await db.execute(
        select(StoryClass).filter(
            StoryClass.id == story_class_id,
            StoryClass.world_id == world_id
        )
    )
    return result.scalars().first()


async def get_story_classes_by_world(db: AsyncSession, world_id: int, skip: int = 0, limit: int = 100) -> List[StoryClass]:
    """Get all story classes for a world."""
    logger.debug(f"Fetching story classes for world ID: {world_id}, skip: {skip}, limit: {limit}")
    result = await db.execute(
        select(StoryClass)
        .filter(StoryClass.world_id == world_id)
        .order_by(StoryClass.name)
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()


async def update_story_class(db: AsyncSession, db_story_class: StoryClass, story_class_in: StoryClassUpdate) -> StoryClass:
    """Update a story class."""
    update_data = story_class_in.model_dump(exclude_unset=True)
    logger.info(f"Updating story class ID: {db_story_class.id} with data: {update_data}")
    
    if update_data:
        for key, value in update_data.items():
            if hasattr(db_story_class, key):
                setattr(db_story_class, key, value)
    
    db.add(db_story_class)
    await db.flush()
    await db.refresh(db_story_class)
    
    logger.info(f"Story class ID: {db_story_class.id} updated in session.")
    return db_story_class


async def delete_story_class(db: AsyncSession, db_story_class: StoryClass) -> StoryClass:
    """Delete a story class."""
    logger.info(f"Deleting story class ID: {db_story_class.id}")
    await db.delete(db_story_class)
    await db.flush()
    logger.info(f"Story class ID: {db_story_class.id} marked for deletion in session.")
    return db_story_class


async def get_default_story_classes_for_world(db: AsyncSession, world_id: int) -> List[StoryClass]:
    """Get default story classes or create them if they don't exist."""
    existing_classes = await get_story_classes_by_world(db, world_id, limit=10)
    
    if not existing_classes:
        # Create some default story classes
        default_classes = [
            {"name": "Action", "description": "High-energy scenes with conflict or movement", "color": "#FF6B6B"},
            {"name": "Dialog", "description": "Character conversations and interactions", "color": "#4ECDC4"},
            {"name": "Exposition", "description": "World-building and background information", "color": "#45B7D1"},
            {"name": "Emotional", "description": "Character development and emotional moments", "color": "#96CEB4"},
            {"name": "Transition", "description": "Scene transitions and pacing", "color": "#FFEAA7"}
        ]
        
        created_classes = []
        for class_data in default_classes:
            from app.schemas.story_class import StoryClassCreate
            story_class_create = StoryClassCreate(**class_data)
            new_class = await create_story_class(db, story_class_create, world_id)
            created_classes.append(new_class)
        
        await db.commit()
        logger.info(f"Created {len(created_classes)} default story classes for world ID: {world_id}")
        return created_classes
    
    return existing_classes
