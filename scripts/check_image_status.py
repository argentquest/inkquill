#!/usr/bin/env python
"""
Script to check image generation status for stories, acts, and scenes.
Usage: python scripts/check_image_status.py [options]
"""

import asyncio
import logging
import argparse
import sys
from pathlib import Path
from typing import Optional, Dict, List

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
    from sqlalchemy import select, and_, or_, func
    from sqlalchemy.orm import selectinload
    from app.db.database import async_session_local
    from app.models.story import Story
    from app.models.act import Act
    from app.models.scene import Scene
    from app.models.world import World
    from app.models.generated_image import GeneratedImage
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)


async def get_story_image_status(
    db: AsyncSession,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None
) -> List[Dict]:
    """Get image status for all stories"""
    
    query = select(Story).options(
        selectinload(Story.current_image),
        selectinload(Story.images),
        selectinload(Story.world)
    )
    
    if story_id:
        query = query.where(Story.id == story_id)
    elif world_id:
        query = query.where(Story.world_id == world_id)
    
    query = query.order_by(Story.world_id, Story.title)
    
    result = await db.execute(query)
    stories = result.scalars().all()
    
    story_status = []
    for story in stories:
        status = {
            'id': story.id,
            'title': story.title,
            'world_name': story.world.name if story.world else 'Unknown',
            'world_id': story.world_id,
            'has_current_image': story.current_image_id is not None,
            'current_image_id': story.current_image_id,
            'total_images': len(story.images) if story.images else 0,
            'image_prompt_defined': bool(story.image_prompt_definition and story.image_prompt_definition.strip()),
            'image_blob_path': story.image_blob_path
        }
        story_status.append(status)
    
    return story_status


async def get_act_image_status(
    db: AsyncSession,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None
) -> List[Dict]:
    """Get image status for all acts"""
    
    # Note: Acts don't have direct image relationships in the current model
    # But we can check if there are any generated images with element_type='act'
    
    query = select(Act).options(
        selectinload(Act.story).selectinload(Story.world)
    )
    
    if story_id:
        query = query.where(Act.story_id == story_id)
    elif world_id:
        query = query.join(Story).where(Story.world_id == world_id)
    
    query = query.order_by(Act.story_id, Act.act_number)
    
    result = await db.execute(query)
    acts = result.scalars().all()
    
    # Get all act images
    act_images_query = select(GeneratedImage).where(GeneratedImage.element_type == 'act')
    act_images_result = await db.execute(act_images_query)
    act_images = act_images_result.scalars().all()
    
    # Create a mapping of act_id -> images
    act_images_map = {}
    for img in act_images:
        act_id = img.associated_element_id
        if act_id not in act_images_map:
            act_images_map[act_id] = []
        act_images_map[act_id].append(img)
    
    act_status = []
    for act in acts:
        images = act_images_map.get(act.id, [])
        current_image = images[0] if images else None  # Most recent
        
        status = {
            'id': act.id,
            'title': act.title,
            'act_number': act.act_number,
            'story_title': act.story.title if act.story else 'Unknown',
            'story_id': act.story_id,
            'world_name': act.story.world.name if act.story and act.story.world else 'Unknown',
            'world_id': act.story.world_id if act.story else None,
            'has_current_image': current_image is not None,
            'current_image_id': current_image.id if current_image else None,
            'total_images': len(images),
            'has_content': bool(act.description and act.description.strip())
        }
        act_status.append(status)
    
    return act_status


