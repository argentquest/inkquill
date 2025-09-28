# /ai_rag_story_app/app/routers/location.py

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
from app.models.location import Location as ModelLocation
from app.models.story import Story as ModelStory
from app.models.uploaded_document import UploadedDocument, SourceElementTypeEnum
from app.schemas.location import LocationCreate, LocationRead, LocationUpdate, StoryLocationLinkCreate, LocationInStoryRead
from app.schemas.image import GeneratedImageRead
from app.crud import generated_image as crud_generated_image
from app.crud import location as crud_location
from app.crud import story as crud_story
from app.crud import world as crud_world
from app.core.config import settings
from app.core.dependencies_shared import (
    get_world_and_verify_ownership as get_world_dependency,
    get_location_and_verify_ownership,
    get_story_and_verify_ownership
)

logger = logging.getLogger(__name__)

router_world_locations = APIRouter(
    prefix="/worlds/{world_id}/locations",
    tags=["world-locations"],
    dependencies=[Depends(get_current_active_user)]
)
router_locations = APIRouter(
    prefix="/locations",
    tags=["locations"],
    dependencies=[Depends(get_current_active_user)]
)
router_story_locations = APIRouter(
    prefix="/stories/{story_id}/locations",
    tags=["story-locations"],
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

@router_world_locations.post("/", response_model=LocationRead, status_code=status.HTTP_201_CREATED, name="create_new_location_for_world")
async def create_new_location_for_world(
    world_id: int,
    location_in: LocationCreate,
    background_tasks: BackgroundTasks,
    db_world: ModelWorld = Depends(get_world_dependency),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"User '{current_user.username}' API creating location '{location_in.name}' in world ID {db_world.id}")
    
    if location_in.parent_location_id is not None:
        parent_location = await crud_location.get_location(db, location_in.parent_location_id)
        if not parent_location or parent_location.world_id != db_world.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent location not found or does not belong to this world."
            )
    
    try:
        created_location = await crud_location.create_location(
            db=db, 
            location_in=location_in, 
            world_id=db_world.id,
            user_id=current_user.id,
            background_tasks=background_tasks
        )
        await db.commit()
        await db.refresh(created_location)
        return created_location
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating location '{location_in.name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not create location.")

@router_world_locations.get("/", response_model=List[LocationRead])
async def list_locations_in_world(
    world_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    logger.info(f"User '{current_user.username}' API listing locations in world ID {world_id}")
    db_world = await crud_world.get_world_for_user(db, world_id=world_id, user_id=current_user.id)
    if not db_world:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="World not found or not accessible.")
    
    locations_from_db = await crud_location.get_locations_by_world(db, world_id=db_world.id, skip=skip, limit=limit)
    
    response_locations = []
    for loc in locations_from_db:
        loc_read = LocationRead.from_orm(loc)
        path_to_check = loc.current_image.blob_path if loc.current_image else loc.image_blob_path
        loc_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
        response_locations.append(loc_read)
        
    return response_locations

