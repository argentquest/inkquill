"""API routes for act."""

# /story_app/app/routers/act.py
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.core.deps import get_db_session, get_current_active_user, get_current_user
from app.core.storage_deps import LocalStorageClient, get_blob_service_client

from app.core.dependencies_shared import verify_story_owner_for_act_operations, get_act_and_verify_ownership
from app.models.user import User as ModelUser
from app.models.story import Story as ModelStory
from app.models.act import Act as ModelAct
from app.models.scene import Scene as ModelScene
from app.models.generated_image import GeneratedImage
from app.schemas.act import ActCreate, ActRead, ActUpdate
from app.schemas.base import ApiResponse
from app.schemas.image import GeneratedImageRead
from app.crud import act as crud_act
from app.crud import scene as crud_scene
from app.crud import generated_image as crud_generated_image
from app.services.summary_generation_service import generate_ai_summary_for_act
from app.services.async_image_service import AsyncImageService
from app.schemas.general import JobSubmissionResponse
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

story_acts_router = APIRouter(
    prefix="/stories/{story_id}/acts",
    tags=["story-acts"]
)
acts_router = APIRouter(
    prefix="/acts",
    tags=["acts"]
)

@story_acts_router.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED, name="create_new_act_for_story")
async def create_new_act_for_story(act_in: ActCreate, story_owner_verified: ModelStory = Depends(verify_story_owner_for_act_operations), db: AsyncSession = Depends(get_db_session), current_user: ModelUser = Depends(get_current_active_user)):
    """Handle POST /."""
    story_id_for_creation = story_owner_verified.id
    username = current_user.username  # Capture username to avoid lazy loading issues
    logger.info(f"User {username} creating new act '{act_in.title}' for story ID {story_id_for_creation}")
    try:
        created_act = await crud_act.create_act(db=db, act_in=act_in, story_id=story_id_for_creation)
        await db.commit()
        await db.refresh(created_act)
        return ApiResponse.success_response(data=ActRead.model_validate(created_act))
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create act for story ID {story_id_for_creation} by user {username}: {e}", exc_info=True)
        if "UniqueViolation" in str(e) or "_story_act_number_uc" in str(e):
             raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"An act with number '{act_in.act_number}' already exists for this story.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create act.")

@story_acts_router.get("/", response_model=ApiResponse, name="list_acts_for_story")
async def list_acts_for_story(story_owner_verified: ModelStory = Depends(verify_story_owner_for_act_operations), skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=200), db: AsyncSession = Depends(get_db_session)):
    """Handle GET /."""
    story_id_for_listing = story_owner_verified.id
    acts = await crud_act.get_acts_by_story(db, story_id=story_id_for_listing, skip=skip, limit=limit)
    return ApiResponse.success_response(data=[ActRead.model_validate(act) for act in acts])

@acts_router.get("/{act_id}", response_model=ApiResponse, name="get_single_act")
async def get_single_act(db_act: ModelAct = Depends(get_act_and_verify_ownership)):
    """Handle GET /{act_id}."""
    return ApiResponse.success_response(data=ActRead.model_validate(db_act))

@acts_router.put("/{act_id}", response_model=ApiResponse, name="update_existing_act")
async def update_existing_act(
    act_in: ActUpdate, 
    request: Request,
    act_id: int = Path(..., description="The ID of the act"),
    db: AsyncSession = Depends(get_db_session), 
    current_user: Optional[ModelUser] = Depends(get_current_user)
):
    # Handle anonymous users
    """Handle PUT /{act_id}."""
    if current_user is None:
        # Get anonymous user from cookies
        from app.services.anonymous_user_service import anonymous_user_service
        from sqlalchemy import select
        
        anon_user_id = request.cookies.get("anon_user_id")
        if not anon_user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Anonymous session not found"
            )
        
        try:
            existing_user = await db.execute(
                select(ModelUser).where(ModelUser.id == int(anon_user_id))
            )
            current_user = existing_user.scalar_one_or_none()
            
            if not current_user or not await anonymous_user_service.is_anonymous_user(current_user):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid anonymous session"
                )
        except (ValueError, Exception):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid anonymous session"
            )
    
    # Get and verify act ownership
    db_act = await crud_act.get_act(db, act_id=act_id)
    if not db_act:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Act not found")
    
    if not db_act.story or db_act.story.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this act")
    
    username = current_user.username  # Capture username to avoid lazy loading issues
    logger.info(f"User {username} updating act ID: {db_act.id} with data: {act_in.model_dump(exclude_unset=True)}")
    try:
        updated_act = await crud_act.update_act(db=db, db_act=db_act, act_update=act_in, updater_user_id=current_user.id)
        await db.commit()
        await db.refresh(updated_act)
        
        # Generate AI summary if description was updated
        if act_in.description is not None and updated_act.description:
            logger.info(f"Description updated for act {updated_act.id}, generating AI summary...")
            await generate_ai_summary_for_act(db=db, act=updated_act, updater_user_id=current_user.id)
            await db.commit()
            await db.refresh(updated_act)
        
        return ApiResponse.success_response(data=ActRead.model_validate(updated_act))
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update act ID {db_act.id} for user {username}: {e}", exc_info=True)
        if "UniqueViolation" in str(e) or "_story_act_number_uc" in str(e):
             raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Could not update. Act number '{act_in.act_number if act_in.act_number is not None else db_act.act_number}' may already exist for this story.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not update act.")