async def get_scene_image_status(
    db: AsyncSession,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None
) -> List[Dict]:
    """Get image status for all scenes"""
    
    query = select(Scene).options(
        selectinload(Scene.current_image),
        selectinload(Scene.images),
        selectinload(Scene.act).selectinload(Act.story).selectinload(Story.world)
    )
    
    if story_id:
        query = query.join(Act).where(Act.story_id == story_id)
    elif world_id:
        query = query.join(Act).join(Story).where(Story.world_id == world_id)
    
    query = query.order_by(Scene.act_id, Scene.scene_number)
    
    result = await db.execute(query)
    scenes = result.scalars().all()
    
    scene_status = []
    for scene in scenes:
        status = {
            'id': scene.id,
            'title': scene.title or f"Scene {scene.scene_number}",
            'scene_number': scene.scene_number,
            'act_title': scene.act.title if scene.act else 'Unknown',
            'act_id': scene.act_id,
            'story_title': scene.act.story.title if scene.act and scene.act.story else 'Unknown',
            'story_id': scene.act.story_id if scene.act else None,
            'world_name': scene.act.story.world.name if scene.act and scene.act.story and scene.act.story.world else 'Unknown',
            'world_id': scene.act.story.world_id if scene.act and scene.act.story else None,
            'has_current_image': scene.current_image_id is not None,
            'current_image_id': scene.current_image_id,
            'total_images': len(scene.images) if scene.images else 0,
            'has_content': bool(scene.content and scene.content.strip())
        }
        scene_status.append(status)
    
    return scene_status


async def get_summary_stats(
    stories: List[Dict],
    acts: List[Dict],
    scenes: List[Dict]
) -> Dict:
    """Calculate summary statistics"""
    
    stats = {
        'stories': {
            'total': len(stories),
            'with_images': len([s for s in stories if s['has_current_image']]),
            'with_prompts': len([s for s in stories if s['image_prompt_defined']]),
            'without_images': len([s for s in stories if not s['has_current_image']])
        },
        'acts': {
            'total': len(acts),
            'with_images': len([a for a in acts if a['has_current_image']]),
            'with_content': len([a for a in acts if a['has_content']]),
            'without_images': len([a for a in acts if not a['has_current_image'] and a['has_content']])
        },
        'scenes': {
            'total': len(scenes),
            'with_images': len([s for s in scenes if s['has_current_image']]),
            'with_content': len([s for s in scenes if s['has_content']]),
            'without_images': len([s for s in scenes if not s['has_current_image'] and s['has_content']])
        }
    }
    
    return stats


async def display_detailed_report(
    stories: List[Dict],
    acts: List[Dict],
    scenes: List[Dict],
    show_details: bool = False
):
    """Display detailed report"""
    
    logger.info("=== IMAGE GENERATION STATUS REPORT ===")
    
    # Summary statistics
    stats = await get_summary_stats(stories, acts, scenes)
    
    logger.info("\n=== SUMMARY STATISTICS ===")
    logger.info(f"Stories: {stats['stories']['total']} total, {stats['stories']['with_images']} with images, {stats['stories']['without_images']} missing images")
    logger.info(f"Acts: {stats['acts']['total']} total, {stats['acts']['with_images']} with images, {stats['acts']['without_images']} missing images (with content)")
    logger.info(f"Scenes: {stats['scenes']['total']} total, {stats['scenes']['with_images']} with images, {stats['scenes']['without_images']} missing images (with content)")
    
    if show_details:
        # Stories without images
        stories_without_images = [s for s in stories if not s['has_current_image']]
        if stories_without_images:
            logger.info("\n=== STORIES WITHOUT IMAGES ===")
            for story in stories_without_images:
                prompt_status = "✓ Prompt defined" if story['image_prompt_defined'] else "✗ No prompt"
                logger.info(f"Story {story['id']}: '{story['title']}' (World: {story['world_name']}) - {prompt_status}")
        
        # Acts without images (with content)
        acts_without_images = [a for a in acts if not a['has_current_image'] and a['has_content']]
        if acts_without_images:
            logger.info("\n=== ACTS WITHOUT IMAGES (WITH CONTENT) ===")
            for act in acts_without_images:
                logger.info(f"Act {act['id']}: '{act['title']}' (Story: {act['story_title']}, World: {act['world_name']})")
        
        # Scenes without images (with content)
        scenes_without_images = [s for s in scenes if not s['has_current_image'] and s['has_content']]
        if scenes_without_images:
            logger.info("\n=== SCENES WITHOUT IMAGES (WITH CONTENT) ===")
            for scene in scenes_without_images[:20]:  # Limit to first 20
                logger.info(f"Scene {scene['id']}: '{scene['title']}' (Act: {scene['act_title']}, Story: {scene['story_title']})")
            
            if len(scenes_without_images) > 20:
                logger.info(f"... and {len(scenes_without_images) - 20} more scenes")