@router_locations.get("/{location_id}", response_model=LocationRead, name="get_single_location")
async def get_single_location(
    db_location: ModelLocation = Depends(get_location_and_verify_ownership),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    loc_read = LocationRead.from_orm(db_location)
    path_to_check = db_location.current_image.blob_path if db_location.current_image else db_location.image_blob_path
    loc_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
    return loc_read

@router_locations.put("/{location_id}", response_model=LocationRead, name="update_existing_location")
async def update_existing_location(
    location_in: LocationUpdate,
    background_tasks: BackgroundTasks,
    db_location: ModelLocation = Depends(get_location_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"User '{current_user.username}' API updating location ID {db_location.id}")
    
    if location_in.parent_location_id is not None:
        if location_in.parent_location_id == db_location.id:
            raise HTTPException(status_code=400, detail="A location cannot be its own parent.")
        parent_location = await crud_location.get_location(db, location_in.parent_location_id)
        if not parent_location or parent_location.world_id != db_location.world_id:
            raise HTTPException(status_code=400, detail="Parent location not found or not in the same world.")
        
        is_valid = await crud_location.validate_location_hierarchy(db, db_location.id, location_in.parent_location_id)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid parent location: would create a circular hierarchy.")

    try:
        updated_location = await crud_location.update_location(
            db=db, 
            db_location=db_location, 
            location_in=location_in,
            user_id=current_user.id,
            background_tasks=background_tasks
        )
        await db.commit()
        await db.refresh(updated_location)
        return updated_location
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating location ID {db_location.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not update location.")


@router_locations.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_existing_location")
async def delete_existing_location(
    background_tasks: BackgroundTasks,
    db_location: ModelLocation = Depends(get_location_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    logger.info(f"User '{current_user.username}' API deleting location ID {db_location.id}")
    try:
        await crud_location.delete_location(
            db=db, 
            db_location=db_location,
            user_id=current_user.id,
            world_id=db_location.world_id,
            background_tasks=background_tasks
        )
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting location ID {db_location.id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Could not delete location.")

@router_locations.get("/{location_id}/images", response_model=List[GeneratedImageRead])
async def list_images_for_location(
    location: ModelLocation = Depends(get_location_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session)
):
    images = await crud_generated_image.get_images_for_element(
        db, element_type="location", element_id=location.id
    )
    return images

@router_locations.post("/{location_id}/set-current-image/{image_id}", response_model=LocationRead)
async def set_current_image_for_location(
    location: ModelLocation = Depends(get_location_and_verify_ownership),
    image_id: int = Path(..., description="The ID of the GeneratedImage to set as current."),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    image_to_set = await crud_generated_image.get_image(db, image_id=image_id)
    if not image_to_set or image_to_set.element_type != 'location' or image_to_set.associated_element_id != location.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found or does not belong to this location.")
    
    location.current_image_id = image_to_set.id
    location.image_blob_path = image_to_set.blob_path
    
    db.add(location)
    await db.commit()
    await db.refresh(location)
    
    location_read = LocationRead.from_orm(location)
    location_read.image_url = await _check_and_get_image_url(blob_service_client, location.image_blob_path)

    return location_read


@router_story_locations.post("/", status_code=status.HTTP_201_CREATED, name="link_location_to_story")
async def link_location_to_story_endpoint(
    story_id: int,
    link_in: StoryLocationLinkCreate,
    db_story: ModelStory = Depends(get_story_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    db_location = await crud_location.get_location(db, location_id=link_in.location_id)
    if not db_location or db_location.world_id != db_story.world_id or db_location.world.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found or not accessible.")
    
    success = await crud_location.link_location_to_story(db, story_id=db_story.id, location_id=link_in.location_id, significance_to_story=link_in.significance_to_story)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to link location.")
    await db.commit()
    return {"message": "Location successfully linked/updated in story."}

@router_story_locations.delete("/{location_id}", status_code=status.HTTP_204_NO_CONTENT, name="unlink_location_from_story")
async def unlink_location_from_story_endpoint(
    story_id: int,
    location_id: int,
    db_story: ModelStory = Depends(get_story_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session)
):
    success = await crud_location.unlink_location_from_story(db, story_id=db_story.id, location_id=location_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Link not found.")
    await db.commit()
    return

@router_story_locations.get("/", response_model=List[LocationInStoryRead], name="list_locations_for_story")
async def list_locations_for_story_endpoint(
    story_id: int,
    db_story: ModelStory = Depends(get_story_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    # --- FIX: Process the list of dicts from CRUD to create Pydantic models ---
    locations_data_raw = await crud_location.get_locations_for_story(db, story_id=db_story.id)
    
    response_locations = []
    for loc_data in locations_data_raw:
        loc_obj = loc_data.get("location")
        if not loc_obj: continue
        
        loc_read = LocationInStoryRead.from_orm(loc_obj)
        loc_read.significance_to_story = loc_data.get('significance_to_story')
        
        path_to_check = loc_obj.current_image.blob_path if loc_obj.current_image else loc_obj.image_blob_path
        loc_read.image_url = await _check_and_get_image_url(blob_service_client, path_to_check)
        
        response_locations.append(loc_read)
        
    return response_locations
    # --- END FIX ---

@router_locations.get("/{location_id}/generated-rag-content", response_model=RAGContentResponse, name="get_location_generated_rag_content")
async def get_location_generated_rag_content_endpoint(
    db_location: ModelLocation = Depends(get_location_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    logger.info(f"User fetching generated RAG content for Location ID: {db_location.id}")
    
    stmt = select(UploadedDocument).where(
        UploadedDocument.source_location_id == db_location.id,
        UploadedDocument.source_element_type == SourceElementTypeEnum.LOCATION_LORE,
        UploadedDocument.world_id == db_location.world_id
    ).order_by(UploadedDocument.uploaded_at.desc())
    
    result = await db.execute(stmt)
    rag_doc_record = result.scalars().first()

    if not rag_doc_record or not rag_doc_record.blob_storage_path:
        return RAGContentResponse(content=None, error="No AI-generated RAG context found for this location.", filename=None)

    try:
        container_name_for_rag = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_RAG_DOCS
        blob_client = blob_service_client.get_blob_client(container=container_name_for_rag, blob=rag_doc_record.blob_storage_path)
        if not await blob_client.exists():
            return RAGContentResponse(content=None, error="RAG file not found in storage.", filename=rag_doc_record.filename)
        
        downloader = await blob_client.download_blob()
        blob_content_bytes = await downloader.readall()
        return RAGContentResponse(content=blob_content_bytes.decode('utf-8', errors='replace'), filename=rag_doc_record.filename)
    except Exception as e_blob:
        logger.error(f"Error fetching RAG content from blob for Location ID {db_location.id}: {e_blob}", exc_info=True)
        return RAGContentResponse(error=f"Error retrieving RAG content from storage.", filename=rag_doc_record.filename)