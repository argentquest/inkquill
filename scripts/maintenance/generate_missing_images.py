#!/usr/bin/env python
"""
Script to generate images for stories, acts, and scenes that don't have them.
Usage: python scripts/generate_missing_images.py [options]
"""

import asyncio
import logging
import argparse
import sys
from pathlib import Path
from typing import Optional, List, Dict

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select, and_
    from sqlalchemy.orm import selectinload
    from app.db.database import async_session_local
    from app.models.story import Story
    from app.models.act import Act
    from app.models.scene import Scene
    from app.models.world import World
    from app.models.generated_image import GeneratedImage
    from app.services.image_service import generate_image_for_element
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error("Make sure you're running from the project root")
    sys.exit(1)


async def get_stories_without_images(
    db: AsyncSession,
    world_id: Optional[int] = None,
    limit: int = 10
) -> List[Story]:
    """Get stories that don't have current images"""
    
    query = select(Story).options(
        selectinload(Story.world)
    ).where(Story.current_image_id.is_(None))
    
    if world_id:
        query = query.where(Story.world_id == world_id)
    
    query = query.order_by(Story.world_id, Story.title).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_acts_without_images(
    db: AsyncSession,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None,
    limit: int = 10
) -> List[Act]:
    """Get acts that don't have images and have content"""
    
    # Get acts with content
    query = select(Act).options(
        selectinload(Act.story).selectinload(Story.world)
    ).where(
        and_(
            Act.description.isnot(None),
            Act.description != ""
        )
    )
    
    if story_id:
        query = query.where(Act.story_id == story_id)
    elif world_id:
        query = query.join(Story).where(Story.world_id == world_id)
    
    query = query.order_by(Act.story_id, Act.act_number).limit(limit)
    
    result = await db.execute(query)
    acts = result.scalars().all()
    
    # Filter out acts that already have images
    # Check GeneratedImage table for element_type='act'
    acts_with_images_result = await db.execute(
        select(GeneratedImage.associated_element_id)
        .where(GeneratedImage.element_type == 'act')
        .distinct()
    )
    acts_with_images = set(acts_with_images_result.scalars().all())
    
    return [act for act in acts if act.id not in acts_with_images]


async def get_scenes_without_images(
    db: AsyncSession,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None,
    limit: int = 10
) -> List[Scene]:
    """Get scenes that don't have current images and have content"""
    
    query = select(Scene).options(
        selectinload(Scene.act).selectinload(Act.story).selectinload(Story.world)
    ).where(
        and_(
            Scene.current_image_id.is_(None),
            Scene.content.isnot(None),
            Scene.content != ""
        )
    )
    
    if story_id:
        query = query.join(Act).where(Act.story_id == story_id)
    elif world_id:
        query = query.join(Act).join(Story).where(Story.world_id == world_id)
    
    query = query.order_by(Scene.act_id, Scene.scene_number).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def generate_story_images(
    db: AsyncSession,
    stories: List[Story],
    user_id: int,
    dry_run: bool = False
):
    """Generate images for stories"""
    
    if not stories:
        logger.info("No stories found that need images")
        return
    
    logger.info(f"Found {len(stories)} stories that need images")
    
    for i, story in enumerate(stories, 1):
        try:
            world_name = story.world.name if story.world else "Unknown World"
            logger.info(f"[{i}/{len(stories)}] Story: '{story.title}' (World: {world_name})")
            
            if dry_run:
                prompt_status = "Has prompt" if story.image_prompt_definition else "Needs prompt"
                logger.info(f"  Would generate image - {prompt_status}")
                continue
            
            # Check if story has image prompt definition
            if not story.image_prompt_definition or not story.image_prompt_definition.strip():
                logger.warning(f"  Story {story.id} has no image prompt definition - skipping")
                continue
            
            # Generate image using the image service
            logger.info(f"  Generating image for story {story.id}...")
            
            # Note: You'll need to implement this service method or use existing one
            # This is a placeholder for the actual image generation call
            logger.info(f"  Image generation would be called here for story {story.id}")
            # await generate_image_for_element(db, 'story', story.id, user_id)
            
        except Exception as e:
            logger.error(f"  Error generating image for story {story.id}: {e}")