@acts_router.delete("/{act_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_existing_act")
async def delete_existing_act(db_act: ModelAct = Depends(get_act_and_verify_ownership), db: AsyncSession = Depends(get_db_session), current_user: ModelUser = Depends(get_current_active_user)):
    """Handle DELETE /{act_id}."""
    username = current_user.username  # Capture username to avoid lazy loading issues
    logger.info(f"User {username} deleting act ID: {db_act.id}")
    try:
        await crud_act.delete_act(db=db, db_act=db_act)
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete act ID {db_act.id} for user {username}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete act.")

@acts_router.post("/{act_id}/compile-scenes", response_model=ApiResponse, name="compile_scenes_to_act_content")
async def compile_scenes_to_act_content(db_act: ModelAct = Depends(get_act_and_verify_ownership), db: AsyncSession = Depends(get_db_session), current_user: ModelUser = Depends(get_current_active_user)):
    """Handle POST /{act_id}/compile-scenes."""
    logger.info(f"User {current_user.username} compiling scenes for Act ID: {db_act.id}")
    scenes: List[ModelScene] = await crud_scene.get_scenes_by_act(db, act_id=db_act.id, limit=1000)
    if not scenes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No scenes found for this act to compile.")
    
    compiled_html_parts = []
    for i, scene_obj in enumerate(scenes):
        title_text = scene_obj.title.strip() if scene_obj.title and scene_obj.title.strip() else 'Untitled Scene'
        compiled_html_parts.append(f"<h3>Scene {scene_obj.scene_number}: {title_text}</h3>\n")
        if scene_obj.summary and scene_obj.summary.strip():
            compiled_html_parts.append(f"<p><em>Summary: {scene_obj.summary.strip()}</em></p>\n")
        compiled_html_parts.append(f"<div>{scene_obj.content.strip() if scene_obj.content and scene_obj.content.strip() else '<p><em>(No content)</em></p>'}</div>\n")
        if i < len(scenes) - 1:
            compiled_html_parts.append("<hr style='margin: 1em 0;'>\n")
    
    new_act_description = "".join(compiled_html_parts).strip()
    updated_act = await crud_act.update_act(db, db_act=db_act, act_update=ActUpdate(description=new_act_description), updater_user_id=current_user.id)
    await db.commit()
    await db.refresh(updated_act)
    
    # Generate AI summary for the compiled content
    logger.info(f"Generating AI summary for compiled act content...")
    await generate_ai_summary_for_act(db=db, act=updated_act, updater_user_id=current_user.id)
    await db.commit()
    await db.refresh(updated_act)
    
    logger.info(f"Act ID: {db_act.id} description updated from compiled scenes by user {current_user.username}.")
    return ApiResponse.success_response(data=ActRead.model_validate(updated_act))

@acts_router.get("/{act_id}/images", response_model=ApiResponse)
async def list_images_for_act(
    db_act: ModelAct = Depends(get_act_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session)
):
    """Handle GET /{act_id}/images."""
    logger.info(f"API: Fetching images for act ID: {db_act.id}, Type: 'act'")
    images = await crud_generated_image.get_images_for_element(
        db, element_type="act", element_id=db_act.id
    )
    logger.info(f"API: Found {len(images)} images for act ID: {db_act.id}")
    return ApiResponse.success_response(data=[GeneratedImageRead.model_validate(image) for image in images])

