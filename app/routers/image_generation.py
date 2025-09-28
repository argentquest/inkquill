import logging
import base64
import uuid
import json
import io
from fastapi import APIRouter, Depends, HTTPException, status, Body, BackgroundTasks, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
from typing import Optional, Dict, Any, Union, List
from decimal import Decimal
from datetime import datetime
import re
from PIL import Image, ImageOps
import math

from app.core.deps import get_db_session, get_current_active_user
from app.core.azure_deps import get_blob_service_client
from azure.storage.blob.aio import BlobServiceClient
from azure.storage.blob import ContentSettings

from app.models.user import User
from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.models.scene import Scene
from app.models.world import World
from app.models.story import Story
from app.models.act import Act
from app.crud import job_status as crud_job_status
from app.crud import prompt as crud_prompt
from app.schemas.general import JobSubmissionResponse
from app.services.billing_service import billing_service
from app.models.prompt import PromptTypeEnum

from app.services.image_service import generate_image_with_active_provider
from app.services.async_image_service import AsyncImageService
from app.models.job_status import JobTypeEnum, JobStatus, JobStateEnum
from app.core.config import settings

logger = logging.getLogger(__name__)


class ImageResponse(BaseModel):
    id: int
    url: str
    prompt: str
    revised_prompt: str
    cost: float
    created_at: str
    is_current: bool
    aspect_ratio: str


def clean_image_prompt(prompt: str) -> str:
    """
    Clean and validate image prompt for DALL-E 3 compatibility.
    
    Args:
        prompt: Raw prompt text
        
    Returns:
        Cleaned and validated prompt
    """
    if not prompt:
        return ""
    
    # Remove newlines and excessive whitespace
    cleaned = re.sub(r'\s+', ' ', prompt.strip())
    
    # Fix common issues from AI-generated prompts
    # Remove incomplete sentences (ending with incomplete words or fragments)
    cleaned = re.sub(r'\s+\w{1,3}$', '', cleaned)  # Remove 1-3 char fragments at end
    cleaned = re.sub(r',\s*\)$', ')', cleaned)     # Fix ", )" at end
    cleaned = re.sub(r'\(\s*[^)]{1,10}\s*\)$', '', cleaned)  # Remove short incomplete parentheses at end
    
    # Remove or fix incomplete sentences and specific problematic endings
    if any(cleaned.endswith(pattern) for pattern in ['aroun', ' She)', ', expressing', 'creatures aroun']):
        # Find the last complete sentence
        sentences = cleaned.split('.')
        if len(sentences) > 1:
            cleaned = '. '.join(sentences[:-1]) + '.'
        else:
            # Find last comma and truncate there, but not if it's too short
            last_comma = cleaned.rfind(',')
            if last_comma > 50:  # Keep reasonable length
                cleaned = cleaned[:last_comma]
    
    # Fix specific issues with problematic prompts
    # Remove incomplete "creatures aroun" and similar fragments
    cleaned = re.sub(r',\s*creating a sanctuary for herself and the creatures aroun.*$', '.', cleaned)
    cleaned = re.sub(r',\s*expressing [^,]*,\s*\([^)]*$', '.', cleaned)  # Remove incomplete expressions
    
    # Remove incomplete parenthetical expressions at the end
    cleaned = re.sub(r',\s*\([^)]*\.\s*$', '.', cleaned)  # Remove incomplete parentheses ending with period
    
    # Ensure prompt doesn't end with incomplete constructions
    cleaned = re.sub(r',\s*$', '', cleaned)  # Remove trailing comma
    cleaned = re.sub(r'\s*\($', '', cleaned)  # Remove trailing open parenthesis
    
    # Limit length for DALL-E 3 (4000 char limit)
    if len(cleaned) > 1000:  # Conservative limit for better results
        # Try to truncate at sentence boundary
        sentences = cleaned[:1000].split('.')
        if len(sentences) > 1:
            cleaned = '. '.join(sentences[:-1]) + '.'
        else:
            cleaned = cleaned[:1000].rstrip() + '...'
    
    # Final cleanup and validation
    cleaned = cleaned.strip()
    
    # Ensure we have a valid prompt (minimum length)
    if len(cleaned) < 10:
        logger.warning(f"Prompt too short after cleaning: '{cleaned}'. Using fallback.")
        return "A beautiful artistic image in fantasy style"
    
    # Log the cleaned prompt for debugging
    logger.info(f"Cleaned prompt: '{cleaned}'")
    
    return cleaned


# Standard dimension presets based on aspect ratios
ASPECT_RATIO_DIMENSIONS = {
    "16:9": {
        "large": (1920, 1080),
        "medium": (1280, 720), 
        "small": (854, 480)
    },
    "4:3": {
        "large": (1600, 1200),
        "medium": (1024, 768),
        "small": (800, 600)
    },
    "1:1": {
        "large": (1200, 1200),
        "medium": (800, 800),
        "small": (400, 400)
    },
    "9:16": {
        "large": (1080, 1920),
        "medium": (720, 1280),
        "small": (480, 854)
    }
}