async def generate_act_images(
    db: AsyncSession,
    acts: List[Act],
    user_id: int,
    dry_run: bool = False
):
    """Generate images for acts"""
    
    if not acts:
        logger.info("No acts found that need images")
        return
    
    logger.info(f"Found {len(acts)} acts that need images")
    
    for i, act in enumerate(acts, 1):
        try:
            story_title = act.story.title if act.story else "Unknown Story"
            world_name = act.story.world.name if act.story and act.story.world else "Unknown World"
            logger.info(f"[{i}/{len(acts)}] Act: '{act.title}' (Story: {story_title}, World: {world_name})")
            
            if dry_run:
                content_length = len(act.description) if act.description else 0
                logger.info(f"  Would generate image - Content length: {content_length} chars")
                continue
            
            # Generate image using the act description as prompt base
            logger.info(f"  Generating image for act {act.id}...")
            
            # Note: You'll need to implement this service method or use existing one
            logger.info(f"  Image generation would be called here for act {act.id}")
            # await generate_image_for_element(db, 'act', act.id, user_id)
            
        except Exception as e:
            logger.error(f"  Error generating image for act {act.id}: {e}")


async def generate_scene_images(
    db: AsyncSession,
    scenes: List[Scene],
    user_id: int,
    dry_run: bool = False
):
    """Generate images for scenes"""
    
    if not scenes:
        logger.info("No scenes found that need images")
        return
    
    logger.info(f"Found {len(scenes)} scenes that need images")
    
    for i, scene in enumerate(scenes, 1):
        try:
            scene_title = scene.title or f"Scene {scene.scene_number}"
            act_title = scene.act.title if scene.act else "Unknown Act"
            story_title = scene.act.story.title if scene.act and scene.act.story else "Unknown Story"
            
            logger.info(f"[{i}/{len(scenes)}] Scene: '{scene_title}' (Act: {act_title}, Story: {story_title})")
            
            if dry_run:
                content_length = len(scene.content) if scene.content else 0
                logger.info(f"  Would generate image - Content length: {content_length} chars")
                continue
            
            # Generate image using the scene content as prompt base
            logger.info(f"  Generating image for scene {scene.id}...")
            
            # Note: You'll need to implement this service method or use existing one
            logger.info(f"  Image generation would be called here for scene {scene.id}")
            # await generate_image_for_element(db, 'scene', scene.id, user_id)
            
        except Exception as e:
            logger.error(f"  Error generating image for scene {scene.id}: {e}")


async def main(args):
    """Main function"""
    async with async_session_local() as db:
        try:
            logger.info("=== MISSING IMAGES GENERATOR ===")
            
            # Apply filters
            world_id = args.world_id
            story_id = args.story_id
            user_id = args.user_id
            
            if world_id:
                result = await db.execute(select(World).where(World.id == world_id))
                world = result.scalar_one_or_none()
                if not world:
                    logger.error(f"World with ID {world_id} not found")
                    return
                logger.info(f"Filtering by world: {world.name}")
            
            if story_id:
                result = await db.execute(select(Story).where(Story.id == story_id))
                story = result.scalar_one_or_none()
                if not story:
                    logger.error(f"Story with ID {story_id} not found")
                    return
                logger.info(f"Filtering by story: {story.title}")
            
            if args.dry_run:
                logger.info("DRY RUN MODE - No images will be generated")
            
            # Get items that need images
            if not args.skip_stories:
                logger.info("\n=== CHECKING STORIES ===")
                stories = await get_stories_without_images(db, world_id, args.limit)
                await generate_story_images(db, stories, user_id, args.dry_run)
            
            if not args.skip_acts:
                logger.info("\n=== CHECKING ACTS ===")
                acts = await get_acts_without_images(db, world_id, story_id, args.limit)
                await generate_act_images(db, acts, user_id, args.dry_run)
            
            if not args.skip_scenes:
                logger.info("\n=== CHECKING SCENES ===")
                scenes = await get_scenes_without_images(db, world_id, story_id, args.limit)
                await generate_scene_images(db, scenes, user_id, args.dry_run)
            
            logger.info("\n=== GENERATION COMPLETE ===")
            
            if args.dry_run:
                logger.info("This was a dry run. Use --generate to actually create images.")
            
        except Exception as e:
            logger.error(f"Error in image generation: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate missing images for stories, acts, and scenes")
    parser.add_argument("--user-id", type=int, default=1, help="User ID for image generation")
    parser.add_argument("--world-id", type=int, help="Filter by world ID")
    parser.add_argument("--story-id", type=int, help="Filter by story ID")
    parser.add_argument("--limit", type=int, default=10, help="Maximum items to process per type")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be generated without doing it")
    parser.add_argument("--skip-stories", action="store_true", help="Skip story image generation")
    parser.add_argument("--skip-acts", action="store_true", help="Skip act image generation")
    parser.add_argument("--skip-scenes", action="store_true", help="Skip scene image generation")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)