@acts_router.post("/{act_id}/set-current-image/{image_id}", response_model=ApiResponse)
async def set_current_image_for_act(
    db_act: ModelAct = Depends(get_act_and_verify_ownership),
    image_id: int = Path(..., description="The ID of the GeneratedImage to set as current."),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: LocalStorageClient = Depends(get_blob_service_client)
):
    """Handle POST /{act_id}/set-current-image/{image_id}."""
    image_to_set = await crud_generated_image.get_image(db, image_id=image_id)
    if not image_to_set or image_to_set.element_type != 'act' or image_to_set.associated_element_id != db_act.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found or does not belong to this act.")
    
    db_act.current_image_id = image_to_set.id
    
    db.add(db_act)
    await db.commit()
    await db.refresh(db_act)
    
    return ApiResponse.success_response(data=ActRead.model_validate(db_act))

class ActImageGenerationRequest(BaseModel):
    """Response or helper model for act image generation request."""
    custom_prompt: Optional[str] = None
    image_style: Optional[str] = None

@acts_router.post("/{act_id}/generate-image", response_model=ApiResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_act_image(
    act_image_request: ActImageGenerationRequest,
    db_act: ModelAct = Depends(get_act_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
):
    """Generate an image for the specified act using AI"""
    logger.info(f"User {current_user.username} generating image for Act ID: {db_act.id}")
    
    # Prepare prompt
    base_prompt = ""
    if act_image_request.custom_prompt and act_image_request.custom_prompt.strip():
        base_prompt = act_image_request.custom_prompt.strip()
    elif db_act.image_prompt_definition and db_act.image_prompt_definition.strip():
        base_prompt = db_act.image_prompt_definition.strip()
    else:
        # Auto-generate prompt from act content
        act_title = db_act.title or f"Act {db_act.act_number}"
        act_content = ""
        if db_act.act_summary:
            act_content = db_act.act_summary[:200]
        elif db_act.description:
            # Strip HTML and limit length
            import re
            clean_content = re.sub(r'<[^>]+>', '', db_act.description)
            act_content = clean_content[:200]
        
        if act_content:
            base_prompt = f"Dramatic scene from act '{act_title}': {act_content.strip()}..."
        else:
            base_prompt = f"Dramatic scene from act '{act_title}'"
    
    # Apply style if provided
    final_prompt = base_prompt
    if act_image_request.image_style and act_image_request.image_style.strip():
        final_prompt = f"{act_image_request.image_style.strip()} --- {base_prompt}"
    
    # Get world_id for the act through the story
    world_id = None
    if db_act.story and db_act.story.world_id:
        world_id = db_act.story.world_id
    
    # Submit the image generation job
    job_id = await AsyncImageService.submit_image_generation_job(
        db=db,
        user_id=current_user.id,
        prompt=final_prompt,
        element_type="act",
        element_id=db_act.id,
        world_id=world_id
    )
    
    # Save auto-generated prompt back to act if no custom prompt was provided
    if not act_image_request.custom_prompt or not act_image_request.custom_prompt.strip():
        try:
            from app.schemas.act import ActUpdate
            act_update = ActUpdate(image_prompt_definition=final_prompt)
            await crud_act.update_act(db=db, db_act=db_act, act_update=act_update, updater_user_id=current_user.id)
            await db.commit()
            logger.info(f"Saved auto-generated prompt to act {db_act.id}")
        except Exception as e:
            logger.warning(f"Could not save auto-generated prompt to act {db_act.id}: {e}")
    
    logger.info(f"Act image generation job {job_id} submitted for Act ID: {db_act.id}")
    
    return JobSubmissionResponse(
        message="Act image generation started successfully.",
        job_id=job_id
    )

@acts_router.post("/{act_id}/generate-summary", response_model=ApiResponse)
async def generate_summary_for_act(
    db_act: ModelAct = Depends(get_act_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: ModelUser = Depends(get_current_active_user)
):
    """Generate an AI summary for the specified act"""
    logger.info(f"User {current_user.username} generating summary for Act ID: {db_act.id}")
    
    if not db_act.description or not db_act.description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot generate summary: Act has no content to summarize."
        )
    
    try:
        # Generate AI summary
        summary = await generate_ai_summary_for_act(db=db, act=db_act, updater_user_id=current_user.id)
        await db.commit()
        await db.refresh(db_act)
        
        if summary:
            logger.info(f"AI summary generated for Act ID: {db_act.id}")
        else:
            logger.warning(f"AI summary generation returned None for Act ID: {db_act.id}")
        
        return ApiResponse.success_response(data=ActRead.model_validate(db_act))
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to generate summary for Act ID: {db_act.id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI summary. Please try again."
        )

