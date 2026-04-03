#!/usr/bin/env python
"""
Script to refresh AI summaries for all Acts and Scenes in the database.
Usage: python scripts/refresh_ai_summaries.py [--user-id USER_ID]
"""

import asyncio
import logging
import argparse
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import async_session_local
from app.models.act import Act
from app.models.scene import Scene
from app.models.user import User
from app.services.summary_generation_service import (
    generate_ai_summary_for_act,
    generate_ai_summary_for_scene
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def get_user(db: AsyncSession, user_id: int) -> User:
    """Get user by ID"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError(f"User with ID {user_id} not found")
    return user


async def refresh_all_act_summaries(db: AsyncSession, user_id: int):
    """Refresh AI summaries for all acts"""
    logger.info("Starting to refresh AI summaries for all acts...")
    
    # Get all acts
    result = await db.execute(
        select(Act).order_by(Act.story_id, Act.act_number)
    )
    acts = result.scalars().all()
    
    total_acts = len(acts)
    success_count = 0
    skip_count = 0
    error_count = 0
    
    logger.info(f"Found {total_acts} acts to process")
    
    for i, act in enumerate(acts, 1):
        try:
            # Skip acts without description
            if not act.description or not act.description.strip():
                logger.info(f"[{i}/{total_acts}] Skipping act {act.id} '{act.title}' - no content")
                skip_count += 1
                continue
            
            logger.info(f"[{i}/{total_acts}] Processing act {act.id} '{act.title}'...")
            
            # Generate summary
            summary = await generate_ai_summary_for_act(db, act, user_id)
            
            if summary:
                logger.info(f"[{i}/{total_acts}] Successfully generated summary for act {act.id}")
                success_count += 1
            else:
                logger.warning(f"[{i}/{total_acts}] Failed to generate summary for act {act.id}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"[{i}/{total_acts}] Error processing act {act.id}: {e}")
            error_count += 1
        
        # Commit after each act to save progress
        await db.commit()
    
    logger.info(f"Act summary refresh completed:")
    logger.info(f"  Total acts: {total_acts}")
    logger.info(f"  Successful: {success_count}")
    logger.info(f"  Skipped (no content): {skip_count}")
    logger.info(f"  Errors: {error_count}")
    
    return {
        "total": total_acts,
        "success": success_count,
        "skipped": skip_count,
        "errors": error_count
    }


async def refresh_all_scene_summaries(db: AsyncSession, user_id: int):
    """Refresh AI summaries for all scenes"""
    logger.info("Starting to refresh AI summaries for all scenes...")
    
    # Get all scenes
    result = await db.execute(
        select(Scene).order_by(Scene.act_id, Scene.scene_number)
    )
    scenes = result.scalars().all()
    
    total_scenes = len(scenes)
    success_count = 0
    skip_count = 0
    error_count = 0
    
    logger.info(f"Found {total_scenes} scenes to process")
    
    for i, scene in enumerate(scenes, 1):
        try:
            # Skip scenes without content
            if not scene.content or not scene.content.strip():
                logger.info(f"[{i}/{total_scenes}] Skipping scene {scene.id} '{scene.title}' - no content")
                skip_count += 1
                continue
            
            logger.info(f"[{i}/{total_scenes}] Processing scene {scene.id} '{scene.title}'...")
            
            # Generate summary
            summary = await generate_ai_summary_for_scene(db, scene, user_id)
            
            if summary:
                logger.info(f"[{i}/{total_scenes}] Successfully generated summary for scene {scene.id}")
                success_count += 1
            else:
                logger.warning(f"[{i}/{total_scenes}] Failed to generate summary for scene {scene.id}")
                error_count += 1
                
        except Exception as e:
            logger.error(f"[{i}/{total_scenes}] Error processing scene {scene.id}: {e}")
            error_count += 1
        
        # Commit after each scene to save progress
        await db.commit()
    
    logger.info(f"Scene summary refresh completed:")
    logger.info(f"  Total scenes: {total_scenes}")
    logger.info(f"  Successful: {success_count}")
    logger.info(f"  Skipped (no content): {skip_count}")
    logger.info(f"  Errors: {error_count}")
    
    return {
        "total": total_scenes,
        "success": success_count,
        "skipped": skip_count,
        "errors": error_count
    }


async def main(user_id: int):
    """Main function to refresh all summaries"""
    async with async_session_local() as db:
        try:
            # Verify user exists
            user = await get_user(db, user_id)
            logger.info(f"Running summary refresh as user: {user.email}")
            
            # Refresh act summaries
            logger.info("\n" + "="*50)
            logger.info("REFRESHING ACT SUMMARIES")
            logger.info("="*50)
            act_results = await refresh_all_act_summaries(db, user_id)
            
            # Refresh scene summaries
            logger.info("\n" + "="*50)
            logger.info("REFRESHING SCENE SUMMARIES")
            logger.info("="*50)
            scene_results = await refresh_all_scene_summaries(db, user_id)
            
            # Final summary
            logger.info("\n" + "="*50)
            logger.info("SUMMARY REFRESH COMPLETE")
            logger.info("="*50)
            logger.info(f"Acts processed: {act_results['total']} "
                       f"(Success: {act_results['success']}, "
                       f"Skipped: {act_results['skipped']}, "
                       f"Errors: {act_results['errors']})")
            logger.info(f"Scenes processed: {scene_results['total']} "
                       f"(Success: {scene_results['success']}, "
                       f"Skipped: {scene_results['skipped']}, "
                       f"Errors: {scene_results['errors']})")
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh AI summaries for all acts and scenes")
    parser.add_argument(
        "--user-id",
        type=int,
        default=1,
        help="User ID to use for the operations (default: 1)"
    )
    args = parser.parse_args()
    
    asyncio.run(main(args.user_id))