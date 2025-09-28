# /ai_rag_story_app/app/crud/scene.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, delete 
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
import logging

from app.models.scene import Scene 
from app.schemas.scene import SceneCreate, SceneUpdate 

logger = logging.getLogger(__name__)

async def get_next_scene_number(db: AsyncSession, act_id: int) -> int:
    max_scene_number_result = await db.execute(select(func.max(Scene.scene_number)).where(Scene.act_id == act_id))
    max_scene_number = max_scene_number_result.scalar_one_or_none()
    return (max_scene_number or 0) + 10

async def create_scene(db: AsyncSession, scene_in: SceneCreate, act_id: int) -> Scene:
    scene_data = scene_in.model_dump()
    logger.info(f"Creating scene for act_id: {act_id} with data: {scene_data}")
    db_scene = Scene(**scene_data, act_id=act_id)
    db.add(db_scene)
    await db.flush()
    await db.refresh(db_scene)
    logger.info(f"Scene ID: {db_scene.id} added to session for act_id: {act_id}")
    return db_scene

async def create_multiple_scenes(db: AsyncSession, scenes_data: List[Dict[str, Any]], act_id: int) -> List[Scene]:
    created_scenes: List[Scene] = []
    current_scene_number = 0 
    logger.info(f"Creating {len(scenes_data)} scenes for act_id: {act_id}")
    for i, scene_dict in enumerate(scenes_data):
        current_scene_number += 10 
        db_scene = Scene(
            act_id=act_id, scene_number=current_scene_number, **scene_dict
        )
        db.add(db_scene)
        created_scenes.append(db_scene)
    await db.flush()
    for scene in created_scenes:
        await db.refresh(scene)
    logger.info(f"Added {len(created_scenes)} scenes to session for act_id: {act_id}")
    return created_scenes

async def get_scene(db: AsyncSession, scene_id: int) -> Optional[Scene]:
    logger.debug(f"Fetching scene with ID: {scene_id}")
    result = await db.execute(select(Scene).filter(Scene.id == scene_id).options(
        selectinload(Scene.act), 
        selectinload(Scene.story_class),
        selectinload(Scene.current_image)
    ))
    return result.scalars().first()

async def get_scenes_by_act(db: AsyncSession, act_id: int, skip: int = 0, limit: int = 100) -> List[Scene]:
    logger.debug(f"Fetching scenes for act_id: {act_id}, skip: {skip}, limit: {limit}")
    result = await db.execute(select(Scene).filter(Scene.act_id == act_id).order_by(Scene.scene_number).offset(skip).limit(limit).options(
        selectinload(Scene.story_class),
        selectinload(Scene.current_image)
    ))
    return result.scalars().all()

async def update_scene(db: AsyncSession, db_scene: Scene, scene_in: SceneUpdate) -> Scene:
    update_data = scene_in.model_dump(exclude_unset=True)
    logger.info(f"Updating scene ID: {db_scene.id} with data: {update_data}")
    if update_data:
        for key, value in update_data.items():
            if hasattr(db_scene, key):
                setattr(db_scene, key, value)
    db.add(db_scene)
    await db.flush()
    await db.refresh(db_scene)
    logger.info(f"Scene ID: {db_scene.id} updated in session.")
    return db_scene

async def delete_scene(db: AsyncSession, db_scene: Scene) -> Scene:
    logger.info(f"Deleting scene ID: {db_scene.id}")
    await db.delete(db_scene)
    await db.flush()
    logger.info(f"Scene ID: {db_scene.id} marked for deletion in session.")
    return db_scene 

async def delete_scenes_for_act(db: AsyncSession, act_id: int) -> int:
    logger.info(f"Attempting to delete all scenes for act_id: {act_id}")
    stmt = delete(Scene).where(Scene.act_id == act_id)
    result = await db.execute(stmt)
    await db.flush()
    deleted_count = result.rowcount
    logger.info(f"Marked {deleted_count} scenes for deletion in session for act_id: {act_id}")
    return deleted_count