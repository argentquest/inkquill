#!/usr/bin/env python
"""
Automatically generate images for all stories, acts, and scenes that don't have them.
Uses default image style and auto-generated prompts.

Usage: python scripts/auto_generate_missing_images.py [options]
"""

import asyncio
import logging
import argparse
import sys
import re
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
    from app.services.async_image_service import AsyncImageService
    from app.core.config import settings
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)


def clean_image_prompt(prompt: str) -> str:
    """Clean and validate image prompt for AI image generation"""
    if not prompt:
        return ""
    
    # Remove newlines and excessive whitespace
    cleaned = re.sub(r'\s+', ' ', prompt.strip())
    
    # Fix common issues from AI-generated prompts
    cleaned = re.sub(r'\s+\w{1,3}$', '', cleaned)
    cleaned = re.sub(r',\s*\)$', ')', cleaned)
    cleaned = re.sub(r'\(\s*[^)]{1,10}\s*\)$', '', cleaned)
    
    # Remove incomplete sentences
    if any(cleaned.endswith(pattern) for pattern in ['aroun', ' She)', ', expressing', 'creatures aroun']):
        sentences = cleaned.split('.')
        if len(sentences) > 1:
            cleaned = '. '.join(sentences[:-1]) + '.'
        else:
            last_comma = cleaned.rfind(',')
            if last_comma > 50:
                cleaned = cleaned[:last_comma]
    
    # Cleanup
    cleaned = re.sub(r',\s*$', '', cleaned)
    cleaned = re.sub(r'\s*\($', '', cleaned)
    
    # Limit length
    if len(cleaned) > 1000:
        sentences = cleaned[:1000].split('.')
        if len(sentences) > 1:
            cleaned = '. '.join(sentences[:-1]) + '.'
        else:
            cleaned = cleaned[:1000].rstrip() + '...'
    
    cleaned = cleaned.strip()
    
    # Ensure minimum length
    if len(cleaned) < 10:
        return "A beautiful artistic image in fantasy style"
    
    return cleaned


def create_story_prompt(story: Story) -> str:
    """Create an image prompt for a story"""
    # Use existing image prompt if available
    if story.image_prompt_definition and story.image_prompt_definition.strip():
        return clean_image_prompt(story.image_prompt_definition)
    
    # Create prompt from story details
    prompt_parts = []
    
    # Base description
    if story.short_description and story.short_description.strip():
        # Extract key visual elements from description
        desc = story.short_description.strip()
        if len(desc) > 200:
            desc = desc[:200] + "..."
        prompt_parts.append(desc)
    else:
        prompt_parts.append(f"Epic fantasy story titled '{story.title}'")
    
    # Add genre and tone if available
    if story.story_genre:
        prompt_parts.append(f"in {story.story_genre} genre")
    
    if story.story_tone:
        prompt_parts.append(f"with {story.story_tone} tone")
    
    # Add world context if available
    if story.world and story.world.name:
        prompt_parts.append(f"set in the world of {story.world.name}")
    
    # Combine and add default style
    base_prompt = " ".join(prompt_parts)
    styled_prompt = f"Fantasy book cover art, cinematic lighting, detailed illustration --- {base_prompt}"
    
    return clean_image_prompt(styled_prompt)


def create_act_prompt(act: Act) -> str:
    """Create an image prompt for an act"""
    # Use existing image prompt if available
    if act.image_prompt_definition and act.image_prompt_definition.strip():
        return clean_image_prompt(act.image_prompt_definition)
    
    prompt_parts = []
    
    # Use act title and description
    if act.title:
        prompt_parts.append(f"Act titled '{act.title}'")
    
    if act.description and act.description.strip():
        # Extract visual elements from HTML content
        desc = re.sub(r'<[^>]+>', ' ', act.description)  # Remove HTML tags
        desc = re.sub(r'\s+', ' ', desc).strip()
        
        # Limit length and find key visual elements
        if len(desc) > 300:
            # Try to extract first few sentences with visual elements
            sentences = desc.split('.')[:3]
            desc = '. '.join(sentences)
            if len(desc) > 300:
                desc = desc[:300] + "..."
        
        prompt_parts.append(desc)
    else:
        prompt_parts.append(f"dramatic scene from {act.title if act.title else 'story act'}")
    
    # Add story context
    if act.story and act.story.title:
        prompt_parts.append(f"from the story '{act.story.title}'")
    
    # Combine with default style
    base_prompt = " ".join(prompt_parts)
    styled_prompt = f"Fantasy scene, dramatic lighting, detailed digital art --- {base_prompt}"
    
    return clean_image_prompt(styled_prompt)


