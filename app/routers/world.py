"""API routes for world."""

# /story_app/app/routers/world.py

from fastapi import APIRouter, Depends, HTTPException, status, Response, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.core.deps import get_db_session, get_current_active_user
from app.core.dependencies_shared import get_world_and_verify_ownership
from app.core.storage_deps import LocalStorageClient, get_blob_service_client
from app.models.user import User
from app.models.world import World as ModelWorld
from app.schemas.world import WorldCreate, WorldRead, WorldUpdate
from app.schemas.base import ApiResponse, ApiMeta
from app.schemas.story import StoryRead
# --- FIX: Import image-related schemas and crud ---
from app.schemas.image import GeneratedImageRead
from app.crud import generated_image as crud_generated_image
# --- END FIX ---
from app.crud import world as crud_world
from app.crud import story as crud_story
from app.schemas.story_generation import StoryGenerationRequest, StoryGenerationResponse
from app.core.config import settings
from app.core.storage_deps import LocalStorageClient

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/worlds", 
    tags=["worlds"]
)

# --- FIX: Add helper function for image URL ---
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
# --- END FIX ---

@router.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, name="create_new_world")
async def create_new_world(
    world_in: WorldCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle POST /."""
    logger.info(f"User '{current_user.username}' creating new world: '{world_in.name}'")
    try:
        created_world = await crud_world.create_world(db=db, world_in=world_in, user_id=current_user.id)
        await db.commit()
        await db.refresh(created_world)
        return ApiResponse.success_response(data=WorldRead.from_orm(created_world))
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating world '{world_in.name}' for user '{current_user.username}': {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create world.")

@router.get("/", response_model=ApiResponse, name="list_my_worlds")
async def list_my_worlds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle GET /."""
    logger.info(f"User '{current_user.username}' listing their worlds (skip: {skip}, limit: {limit}).")
    worlds = await crud_world.get_worlds_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return ApiResponse.success_response(
        data=[WorldRead.from_orm(w) for w in worlds],
        meta=ApiMeta(page=skip // limit + 1 if limit > 0 else 1, limit=limit, total=len(worlds))
    )

@router.get("/has-non-shadow-worlds", name="check_user_has_non_shadow_worlds")
async def check_user_has_non_shadow_worlds(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Check if the current user has any non-shadow worlds."""
    try:
        has_worlds = await crud_world.user_has_non_shadow_worlds(db, current_user.id)
        return {"has_non_shadow_worlds": has_worlds}
    except Exception as e:
        logger.error(f"Error checking non-shadow worlds for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error checking user worlds"
        )

@router.get("/{world_id}", response_model=ApiResponse, name="get_single_world")
async def get_single_world(
    db_world: ModelWorld = Depends(get_world_and_verify_ownership),
    blob_service_client: LocalStorageClient = Depends(get_blob_service_client)
):
    """Handle GET /{world_id}."""
    logger.info(f"User (from dependency context) viewing world ID: {db_world.id} ('{db_world.name}')")
    world_read = WorldRead.from_orm(db_world)
    world_read.image_url = await _check_and_get_image_url(blob_service_client, db_world.image_blob_path)
    return ApiResponse.success_response(data=world_read)

@router.put("/{world_id}", response_model=ApiResponse, name="update_existing_world")
async def update_existing_world(
    world_in: WorldUpdate,
    db_world: ModelWorld = Depends(get_world_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle PUT /{world_id}."""
    logger.info(f"User '{current_user.username}' updating world ID: {db_world.id} ('{db_world.name}')")
    try:
        updated_world = await crud_world.update_world(db=db, db_world=db_world, world_in=world_in)
        await db.commit()
        await db.refresh(updated_world)
        return ApiResponse.success_response(data=WorldRead.from_orm(updated_world))
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating world ID {db_world.id} by user '{current_user.username}': {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update world.")

@router.delete("/{world_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_existing_world")
async def delete_existing_world(
    db_world: ModelWorld = Depends(get_world_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle DELETE /{world_id}."""
    logger.info(f"User '{current_user.username}' attempting to delete world ID: {db_world.id} ('{db_world.name}')")
    stories_in_this_world = await crud_story.get_stories_by_world_id(db, world_id=db_world.id, limit=1) 
    if stories_in_this_world:
        logger.warning(f"User '{current_user.username}' attempted to delete world ID {db_world.id} which has associated stories.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, 
            detail=f"Cannot delete world '{db_world.name}'. It is currently associated with one or more stories. Please reassign or delete those stories first."
        )
    try:
        await crud_world.delete_world(db=db, db_world=db_world)
        await db.commit()
        logger.info(f"World ID {db_world.id} deleted successfully by user '{current_user.username}'.")
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting world ID {db_world.id} by user '{current_user.username}': {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete world.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{world_id}/stories", response_model=ApiResponse, name="list_stories_for_world")
async def list_stories_for_world(
    db_world: ModelWorld = Depends(get_world_and_verify_ownership),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Handle GET /{world_id}/stories."""
    logger.info(f"User '{current_user.username}' listing stories for their world ID: {db_world.id} ('{db_world.name}')")
    stories = await crud_story.get_stories_by_world_id(
        db, world_id=db_world.id, user_id=current_user.id, skip=skip, limit=limit
    )
    return ApiResponse.success_response(data=[StoryRead.from_orm(s) for s in stories])

# --- FIX: Add image management endpoints for Worlds ---
@router.get("/{world_id}/images", response_model=ApiResponse)
async def list_images_for_world(
    world: ModelWorld = Depends(get_world_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session)
):
    """Handle GET /{world_id}/images."""
    images = await crud_generated_image.get_images_for_element(
        db, element_type="world", element_id=world.id
    )
    return ApiResponse.success_response(data=[GeneratedImageRead.from_orm(img) for img in images])

@router.post("/{world_id}/set-current-image/{image_id}", response_model=ApiResponse)
async def set_current_image_for_world(
    world: ModelWorld = Depends(get_world_and_verify_ownership),
    image_id: int = Path(..., description="The ID of the GeneratedImage to set as current."),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: LocalStorageClient = Depends(get_blob_service_client)
):
    """Handle POST /{world_id}/set-current-image/{image_id}."""
    image_to_set = await crud_generated_image.get_image(db, image_id=image_id)
    if not image_to_set or image_to_set.element_type != 'world' or image_to_set.associated_element_id != world.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found or does not belong to this world.")
    
    world.current_image_id = image_to_set.id
    world.image_blob_path = image_to_set.blob_path

    db.add(world)
    await db.commit()
    await db.refresh(world)

    world_read = WorldRead.from_orm(world)
    world_read.image_url = await _check_and_get_image_url(blob_service_client, world.image_blob_path)
    return ApiResponse.success_response(data=world_read)
# --- END FIX ---


@router.post("/{world_id}/stories/generate", response_model=ApiResponse, name="generate_story_from_world")
async def generate_story_from_world(
    request: StoryGenerationRequest,
    world: ModelWorld = Depends(get_world_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate a new story using selected world elements and AI.
    
    This endpoint will:
    1. Validate the selected elements belong to the world
    2. Call the AI service to generate a story outline
    3. Create the story, acts, and scenes in the database
    4. Return the created story ID and summary
    """
    # Capture IDs early to avoid lazy loading issues in error handler
    user_id = current_user.id
    world_id = world.id
    username = current_user.username
    world_name = world.name
    
    logger.info(f"User '{username}' generating story for world '{world_name}'")
    
    try:
        # Import story generation service
        from app.services.story_generation_service import StoryGenerationService
        
        # Initialize the service
        service = StoryGenerationService(db, current_user)
        
        # Generate the story
        result = await service.generate_story_from_world(world, request)

        logger.info(f"Story generation completed for user '{username}', world '{world_name}': success={result.success}")
        return ApiResponse.success_response(data=result)
        
    except Exception as e:
        # Use pre-captured IDs to avoid SQLAlchemy greenlet issues
        logger.error(f"Error generating story for user_id '{user_id}', world_id '{world_id}': {e}", exc_info=True)
        return StoryGenerationResponse(
            success=False,
            error=f"An unexpected error occurred during story generation: {str(e)}",
            message="Please try again or contact support if the issue persists."
        )

@router.post("/dev/reload-kernel")
async def reload_semantic_kernel(current_user: User = Depends(get_current_active_user)):
    """
    Development endpoint to reload the Semantic Kernel without restarting the server.
    Only available in development environment.
    """
    if settings.APP_ENV != "development":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="This endpoint is only available in development mode"
        )
    
    try:
        from app.services.sk_kernel_instance import reload_kernel
        reload_kernel()
        logger.info(f"Kernel reloaded successfully by user '{current_user.username}'")
        return {"success": True, "message": "Semantic Kernel reloaded successfully"}
    except Exception as e:
        logger.error(f"Error reloading kernel: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reloading kernel: {str(e)}"
        )

