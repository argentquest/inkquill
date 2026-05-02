#!/usr/bin/env python3
"""
Update World Descriptions for Document Imports

This script finds worlds with generic descriptions like "World generated from document: filename.txt"
and generates proper AI-generated descriptions for them.

Usage:
    python update_world_descriptions.py [--dry-run] [--world-id WORLD_ID]

Options:
    --dry-run: Show what would be updated without making changes
    --world-id: Only process a specific world ID
"""

import asyncio
import logging
import argparse
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Add the app directory to the path so we can import modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import async_session_local
from app.models.world import World
from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.services.ai_model_cache import model_cache
from app.processing.importer_jobs import _call_ai_for_world_extraction

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def find_worlds_needing_descriptions(db: AsyncSession, world_id: Optional[int] = None) -> List[World]:
    """Find worlds that have generic descriptions and need AI-generated ones."""
    
    if world_id:
        # Get specific world
        world = await db.get(World, world_id)
        return [world] if world else []
    else:
        # Find worlds with generic descriptions
        result = await db.execute(
            select(World).where(
                World.description.like("World generated from document:%")
            )
        )
        return result.scalars().all()

async def generate_world_description_for_world(world: World, db: AsyncSession, dry_run: bool = False) -> Optional[str]:
    """Generate a proper description for a world based on its elements."""
    
    logger.info(f"Processing World ID {world.id}: '{world.name}'")
    
    # Get world elements
    characters_result = await db.execute(select(Character).where(Character.world_id == world.id))
    locations_result = await db.execute(select(Location).where(Location.world_id == world.id))
    lore_items_result = await db.execute(select(LoreItem).where(LoreItem.world_id == world.id))
    
    characters = characters_result.scalars().all()
    locations = locations_result.scalars().all()
    lore_items = lore_items_result.scalars().all()
    
    if not characters and not locations and not lore_items:
        logger.warning(f"  World {world.id} has no elements - skipping")
        return None
    
    logger.info(f"  Found {len(characters)} characters, {len(locations)} locations, {len(lore_items)} lore items")
    
    # Create a summary of the world elements for AI
    world_summary = f"World '{world.name}' containing:\n"
    world_summary += f"- {len(characters)} characters\n"
    world_summary += f"- {len(locations)} locations\n"
    world_summary += f"- {len(lore_items)} lore items\n\n"
    
    # Add character details
    if characters:
        world_summary += "Characters:\n"
        for char in characters[:10]:  # Limit to first 10
            world_summary += f"- {char.name}: {char.description[:100] if char.description else 'No description'}...\n"
        if len(characters) > 10:
            world_summary += f"... and {len(characters) - 10} more characters\n"
        world_summary += "\n"
    
    # Add location details
    if locations:
        world_summary += "Locations:\n"
        for loc in locations[:10]:  # Limit to first 10
            world_summary += f"- {loc.name}: {loc.description[:100] if loc.description else 'No description'}...\n"
        if len(locations) > 10:
            world_summary += f"... and {len(locations) - 10} more locations\n"
        world_summary += "\n"
    
    # Add lore details
    if lore_items:
        world_summary += "Lore Items:\n"
        for lore in lore_items[:10]:  # Limit to first 10
            world_summary += f"- {lore.title}: {lore.description[:100] if lore.description else 'No description'}...\n"
        if len(lore_items) > 10:
            world_summary += f"... and {len(lore_items) - 10} more lore items\n"
    
    logger.info(f"  Generated summary: {len(world_summary)} characters")
    
    if dry_run:
        logger.info(f"  [DRY RUN] Would generate description for: {world.name}")
        logger.info(f"  Current description: {world.description}")
        return world_summary[:500] + "..."
    
    # Generate world description using AI
    world_desc_prompt = """You are a world-building expert. Based on the provided world elements and character/location/lore information, create a compelling 2-3 paragraph description of this fictional world that captures its essence, tone, and key themes.

The description should:
- Capture the overall atmosphere and setting
- Mention key themes or concepts
- Be engaging and immersive
- Synthesize the elements into a cohesive world vision
- Avoid listing individual characters or locations (focus on the world as a whole)

Respond with ONLY the world description text, no JSON or formatting."""

    try:
        # Use the default generation model for this task
        model_config = model_cache.default_generation_model
        if not model_config:
            logger.error("No default generation model available")
            return None
        
        logger.info(f"  Using model: {model_config.display_name}")
        
        description, _, _ = await _call_ai_for_world_extraction(
            model_config, world_desc_prompt, world_summary, f"world_desc_{world.id}"
        )
        
        if description and description.strip():
            logger.info(f"  Generated description: {len(description)} characters")
            return description.strip()
        else:
            logger.warning(f"  Empty description generated for world {world.id}")
            return None
            
    except Exception as e:
        logger.error(f"  Failed to generate description for world {world.id}: {e}")
        return None

async def update_world_descriptions(dry_run: bool = False, world_id: Optional[int] = None):
    """Update world descriptions for worlds that need them."""
    
    async with async_session_local() as db:
        if world_id:
            logger.info(f"Processing specific world ID: {world_id}")
        else:
            logger.info("Finding worlds with generic descriptions...")
        
        worlds = await find_worlds_needing_descriptions(db, world_id)
        
        logger.info(f"Found {len(worlds)} worlds needing description updates")
        
        if not worlds:
            logger.info("No worlds need description updates!")
            return
        
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
        
        updated_count = 0
        
        for world in worlds:
            try:
                new_description = await generate_world_description_for_world(world, db, dry_run)
                
                if new_description and not dry_run:
                    world.description = new_description
                    db.add(world)
                    await db.commit()
                    updated_count += 1
                    logger.info(f"  ✅ Updated world '{world.name}' (ID: {world.id})")
                elif new_description and dry_run:
                    logger.info(f"  [DRY RUN] Would update world '{world.name}' (ID: {world.id})")
                    updated_count += 1
                else:
                    logger.warning(f"  ❌ Failed to generate description for world '{world.name}' (ID: {world.id})")
                    
            except Exception as e:
                logger.error(f"  ❌ Error processing world '{world.name}' (ID: {world.id}): {e}")
                await db.rollback()
                continue
        
        if dry_run:
            logger.info(f"DRY RUN COMPLETE: Would update {updated_count} world descriptions")
        else:
            logger.info(f"✅ Successfully updated {updated_count} world descriptions")

async def main():
    parser = argparse.ArgumentParser(description="Update world descriptions for document imports")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making changes")
    parser.add_argument("--world-id", type=int, help="Only process a specific world ID")
    
    args = parser.parse_args()
    
    try:
        await update_world_descriptions(dry_run=args.dry_run, world_id=args.world_id)
    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())