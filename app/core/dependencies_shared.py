"""Core application helpers for dependencies shared."""

# /story_app/app/core/dependencies_shared.py
from fastapi import Depends, HTTPException, status, Path
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.models.world import World as ModelWorld
from app.models.character import Character as ModelCharacter
from app.models.location import Location as ModelLocation
from app.models.lore_item import LoreItem as ModelLoreItem
from app.models.story import Story as ModelStory
from app.models.act import Act as ModelAct
from app.crud import world as crud_world
from app.crud import character as crud_character
from app.crud import location as crud_location
from app.crud import lore_item as crud_lore_item
from app.crud import story as crud_story
from app.crud import act as crud_act

logger = logging.getLogger(__name__)

async def get_world_and_verify_ownership(
    world_id: int = Path(..., description="The ID of the world to retrieve"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> ModelWorld:
    """Return world and verify ownership."""
    db_world = await crud_world.get_world_for_user(db, world_id=world_id, user_id=current_user.id)
    if not db_world:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="World not found or you do not have permission to access it."
        )
    return db_world

async def get_character_and_verify_ownership(
    character_id: int = Path(..., description="The ID of the character"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> ModelCharacter:
    """Return character and verify ownership."""
    db_character = await crud_character.get_character(db, character_id=character_id)
    if not db_character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found")
    # Check ownership via the character's parent world
    if not db_character.world or db_character.world.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this character.")
    return db_character

async def get_location_and_verify_ownership(
    location_id: int = Path(..., description="The ID of the location"), 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user)
) -> ModelLocation:
    """Return location and verify ownership."""
    db_location = await crud_location.get_location(db, location_id=location_id)
    if not db_location or not db_location.world or db_location.world.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Location not found or not accessible.")
    return db_location

async def get_lore_item_and_verify_ownership(
    lore_item_id: int = Path(..., description="The ID of the lore item"), 
    db: AsyncSession = Depends(get_db_session), 
    current_user: User = Depends(get_current_active_user)
) -> ModelLoreItem:
    """Return lore item and verify ownership."""
    db_lore_item = await crud_lore_item.get_lore_item(db, lore_item_id=lore_item_id)
    if not db_lore_item or not db_lore_item.world or db_lore_item.world.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Lore item not found or not accessible.")
    return db_lore_item

async def get_story_and_verify_ownership( 
    story_id: int = Path(..., description="The ID of the story"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> ModelStory:
    """Return story and verify ownership."""
    db_story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not db_story:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found or not accessible.")
    return db_story

async def verify_story_owner_for_act_operations(
    story_id: int = Path(..., description="The ID of the story for which act operations are being performed"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> ModelStory:
    """Provide dependency and core support for verify story owner for act operations."""
    story = await crud_story.get_story_for_user(db, story_id=story_id, user_id=current_user.id)
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Story not found or user does not have access"
        )
    return story

async def get_act_and_verify_ownership(
    act_id: int = Path(..., description="The ID of the act"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> ModelAct:
    """
    Dependency to fetch an Act by ID and verify that the current user owns
    the parent Story of this Act. Eager loads act.story.
    """
    logger.debug(f"Dependency (shared): Verifying ownership for Act ID: {act_id}, User: {current_user.username}")
    db_act = await crud_act.get_act(db, act_id=act_id) 
    if not db_act:
        logger.warning(f"Dependency (shared): User {current_user.username} attempting to access non-existent act ID: {act_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")

    if not db_act.story or db_act.story.user_id != current_user.id: 
        logger.warning(f"Dependency (shared): User {current_user.username} forbidden to access act ID {act_id} (parent story ID {db_act.story_id} not owned or story link missing).")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this act's story")
    
    logger.debug(f"Dependency (shared): Ownership verified for Act ID: {act_id}")
    return db_act
