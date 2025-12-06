# /ai_rag_story_app/app/routers/lore_item.py

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
from app.models.lore_item import LoreItem as ModelLoreItem, LoreItemCategoryEnum
from app.models.story import Story as ModelStory
from app.models.uploaded_document import UploadedDocument, SourceElementTypeEnum
from app.schemas.image import GeneratedImageRead
from app.schemas.base import ApiResponse
from app.crud import generated_image as crud_generated_image
from app.schemas.lore_item import (
    LoreItemCreate, LoreItemRead, LoreItemUpdate,
    StoryLoreItemLinkCreate, LoreItemInStoryRead
)
from app.crud import lore_item as crud_lore_item
from app.crud import story as crud_story
from app.crud import world as crud_world
from app.core.config import settings
from app.core.dependencies_shared import (
    get_world_and_verify_ownership as get_world_dependency,
    get_lore_item_and_verify_ownership,
    get_story_and_verify_ownership
)

logger = logging.getLogger(__name__)

router_world_lore_items = APIRouter(
    prefix="/worlds/{world_id}/lore-items",
    tags=["world-lore-items"],
    dependencies=[Depends(get_current_active_user)]
)
router_lore_items = APIRouter(
    prefix="/lore-items",
    tags=["lore-items"],
    dependencies=[Depends(get_current_active_user)]
)
router_story_lore_items = APIRouter(
    prefix="/stories/{story_id}/lore-items",
    tags=["story-lore-items"],
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

# ... (create, get_single, update, delete endpoints remain the same) ...

@router_world_lore_items.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, name="create_new_lore_item_for_world")
async def create_new_lore_item_for_world(
    world_id: int,
    lore_item_in: LoreItemCreate,
    background_tasks: BackgroundTasks,
    db_world: ModelWorld = Depends(get_world_dependency),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"User '{current_user.username}' API creating lore item '{lore_item_in.title}' in world ID {db_world.id}")
    try:
        created_item = await crud_lore_item.create_lore_item(
            db=db, 
            lore_item_in=lore_item_in, 
            world_id=db_world.id,
            user_id=current_user.id,
            background_tasks=background_tasks
        )
        await db.commit()
        await db.refresh(created_item)
        return created_item
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating lore item '{lore_item_in.title}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not create lore item.")

