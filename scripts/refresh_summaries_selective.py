#!/usr/bin/env python
"""
Script to selectively refresh AI summaries for acts and scenes.
Can filter by world, story, or process only items without summaries.

Usage examples:
    # Refresh all summaries
    python scripts/refresh_summaries_selective.py
    
    # Refresh only for a specific world
    python scripts/refresh_summaries_selective.py --world-id 5
    
    # Refresh only for a specific story
    python scripts/refresh_summaries_selective.py --story-id 10
    
    # Only process items without existing summaries
    python scripts/refresh_summaries_selective.py --only-missing
    
    # Combine filters
    python scripts/refresh_summaries_selective.py --world-id 5 --only-missing
"""

import asyncio
import logging
import argparse
import sys
from pathlib import Path
from typing import Optional, List

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from app.db.database import async_session_local
from app.models.act import Act
from app.models.scene import Scene
from app.models.story import Story
from app.models.world import World
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


async def get_filtered_acts(
    db: AsyncSession,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None,
    only_missing: bool = False
) -> List[Act]:
    """Get acts based on filters"""
    query = select(Act).options(selectinload(Act.story))
    
    conditions = []
    
    if story_id:
        conditions.append(Act.story_id == story_id)
    elif world_id:
        # Need to join with Story to filter by world
        query = query.join(Story).where(Story.world_id == world_id)
    
    if only_missing:
        conditions.append(or_(Act.ai_summary == None, Act.ai_summary == ""))
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Act.story_id, Act.act_number)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_filtered_scenes(
    db: AsyncSession,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None,
    only_missing: bool = False
) -> List[Scene]:
    """Get scenes based on filters"""
    query = select(Scene).options(selectinload(Scene.act).selectinload(Act.story))
    
    conditions = []
    
    if story_id:
        query = query.join(Act).where(Act.story_id == story_id)
    elif world_id:
        # Need to join with Act and Story to filter by world
        query = query.join(Act).join(Story).where(Story.world_id == world_id)
    
    if only_missing:
        conditions.append(or_(Scene.ai_summary == None, Scene.ai_summary == ""))
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.order_by(Scene.act_id, Scene.scene_number)
    
    result = await db.execute(query)
    return result.scalars().all()


async def refresh_filtered_act_summaries(
    db: AsyncSession,
    user_id: int,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None,
    only_missing: bool = False,
    dry_run: bool = False
):
    """Refresh AI summaries for filtered acts"""
    acts = await get_filtered_acts(db, world_id, story_id, only_missing)
    
    total_acts = len(acts)
    success_count = 0
    skip_count = 0
    error_count = 0
    
    logger.info(f"Found {total_acts} acts matching filters")
    
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        for act in acts:
            story_title = act.story.title if act.story else "Unknown Story"
            has_summary = bool(act.ai_summary and act.ai_summary.strip())
            logger.info(f"  Act {act.id}: '{act.title}' (Story: {story_title}) - Has summary: {has_summary}")
        return
    
    for i, act in enumerate(acts, 1):
        try:
            # Skip acts without description
            if not act.description or not act.description.strip():
                logger.info(f"[{i}/{total_acts}] Skipping act {act.id} '{act.title}' - no content")
                skip_count += 1
                continue
            
            story_title = act.story.title if act.story else "Unknown Story"
            logger.info(f"[{i}/{total_acts}] Processing act {act.id} '{act.title}' from '{story_title}'...")
            
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
    
    return {
        "total": total_acts,
        "success": success_count,
        "skipped": skip_count,
        "errors": error_count
    }


