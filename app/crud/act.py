# /ai_rag_story_app/app/crud/act.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging

from app.models.act import Act
from app.schemas.act import ActCreate, ActUpdate

logger = logging.getLogger(__name__)

async def create_act(db: AsyncSession, act_in: ActCreate, story_id: int) -> Act:
    """
    Creates a new Act record in the database session.
    """
    logger.info(f"Creating new act '{act_in.title}' (Number: {act_in.act_number}) for story ID: {story_id}")
    db_act = Act(**act_in.model_dump(), story_id=story_id)
    db.add(db_act)
    # Note: A commit will be handled by the calling router function after this.
    return db_act

async def get_act(db: AsyncSession, act_id: int) -> Optional[Act]:
    """
    Retrieves a single Act by its ID, eager loading the story and system prompt.
    """
    logger.debug(f"Fetching act with ID: {act_id}")
    result = await db.execute(
        select(Act)
        .filter(Act.id == act_id)
        .options(selectinload(Act.story), selectinload(Act.system_prompt), selectinload(Act.story_class), selectinload(Act.current_image))
    )
    return result.scalars().first()

async def get_acts_by_story(db: AsyncSession, story_id: int, skip: int = 0, limit: int = 100) -> List[Act]:
    """
    Retrieves a list of Acts for a specific story, ordered by act_number.
    """
    logger.debug(f"Fetching acts for story ID: {story_id}, skip: {skip}, limit: {limit}")
    result = await db.execute(
        select(Act)
        .filter(Act.story_id == story_id)
        .order_by(Act.act_number)
        .offset(skip)
        .limit(limit)
        .options(selectinload(Act.system_prompt), selectinload(Act.story_class), selectinload(Act.scenes), selectinload(Act.current_image)) # Eager load for list view
    )
    return result.scalars().all()

async def update_act(db: AsyncSession, db_act: Act, act_update: ActUpdate, updater_user_id: int) -> Act:
    """
    Updates an existing Act record in the database session.
    """
    update_data = act_update.model_dump(exclude_unset=True)
    logger.info(f"User ID {updater_user_id} updating act ID: {db_act.id} with data: {update_data}")
    for key, value in update_data.items():
        if hasattr(db_act, key):
            setattr(db_act, key, value)
    db.add(db_act)
    return db_act

async def delete_act(db: AsyncSession, db_act: Act) -> Act:
    """
    Marks an Act for deletion in the database session.
    """
    logger.info(f"Deleting act ID: {db_act.id} ('{db_act.title}')")
    await db.delete(db_act)
    return db_act