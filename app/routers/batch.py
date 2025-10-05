# /ai_rag_story_app/app/routers/batch.py

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import logging

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user_from_bearer_token
from app.models.user import User
from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.schemas.base import ApiResponse
from app.schemas.character import CharacterBase, CharacterCreate
from app.schemas.location import LocationBase, LocationCreate
from app.schemas.lore_item import LoreItemBase, LoreItemCreate

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/batch",
    tags=["batch-operations"],
)

# --- Batch Response Schemas ---
class BatchResponse:
    """Response for batch operations"""
    success_count: int
    error_count: int
    results: List[dict]

# Character batch endpoints
@router.post("/characters", response_model=ApiResponse)
async def create_batch_characters(
    characters: List[CharacterCreate],
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user_from_bearer_token)
):
    """
    Create multiple characters in batch.
    """
    try:
        logger.info(f"Creating batch characters for user {current_user.id}: {len(characters)} items")

        created_characters = []
        errors = []

        for char_data in characters:
            try:
                # Create character
                db_character = Character(
                    user_id=current_user.id,
                    world_id=char_data.world_id,
                    name=char_data.name,
                    title=char_data.title,
                    backstory=char_data.backstory,
                    personality=char_data.personality,
                    motivations=char_data.motivations,
                    physical_description=char_data.physical_description,
                    age=char_data.age,
                    occupation=char_data.occupation,
                    skills=char_data.skills,
                    relationships=char_data.relationships
                )

                db.add(db_character)
                await db.commit()
                await db.refresh(db_character)

                created_characters.append({
                    "id": db_character.id,
                    "name": db_character.name,
                    "status": "created"
                })

            except Exception as e:
                logger.warning(f"Failed to create character '{char_data.name}': {e}")
                errors.append({
                    "name": char_data.name,
                    "error": str(e)
                })

        results = created_characters + errors
        response = BatchResponse(
            success_count=len(created_characters),
            error_count=len(errors),
            results=results
        )

        logger.info(f"Batch character creation completed: {len(created_characters)} success, {len(errors)} errors")
        return ApiResponse.success_response(data=response)

    except Exception as e:
        logger.error(f"Error in batch character creation for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create batch characters"
        ) from e

@router.get("/characters", response_model=ApiResponse)
async def get_batch_characters(
    character_ids: List[int],
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user_from_bearer_token)
):
    """
    Get multiple characters by IDs in batch.
    """
    try:
        if not character_ids:
            return ApiResponse.success_response(data=[])

        logger.info(f"Getting batch characters for user {current_user.id}: {len(character_ids)} items")

        # Query characters that belong to the current user
        query = select(Character).where(
            Character.id.in_(character_ids),
            Character.user_id == current_user.id
        )
        result = await db.execute(query)
        characters = result.scalars().all()

        # Convert to response schema
        character_responses = [CharacterBase.model_validate(char) for char in characters]

        logger.info(f"Retrieved {len(characters)} characters from batch query")
        return ApiResponse.success_response(data=character_responses)

    except Exception as e:
        logger.error(f"Error retrieving batch characters for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve batch characters"
        ) from e

# Location batch endpoints
@router.post("/locations", response_model=ApiResponse)
async def create_batch_locations(
    locations: List[LocationCreate],
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user_from_bearer_token)
):
    """
    Create multiple locations in batch.
    """
    try:
        logger.info(f"Creating batch locations for user {current_user.id}: {len(locations)} items")

        created_locations = []
        errors = []

        for loc_data in locations:
            try:
                # Create location
                db_location = Location(
                    user_id=current_user.id,
                    world_id=loc_data.world_id,
                    name=loc_data.name,
                    description=loc_data.description,
                    type=loc_data.type,
                    climate=loc_data.climate,
                    geography=loc_data.geography,
                    population=loc_data.population,
                    government=loc_data.government,
                    economy=loc_data.economy,
                    culture=loc_data.culture
                )

                db.add(db_location)
                await db.commit()
                await db.refresh(db_location)

                created_locations.append({
                    "id": db_location.id,
                    "name": db_location.name,
                    "status": "created"
                })

            except Exception as e:
                logger.warning(f"Failed to create location '{loc_data.name}': {e}")
                errors.append({
                    "name": loc_data.name,
                    "error": str(e)
                })

        results = created_locations + errors
        response = BatchResponse(
            success_count=len(created_locations),
            error_count=len(errors),
            results=results
        )

        logger.info(f"Batch location creation completed: {len(created_locations)} success, {len(errors)} errors")
        return ApiResponse.success_response(data=response)

    except Exception as e:
        logger.error(f"Error in batch location creation for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create batch locations"
        ) from e