def create_scene_prompt(scene: Scene) -> str:
    """Create an image prompt for a scene"""
    # Use existing image prompt if available
    if scene.image_prompt_definition and scene.image_prompt_definition.strip():
        return clean_image_prompt(scene.image_prompt_definition)
    
    prompt_parts = []
    
    # Use scene title and content
    scene_title = scene.title or f"Scene {scene.scene_number}"
    prompt_parts.append(f"Scene titled '{scene_title}'")
    
    if scene.content and scene.content.strip():
        # Extract visual elements from content
        content = re.sub(r'<[^>]+>', ' ', scene.content)  # Remove HTML tags
        content = re.sub(r'\s+', ' ', content).strip()
        
        # Extract key visual elements (first paragraph or first 200 chars)
        paragraphs = content.split('\n\n')
        if paragraphs:
            desc = paragraphs[0]
        else:
            desc = content
        
        if len(desc) > 250:
            # Find a natural break point
            sentences = desc.split('.')[:2]
            desc = '. '.join(sentences)
            if len(desc) > 250:
                desc = desc[:250] + "..."
        
        prompt_parts.append(desc)
    else:
        prompt_parts.append(f"dramatic scene showing {scene_title}")
    
    # Add mood if available
    if scene.mood:
        prompt_parts.append(f"with {scene.mood} mood")
    
    # Add act/story context
    if scene.act and scene.act.title:
        prompt_parts.append(f"from act '{scene.act.title}'")
    
    # Combine with default style
    base_prompt = " ".join(prompt_parts)
    styled_prompt = f"Fantasy scene, atmospheric lighting, detailed illustration --- {base_prompt}"
    
    return clean_image_prompt(styled_prompt)


async def get_stories_without_images(
    db: AsyncSession,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None,
    limit: int = 50
) -> List[Story]:
    """Get stories that don't have current images"""
    query = select(Story).options(
        selectinload(Story.world)
    ).where(Story.current_image_id.is_(None))
    
    if story_id:
        query = query.where(Story.id == story_id)
    elif world_id:
        query = query.where(Story.world_id == world_id)
    
    query = query.order_by(Story.world_id, Story.title).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_acts_without_images(
    db: AsyncSession,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None,
    limit: int = 50
) -> List[Act]:
    """Get acts that don't have images and have content"""
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
    limit: int = 50
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
) -> Dict[str, int]:
    """Generate images for stories"""
    stats = {"processed": 0, "queued": 0, "skipped": 0}
    
    if not stories:
        logger.info("No stories found that need images")
        return stats
    
    logger.info(f"Processing {len(stories)} stories for image generation")
    
    for i, story in enumerate(stories, 1):
        try:
            world_name = story.world.name if story.world else "Unknown World"
            logger.info(f"[{i}/{len(stories)}] Story: '{story.title}' (World: {world_name})")
            
            # Create prompt
            prompt = create_story_prompt(story)
            
            if dry_run:
                logger.info(f"  Would generate with prompt: {prompt[:100]}...")
                stats["processed"] += 1
                continue
            
            # Submit image generation job
            job_id = await AsyncImageService.submit_image_generation_job(
                db=db,
                user_id=user_id,
                prompt=prompt,
                element_type="story",
                element_id=story.id,
                world_id=story.world_id
            )
            
            logger.info(f"  Queued image generation job: {job_id}")
            stats["queued"] += 1
            
            # Small delay to avoid overwhelming the system
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"  Error processing story {story.id}: {e}")
            stats["skipped"] += 1
    
    return stats


async def generate_act_images(
    db: AsyncSession,
    acts: List[Act],
    user_id: int,
    dry_run: bool = False
) -> Dict[str, int]:
    """Generate images for acts"""
    stats = {"processed": 0, "queued": 0, "skipped": 0}
    
    if not acts:
        logger.info("No acts found that need images")
        return stats
    
    logger.info(f"Processing {len(acts)} acts for image generation")
    
    for i, act in enumerate(acts, 1):
        try:
            story_title = act.story.title if act.story else "Unknown Story"
            world_name = act.story.world.name if act.story and act.story.world else "Unknown World"
            logger.info(f"[{i}/{len(acts)}] Act: '{act.title}' (Story: {story_title}, World: {world_name})")
            
            # Create prompt
            prompt = create_act_prompt(act)
            
            if dry_run:
                logger.info(f"  Would generate with prompt: {prompt[:100]}...")
                stats["processed"] += 1
                continue
            
            # Submit image generation job
            job_id = await AsyncImageService.submit_image_generation_job(
                db=db,
                user_id=user_id,
                prompt=prompt,
                element_type="act",
                element_id=act.id,
                world_id=act.story.world_id if act.story else None
            )
            
            logger.info(f"  Queued image generation job: {job_id}")
            stats["queued"] += 1
            
            # Small delay
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"  Error processing act {act.id}: {e}")
            stats["skipped"] += 1
    
    return stats


