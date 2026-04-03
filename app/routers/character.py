"""API routes for character."""

# /story_app/app/routers/character.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, BackgroundTasks, Response
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import List, Optional
import logging

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user
from app.core.storage_deps import LocalStorageClient, get_blob_service_client
from app.core.storage_deps import LocalStorageClient
from app.models.user import User
from app.models.world import World as ModelWorld
from app.models.character import Character as ModelCharacter
from app.models.story import Story as ModelStory
from app.models.generated_image import GeneratedImage
from app.schemas.character import CharacterCreate, CharacterRead, CharacterUpdate, StoryCharacterLinkCreate, CharacterInStoryRead
from app.schemas.base import ApiResponse
from app.schemas.image import GeneratedImageRead
from app.crud import character as crud_character, generated_image as crud_generated_image
from app.crud import story as crud_story
from app.crud import world as crud_world
from app.core.config import settings
from app.core.dependencies_shared import (
    get_world_and_verify_ownership as get_world_dependency,
    get_character_and_verify_ownership, 
    get_story_and_verify_ownership
)

logger = logging.getLogger(__name__)

router_world_characters = APIRouter(
    prefix="/worlds/{world_id}/characters",
    tags=["world-characters"],
    dependencies=[Depends(get_current_active_user)]
)
router_characters = APIRouter(
    prefix="/characters",
    tags=["characters"],
    dependencies=[Depends(get_current_active_user)]
)
router_story_characters = APIRouter(
    prefix="/stories/{story_id}/characters",
    tags=["story-characters"],
    dependencies=[Depends(get_current_active_user)]
)

class ContextContentResponse(BaseModel):
    """Response or helper model for context content response."""
    content: Optional[str] = None
    error: Optional[str] = None
    filename: Optional[str] = None


def _build_character_context(character: ModelCharacter) -> str:
    """Provide internal router support for build character context."""
    parts = [
        f"Name: {character.name}",
        f"Description: {character.description or 'N/A'}",
        f"Personality Traits: {character.personality_traits or 'N/A'}",
        f"Backstory: {character.backstory or 'N/A'}",
        f"Short Backstory: {character.short_backstory or 'N/A'}",
        f"Profession: {character.profession or 'N/A'}",
        f"Core Motivations: {character.core_motivations or 'N/A'}",
        f"Visual Prompt: {character.visual_prompt or 'N/A'}",
        f"Relationships: {character.relationships or 'N/A'}",
    ]
    return "\n".join(parts)

async def _check_and_get_image_url(blob_service_client: LocalStorageClient, blob_path: Optional[str]) -> Optional[str]:
    """Provide internal router support for check and get image url."""
    if not blob_path:
        return None
    try:
        container_name = "generated-images"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
        if await blob_client.exists():
            return blob_client.url
    except Exception as e:
        logger.warning(f"Could not check for blob '{blob_path}' due to error: {e}")
    return None

@router_world_characters.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, name="create_new_character_for_world")
async def create_new_character_for_world(
    world_id: int, 
    character_in: CharacterCreate,
    background_tasks: BackgroundTasks,
    db_world: ModelWorld = Depends(get_world_dependency), 
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user) 
):
    """Handle POST /."""
    logger.info(f"User '{current_user.username}' API creating character '{character_in.name}' in world ID {db_world.id}")
    new_char = await crud_character.create_character(
        db=db, 
        character_in=character_in, 
        world_id=db_world.id,
        user_id=current_user.id,
        background_tasks=background_tasks
    )
    await db.commit()
    await db.refresh(new_char)
    return ApiResponse.success_response(data=CharacterRead.from_orm(new_char))

@router_world_characters.get("/", response_model=ApiResponse, name="list_characters_for_world_api")
async def list_characters_in_world(
    world_id: int, 
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    blob_service_client: LocalStorageClient = Depends(get_blob_service_client)
):
    """Handle GET /."""
    logger.info(f"User '{current_user.username}' API listing characters in world ID {world_id}")
    db_world = await crud_world.get_world_for_user(db, world_id=world_id, user_id=current_user.id)
    if not db_world:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="World not found or you do not have permission to access it."
        )
    characters_from_db = await crud_character.get_characters_by_world(db, world_id=db_world.id, skip=skip, limit=limit)
    
    response_characters = []
    for char in characters_from_db:
        char_read = CharacterRead.from_orm(char)
        path_to_check = char.current_image.blob_path if char.current_image else char.image_blob_path
        char_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
        response_characters.append(char_read)
    
    return ApiResponse.success_response(data=response_characters)

@router_characters.get("/{character_id}", response_model=ApiResponse, name="get_single_character")
async def get_single_character(
    db_character: ModelCharacter = Depends(get_character_and_verify_ownership),
    blob_service_client: LocalStorageClient = Depends(get_blob_service_client)
):
    """Handle GET /{character_id}."""
    char_read = CharacterRead.from_orm(db_character)
    path_to_check = db_character.current_image.blob_path if db_character.current_image else db_character.image_blob_path
    char_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
    return ApiResponse.success_response(data=char_read)