def process_uploaded_image(
    image_data: bytes,
    aspect_ratio: str,
    dimension: str
) -> tuple[bytes, str]:
    """
    Process uploaded image: resize, crop to aspect ratio, and compress.
    
    Args:
        image_data: Raw image data bytes
        aspect_ratio: Target aspect ratio (16:9, 4:3, 1:1, 9:16)
        dimension: Target dimension string (e.g., "1344x768")
        
    Returns:
        Tuple of (processed_image_bytes, file_extension)
    """
    if aspect_ratio not in ASPECT_RATIO_DIMENSIONS:
        raise ValueError(f"Unsupported aspect ratio: {aspect_ratio}")
    
    if dimension not in ASPECT_RATIO_DIMENSIONS[aspect_ratio]:
        raise ValueError(f"Unsupported dimension: {dimension}")
    
    # Parse dimension string (e.g., "1344x768" -> (1344, 768))
    try:
        width_str, height_str = dimension.split('x')
        target_width, target_height = int(width_str), int(height_str)
    except ValueError:
        raise ValueError(f"Invalid dimension format: {dimension}. Expected format: WIDTHxHEIGHT")
    
    # Open and process the image
    try:
        # Open image from raw data
        image = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed (handles RGBA, P, etc.)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Calculate crop dimensions for center crop
        img_width, img_height = image.size
        target_aspect = target_width / target_height
        img_aspect = img_width / img_height
        
        if img_aspect > target_aspect:
            # Image is wider than target - crop horizontally
            new_width = int(img_height * target_aspect)
            left = (img_width - new_width) // 2
            right = left + new_width
            top = 0
            bottom = img_height
        else:
            # Image is taller than target - crop vertically  
            new_height = int(img_width / target_aspect)
            top = (img_height - new_height) // 2
            bottom = top + new_height
            left = 0
            right = img_width
        
        # Perform center crop
        cropped_image = image.crop((left, top, right, bottom))
        
        # Resize to target dimensions
        final_image = cropped_image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Optimize and compress
        final_image = ImageOps.exif_transpose(final_image)  # Fix orientation
        
        # Save to bytes with compression
        output_buffer = io.BytesIO()
        final_image.save(
            output_buffer, 
            format='JPEG', 
            quality=85,  # Good balance of quality vs file size
            optimize=True
        )
        
        return output_buffer.getvalue(), 'jpg'
        
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise ValueError(f"Failed to process image: {str(e)}")


# Aspect ratio to dimension mapping
ASPECT_RATIO_DIMENSIONS = {
    '16x9': ['1344x768', '1920x1080', '2560x1440'],
    '4x3': ['1280x960', '1600x1200', '2048x1536'], 
    '1x1': ['1024x1024', '1280x1280', '1536x1536'],
    '9x16': ['768x1344', '1080x1920', '1440x2560']
}

router = APIRouter(
    prefix="/images",
    tags=["image-generation"],
    dependencies=[Depends(get_current_active_user)]
)

class ImageGenerationRequest(BaseModel):
    element_type: str
    element_id: int
    prompt_override: Optional[str] = None
    style_prompt: Optional[str] = None

class ImageGenerationModalRequest(BaseModel):
    entity_type: str
    entity_id: int
    prompt: str
    style: Optional[str] = None
    aspect_ratio: Optional[str] = None
    size: Optional[str] = None

class ImageUploadRequest(BaseModel):
    entity_type: str
    entity_id: int
    aspect_ratio: str  # 16:9, 4:3, 1:1, 9:16
    dimension: str     # Based on aspect ratio preset

class ImageResponse(BaseModel):
    id: int
    url: str
    prompt: str
    revised_prompt: Optional[str]
    created_at: str
    is_current: bool
    aspect_ratio: Optional[str] = None

class SetCurrentImageResponse(BaseModel):
    message: str
    image_id: int
    image_url: Optional[str]

