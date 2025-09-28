# /ai_rag_story_app/app/core/dependencies_act.py
from fastapi import Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User as ModelUser
from app.models.story import Story as ModelStory
from app.models.act import Act as ModelAct
from app.crud import story as crud_story
from app.crud import act as crud_act

logger = logging.getLogger(__name__)

async def verify_story_owner_for_act_operations(
    story_id: int = Path(..., description="The ID of the story for which act operations are being performed"),
    current_user: ModelUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> ModelStory:
    """
    Dependency to verify that the current user owns the story
    before performing operations on its acts.
    """
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        logger.warning(f"User {current_user.username} attempt to access unowned/non-existent story ID {story_id} for act operation.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found or user does not have access"
        )
    return story

async def get_act_and_verify_ownership(
    act_id: int = Path(..., description="The ID of the act"),
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
) -> ModelAct:
    """
    Dependency to fetch an Act by ID and verify that the current user owns
    the parent Story of this Act. Eager loads act.story.
    """
    logger.debug(f"Dependency (shared): Verifying ownership for Act ID: {act_id}, User: {current_user.username}")
    # crud_act.get_act already eager loads story and system_prompt
    db_act = await crud_act.get_act(db, act_id=act_id) 
    if not db_act:
        logger.warning(f"Dependency (shared): User {current_user.username} attempting to access non-existent act ID: {act_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")

    # The story is eager loaded by crud_act.get_act
    if not db_act.story or db_act.story.user_id != current_user.id: 
        logger.warning(f"Dependency (shared): User {current_user.username} forbidden to access act ID {act_id} (parent story ID {db_act.story_id} not owned or story link missing).")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this act's story")
    
    logger.debug(f"Dependency (shared): Ownership verified for Act ID: {act_id}")
    return db_act