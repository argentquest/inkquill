"""Service helpers for async image service."""

# /story_app/app/services/async_image_service.py

import asyncio
import uuid
import logging
import json
import base64
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.job_status import JobStatus, JobTypeEnum, JobStateEnum
from app.models.generated_image import GeneratedImage
from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.models.act import Act
from app.models.scene import Scene
from app.models.story import Story
from app.crud import job_status as crud_job_status
from app.services.image_service import generate_image_with_active_provider
from app.core.config import settings
from app.core.deps import get_db_session
from app.db import database as db_database
from app.services.storage_service import save_blob

logger = logging.getLogger(__name__)

# Global task storage for tracking active image generation tasks
active_image_tasks: Dict[str, asyncio.Task] = {}

class AsyncImageService:
    """Service for handling asynchronous image generation with job tracking"""
    
    @staticmethod
    async def submit_image_generation_job(
        db: AsyncSession,
        user_id: int,
        prompt: str,
        element_type: str,  # "character", "location", "lore_item", "act", "scene", "story"
        element_id: int,
        world_id: Optional[int] = None
    ) -> str:
        """
        Submit an image generation job and return job_id for tracking
        
        Args:
            db: Database session
            user_id: ID of user requesting generation
            prompt: Image generation prompt
            element_type: Type of element (character, location, etc.)
            element_id: ID of the specific element
            world_id: Optional world ID for organization
            
        Returns:
            job_id: Unique identifier for tracking the job
        """
        job_id = str(uuid.uuid4())
        
        # Create job metadata
        job_metadata = {
            "prompt": prompt,
            "element_type": element_type,
            "element_id": element_id,
            "world_id": world_id,
            "image_provider": settings.ACTIVE_IMAGE_PROVIDER,
            "image_size": settings.DEFAULT_IMAGE_SIZE
        }
        
        # Create job record
        await crud_job_status.create_job_status(
            db=db,
            job_id=job_id,
            job_type=JobTypeEnum.IMAGE_GENERATION,
            user_id=user_id,
            world_id=world_id,
            status_message="Image generation queued",
            result_message=json.dumps(job_metadata)
        )
        
        await db.commit()
        
        # Create detached async task for processing
        task = asyncio.create_task(
            AsyncImageService._process_image_generation_job(job_id)
        )
        active_image_tasks[job_id] = task
        
        logger.info(f"Created async image generation job {job_id} for user {user_id}, element {element_type}:{element_id}")
        return job_id
    
    @staticmethod
    async def _process_image_generation_job(job_id: str) -> None:
        """
        Process an image generation job asynchronously (detached from HTTP request)
        """
        # Use proper session context manager
        async with db_database.async_session_local() as db_session:
            try:
                # Get job details
                result = await db_session.execute(
                    select(JobStatus).where(JobStatus.job_id == job_id)
                )
                job = result.scalar_one_or_none()
                
                if not job:
                    logger.error(f"Job {job_id} not found")
                    return
                
                # Update job status to running
                job.state = JobStateEnum.RUNNING
                job.status_message = "Generating image with AI provider..."
                await db_session.commit()
                
                # Parse job metadata
                metadata = json.loads(job.result_message)
                prompt = metadata["prompt"]
                element_type = metadata["element_type"]
                element_id = metadata["element_id"]
                world_id = metadata.get("world_id")
                
                logger.info(f"Processing image generation job {job_id}: {element_type}:{element_id}")
                
                # Validate and clean the prompt
                from app.utils.prompt_validator import PromptValidator
                is_valid, cleaned_prompt, validation_msg = PromptValidator.validate_and_clean(prompt, element_type)
                
                if validation_msg:
                    logger.info(f"Prompt validation for job {job_id}: {validation_msg}")
                
                # Use the cleaned prompt
                prompt = cleaned_prompt
                
                # Generate image using active provider
                image_result = await generate_image_with_active_provider(
                    prompt=prompt,
                    user_id_for_log=job.user_id
                )
                
                if not image_result:
                    raise Exception("Image generation failed - no result returned")
                
                # Persist generated image to local storage
                blob_path = await AsyncImageService._upload_generated_image(
                    image_data=image_result.image_bytes,
                    element_type=element_type,
                    element_id=element_id,
                    world_id=world_id
                )
                
                # Create GeneratedImage record
                generated_image = GeneratedImage(
                    prompt=metadata["prompt"],
                    revised_prompt=image_result.revised_prompt,
                    blob_path=blob_path,
                    element_type=element_type,
                    associated_element_id=element_id,
                    user_id=job.user_id
                )
                db_session.add(generated_image)
                await db_session.flush()  # Get the ID
                
                # Update element's current_image_id
                await AsyncImageService._update_element_image(
                    db=db_session,
                    element_type=element_type,
                    element_id=element_id,
                    image_id=generated_image.id
                )
                
                # Update job status to completed
                job.state = JobStateEnum.COMPLETED
                job.status_message = "Image generation completed successfully"
                
                # Store result details
                result_data = {
                    "image_id": generated_image.id,
                    "blob_path": blob_path,
                    "revised_prompt": image_result.revised_prompt,
                    "provider": settings.ACTIVE_IMAGE_PROVIDER,
                    "element_type": element_type,
                    "element_id": element_id,
                    "world_id": world_id
                }
                job.result_message = json.dumps(result_data)
                
                await db_session.commit()
                
                logger.info(f"Completed image generation job {job_id}: created image {generated_image.id}")
                
            except Exception as e:
                logger.error(f"Image generation job {job_id} failed: {e}", exc_info=True)
                
                # Update job status to failed
                try:
                    result = await db_session.execute(
                        select(JobStatus).where(JobStatus.job_id == job_id)
                    )
                    job = result.scalar_one_or_none()
                    if job:
                        job.state = JobStateEnum.FAILED
                        job.status_message = f"Image generation failed: {str(e)}"
                        await db_session.commit()
                except Exception as commit_error:
                    logger.error(f"Failed to update job status for {job_id}: {commit_error}")
            
            finally:
                # Clean up task reference
                active_image_tasks.pop(job_id, None)
    
    @staticmethod
    async def _upload_generated_image(
        image_data: bytes,
        element_type: str,
        element_id: int,
        world_id: Optional[int]
    ) -> str:
        """Upload image bytes to local storage."""
        # Generate blob path
        image_uuid = str(uuid.uuid4())
        if world_id:
            blob_path = f"worlds/{world_id}/{element_type}s/{element_id}/{image_uuid}.png"
        else:
            blob_path = f"{element_type}s/{element_id}/{image_uuid}.png"

        await save_blob("generated-images", blob_path, image_data, "image/png")
        logger.info(f"Uploaded image to local storage path: {blob_path}")
        return blob_path
    
    @staticmethod
    async def _update_element_image(
        db: AsyncSession,
        element_type: str,
        element_id: int,
        image_id: int
    ) -> None:
        """Update the element's current_image_id"""
        
        if element_type == "character":
            result = await db.execute(
                select(Character).where(Character.id == element_id)
            )
            element = result.scalar_one_or_none()
        elif element_type == "location":
            result = await db.execute(
                select(Location).where(Location.id == element_id)
            )
            element = result.scalar_one_or_none()
        elif element_type == "lore_item":
            result = await db.execute(
                select(LoreItem).where(LoreItem.id == element_id)
            )
            element = result.scalar_one_or_none()
        elif element_type == "act":
            result = await db.execute(
                select(Act).where(Act.id == element_id)
            )
            element = result.scalar_one_or_none()
        elif element_type == "scene":
            result = await db.execute(
                select(Scene).where(Scene.id == element_id)
            )
            element = result.scalar_one_or_none()
        elif element_type == "story":
            result = await db.execute(
                select(Story).where(Story.id == element_id)
            )
            element = result.scalar_one_or_none()
        else:
            logger.warning(f"Unknown element type for image update: {element_type}")
            return
        
        if element:
            element.current_image_id = image_id
            logger.info(f"Updated {element_type} {element_id} with new image {image_id}")
    
    @staticmethod
    async def get_job_status(db: AsyncSession, job_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of an image generation job"""
        result = await db.execute(
            select(JobStatus).where(JobStatus.job_id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            return None
        
        status_data = {
            "job_id": job.job_id,
            "state": job.state.value,
            "status_message": job.status_message,
            "created_at": job.created_at.isoformat(),
            "updated_at": job.updated_at.isoformat()
        }
        
        # Include result data if completed
        if job.state == JobStateEnum.COMPLETED and job.result_message:
            try:
                result_data = json.loads(job.result_message)
                if "image_id" in result_data:
                    status_data["result"] = result_data
                    
                    # Also fetch the actual image URL for immediate display
                    from app.models.generated_image import GeneratedImage
                    image_result = await db.execute(
                        select(GeneratedImage).where(GeneratedImage.id == result_data["image_id"])
                    )
                    generated_image = image_result.scalar_one_or_none()
                    if generated_image and generated_image.blob_url:
                        status_data["result"]["image_url"] = generated_image.blob_url
                        
                    # Include the element info for context
                    if "element_type" in result_data and "element_id" in result_data:
                        status_data["result"]["element_type"] = result_data["element_type"]
                        status_data["result"]["element_id"] = result_data["element_id"]
            except Exception as e:
                logger.warning(f"Error parsing job result data for {job.job_id}: {e}")
                pass
        
        return status_data
    
    @staticmethod
    async def get_user_image_jobs(
        db: AsyncSession, 
        user_id: int, 
        limit: int = 20
    ) -> list[Dict[str, Any]]:
        """Get recent image generation jobs for a user"""
        result = await db.execute(
            select(JobStatus)
            .where(JobStatus.user_id == user_id)
            .where(JobStatus.job_type == JobTypeEnum.IMAGE_GENERATION)
            .order_by(JobStatus.created_at.desc())
            .limit(limit)
        )
        jobs = result.scalars().all()
        
        job_list = []
        for job in jobs:
            job_data = {
                "job_id": job.job_id,
                "state": job.state.value,
                "status_message": job.status_message,
                "created_at": job.created_at.isoformat(),
                "updated_at": job.updated_at.isoformat()
            }
            
            # Parse metadata if available
            if job.result_message:
                try:
                    metadata = json.loads(job.result_message)
                    if job.state in [JobStateEnum.PENDING, JobStateEnum.RUNNING]:
                        # Job metadata
                        job_data["element_type"] = metadata.get("element_type")
                        job_data["element_id"] = metadata.get("element_id")
                        prompt = metadata.get("prompt", "")
                        job_data["prompt"] = prompt[:100] + "..." if len(prompt) > 100 else prompt
                    else:
                        # Result data for completed jobs
                        if "image_id" in metadata:
                            job_data["result"] = metadata
                except:
                    pass
            
            job_list.append(job_data)
        
        return job_list
    
    @staticmethod
    def get_active_task_count() -> int:
        """Get number of currently active image generation tasks"""
        return len(active_image_tasks)
    
    @staticmethod
    def get_active_task_ids() -> list[str]:
        """Get list of currently active job IDs"""
        return list(active_image_tasks.keys())