async def generate_and_save_image_task(
    job_id: str,
    user_id: int,
    element_type: str,
    element_id: int,
    prompt: str
):
    from app.db.database import async_session_local
    from app.core.config import settings
    from app.models.generated_image import GeneratedImage

    logger.info(f"JOB_ID: {job_id} - Starting image generation for {element_type} ID: {element_id}")
    
    async with async_session_local() as db:
        await crud_job_status.update_job_status(db, job_id, state="RUNNING", status_message="Generating image with AI provider...")

    generation_result = await generate_image_with_active_provider(prompt, user_id)
    
    if not generation_result:
        async with async_session_local() as db:
            await crud_job_status.update_job_status(db, job_id, state="FAILED", result_message="AI image generation service failed.")
        return

    revised_prompt, content_type, image_bytes = generation_result.revised_prompt, generation_result.content_type, generation_result.image_bytes
    
    blob_service_client_async = None
    credential_for_storage_async = None
    image_url = None
    blob_name = ""

    try:
        async with async_session_local() as db:
            await crud_job_status.update_job_status(db, job_id, state="RUNNING", status_message="Uploading image to storage...")

        if settings.AZURE_STORAGE_CONNECTION_STRING:
            from azure.storage.blob.aio import BlobServiceClient
            blob_service_client_async = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        elif settings.AZURE_STORAGE_ACCOUNT_NAME:
            from azure.identity.aio import DefaultAzureCredential
            from azure.storage.blob.aio import BlobServiceClient
            account_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
            credential_for_storage_async = DefaultAzureCredential()
            blob_service_client_async = BlobServiceClient(account_url=account_url, credential=credential_for_storage_async)
        
        if not blob_service_client_async:
            raise ConnectionError("Azure Storage not configured for image upload.")

        async with blob_service_client_async:
            container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
            container_client = blob_service_client_async.get_container_client(container_name)
            
            if not await container_client.exists():
                await container_client.create_container(public_access='blob')
                logger.info(f"Created public blob container: {container_name}")

            image_uuid_for_path = uuid.uuid4()
            async with async_session_local() as db:
                element: Any = None
                world_id_for_path: Union[int, str] = "unknown_world"

                if element_type == "world":
                    element = await db.get(World, element_id)
                    if element: world_id_for_path = element.id
                elif element_type == "character":
                    element = await db.get(Character, element_id)
                    if element: world_id_for_path = element.world_id
                elif element_type == "location":
                    element = await db.get(Location, element_id)
                    if element: world_id_for_path = element.world_id
                elif element_type == "lore_item":
                    element = await db.get(LoreItem, element_id)
                    if element: world_id_for_path = element.world_id
                elif element_type == "act":
                    element = await db.get(Act, element_id)
                    if element and element.story: world_id_for_path = element.story.world_id
                elif element_type == "scene":
                    element = await db.get(Scene, element_id)
                    if element and element.act: world_id_for_path = element.act.story.world_id
                elif element_type == "story":
                    element = await db.get(Story, element_id)
                    if element: world_id_for_path = element.world_id
                elif element_type == "blog_post":
                    from app.models.blog_post import BlogPost
                    # For new blog posts, element_id might be 1 (dummy), so we handle it differently
                    if element_id == 1:
                        element = True  # Dummy element for validation
                        world_id_for_path = "blog"  # Use blog folder for new/temporary blog posts
                    else:
                        element = await db.get(BlogPost, element_id)
                        if element: 
                            world_id_for_path = "blog"  # Blog posts don't belong to a specific world
                
                if not element:
                    raise ValueError(f"Element {element_type} with ID {element_id} not found.")

                blob_name = f"worlds/{world_id_for_path}/{element_type}s/{element_id}/{image_uuid_for_path}.png"

            blob_client = container_client.get_blob_client(blob=blob_name)
            
            blob_content_settings = ContentSettings(content_type=content_type)
            await blob_client.upload_blob(image_bytes, overwrite=True, content_settings=blob_content_settings)
            image_url = blob_client.url
        
        async with async_session_local() as db:
            await crud_job_status.update_job_status(db, job_id, state="RUNNING", status_message="Updating database record...")
            
            new_image_record = GeneratedImage(
                image_uuid=image_uuid_for_path,
                blob_path=blob_name,
                prompt=prompt,
                revised_prompt=revised_prompt,
                element_type=element_type,
                associated_element_id=element_id,
                user_id=user_id
            )
            db.add(new_image_record)
            await db.flush()
            
            # --- BEGIN SECURITY FIX ---
            element_to_update: Any = None
            
            # Fetch the element with necessary relationships to check ownership
            if element_type == "world":
                element_to_update = await db.get(World, element_id)
                if element_to_update and element_to_update.user_id != user_id:
                    raise PermissionError(f"User {user_id} is not authorized to modify World {element_id}.")
            else:
                query = None
                if element_type == "character":
                    query = select(Character).where(Character.id == element_id).options(selectinload(Character.world))
                elif element_type == "location":
                    query = select(Location).where(Location.id == element_id).options(selectinload(Location.world))
                elif element_type == "lore_item":
                    query = select(LoreItem).where(LoreItem.id == element_id).options(selectinload(LoreItem.world))
                elif element_type == "act":
                    query = select(Act).where(Act.id == element_id).options(selectinload(Act.story).selectinload(Story.world))
                elif element_type == "story":
                    query = select(Story).where(Story.id == element_id).options(selectinload(Story.world))
                elif element_type == "scene":
                    query = select(Scene).where(Scene.id == element_id).options(selectinload(Scene.act).selectinload(Act.story).selectinload(Story.world))
                
                if query is not None:
                    result = await db.execute(query)
                    element_to_update = result.scalars().first()
                else:
                    raise ValueError(f"Invalid element_type '{element_type}' provided.")

                # Now, check ownership through the parent world
                if element_to_update:
                    owner_id = None
                    if hasattr(element_to_update, 'world') and element_to_update.world:
                        owner_id = element_to_update.world.user_id
                    elif hasattr(element_to_update, 'story') and element_to_update.story.world:
                        owner_id = element_to_update.story.world.user_id
                    elif hasattr(element_to_update, 'act') and element_to_update.act.story.world:
                        owner_id = element_to_update.act.story.world.user_id

                    if owner_id != user_id:
                        raise PermissionError(f"User {user_id} is not authorized to modify {element_type} ID {element_id}.")
            
            if not element_to_update:
                raise ValueError(f"Element {element_type} with ID {element_id} not found or permission denied.")
            # --- END SECURITY FIX ---

            element_to_update.current_image_id = new_image_record.id
            element_to_update.image_blob_path = blob_name
            db.add(element_to_update)
            await db.commit()
            logger.info(f"JOB_ID: {job_id} - Successfully created GeneratedImage ID {new_image_record.id} and linked it to {element_type} ID {element_id}.")

            await crud_job_status.update_job_status(db, job_id, state="COMPLETED", status_message="Image generation complete!", result_message=image_url)

    except (ValueError, PermissionError) as auth_err:
        logger.error(f"JOB_ID: {job_id} - Failed due to invalid data or permissions. Error: {auth_err}", exc_info=True)
        async with async_session_local() as db:
            await crud_job_status.update_job_status(db, job_id, state="FAILED", result_message=f"Authorization or value error: {str(auth_err)[:200]}")
    except Exception as e:
        logger.error(f"JOB_ID: {job_id} - Failed during image save/upload. Error: {e}", exc_info=True)
        async with async_session_local() as db:
            await crud_job_status.update_job_status(db, job_id, state="FAILED", result_message=f"Error: {str(e)[:200]}")
    finally:
        if credential_for_storage_async:
            await credential_for_storage_async.close()