@router_characters.put("/{character_id}", response_model=ApiResponse, name="update_existing_character")
async def update_existing_character(
    character_in: CharacterUpdate,
    background_tasks: BackgroundTasks,
    db_character: ModelCharacter = Depends(get_character_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle PUT /{character_id}."""
    logger.info(f"User '{current_user.username}' API updating character ID {db_character.id}")
    updated_char = await crud_character.update_character(
        db=db, 
        db_character=db_character, 
        character_in=character_in,
        user_id=current_user.id,
        background_tasks=background_tasks
    )
    await db.commit()
    await db.refresh(updated_char)
    return ApiResponse.success_response(data=CharacterRead.from_orm(updated_char))

@router_characters.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_existing_character")
async def delete_existing_character(
    background_tasks: BackgroundTasks,
    db_character: ModelCharacter = Depends(get_character_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle DELETE /{character_id}."""
    logger.info(f"User '{current_user.username}' API deleting character ID {db_character.id}")
    await crud_character.delete_character(
        db=db, 
        db_character=db_character,
        user_id=current_user.id,
        world_id=db_character.world_id,
        background_tasks=background_tasks
    )
    await db.commit()
    return

@router_characters.get("/{character_id}/images", response_model=ApiResponse)
async def list_images_for_character(
    character: ModelCharacter = Depends(get_character_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session)
):
    """Handle GET /{character_id}/images."""
    logger.info(f"API: Fetching images for character ID: {character.id}, Type: 'character'")
    images = await crud_generated_image.get_images_for_element(
        db, element_type="character", element_id=character.id
    )
    logger.info(f"API: Found {len(images)} images for character ID: {character.id}")
    return ApiResponse.success_response(data=[GeneratedImageRead.from_orm(image) for image in images])

@router_characters.post("/{character_id}/set-current-image/{image_id}", response_model=ApiResponse)
async def set_current_image_for_character(
    character: ModelCharacter = Depends(get_character_and_verify_ownership),
    image_id: int = Path(..., description="The ID of the GeneratedImage to set as current."),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: LocalStorageClient = Depends(get_blob_service_client)
):
    """Handle POST /{character_id}/set-current-image/{image_id}."""
    image_to_set = await crud_generated_image.get_image(db, image_id=image_id)
    if not image_to_set or image_to_set.element_type != 'character' or image_to_set.associated_element_id != character.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found or does not belong to this character.")
    
    character.current_image_id = image_to_set.id
    character.image_blob_path = image_to_set.blob_path
    
    db.add(character)
    await db.commit()
    await db.refresh(character)
    
    character_read = CharacterRead.from_orm(character)
    character_read.image_url = await _check_and_get_image_url(blob_service_client, character.image_blob_path)

    return ApiResponse.success_response(data=character_read)

@router_story_characters.post("/", status_code=status.HTTP_201_CREATED, name="link_character_to_story")
async def link_character_to_story_endpoint(
    story_id: int, 
    link_in: StoryCharacterLinkCreate, 
    db_story: ModelStory = Depends(get_story_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle POST /."""
    db_character = await crud_character.get_character(db, character_id=link_in.character_id)
    if not db_character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Character with ID {link_in.character_id} not found.")
    if db_character.world_id != db_story.world_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Character does not belong to the story's world.")
    if not db_character.world or db_character.world.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to use this character.")
    
    success = await crud_character.link_character_to_story(
        db, story_id=db_story.id, character_id=link_in.character_id, role_in_story=link_in.role_in_story
    )
    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to link character to story.")
    await db.commit()
    return ApiResponse.success_response(data={"message": "Character successfully linked/updated in story."})

@router_story_characters.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT, name="unlink_character_from_story")
async def unlink_character_from_story_endpoint(
    story_id: int, 
    character_id: int, 
    db_story: ModelStory = Depends(get_story_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session)
):
    """Handle DELETE /{character_id}."""
    success = await crud_character.unlink_character_from_story(db, story_id=db_story.id, character_id=character_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found.")
    await db.commit()
    return

@router_story_characters.get("/", response_model=ApiResponse, name="list_characters_for_story")
async def list_characters_for_story_endpoint(
    story_id: int,
    db_story: ModelStory = Depends(get_story_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: LocalStorageClient = Depends(get_blob_service_client)
):
    """Handle GET /."""
    characters_data_raw = await crud_character.get_characters_for_story(db, story_id=db_story.id)
    
    response_characters = []
    for char_data in characters_data_raw:
        char_obj = char_data.get("character")
        if not char_obj:
            continue

        char_read = CharacterInStoryRead.from_orm(char_obj)
        char_read.role_in_story = char_data.get('role_in_story')
        
        path_to_check = char_obj.current_image.blob_path if char_obj.current_image else char_obj.image_blob_path
        char_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
        
        response_characters.append(char_read)
        
    return ApiResponse.success_response(data=response_characters)

@router_characters.get("/{character_id}/generated-context", response_model=ApiResponse, name="get_character_generated_context")
async def get_character_generated_context_endpoint(
    db_character: ModelCharacter = Depends(get_character_and_verify_ownership),
):
    """Handle GET /{character_id}/generated-context."""
    logger.info(f"User (from dep) fetching generated context for Character ID: {db_character.id}")
    return ApiResponse.success_response(
        data=ContextContentResponse(
            content=_build_character_context(db_character),
            filename=f"character_{db_character.id}_context.txt",
        )
    )