async def refresh_filtered_scene_summaries(
    db: AsyncSession,
    user_id: int,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None,
    only_missing: bool = False,
    dry_run: bool = False
):
    """Refresh AI summaries for filtered scenes"""
    scenes = await get_filtered_scenes(db, world_id, story_id, only_missing)
    
    total_scenes = len(scenes)
    success_count = 0
    skip_count = 0
    error_count = 0
    
    logger.info(f"Found {total_scenes} scenes matching filters")
    
    if dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        for scene in scenes:
            act_title = scene.act.title if scene.act else "Unknown Act"
            story_title = scene.act.story.title if scene.act and scene.act.story else "Unknown Story"
            has_summary = bool(scene.ai_summary and scene.ai_summary.strip())
            logger.info(f"  Scene {scene.id}: '{scene.title}' (Act: {act_title}, Story: {story_title}) - Has summary: {has_summary}")
        return
    
    for i, scene in enumerate(scenes, 1):
        try:
            # Skip scenes without content
            if not scene.content or not scene.content.strip():
                logger.info(f"[{i}/{total_scenes}] Skipping scene {scene.id} '{scene.title}' - no content")
                skip_count += 1
                continue
            
            act_title = scene.act.title if scene.act else "Unknown Act"
            logger.info(f"[{i}/{total_scenes}] Processing scene {scene.id} '{scene.title}' from act '{act_title}'...")
            
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
    
    return {
        "total": total_scenes,
        "success": success_count,
        "skipped": skip_count,
        "errors": error_count
    }


async def main(args):
    """Main function"""
    async with async_session_local() as db:
        try:
            # Verify user exists
            result = await db.execute(select(User).where(User.id == args.user_id))
            user = result.scalar_one_or_none()
            if not user:
                logger.error(f"User with ID {args.user_id} not found")
                return
            
            logger.info(f"Running summary refresh as user: {user.email}")
            
            # Log filters
            filters = []
            if args.world_id:
                result = await db.execute(select(World).where(World.id == args.world_id))
                world = result.scalar_one_or_none()
                if world:
                    filters.append(f"World: {world.name}")
                else:
                    logger.error(f"World with ID {args.world_id} not found")
                    return
            
            if args.story_id:
                result = await db.execute(select(Story).where(Story.id == args.story_id))
                story = result.scalar_one_or_none()
                if story:
                    filters.append(f"Story: {story.title}")
                else:
                    logger.error(f"Story with ID {args.story_id} not found")
                    return
            
            if args.only_missing:
                filters.append("Only items without summaries")
            
            if filters:
                logger.info(f"Filters: {', '.join(filters)}")
            else:
                logger.info("No filters - processing all items")
            
            if args.dry_run:
                logger.info("DRY RUN MODE ENABLED")
            
            # Process based on what user wants
            if not args.skip_acts:
                logger.info("\n" + "="*50)
                logger.info("REFRESHING ACT SUMMARIES")
                logger.info("="*50)
                act_results = await refresh_filtered_act_summaries(
                    db, args.user_id, args.world_id, args.story_id, 
                    args.only_missing, args.dry_run
                )
                
                if not args.dry_run:
                    logger.info(f"Acts: {act_results['total']} total, "
                               f"{act_results['success']} success, "
                               f"{act_results['skipped']} skipped, "
                               f"{act_results['errors']} errors")
            
            if not args.skip_scenes:
                logger.info("\n" + "="*50)
                logger.info("REFRESHING SCENE SUMMARIES")
                logger.info("="*50)
                scene_results = await refresh_filtered_scene_summaries(
                    db, args.user_id, args.world_id, args.story_id, 
                    args.only_missing, args.dry_run
                )
                
                if not args.dry_run:
                    logger.info(f"Scenes: {scene_results['total']} total, "
                               f"{scene_results['success']} success, "
                               f"{scene_results['skipped']} skipped, "
                               f"{scene_results['errors']} errors")
            
            logger.info("\n" + "="*50)
            logger.info("REFRESH COMPLETE")
            logger.info("="*50)
            
        except Exception as e:
            logger.error(f"Fatal error: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Selectively refresh AI summaries")
    parser.add_argument("--user-id", type=int, default=1, help="User ID for operations")
    parser.add_argument("--world-id", type=int, help="Filter by world ID")
    parser.add_argument("--story-id", type=int, help="Filter by story ID")
    parser.add_argument("--only-missing", action="store_true", help="Only process items without summaries")
    parser.add_argument("--skip-acts", action="store_true", help="Skip processing acts")
    parser.add_argument("--skip-scenes", action="store_true", help="Skip processing scenes")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without making changes")
    
    args = parser.parse_args()
    
    if args.world_id and args.story_id:
        logger.warning("Both world-id and story-id specified. Story-id filter will take precedence.")
    
    asyncio.run(main(args))