# /ai_rag_story_app/app/routers/character.py

from fastapi import APIRouter, Depends, HTTPException, status, Query, Path, Body, BackgroundTasks, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from typing import List, Optional
import logging

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user
from app.core.azure_deps import get_blob_service_client
from azure.storage.blob.aio import BlobServiceClient
from app.models.user import User
from app.models.world import World as ModelWorld
from app.models.character import Character as ModelCharacter
from app.models.story import Story as ModelStory
from app.models.uploaded_document import UploadedDocument, SourceElementTypeEnum
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

class RAGContentResponse(BaseModel):
    content: Optional[str] = None
    error: Optional[str] = None
    filename: Optional[str] = None

async def _check_and_get_image_url(blob_service_client: BlobServiceClient, blob_path: Optional[str]) -> Optional[str]:
    if not blob_path:
        return None
    try:
        container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
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
    return new_char

@router_world_characters.get("/", response_model=ApiResponse, name="list_characters_for_world_api")
async def list_characters_in_world(
    world_id: int, 
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
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
    
    return response_characters

@router_characters.get("/{character_id}", response_model=ApiResponse, name="get_single_character")
async def get_single_character(
    db_character: ModelCharacter = Depends(get_character_and_verify_ownership),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    char_read = CharacterRead.from_orm(db_character)
    path_to_check = db_character.current_image.blob_path if db_character.current_image else db_character.image_blob_path
    char_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
    return char_read

@router_characters.put("/{character_id}", response_model=ApiResponse, name="update_existing_character")
async def update_existing_character(
    character_in: CharacterUpdate,
    background_tasks: BackgroundTasks,
    db_character: ModelCharacter = Depends(get_character_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
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
    return updated_char

@router_characters.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_existing_character")
async def delete_existing_character(
    background_tasks: BackgroundTasks,
    db_character: ModelCharacter = Depends(get_character_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
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
    logger.info(f"API: Fetching images for character ID: {character.id}, Type: 'character'")
    images = await crud_generated_image.get_images_for_element(
        db, element_type="character", element_id=character.id
    )
    logger.info(f"API: Found {len(images)} images for character ID: {character.id}")
    return images

@router_characters.post("/{character_id}/set-current-image/{image_id}", response_model=ApiResponse)
async def set_current_image_for_character(
    character: ModelCharacter = Depends(get_character_and_verify_ownership),
    image_id: int = Path(..., description="The ID of the GeneratedImage to set as current."),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
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

    return character_read

@router_story_characters.post("/", status_code=status.HTTP_201_CREATED, name="link_character_to_story")
async def link_character_to_story_endpoint(
    story_id: int, 
    link_in: StoryCharacterLinkCreate, 
    db_story: ModelStory = Depends(get_story_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
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
    return {"message": "Character successfully linked/updated in story."}

@router_story_characters.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT, name="unlink_character_from_story")
async def unlink_character_from_story_endpoint(
    story_id: int, 
    character_id: int, 
    db_story: ModelStory = Depends(get_story_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session)
):
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
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
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
        
    return response_characters

@router_characters.get("/{character_id}/generated-rag-content", response_model=ApiResponse, name="get_character_generated_rag_content")
async def get_character_generated_rag_content_endpoint(
    db_character: ModelCharacter = Depends(get_character_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    logger.info(f"User (from dep) fetching generated RAG content for Character ID: {db_character.id}")
    
    stmt = select(UploadedDocument).where(
        UploadedDocument.source_character_id == db_character.id,
        UploadedDocument.source_element_type == SourceElementTypeEnum.CHARACTER_LORE
    ).order_by(UploadedDocument.uploaded_at.desc())
    
    result = await db.execute(stmt)
    rag_doc_record = result.scalars().first()

    if not rag_doc_record or not rag_doc_record.blob_storage_path:
        return RAGContentResponse(content=None, error="No AI-generated RAG context found for this character.", filename=None)

    try:
        container_name_for_rag = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_RAG_DOCS
        blob_client = blob_service_client.get_blob_client(container=container_name_for_rag, blob=rag_doc_record.blob_storage_path)
        if not await blob_client.exists():
            return RAGContentResponse(content=None, error="RAG file not found in storage.", filename=rag_doc_record.filename)
        
        downloader = await blob_client.download_blob()
        blob_content_bytes = await downloader.readall()
        return RAGContentResponse(content=blob_content_bytes.decode('utf-8', errors='replace'), filename=rag_doc_record.filename)
    except Exception as e_blob:
        logger.error(f"Error fetching RAG content from blob for Character ID {db_character.id}: {e_blob}", exc_info=True)
        return RAGContentResponse(error=f"Error retrieving RAG content from storage.", filename=rag_doc_record.filename)