@router.get("/locations", response_model=ApiResponse)
async def get_batch_locations(
    location_ids: List[int],
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user_from_bearer_token)
):
    """
    Get multiple locations by IDs in batch.
    """
    try:
        if not location_ids:
            return ApiResponse.success_response(data=[])

        logger.info(f"Getting batch locations for user {current_user.id}: {len(location_ids)} items")

        # Query locations that belong to the current user
        query = select(Location).where(
            Location.id.in_(location_ids),
            Location.user_id == current_user.id
        )
        result = await db.execute(query)
        locations = result.scalars().all()

        # Convert to response schema
        location_responses = [LocationBase.model_validate(loc) for loc in locations]

        logger.info(f"Retrieved {len(locations)} locations from batch query")
        return ApiResponse.success_response(data=location_responses)

    except Exception as e:
        logger.error(f"Error retrieving batch locations for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve batch locations"
        ) from e

# Lore Item batch endpoints
@router.post("/lore-items", response_model=ApiResponse)
async def create_batch_lore_items(
    lore_items: List[LoreItemCreate],
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user_from_bearer_token)
):
    """
    Create multiple lore items in batch.
    """
    try:
        logger.info(f"Creating batch lore-items for user {current_user.id}: {len(lore_items)} items")

        created_lore_items = []
        errors = []

        for lore_data in lore_items:
            try:
                # Create lore item
                db_lore_item = LoreItem(
                    user_id=current_user.id,
                    world_id=lore_data.world_id,
                    name=lore_data.name,
                    description=lore_data.description,
                    type=lore_data.type,
                    category=lore_data.category,
                    rarity=lore_data.rarity,
                    lore=lore_data.lore
                )

                db.add(db_lore_item)
                await db.commit()
                await db.refresh(db_lore_item)

                created_lore_items.append({
                    "id": db_lore_item.id,
                    "name": db_lore_item.name,
                    "status": "created"
                })

            except Exception as e:
                logger.warning(f"Failed to create lore item '{lore_data.name}': {e}")
                errors.append({
                    "name": lore_data.name,
                    "error": str(e)
                })

        results = created_lore_items + errors
        response = BatchResponse(
            success_count=len(created_lore_items),
            error_count=len(errors),
            results=results
        )

        logger.info(f"Batch lore-item creation completed: {len(created_lore_items)} success, {len(errors)} errors")
        return ApiResponse.success_response(data=response)

    except Exception as e:
        logger.error(f"Error in batch lore-item creation for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create batch lore items"
        ) from e

@router.get("/lore-items", response_model=ApiResponse)
async def get_batch_lore_items(
    lore_item_ids: List[int],
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user_from_bearer_token)
):
    """
    Get multiple lore items by IDs in batch.
    """
    try:
        if not lore_item_ids:
            return ApiResponse.success_response(data=[])

        logger.info(f"Getting batch lore-items for user {current_user.id}: {len(lore_item_ids)} items")

        # Query lore items that belong to the current user
        query = select(LoreItem).where(
            LoreItem.id.in_(lore_item_ids),
            LoreItem.user_id == current_user.id
        )
        result = await db.execute(query)
        lore_items = result.scalars().all()

        # Convert to response schema
        lore_item_responses = [LoreItemBase.model_validate(item) for item in lore_items]

        logger.info(f"Retrieved {len(lore_items)} lore items from batch query")
        return ApiResponse.success_response(data=lore_item_responses)

    except Exception as e:
        logger.error(f"Error retrieving batch lore items for user {current_user.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve batch lore items"
        ) from e