@router.post("/", response_model=JobSubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
async def handle_image_generation_request(
    request: ImageGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    element_type = request.element_type
    element_id = request.element_id
    
    # Fetch the element to get its image_prompt_definition if no override is provided
    base_prompt = ""
    if not request.prompt_override or not request.prompt_override.strip():
        try:
            if element_type == "character":
                from app.crud import character as crud_character
                element = await crud_character.get_character(db, element_id)
                if element and element.image_prompt_definition:
                    base_prompt = element.image_prompt_definition.strip()
            elif element_type == "location":
                from app.crud import location as crud_location
                element = await crud_location.get_location(db, element_id)
                if element and element.image_prompt_definition:
                    base_prompt = element.image_prompt_definition.strip()
            elif element_type == "lore_item":
                from app.crud import lore_item as crud_lore_item
                element = await crud_lore_item.get_lore_item(db, element_id)
                if element and element.image_prompt_definition:
                    base_prompt = element.image_prompt_definition.strip()
            elif element_type == "act":
                from app.crud import act as crud_act
                element = await crud_act.get_act(db, element_id)
                if element and element.image_prompt_definition:
                    base_prompt = element.image_prompt_definition.strip()
            elif element_type == "scene":
                from app.crud import scene as crud_scene
                element = await crud_scene.get_scene(db, element_id)
                if element and element.image_prompt_definition:
                    base_prompt = element.image_prompt_definition.strip()
            elif element_type == "story":
                from app.crud import story as crud_story
                element = await crud_story.get_story(db, element_id)
                if element and element.image_prompt_definition:
                    base_prompt = element.image_prompt_definition.strip()
            
            if not base_prompt:
                # Fallback: create a basic prompt using element name/title
                if element_type == "character" and element and hasattr(element, 'name'):
                    base_prompt = f"Portrait of {element.name}"
                elif element_type == "location" and element and hasattr(element, 'name'):
                    base_prompt = f"Scenic view of {element.name}"
                elif element_type == "lore_item" and element and hasattr(element, 'title'):
                    base_prompt = f"Artistic depiction of {element.title}"
                elif element_type == "act" and element and hasattr(element, 'title'):
                    base_prompt = f"Dramatic scene from act '{element.title}'"
                elif element_type == "scene" and element and hasattr(element, 'title'):
                    # Create more detailed prompt for scenes using available content
                    scene_title = element.title or f"Scene {element.scene_number}"
                    scene_content = ""
                    if hasattr(element, 'summary') and element.summary:
                        scene_content = element.summary[:200]  # Limit length
                    elif hasattr(element, 'content') and element.content:
                        # Strip HTML and limit length
                        import re
                        clean_content = re.sub(r'<[^>]+>', '', element.content)
                        scene_content = clean_content[:200]
                    
                    if scene_content:
                        base_prompt = f"Fantasy scene, atmospheric lighting, detailed illustration --- Scene titled '{scene_title}' {scene_content.strip()}..."
                    else:
                        base_prompt = f"Fantasy scene, atmospheric lighting, detailed illustration --- Scene showing '{scene_title}'"
                elif element_type == "story" and element and hasattr(element, 'title'):
                    base_prompt = f"Fantasy book cover for '{element.title}'"
                else:
                    base_prompt = f"Artistic depiction of {element_type}"
                
                logger.warning(f"No image_prompt_definition found for {element_type} ID {element_id}, using fallback: {base_prompt}")
        
        except Exception as e:
            logger.error(f"Error fetching {element_type} ID {element_id} for image prompt: {e}")
            base_prompt = f"Artistic depiction of {element_type}"
    else:
        # Use the provided override
        base_prompt = request.prompt_override.strip()
    
    # Apply style prompt if provided
    final_prompt = base_prompt
    if request.style_prompt and request.style_prompt.strip():
        final_prompt = f"{request.style_prompt.strip()} --- {base_prompt}"
    
    # Clean and validate the final prompt using our cleaning function
    final_prompt = clean_image_prompt(final_prompt)
    if not final_prompt:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot generate image from an empty prompt.")
    
    # Save auto-generated prompt back to the element if no custom prompt was provided
    if not request.prompt_override or not request.prompt_override.strip():
        try:
            if element_type == "scene":
                from app.crud import scene as crud_scene
                scene_update_data = {"image_prompt_definition": final_prompt}
                await crud_scene.update_scene(db, element_id, scene_update_data)
                logger.info(f"Saved auto-generated prompt to scene {element_id}")
            elif element_type == "act":
                from app.crud import act as crud_act
                act_update_data = {"image_prompt_definition": final_prompt}
                await crud_act.update_act(db, element_id, act_update_data)
                logger.info(f"Saved auto-generated prompt to act {element_id}")
            elif element_type == "story":
                from app.crud import story as crud_story
                story_update_data = {"image_prompt_definition": final_prompt}
                await crud_story.update_story(db, element_id, story_update_data)
                logger.info(f"Saved auto-generated prompt to story {element_id}")
        except Exception as e:
            logger.warning(f"Could not save auto-generated prompt to {element_type} {element_id}: {e}")
    
    logger.info(f"Image generation for {element_type} ID {element_id} - Final prompt: {final_prompt[:150]}...")

    # Determine world_id for the element
    world_id = None
    try:
        if element_type == "character":
            from app.crud import character as crud_character
            element = await crud_character.get_character(db, element_id)
            if element: world_id = element.world_id
        elif element_type == "location":
            from app.crud import location as crud_location
            element = await crud_location.get_location(db, element_id)
            if element: world_id = element.world_id
        elif element_type == "lore_item":
            from app.crud import lore_item as crud_lore_item
            element = await crud_lore_item.get_lore_item(db, element_id)
            if element: world_id = element.world_id
        # Add other element types as needed
    except Exception as e:
        logger.warning(f"Could not determine world_id for {element_type} {element_id}: {e}")
    
    # Use async image service for detached processing
    job_id = await AsyncImageService.submit_image_generation_job(
        db=db,
        user_id=current_user.id,
        prompt=final_prompt,
        element_type=element_type,
        element_id=element_id,
        world_id=world_id
    )
    
    return JobSubmissionResponse(
        message="Image generation job started successfully.",
        job_id=job_id
    )


@router.get("/job/{job_id}/status")
async def get_image_generation_job_status(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get the current status of an image generation job"""
    job_status = await AsyncImageService.get_job_status(db, job_id)
    
    if not job_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Verify job belongs to current user (security check)
    result = await db.execute(
        select(JobStatus).where(
            JobStatus.job_id == job_id,
            JobStatus.user_id == current_user.id
        )
    )
    job_record = result.scalar_one_or_none()
    
    if not job_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or access denied"
        )
    
    return job_status


@router.get("/jobs")
async def list_user_image_generation_jobs(
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List recent image generation jobs for the current user"""
    if limit > 100:
        limit = 100  # Prevent excessive queries
    
    jobs = await AsyncImageService.get_user_image_jobs(db, current_user.id, limit)
    
    return {
        "jobs": jobs,
        "active_task_count": AsyncImageService.get_active_task_count()
    }


@router.get("/jobs/all")
async def list_all_image_generation_jobs(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """List all image generation jobs (admin only)"""
    
    # Check if user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    if limit > 200:
        limit = 200  # Prevent excessive queries
    
    # Get all jobs with user information
    result = await db.execute(
        select(JobStatus, User)
        .join(User, JobStatus.user_id == User.id)
        .where(JobStatus.job_type == JobTypeEnum.IMAGE_GENERATION)
        .order_by(JobStatus.created_at.desc())
        .limit(limit)
    )
    
    jobs_with_users = result.all()
    
    job_list = []
    for job, user in jobs_with_users:
        job_data = {
            "job_id": job.job_id,
            "state": job.state.value,
            "status_message": job.status_message,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat(),
            "user_id": user.id,
            "username": user.username,
            "user_display_name": user.display_name or user.username
        }
        
        # Parse metadata from result_message JSON field
        if job.result_message:
            try:
                metadata = json.loads(job.result_message)
                
                if job.state in [JobStateEnum.PENDING, JobStateEnum.RUNNING]:
                    # For pending/running jobs, result_message contains initial metadata
                    job_data["element_type"] = metadata.get("element_type")
                    job_data["element_id"] = metadata.get("element_id")
                    job_data["world_id"] = metadata.get("world_id")
                    prompt = metadata.get("prompt", "")
                    job_data["prompt"] = prompt[:100] + "..." if len(prompt) > 100 else prompt
                
                elif job.state == JobStateEnum.COMPLETED:
                    # For completed jobs, result_message contains result data
                    job_data["element_type"] = metadata.get("element_type")
                    job_data["element_id"] = metadata.get("element_id")
                    job_data["world_id"] = metadata.get("world_id")
                    
                    if "image_id" in metadata:
                        job_data["result"] = {
                            "image_id": metadata["image_id"],
                            "blob_path": metadata.get("blob_path")
                        }
                        
                        # Get prompt from the GeneratedImage record
                        try:
                            from app.models.generated_image import GeneratedImage
                            gen_image_result = await db.execute(
                                select(GeneratedImage).where(GeneratedImage.id == metadata["image_id"])
                            )
                            gen_image = gen_image_result.scalar_one_or_none()
                            
                            if gen_image and gen_image.prompt:
                                prompt = gen_image.prompt
                                job_data["prompt"] = prompt[:100] + "..." if len(prompt) > 100 else prompt
                        except Exception as e:
                            logger.warning(f"Failed to get prompt from GeneratedImage for job {job.job_id}: {e}")
                        
                        # Construct image URL
                        if metadata.get("blob_path") and settings.AZURE_STORAGE_ACCOUNT_NAME:
                            container = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
                            image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container}/{metadata['blob_path']}"
                            job_data["image_url"] = image_url
                
            except Exception as e:
                logger.warning(f"Failed to parse job result_message for job {job.job_id}: {e}")
        
        job_list.append(job_data)
    
    return {
        "jobs": job_list,
        "active_task_count": AsyncImageService.get_active_task_count()
    }


# New endpoints for the image generation modal
@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_image_for_modal(
    request: ImageGenerationModalRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Generate image for the modal interface with immediate response"""
    
    # Check user balance (100 coins per generation)
    generation_cost = 100
    from app.crud.billing import billing_crud
    user_account = await billing_crud.get_or_create_user_account(db, current_user.id)
    if user_account.current_balance < generation_cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient coins for image generation"
        )
    
    # Build the prompt with style
    final_prompt = request.prompt
    if request.style and request.style != "realistic":
        # Load art styles from the Prompts table
        art_style_prompts = await crud_prompt.get_prompts_by_type(
            db=db,
            prompt_type=PromptTypeEnum.IMAGE_STYLE,
            is_active=True
        )
        
        # Convert to dictionary for lookup
        style_prefixes = {}
        for prompt in art_style_prompts:
            # Use the prompt title as the style key (lowercase with underscores)
            style_key = prompt.title.lower().replace(' ', '_')
            style_prefixes[style_key] = prompt.prompt_content
        
        if request.style in style_prefixes:
            final_prompt = f"{style_prefixes[request.style]} --- {request.prompt}"
    
    # Clean the prompt
    final_prompt = clean_image_prompt(final_prompt)
    if not final_prompt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid prompt provided"
        )
    
    try:
        # Determine image size from request
        image_size = request.size or settings.DEFAULT_IMAGE_SIZE
        
        # Generate image synchronously for immediate response
        generation_result = await generate_image_with_active_provider(final_prompt, current_user.id, image_size)
        
        if not generation_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Image generation failed"
            )
        
        # Deduct coins for image generation
        from app.models.user_transaction import TransactionType
        from app.schemas.billing import UserTransactionCreate
        from decimal import Decimal
        
        # Update account balance
        new_balance = user_account.current_balance - Decimal(str(generation_cost))
        
        # Create transaction record
        transaction_data = UserTransactionCreate(
            user_account_id=user_account.id,
            transaction_type=TransactionType.AI_COST_DEDUCTION,
            amount=-Decimal(str(generation_cost)),  # Negative for deduction
            balance_after=new_balance,
            description=f"Image generation for {request.entity_type} {request.entity_id}"
        )
        
        await billing_crud.create_transaction(db, transaction_data)
        
        # Update account balance
        user_account.current_balance = new_balance
        user_account.total_spent += Decimal(str(generation_cost))
        await db.commit()
        
        # Upload to Azure Storage
        blob_service_client_async = None
        if settings.AZURE_STORAGE_CONNECTION_STRING:
            blob_service_client_async = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        elif settings.AZURE_STORAGE_ACCOUNT_NAME:
            from azure.identity.aio import DefaultAzureCredential
            account_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
            credential = DefaultAzureCredential()
            blob_service_client_async = BlobServiceClient(account_url=account_url, credential=credential)
        
        if not blob_service_client_async:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Azure Storage not configured"
            )
        
        # Convert to JPEG for storage saving
        from PIL import Image
        import io
        
        # Convert image to JPEG
        original_image = Image.open(io.BytesIO(generation_result.image_bytes))
        if original_image.mode in ("RGBA", "LA", "P"):
            # Convert to RGB for JPEG
            rgb_image = Image.new("RGB", original_image.size, (255, 255, 255))
            rgb_image.paste(original_image, mask=original_image.split()[-1] if original_image.mode == "RGBA" else None)
            original_image = rgb_image
        
        # Save as JPEG with quality compression
        jpeg_buffer = io.BytesIO()
        original_image.save(jpeg_buffer, format="JPEG", quality=85, optimize=True)
        jpeg_bytes = jpeg_buffer.getvalue()
        
        async with blob_service_client_async:
            container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
            container_client = blob_service_client_async.get_container_client(container_name)
            
            if not await container_client.exists():
                await container_client.create_container(public_access='blob')
            
            # Generate blob path
            image_uuid = uuid.uuid4()
            world_id = "unknown_world"
            
            # Get world_id based on entity type
            if request.entity_type == "story":
                story = await db.get(Story, request.entity_id)
                if story:
                    world_id = story.world_id
            elif request.entity_type == "act":
                act = await db.get(Act, request.entity_id)
                if act and act.story:
                    world_id = act.story.world_id
            elif request.entity_type == "scene":
                scene = await db.get(Scene, request.entity_id)
                if scene and scene.act and scene.act.story:
                    world_id = scene.act.story.world_id
            elif request.entity_type == "blog_post":
                from app.models.blog_post import BlogPost
                # For new blog posts, entity_id might be 1 (dummy), so we handle it differently
                if request.entity_id == 1:
                    world_id = "blog"  # Use blog folder for new/temporary blog posts
                else:
                    blog_post = await db.get(BlogPost, request.entity_id)
                    if blog_post:
                        world_id = "blog"  # Blog posts don't belong to a specific world
            
            blob_name = f"worlds/{world_id}/{request.entity_type}s/{request.entity_id}/{image_uuid}.jpg"
            blob_client = container_client.get_blob_client(blob=blob_name)
            
            blob_content_settings = ContentSettings(content_type="image/jpeg")
            await blob_client.upload_blob(jpeg_bytes, overwrite=True, content_settings=blob_content_settings)
            image_url = blob_client.url
        
        # Save to database
        from app.models.generated_image import GeneratedImage
        new_image = GeneratedImage(
            image_uuid=image_uuid,
            blob_path=blob_name,
            prompt=final_prompt,
            revised_prompt=generation_result.revised_prompt,
            element_type=request.entity_type,
            associated_element_id=request.entity_id,
            user_id=current_user.id,
            aspect_ratio=request.aspect_ratio  # Store aspect ratio for gallery display
        )
        db.add(new_image)
        await db.commit()
        await db.refresh(new_image)
        
        return {
            "id": new_image.id,
            "url": image_url,
            "prompt": final_prompt,
            "revised_prompt": generation_result.revised_prompt,
            "cost": generation_cost,
            "created_at": new_image.created_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )


@router.post("/upload")
async def upload_image(
    entity_type: str = Form(...),
    entity_id: int = Form(...),
    aspect_ratio: str = Form(...),
    image_file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Upload and process an image with specified aspect ratio and dimensions.
    Treats uploaded images the same as generated images in the system.
    """
    logger.info(f"Starting image upload for {entity_type} {entity_id} by user {current_user.id}")
    
    try:
        # Validate file type
        if not image_file.content_type or not image_file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Validate aspect ratio and get standard dimension
        if aspect_ratio not in ASPECT_RATIO_DIMENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid aspect ratio. Must be one of: {list(ASPECT_RATIO_DIMENSIONS.keys())}"
            )
        
        # Always use the first (standard) dimension for the aspect ratio
        dimension = ASPECT_RATIO_DIMENSIONS[aspect_ratio][0]
        
        # For now, we'll trust that the user has access to the entity they're uploading for
        # TODO: Add proper entity access validation if needed
        
        # Charge user for image upload processing (200 coins)
        upload_cost = Decimal('200.0000')
        charge_successful = await billing_service.charge_fixed_amount(
            db=db,
            user_id=current_user.id,
            amount=upload_cost,
            description=f"Image upload processing - {aspect_ratio} aspect ratio",
            service_type="image_upload"
        )
        
        if not charge_successful:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to process payment for image upload"
            )
        
        # Read and process the uploaded image
        image_data = await image_file.read()
        processed_image_data, file_extension = process_uploaded_image(
            image_data, aspect_ratio, dimension
        )
        
        # Upload to Azure Storage (same pattern as generate endpoint)
        blob_service_client_async = None
        if settings.AZURE_STORAGE_CONNECTION_STRING:
            blob_service_client_async = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
        elif settings.AZURE_STORAGE_ACCOUNT_NAME:
            from azure.identity.aio import DefaultAzureCredential
            account_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
            credential = DefaultAzureCredential()
            blob_service_client_async = BlobServiceClient(account_url=account_url, credential=credential)
        
        if not blob_service_client_async:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Azure Storage not configured"
            )
        
        async with blob_service_client_async:
            container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
            container_client = blob_service_client_async.get_container_client(container_name)
            
            if not await container_client.exists():
                await container_client.create_container(public_access='blob')
            
            # Generate blob path
            image_uuid = uuid.uuid4()
            world_id = "unknown_world"
            
            # Get world_id based on entity type (same logic as generate endpoint)
            if entity_type == "story":
                story = await db.get(Story, entity_id)
                if story:
                    world_id = story.world_id
            elif entity_type == "act":
                act = await db.get(Act, entity_id)
                if act and act.story:
                    world_id = act.story.world_id
            elif entity_type == "scene":
                scene = await db.get(Scene, entity_id)
                if scene and scene.act and scene.act.story:
                    world_id = scene.act.story.world_id
            elif entity_type == "blog_post":
                from app.models.blog_post import BlogPost
                if entity_id == 1:
                    world_id = "blog"  # Use blog folder for new/temporary blog posts
                else:
                    blog_post = await db.get(BlogPost, entity_id)
                    if blog_post:
                        world_id = "blog"  # Blog posts don't belong to a specific world
            
            blob_name = f"worlds/{world_id}/{entity_type}s/{entity_id}/{image_uuid}.jpg"
            blob_client = container_client.get_blob_client(blob=blob_name)
            
            blob_content_settings = ContentSettings(content_type="image/jpeg")
            await blob_client.upload_blob(processed_image_data, overwrite=True, content_settings=blob_content_settings)
            blob_url = blob_client.url
        
        logger.info(f"Uploaded image to blob storage: {blob_url}")
        
        # Save to database (same pattern as generate endpoint)
        from app.models.generated_image import GeneratedImage
        new_image = GeneratedImage(
            image_uuid=image_uuid,
            blob_path=blob_name,
            prompt=f"Uploaded image - {aspect_ratio} aspect ratio, {dimension} dimensions",
            revised_prompt=f"User uploaded image processed to {aspect_ratio} aspect ratio with {dimension} dimensions",
            element_type=entity_type,
            associated_element_id=entity_id,
            user_id=current_user.id,
            aspect_ratio=aspect_ratio  # Store aspect ratio for gallery display
        )
        
        db.add(new_image)
        await db.commit()
        await db.refresh(new_image)
        
        logger.info(f"Image upload completed successfully: {new_image.id}")
        
        return {
            "id": new_image.id,
            "url": blob_url,
            "prompt": new_image.prompt,
            "revised_prompt": new_image.revised_prompt,
            "cost": float(upload_cost),  # 200 coins for upload processing
            "created_at": new_image.created_at.isoformat(),
            "is_current": False,  # Uploaded images start as not current
            "aspect_ratio": aspect_ratio
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image upload failed: {str(e)}"
        )


@router.get("/{entity_type}/{entity_id}", response_model=List[ImageResponse])
async def get_entity_images(
    entity_type: str,
    entity_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all images for a specific entity"""
    
    # Verify user has access to this entity
    # This is a simplified check - you may want to implement more detailed authorization
    
    from app.models.generated_image import GeneratedImage
    
    # Get current image ID for the entity
    current_image_id = None
    if entity_type == "story":
        entity = await db.get(Story, entity_id)
        if entity:
            current_image_id = entity.current_image_id
    elif entity_type == "act":
        entity = await db.get(Act, entity_id)
        if entity:
            current_image_id = entity.current_image_id
    elif entity_type == "scene":
        entity = await db.get(Scene, entity_id)
        if entity:
            current_image_id = entity.current_image_id
    elif entity_type == "blog_post":
        from app.models.blog_post import BlogPost
        # For blog posts, we don't track current_image_id, so we'll determine it from featured_image_url
        # This is handled differently since blog posts store the URL directly
        pass
    
    # Get all images for this entity
    result = await db.execute(
        select(GeneratedImage)
        .where(GeneratedImage.element_type == entity_type)
        .where(GeneratedImage.associated_element_id == entity_id)
        .order_by(GeneratedImage.created_at.desc())
    )
    images = result.scalars().all()
    
    # Build response with image URLs
    image_list = []
    for image in images:
        image_url = None
        if image.blob_path and settings.AZURE_STORAGE_ACCOUNT_NAME:
            container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
            image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{image.blob_path}"
        
        image_list.append(ImageResponse(
            id=image.id,
            url=image_url or "",
            prompt=image.prompt or "",
            revised_prompt=image.revised_prompt,
            created_at=image.created_at.isoformat(),
            is_current=(current_image_id == image.id),
            aspect_ratio=image.aspect_ratio
        ))
    
    return image_list


@router.post("/{entity_type}/{entity_id}/set-current/{image_id}", response_model=SetCurrentImageResponse)
async def set_current_image(
    entity_type: str,
    entity_id: int,
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Set the current image for an entity"""
    
    # Verify the image exists and belongs to this entity
    from app.models.generated_image import GeneratedImage
    
    result = await db.execute(
        select(GeneratedImage)
        .where(GeneratedImage.id == image_id)
        .where(GeneratedImage.element_type == entity_type)
        .where(GeneratedImage.associated_element_id == entity_id)
    )
    image = result.scalar_one_or_none()
    
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found"
        )
    
    # Update the entity's current image
    if entity_type == "story":
        entity = await db.get(Story, entity_id)
        if entity:
            entity.current_image_id = image_id
            entity.image_blob_path = image.blob_path
    elif entity_type == "act":
        entity = await db.get(Act, entity_id)
        if entity:
            entity.current_image_id = image_id
            entity.image_blob_path = image.blob_path
    elif entity_type == "scene":
        entity = await db.get(Scene, entity_id)
        if entity:
            entity.current_image_id = image_id
            entity.image_blob_path = image.blob_path
    elif entity_type == "blog_post":
        from app.models.blog_post import BlogPost
        # For dummy blog post ID (new posts), we don't update the database
        # The frontend will handle setting the featured_image_url when saving
        if entity_id != 1:
            entity = await db.get(BlogPost, entity_id)
            if entity:
                # Update the blog post's featured image URL
                entity.featured_image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES}/{image.blob_path}"
    
    await db.commit()
    
    # Build image URL for response
    image_url = None
    if image.blob_path and settings.AZURE_STORAGE_ACCOUNT_NAME:
        container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
        image_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{container_name}/{image.blob_path}"
    
    return SetCurrentImageResponse(
        message="Current image updated successfully",
        image_id=image_id,
        image_url=image_url
    )


