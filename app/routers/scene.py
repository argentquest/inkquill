# /ai_rag_story_app/app/routers/scene.py

from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_active_user
from app.core.azure_deps import get_blob_service_client
from azure.storage.blob.aio import BlobServiceClient
from app.models.user import User
from app.models.act import Act
from app.models.story import Story
from app.models.scene import Scene
from app.models.generated_image import GeneratedImage
from app.schemas.scene import SceneCreate, SceneRead, SceneUpdate
from app.schemas.image import GeneratedImageRead
from app.crud import scene as crud_scene
from app.crud import story as crud_story
from app.crud import generated_image as crud_generated_image
from app.processing.scene_processor import generate_and_save_scenes_for_act_task
from app.services.summary_generation_service import generate_ai_summary_for_scene

# --- Use shared dependencies for consistency ---
from app.core.dependencies_shared import get_act_and_verify_ownership

logger = logging.getLogger(__name__)

router_act_scenes = APIRouter(
    prefix="/acts/{act_id}/scenes", 
    tags=["act-scenes"],
    dependencies=[Depends(get_current_active_user)] 
)

router_scenes = APIRouter(
    prefix="/scenes",
    tags=["scenes"],
    dependencies=[Depends(get_current_active_user)]
)

async def get_scene_and_verify_ownership(
    scene_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
) -> Scene:
    db_scene = await crud_scene.get_scene(db, scene_id=scene_id)
    if not db_scene:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scene not found")
    if not db_scene.act or not await crud_story.get_story_for_user(db, story_id=db_scene.act.story_id, user_id=current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this scene")
    return db_scene

@router_act_scenes.post("/generate-scenes", status_code=status.HTTP_202_ACCEPTED, name="trigger_generate_scenes_for_act")
async def trigger_generate_scenes_for_act(
    background_tasks: BackgroundTasks, 
    db_act: Act = Depends(get_act_and_verify_ownership), 
    current_user: User = Depends(get_current_active_user) 
):
    if not db_act.description or not db_act.description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Act has no content to generate scenes from. Please add content to the act first."
        )
    
    background_tasks.add_task(
        generate_and_save_scenes_for_act_task,
        db_act_id=db_act.id,
        act_content_html=db_act.description, 
        story_id=db_act.story_id, 
        user_id=current_user.id 
    )
    
    return {"message": f"Scene generation started for Act '{db_act.title}'. Results will be available shortly."}


@router_act_scenes.get("/", response_model=List[SceneRead], name="list_scenes_for_act")
async def list_scenes_for_act(
    db_act: Act = Depends(get_act_and_verify_ownership), 
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session)
):
    return await crud_scene.get_scenes_by_act(db, act_id=db_act.id, skip=skip, limit=limit)

@router_act_scenes.post("/", response_model=SceneRead, status_code=status.HTTP_201_CREATED, name="create_new_scene_for_act")
async def create_new_scene_for_act(
    scene_in: SceneCreate, 
    db_act: Act = Depends(get_act_and_verify_ownership), 
    db: AsyncSession = Depends(get_db_session)
):
    if scene_in.scene_number is None: 
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Scene number is required.")
    try:
        created_scene = await crud_scene.create_scene(db=db, scene_in=scene_in, act_id=db_act.id)
        await db.commit()
        await db.refresh(created_scene)
        return created_scene
    except Exception as e: 
        await db.rollback()
        if "UniqueViolation" in str(e) or "_act_scene_number_uc" in str(e):
             raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"A scene with number '{scene_in.scene_number}' already exists for this act.")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not create scene.")


@router_scenes.get("/{scene_id}", response_model=SceneRead, name="get_single_scene")
async def get_single_scene(db_scene: Scene = Depends(get_scene_and_verify_ownership)):
    return db_scene

@router_scenes.put("/{scene_id}", response_model=SceneRead, name="update_existing_scene")
async def update_existing_scene(
    scene_in: SceneUpdate,
    db_scene: Scene = Depends(get_scene_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    try:
        updated_scene = await crud_scene.update_scene(db=db, db_scene=db_scene, scene_in=scene_in)
        await db.commit()
        await db.refresh(updated_scene)
        
        # Generate AI summary if content was updated
        if scene_in.content is not None and updated_scene.content:
            logger.info(f"Content updated for scene {updated_scene.id}, generating AI summary...")
            await generate_ai_summary_for_scene(db=db, scene=updated_scene, updater_user_id=current_user.id)
            await db.commit()
            await db.refresh(updated_scene)
        
        return updated_scene
    except Exception as e:
        await db.rollback()
        if "UniqueViolation" in str(e) or "_act_scene_number_uc" in str(e):
             raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Could not update. A scene with number '{scene_in.scene_number}' may already exist for this act.")
        raise HTTPException(status_code=500, detail="Could not update scene.")

@router_scenes.delete("/{scene_id}", status_code=status.HTTP_204_NO_CONTENT, name="delete_existing_scene")
async def delete_existing_scene(
    db_scene: Scene = Depends(get_scene_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        await crud_scene.delete_scene(db=db, db_scene=db_scene)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not delete scene.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router_scenes.get("/{scene_id}/images", response_model=List[GeneratedImageRead])
async def list_images_for_scene(
    db_scene: Scene = Depends(get_scene_and_verify_ownership),
    db: AsyncSession = Depends(get_db_session)
):
    logger.info(f"API: Fetching images for scene ID: {db_scene.id}, Type: 'scene'")
    images = await crud_generated_image.get_images_for_element(
        db, element_type="scene", element_id=db_scene.id
    )
    logger.info(f"API: Found {len(images)} images for scene ID: {db_scene.id}")
    return images

@router_scenes.post("/{scene_id}/set-current-image/{image_id}", response_model=SceneRead)
async def set_current_image_for_scene(
    db_scene: Scene = Depends(get_scene_and_verify_ownership),
    image_id: int = Path(..., description="The ID of the GeneratedImage to set as current."),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    image_to_set = await crud_generated_image.get_image(db, image_id=image_id)
    if not image_to_set or image_to_set.element_type != 'scene' or image_to_set.associated_element_id != db_scene.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found or does not belong to this scene.")
    
    db_scene.current_image_id = image_to_set.id
    
    db.add(db_scene)
    await db.commit()
    await db.refresh(db_scene)
    
    return db_scene