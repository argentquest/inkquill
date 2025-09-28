# /ai_rag_story_app/app/routers/prompt.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict
import logging

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User as ModelUser
from app.models.prompt import Prompt, PromptTypeEnum, AgeTargetEnum
from app.schemas import prompt as schema_prompt
from app.crud import prompt as crud_prompt

logger = logging.getLogger(__name__)

# --- Router Configuration ---
router = APIRouter(
    prefix="/prompts",
    tags=["prompts"],
    dependencies=[Depends(get_current_active_user)]
)

@router.post("/", response_model=schema_prompt.PromptRead, status_code=status.HTTP_201_CREATED, name="create_new_prompt")
async def create_new_prompt(
    prompt_in: schema_prompt.PromptCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
):
    logger.info(f"User '{current_user.username}' creating new prompt: '{prompt_in.title}'")
    try:
        created_prompt = await crud_prompt.create_prompt(db=db, prompt_in=prompt_in, creator_user_id=current_user.id)
        await db.commit()
        await db.refresh(created_prompt)
        return created_prompt
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating prompt '{prompt_in.title}': {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create prompt.")

@router.get("/story-options", response_model=Dict[str, List[schema_prompt.PromptRead]], name="get_story_options")
async def get_story_options(
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
):
    """Get all story generation options (genres, tones, conflicts) from prompts table."""
    logger.info(f"User '{current_user.username}' fetching story generation options")
    
    try:
        # Fetch all active story-related prompts
        genres = await crud_prompt.get_prompts_by_type(
            db=db, 
            prompt_type=PromptTypeEnum.STORY_GENRE,
            is_active=True
        )
        
        tones = await crud_prompt.get_prompts_by_type(
            db=db,
            prompt_type=PromptTypeEnum.STORY_TONE,
            is_active=True
        )
        
        conflicts = await crud_prompt.get_prompts_by_type(
            db=db,
            prompt_type=PromptTypeEnum.STORY_CONFLICT,
            is_active=True
        )
        
        # Convert SQLAlchemy models to Pydantic schemas for proper serialization
        return {
            "genres": [schema_prompt.PromptRead.model_validate(genre) for genre in genres],
            "tones": [schema_prompt.PromptRead.model_validate(tone) for tone in tones],
            "conflicts": [schema_prompt.PromptRead.model_validate(conflict) for conflict in conflicts]
        }
    except Exception as e:
        logger.error(f"Error fetching story options: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch story options"
        )


@router.get("/character-roles", response_model=List[schema_prompt.PromptRead], name="get_character_roles")
async def get_character_roles(
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
):
    """Get all character role options from prompts table."""
    logger.info(f"User '{current_user.username}' fetching character role options")
    
    try:
        roles = await crud_prompt.get_prompts_by_type(
            db=db,
            prompt_type=PromptTypeEnum.CHARACTER_ROLE,
            is_active=True
        )
        return roles
    except Exception as e:
        logger.error(f"Error fetching character roles: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch character roles"
        )


@router.get("/art-styles", response_model=List[schema_prompt.PromptRead], name="get_art_styles")
async def get_art_styles(
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
):
    """Get all art style options from prompts table."""
    logger.info(f"User '{current_user.username}' fetching art style options")
    
    try:
        styles = await crud_prompt.get_prompts_by_type(
            db=db,
            prompt_type=PromptTypeEnum.IMAGE_STYLE,
            is_active=True
        )
        return styles
    except Exception as e:
        logger.error(f"Error fetching art styles: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not fetch art styles"
        )


@router.get("/my-prompts", response_model=List[schema_prompt.PromptRead], name="list_my_prompts")
async def list_my_prompts(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200),
    filter_prompt_type: Optional[PromptTypeEnum] = Query(None), # Reverted to use Enum directly
    filter_age_target: Optional[AgeTargetEnum] = Query(None),
    filter_is_active: Optional[bool] = Query(None), # This now works with the JS fix
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
):
    logger.info(f"API list_my_prompts called by '{current_user.username}' with filter_prompt_type: {filter_prompt_type}")
    
    # The fix is now in the frontend JS, so the backend can be cleaner.
    # The JS will send `None` (by omitting the param) instead of `""`.
    
    prompts = await crud_prompt.get_prompts_by_user(
        db, user_id=current_user.id, prompt_type=filter_prompt_type,
        age_target=filter_age_target, is_active=filter_is_active, skip=skip, limit=limit
    )
    logger.info(f"API list_my_prompts found {len(prompts)} prompts for user '{current_user.username}' with the specified filters.")
    return prompts

@router.get("/shared", response_model=List[schema_prompt.PromptRead], name="list_shared_prompts")
async def list_shared_prompts(
    skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200),
    filter_prompt_type: Optional[PromptTypeEnum] = Query(None), # Reverted to use Enum directly
    filter_age_target: Optional[AgeTargetEnum] = Query(None),
    filter_is_active: Optional[bool] = Query(True),
    db: AsyncSession = Depends(get_db_session)
):
    logger.info(f"API list_shared_prompts called with filter_prompt_type: {filter_prompt_type}")
    
    prompts = await crud_prompt.get_shared_prompts(
        db, prompt_type=filter_prompt_type,
        age_target=filter_age_target, is_active=filter_is_active, skip=skip, limit=limit
    )
    logger.info(f"API list_shared_prompts found {len(prompts)} prompts with the specified filters.")
    return prompts

# ... the rest of the file (get_single_prompt, update_existing_prompt, delete_existing_prompt) remains unchanged ...

@router.get("/{prompt_id}", response_model=schema_prompt.PromptRead, name="get_single_prompt")
async def get_single_prompt(
    prompt_id: int, db: AsyncSession = Depends(get_db_session), current_user: ModelUser = Depends(get_current_active_user)
):
    db_prompt = await crud_prompt.get_prompt(db, prompt_id=prompt_id)
    if not db_prompt:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prompt not found")
    if db_prompt.user_id is not None and db_prompt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this prompt")
    return db_prompt

@router.put("/{prompt_id}", response_model=schema_prompt.PromptRead, name="update_existing_prompt")
async def update_existing_prompt(
    prompt_id: int, prompt_in: schema_prompt.PromptUpdate,
    db: AsyncSession = Depends(get_db_session), current_user: ModelUser = Depends(get_current_active_user)
):
    db_prompt = await crud_prompt.get_prompt(db, prompt_id=prompt_id)
    if not db_prompt or db_prompt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Prompt not found or not owned by user.")
    try:
        updated_prompt = await crud_prompt.update_prompt(db, db_prompt, prompt_in, current_user.id)
        await db.commit()
        await db.refresh(updated_prompt)
        return updated_prompt
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Could not update prompt.")

@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_existing_prompt")
async def delete_existing_prompt(
    prompt_id: int, db: AsyncSession = Depends(get_db_session), current_user: ModelUser = Depends(get_current_active_user)
):
    db_prompt = await crud_prompt.get_prompt(db, prompt_id=prompt_id)
    if not db_prompt or db_prompt.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Prompt not found or not owned by user.")
    try:
        await crud_prompt.delete_prompt(db, db_prompt)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail="Could not delete prompt.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)