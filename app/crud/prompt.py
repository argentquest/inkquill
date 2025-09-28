# /ai_rag_story_app/app/crud/prompt.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload 
from typing import List, Optional
import logging

from app.models.prompt import Prompt, PromptTypeEnum, AgeTargetEnum 
from app.schemas.prompt import PromptCreate, PromptUpdate 

logger = logging.getLogger(__name__)

async def create_prompt(db: AsyncSession, prompt_in: PromptCreate, creator_user_id: int) -> Prompt:
    prompt_data = prompt_in.model_dump()
    logger.info(f"Creating prompt '{prompt_data.get('title')}' by user_id: {creator_user_id}")
    db_prompt = Prompt(**prompt_data, user_id=creator_user_id, last_updated_by_user_id=creator_user_id)
    db.add(db_prompt)
    await db.flush()
    await db.refresh(db_prompt)
    logger.info(f"Prompt ID: {db_prompt.id} added to session.")
    return db_prompt

async def get_prompt(db: AsyncSession, prompt_id: int) -> Optional[Prompt]:
    logger.debug(f"Fetching prompt with ID: {prompt_id}")
    result = await db.execute(
        select(Prompt).filter(Prompt.id == prompt_id).options(selectinload(Prompt.owner), selectinload(Prompt.last_updated_by))
    )
    return result.scalars().first()

async def get_prompts_by_user(
    db: AsyncSession, user_id: int, prompt_type: Optional[PromptTypeEnum] = None,
    age_target: Optional[AgeTargetEnum] = None, is_active: Optional[bool] = None, 
    skip: int = 0, limit: int = 100
) -> List[Prompt]:
    query = select(Prompt).filter(Prompt.user_id == user_id)
    if prompt_type is not None: query = query.filter(Prompt.prompt_type == prompt_type)
    if age_target is not None: query = query.filter(Prompt.age_target == age_target)
    if is_active is not None: query = query.filter(Prompt.is_active == is_active)
    query = query.order_by(Prompt.age_target, Prompt.prompt_type, Prompt.title).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def get_shared_prompts(
    db: AsyncSession, prompt_type: Optional[PromptTypeEnum] = None,
    age_target: Optional[AgeTargetEnum] = None, is_active: Optional[bool] = None, 
    skip: int = 0, limit: int = 100
) -> List[Prompt]:
    query = select(Prompt)
    if prompt_type is not None: query = query.filter(Prompt.prompt_type == prompt_type)
    if age_target is not None: query = query.filter(Prompt.age_target == age_target)
    if is_active is not None: query = query.filter(Prompt.is_active == is_active)
    query = query.order_by(Prompt.age_target, Prompt.prompt_type, Prompt.title).offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def update_prompt(db: AsyncSession, db_prompt: Prompt, prompt_in: PromptUpdate, updater_user_id: int) -> Prompt:
    update_data = prompt_in.model_dump(exclude_unset=True)
    logger.info(f"Updating prompt ID: {db_prompt.id} by user_id: {updater_user_id}")
    if update_data:
        for key, value in update_data.items():
            if hasattr(db_prompt, key):
                setattr(db_prompt, key, value)
    db_prompt.last_updated_by_user_id = updater_user_id
    db.add(db_prompt)
    await db.flush()
    await db.refresh(db_prompt)
    logger.info(f"Prompt ID: {db_prompt.id} updated in session.")
    return db_prompt

async def delete_prompt(db: AsyncSession, db_prompt: Prompt) -> Prompt:
    logger.info(f"Deleting prompt ID: {db_prompt.id}")
    await db.delete(db_prompt)
    await db.flush()
    logger.info(f"Prompt ID: {db_prompt.id} marked for deletion in session.")
    return db_prompt


async def get_prompts_by_type(
    db: AsyncSession, 
    prompt_type: PromptTypeEnum,
    is_active: bool = True
) -> List[Prompt]:
    """Get all prompts of a specific type, optionally filtered by active status."""
    logger.debug(f"Fetching prompts of type: {prompt_type}, is_active: {is_active}")
    query = select(Prompt).filter(Prompt.prompt_type == prompt_type)
    if is_active is not None:
        query = query.filter(Prompt.is_active == is_active)
    query = query.order_by(Prompt.title)
    result = await db.execute(query)
    return result.scalars().all()