async def export_missing_images_report(
    stories: List[Dict],
    acts: List[Dict],
    scenes: List[Dict],
    output_file: str = "missing_images_report.txt"
):
    """Export detailed report of missing images to a file"""
    
    with open(output_file, 'w') as f:
        f.write("IMAGE GENERATION STATUS REPORT\n")
        f.write("=" * 50 + "\n\n")
        
        # Summary
        stats = await get_summary_stats(stories, acts, scenes)
        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 20 + "\n")
        f.write(f"Stories: {stats['stories']['total']} total, {stats['stories']['with_images']} with images, {stats['stories']['without_images']} missing\n")
        f.write(f"Acts: {stats['acts']['total']} total, {stats['acts']['with_images']} with images, {stats['acts']['without_images']} missing\n")
        f.write(f"Scenes: {stats['scenes']['total']} total, {stats['scenes']['with_images']} with images, {stats['scenes']['without_images']} missing\n\n")
        
        # Stories without images
        stories_without_images = [s for s in stories if not s['has_current_image']]
        if stories_without_images:
            f.write("STORIES WITHOUT IMAGES\n")
            f.write("-" * 25 + "\n")
            for story in stories_without_images:
                prompt_status = "Has prompt" if story['image_prompt_defined'] else "No prompt"
                f.write(f"ID: {story['id']}, Title: '{story['title']}', World: {story['world_name']}, Status: {prompt_status}\n")
            f.write("\n")
        
        # Acts without images
        acts_without_images = [a for a in acts if not a['has_current_image'] and a['has_content']]
        if acts_without_images:
            f.write("ACTS WITHOUT IMAGES (WITH CONTENT)\n")
            f.write("-" * 35 + "\n")
            for act in acts_without_images:
                f.write(f"ID: {act['id']}, Title: '{act['title']}', Story: {act['story_title']}, World: {act['world_name']}\n")
            f.write("\n")
        
        # Scenes without images
        scenes_without_images = [s for s in scenes if not s['has_current_image'] and s['has_content']]
        if scenes_without_images:
            f.write("SCENES WITHOUT IMAGES (WITH CONTENT)\n")
            f.write("-" * 37 + "\n")
            for scene in scenes_without_images:
                f.write(f"ID: {scene['id']}, Title: '{scene['title']}', Act: {scene['act_title']}, Story: {scene['story_title']}, World: {scene['world_name']}\n")
    
    logger.info(f"Detailed report exported to: {output_file}")


async def main(args):
    """Main function"""
    async with async_session_local() as db:
        try:
            logger.info("Checking image generation status...")
            
            # Apply filters
            world_id = args.world_id
            story_id = args.story_id
            
            if world_id:
                # Verify world exists
                result = await db.execute(select(World).where(World.id == world_id))
                world = result.scalar_one_or_none()
                if not world:
                    logger.error(f"World with ID {world_id} not found")
                    return
                logger.info(f"Filtering by world: {world.name}")
            
            if story_id:
                # Verify story exists
                result = await db.execute(select(Story).where(Story.id == story_id))
                story = result.scalar_one_or_none()
                if not story:
                    logger.error(f"Story with ID {story_id} not found")
                    return
                logger.info(f"Filtering by story: {story.title}")
            
            # Get image status for all types
            logger.info("Gathering story image status...")
            stories = await get_story_image_status(db, world_id, story_id)
            
            logger.info("Gathering act image status...")
            acts = await get_act_image_status(db, world_id, story_id)
            
            logger.info("Gathering scene image status...")
            scenes = await get_scene_image_status(db, world_id, story_id)
            
            # Display report
            await display_detailed_report(stories, acts, scenes, args.show_details)
            
            # Export report if requested
            if args.export:
                await export_missing_images_report(stories, acts, scenes, args.export)
            
        except Exception as e:
            logger.error(f"Error checking image status: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check image generation status for stories, acts, and scenes")
    parser.add_argument("--world-id", type=int, help="Filter by world ID")
    parser.add_argument("--story-id", type=int, help="Filter by story ID")
    parser.add_argument("--show-details", action="store_true", help="Show detailed list of items without images")
    parser.add_argument("--export", type=str, help="Export detailed report to file")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)