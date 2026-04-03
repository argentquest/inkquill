"""Database CRUD helpers for story."""

# /story_app/app/crud/story.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging

from app.models import story as model_story
from app.schemas import story as schema_story

logger = logging.getLogger(__name__)

async def create_story(db: AsyncSession, story: schema_story.StoryCreate, user_id: int) -> model_story.Story:
    """Create story."""
    logger.info(f"User ID {user_id} creating new story: '{story.title}', linking to world_id: {story.world_id}")
    db_story = model_story.Story(**story.model_dump(), user_id=user_id)
    db.add(db_story)
    await db.flush()
    await db.refresh(db_story, attribute_names=['OwnerUser', 'world', 'published_version'])
    logger.info(f"Story '{db_story.title}' (ID: {db_story.id}) added to session.")
    return db_story

async def get_story(db: AsyncSession, story_id: int) -> Optional[model_story.Story]:
    """Return story."""
    logger.debug(f"Fetching story with ID: {story_id}")
    result = await db.execute(
        select(model_story.Story)
        .filter(model_story.Story.id == story_id)
        .options(
            selectinload(model_story.Story.OwnerUser), 
            selectinload(model_story.Story.world),
            selectinload(model_story.Story.published_version)
        )
    )
    return result.scalars().first()

async def get_story_for_user(db: AsyncSession, story_id: int, user_id: int) -> Optional[model_story.Story]:
    """Return story for user."""
    logger.debug(f"Fetching story ID: {story_id} for user ID: {user_id}")
    result = await db.execute(
        select(model_story.Story)
        .filter(model_story.Story.id == story_id, model_story.Story.user_id == user_id)
        .options(
            selectinload(model_story.Story.world), 
            selectinload(model_story.Story.OwnerUser),
            selectinload(model_story.Story.published_version),
            selectinload(model_story.Story.current_image)
        )
    )
    return result.scalars().first()

async def get_stories_by_user(
    db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
) -> List[model_story.Story]:
    """Return stories by user."""
    logger.debug(f"Fetching stories for user ID: {user_id}, skip: {skip}, limit: {limit}")
    result = await db.execute(
        select(model_story.Story)
        .filter(model_story.Story.user_id == user_id)
        .options(
            selectinload(model_story.Story.world), 
            selectinload(model_story.Story.OwnerUser),
            selectinload(model_story.Story.published_version),
            selectinload(model_story.Story.current_image)
        )
        .offset(skip)
        .limit(limit)
        .order_by(model_story.Story.created_at.desc())
    )
    return result.scalars().all()

async def get_stories_by_world_id(
    db: AsyncSession, world_id: int, user_id: Optional[int] = None, skip: int = 0, limit: int = 100
) -> List[model_story.Story]:
    """Return stories by world id."""
    logger.debug(f"Fetching stories for world ID: {world_id}, user ID filter: {user_id}, skip: {skip}, limit: {limit}")
    query = select(model_story.Story).filter(model_story.Story.world_id == world_id)
    if user_id is not None:
        query = query.filter(model_story.Story.user_id == user_id)
    
    query = query.options(
        selectinload(model_story.Story.OwnerUser), 
        selectinload(model_story.Story.acts),
        selectinload(model_story.Story.published_version)
    )
    query = query.order_by(model_story.Story.title).offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()

async def get_all_stories(
    db: AsyncSession, skip: int = 0, limit: int = 100
) -> List[model_story.Story]:
    """Return all stories."""
    logger.debug(f"Fetching all stories, skip: {skip}, limit: {limit}")
    result = await db.execute(
        select(model_story.Story)
        .options(
            selectinload(model_story.Story.OwnerUser), 
            selectinload(model_story.Story.world),
            selectinload(model_story.Story.published_version)
        )
        .offset(skip)
        .limit(limit)
        .order_by(model_story.Story.created_at.desc())
    )
    return result.scalars().all()

async def update_story(
    db: AsyncSession, story_id: int, story_update: schema_story.StoryUpdate, user_id: int
) -> Optional[model_story.Story]:
    """Update story."""
    db_story = await get_story_for_user(db, story_id=story_id, user_id=user_id)
    if not db_story:
        return None
    update_data = story_update.model_dump(exclude_unset=True)
    logger.info(f"User ID {user_id} updating story ID: {story_id} with data: {update_data}")
    
    for key, value in update_data.items():
        if hasattr(db_story, key):
            setattr(db_story, key, value)
    
    db.add(db_story)
    await db.flush()
    await db.refresh(db_story)
    await db.refresh(db_story, attribute_names=['OwnerUser', 'world', 'published_version'])
    logger.info(f"Story ID: {story_id} updated in session.")
    return db_story

async def delete_story(db: AsyncSession, story_id: int, user_id: int) -> Optional[model_story.Story]:
    """Delete story."""
    db_story = await get_story_for_user(db, story_id=story_id, user_id=user_id)
    if not db_story:
        return None
    logger.info(f"User ID {user_id} deleting story ID: {story_id} ('{db_story.title}')")
    await db.delete(db_story)
    await db.flush()
    logger.info(f"Story ID: {story_id} marked for deletion in session.")
    return db_story