@router_world_lore_items.get("/", response_model=ApiResponse)
async def list_lore_items_in_world(
    world_id: int,
    category: Optional[LoreItemCategoryEnum] = Query(None, description="Filter by lore item category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    logger.info(f"User '{current_user.username}' API listing lore items in world ID {world_id}")
    db_world = await crud_world.get_world_for_user(db, world_id=world_id, user_id=current_user.id)
    if not db_world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found or not accessible.")
    
    lore_items_db = await crud_lore_item.get_lore_items_by_world(
        db, world_id=db_world.id, category=category, skip=skip, limit=limit
    )

    response_items = []
    for item in lore_items_db:
        item_read = LoreItemRead.from_orm(item)
        path_to_check = item.current_image.blob_path if item.current_image else item.image_blob_path
        item_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
        response_items.append(item_read)
    
    return response_items

@router_lore_items.get("/{lore_item_id}", response_model=ApiResponse, name="get_single_lore_item")
async def get_single_lore_item(
    db_lore_item: ModelLoreItem = Depends(get_lore_item_and_verify_ownership),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    item_read = LoreItemRead.from_orm(db_lore_item)
    path_to_check = db_lore_item.current_image.blob_path if db_lore_item.current_image else db_lore_item.image_blob_path
    item_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
    return item_read

@router_lore_items.put("/{lore_item_id}", response_model=ApiResponse, name="update_existing_lore_item")
async def update_existing_lore_item(
    lore_item_in: LoreItemUpdate,
    background_tasks: BackgroundTasks,
    db_lore_item: ModelLoreItem = Depends(get_lore_item_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"User '{current_user.username}' API updating lore item ID {db_lore_item.id}")
    try:
        updated_item = await crud_lore_item.update_lore_item(
            db=db, 
            db_lore_item=db_lore_item, 
            lore_item_in=lore_item_in,
            user_id=current_user.id,
            background_tasks=background_tasks
        )
        await db.commit()
        await db.refresh(updated_item)
        return updated_item
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating lore item ID {db_lore_item.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not update lore item.")

@router_lore_items.delete("/{lore_item_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_existing_lore_item")
async def delete_existing_lore_item(
    background_tasks: BackgroundTasks,
    db_lore_item: ModelLoreItem = Depends(get_lore_item_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"User '{current_user.username}' API deleting lore item ID {db_lore_item.id}")
    try:
        await crud_lore_item.delete_lore_item(
            db=db, 
            db_lore_item=db_lore_item,
            user_id=current_user.id,
            world_id=db_lore_item.world_id,
            background_tasks=background_tasks
        )
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting lore item ID {db_lore_item.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not delete lore item.")

@router_lore_items.get("/{lore_item_id}/images", response_model=ApiResponse)
async def list_images_for_lore_item(
    lore_item: ModelLoreItem = Depends(get_lore_item_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session)
):
    images = await crud_generated_image.get_images_for_element(
        db, element_type="lore_item", element_id=lore_item.id
    )
    return images

@router_lore_items.post("/{lore_item_id}/set-current-image/{image_id}", response_model=ApiResponse)
async def set_current_image_for_lore_item(
    lore_item: ModelLoreItem = Depends(get_lore_item_and_verify_ownership),
    image_id: int = Path(..., description="The ID of the GeneratedImage to set as current."),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    image_to_set = await crud_generated_image.get_image(db, image_id=image_id)
    if not image_to_set or image_to_set.element_type != 'lore_item' or image_to_set.associated_element_id != lore_item.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found or does not belong to this lore item.")
    
    lore_item.current_image_id = image_to_set.id
    lore_item.image_blob_path = image_to_set.blob_path
    
    db.add(lore_item)
    await db.commit()
    await db.refresh(lore_item)
    
    item_read = LoreItemRead.from_orm(lore_item)
    item_read.image_url = await _check_and_get_image_url(blob_service_client, lore_item.image_blob_path)

    return item_read


@router_story_lore_items.post("/", status_code=status.HTTP_201_CREATED, name="link_lore_item_to_story")
async def link_lore_item_to_story_endpoint(
    story_id: int,
    link_in: StoryLoreItemLinkCreate,
    db_story: ModelStory = Depends(get_story_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    db_lore_item = await crud_lore_item.get_lore_item(db, lore_item_id=link_in.lore_item_id)
    if not db_lore_item or db_lore_item.world_id != db_story.world_id or db_lore_item.world.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Lore item not found or not accessible.")
        
    success = await crud_lore_item.link_lore_item_to_story(db, story_id=db_story.id, lore_item_id=link_in.lore_item_id, relevance_to_story=link_in.relevance_to_story)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to link lore item.")
    await db.commit()
    return {"message": "Lore item successfully linked/updated in story."}

@router_story_lore_items.delete("/{lore_item_id}", status_code=status.HTTP_204_NO_CONTENT, name="unlink_lore_item_from_story")
async def unlink_lore_item_from_story_endpoint(
    story_id: int,
    lore_item_id: int,
    db_story: ModelStory = Depends(get_story_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session)
):
    success = await crud_lore_item.unlink_lore_item_from_story(db, story_id=db_story.id, lore_item_id=lore_item_id)
    if not success:
        raise HTTPException(status_code=404, detail="Link not found.")
    await db.commit()
    return

@router_story_lore_items.get("/", response_model=ApiResponse, name="list_lore_items_for_story")
async def list_lore_items_for_story_endpoint(
    story_id: int,
    db_story: ModelStory = Depends(get_story_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    # --- FIX: Process the list of dicts from CRUD to create Pydantic models ---
    lore_items_data_raw = await crud_lore_item.get_lore_items_for_story(db, story_id=db_story.id)
    
    response_items = []
    for item_data in lore_items_data_raw:
        item_obj = item_data.get("lore_item")
        if not item_obj: continue

        item_read = LoreItemInStoryRead.from_orm(item_obj)
        item_read.relevance_to_story = item_data.get('relevance_to_story')
        
        path_to_check = item_obj.current_image.blob_path if item_obj.current_image else item_obj.image_blob_path
        item_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)

        response_items.append(item_read)

    return response_items
    # --- END FIX ---

@router_lore_items.get("/{lore_item_id}/generated-rag-content", response_model=ApiResponse, name="get_lore_item_generated_rag_content")
async def get_lore_item_generated_rag_content_endpoint(
    db_lore_item: ModelLoreItem = Depends(get_lore_item_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    logger.info(f"User fetching generated RAG content for Lore Item ID: {db_lore_item.id}")
    
    stmt = select(UploadedDocument).where(
        UploadedDocument.source_lore_item_id == db_lore_item.id,
        UploadedDocument.source_element_type == SourceElementTypeEnum.LORE_ITEM_LORE,
        UploadedDocument.world_id == db_lore_item.world_id
    ).order_by(UploadedDocument.uploaded_at.desc())
    
    result = await db.execute(stmt)
    rag_doc_record = result.scalars().first()

    if not rag_doc_record or not rag_doc_record.blob_storage_path:
        return RAGContentResponse(content=None, error="No AI-generated RAG context found for this lore item.", filename=None)

    try:
        container_name_for_rag = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_RAG_DOCS
        blob_client = blob_service_client.get_blob_client(container=container_name_for_rag, blob=rag_doc_record.blob_storage_path)
        if not await blob_client.exists():
            return RAGContentResponse(content=None, error="RAG file not found in storage.", filename=rag_doc_record.filename)
        
        downloader = await blob_client.download_blob()
        blob_content_bytes = await downloader.readall()
        return RAGContentResponse(content=blob_content_bytes.decode('utf-8', errors='replace'), filename=rag_doc_record.filename)
    except Exception as e_blob:
        logger.error(f"Error fetching RAG content from blob for Lore Item ID {db_lore_item.id}: {e_blob}", exc_info=True)
        return RAGContentResponse(error=f"Error retrieving RAG content from storage.", filename=rag_doc_record.filename)