async def generate_scene_images(
    db: AsyncSession,
    scenes: List[Scene],
    user_id: int,
    dry_run: bool = False
) -> Dict[str, int]:
    """Generate images for scenes"""
    stats = {"processed": 0, "queued": 0, "skipped": 0}
    
    if not scenes:
        logger.info("No scenes found that need images")
        return stats
    
    logger.info(f"Processing {len(scenes)} scenes for image generation")
    
    for i, scene in enumerate(scenes, 1):
        try:
            scene_title = scene.title or f"Scene {scene.scene_number}"
            act_title = scene.act.title if scene.act else "Unknown Act"
            story_title = scene.act.story.title if scene.act and scene.act.story else "Unknown Story"
            
            logger.info(f"[{i}/{len(scenes)}] Scene: '{scene_title}' (Act: {act_title}, Story: {story_title})")
            
            # Create prompt
            prompt = create_scene_prompt(scene)
            
            if dry_run:
                logger.info(f"  Would generate with prompt: {prompt[:100]}...")
                stats["processed"] += 1
                continue
            
            # Submit image generation job
            job_id = await AsyncImageService.submit_image_generation_job(
                db=db,
                user_id=user_id,
                prompt=prompt,
                element_type="scene",
                element_id=scene.id,
                world_id=scene.act.story.world_id if scene.act and scene.act.story else None
            )
            
            logger.info(f"  Queued image generation job: {job_id}")
            stats["queued"] += 1
            
            # Small delay
            await asyncio.sleep(1)
            
        except Exception as e:
            logger.error(f"  Error processing scene {scene.id}: {e}")
            stats["skipped"] += 1
    
    return stats


async def main(args):
    """Main function"""
    async with async_session_local() as db:
        try:
            logger.info("=== AUTOMATIC IMAGE GENERATION ===")
            logger.info(f"Active image provider: {settings.ACTIVE_IMAGE_PROVIDER}")
            logger.info(f"Default image size: {settings.DEFAULT_IMAGE_SIZE}")
            
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
            
            # Track overall stats
            total_stats = {"stories": {}, "acts": {}, "scenes": {}}
            
            # Process stories
            if not args.skip_stories:
                logger.info("\n=== PROCESSING STORIES ===")
                stories = await get_stories_without_images(db, world_id, story_id, args.limit)
                total_stats["stories"] = await generate_story_images(db, stories, user_id, args.dry_run)
            
            # Process acts
            if not args.skip_acts:
                logger.info("\n=== PROCESSING ACTS ===")
                acts = await get_acts_without_images(db, world_id, story_id, args.limit)
                total_stats["acts"] = await generate_act_images(db, acts, user_id, args.dry_run)
            
            # Process scenes
            if not args.skip_scenes:
                logger.info("\n=== PROCESSING SCENES ===")
                scenes = await get_scenes_without_images(db, world_id, story_id, args.limit)
                total_stats["scenes"] = await generate_scene_images(db, scenes, user_id, args.dry_run)
            
            # Final summary
            logger.info("\n=== GENERATION SUMMARY ===")
            for element_type, stats in total_stats.items():
                if stats:
                    if args.dry_run:
                        logger.info(f"{element_type.title()}: {stats.get('processed', 0)} would be processed")
                    else:
                        logger.info(f"{element_type.title()}: {stats.get('queued', 0)} jobs queued, {stats.get('skipped', 0)} skipped")
            
            if not args.dry_run:
                logger.info("\nImage generation jobs have been queued and will process in the background.")
                logger.info("Check the job_statuses table or application logs to monitor progress.")
            
        except Exception as e:
            logger.error(f"Error in image generation: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatically generate missing images with default style")
    parser.add_argument("--user-id", type=int, default=1, help="User ID for image generation")
    parser.add_argument("--world-id", type=int, help="Filter by world ID")
    parser.add_argument("--story-id", type=int, help="Filter by story ID")
    parser.add_argument("--limit", type=int, default=50, help="Maximum items to process per type")
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