@router.delete("/{image_id}")
async def delete_image(
    image_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Delete an image from the gallery and Azure blob storage.
    Only the user who created the image can delete it.
    """
    logger.info(f"Deleting image {image_id} by user {current_user.id}")
    
    try:
        # Get the image and verify ownership
        from app.models.generated_image import GeneratedImage
        result = await db.execute(
            select(GeneratedImage).where(GeneratedImage.id == image_id)
        )
        image = result.scalar_one_or_none()
        
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Image not found"
            )
        
        # Verify user owns this image
        if image.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own images"
            )
        
        # Delete from Azure blob storage if blob_path exists
        if image.blob_path:
            try:
                blob_service_client_async = None
                if settings.AZURE_STORAGE_CONNECTION_STRING:
                    blob_service_client_async = BlobServiceClient.from_connection_string(settings.AZURE_STORAGE_CONNECTION_STRING)
                elif settings.AZURE_STORAGE_ACCOUNT_NAME:
                    from azure.identity.aio import DefaultAzureCredential
                    account_url = f"https://{settings.AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
                    credential = DefaultAzureCredential()
                    blob_service_client_async = BlobServiceClient(account_url=account_url, credential=credential)
                
                if blob_service_client_async:
                    async with blob_service_client_async:
                        container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
                        container_client = blob_service_client_async.get_container_client(container_name)
                        
                        # Delete the blob
                        blob_client = container_client.get_blob_client(blob=image.blob_path)
                        await blob_client.delete_blob()
                        logger.info(f"Deleted blob: {image.blob_path}")
                        
            except Exception as e:
                # Log but don't fail if blob deletion fails
                logger.warning(f"Failed to delete blob {image.blob_path}: {e}")
        
        # Delete from database
        await db.delete(image)
        await db.commit()
        
        logger.info(f"Successfully deleted image {image_id}")
        
        return {
            "message": "Image deleted successfully",
            "deleted_image_id": image_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting image {image_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete image: {str(e)}"
        )