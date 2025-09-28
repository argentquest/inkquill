#!/usr/bin/env python3
"""
Generate Missing AI Image Prompts for World Elements

This script finds all world elements (characters, locations, lore items) that have
empty or null image_prompt_definition fields and generates AI image prompts for them
using the existing element data.

Usage:
    python generate_missing_image_prompts.py [--dry-run] [--world-id WORLD_ID]

Options:
    --dry-run: Show what would be updated without making changes
    --world-id: Only process elements from a specific world ID
"""

import asyncio
import logging
from typing import List, Optional
import argparse
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

# Add the app directory to the path so we can import modules
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import async_session_local
from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.services.sk_kernel_instance import kernel
from app.services.ai_model_cache import model_cache
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai import AzureChatPromptExecutionSettings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def clean_prompt_text(prompt: str) -> str:
    """Clean and validate prompt text for image generation."""
    if not prompt:
        return ""
    
    # Remove newlines and excessive whitespace
    cleaned = re.sub(r'\s+', ' ', prompt.strip())
    
    # Remove incomplete fragments and fix common issues
    cleaned = re.sub(r'\s+\w{1,3}$', '', cleaned)  # Remove 1-3 char fragments at end
    cleaned = re.sub(r',\s*\)$', ')', cleaned)     # Fix ", )" at end
    cleaned = re.sub(r'\(\s*[^)]{1,15}\s*\)$', '', cleaned)  # Remove short incomplete parentheses
    cleaned = re.sub(r',\s*$', '', cleaned)        # Remove trailing comma
    cleaned = re.sub(r'\s*\($', '', cleaned)       # Remove trailing open parenthesis
    
    # Limit length (conservative for DALL-E)
    if len(cleaned) > 800:
        sentences = cleaned[:800].split('.')
        if len(sentences) > 1:
            cleaned = '. '.join(sentences[:-1]) + '.'
        else:
            cleaned = cleaned[:800].rstrip() + '...'
    
    return cleaned.strip()


async def generate_image_prompt_for_character(character: Character) -> str:
    """Generate an AI image prompt for a character based on their existing data."""
    prompt_parts = []
    
    # Start with character name
    base = f"Portrait of {character.name}"
    
    if character.description:
        # Extract key visual details from description (first sentence or 150 chars)
        desc = character.description.strip()
        if '.' in desc:
            first_sentence = desc.split('.')[0] + '.'
            if len(first_sentence) < 200:
                prompt_parts.append(first_sentence)
            else:
                prompt_parts.append(desc[:150] + "...")
        else:
            prompt_parts.append(desc[:150] + "..." if len(desc) > 150 else desc)
    
    if character.personality_traits:
        # Add 2-3 key personality traits for expression
        traits = [t.strip() for t in character.personality_traits.split(',')][:3]
        if traits:
            trait_desc = ', '.join(traits)
            prompt_parts.append(f"with {trait_desc} expression")
    
    # Combine parts cleanly
    if prompt_parts:
        image_prompt = f"{base}, {', '.join(prompt_parts)}"
    else:
        image_prompt = base
    
    # Clean and validate
    image_prompt = clean_prompt_text(image_prompt)
    return image_prompt


async def generate_image_prompt_for_location(location: Location) -> str:
    """Generate an AI image prompt for a location based on their existing data."""
    prompt_parts = []
    
    # Start with location name and type
    base = f"Scenic view of {location.name}"
    
    if location.description:
        # Extract key visual details from description
        desc = location.description.strip()
        if '.' in desc:
            first_sentence = desc.split('.')[0] + '.'
            if len(first_sentence) < 200:
                prompt_parts.append(first_sentence)
            else:
                prompt_parts.append(desc[:150] + "...")
        else:
            prompt_parts.append(desc[:150] + "..." if len(desc) > 150 else desc)
    
    if location.atmosphere:
        atmosphere = location.atmosphere.strip()
        if atmosphere:
            prompt_parts.append(f"{atmosphere} atmosphere")
    
    if location.geography and len(location.geography.strip()) > 5:
        geo = location.geography.strip()[:100]
        prompt_parts.append(f"featuring {geo}")
    
    # Combine parts cleanly
    if prompt_parts:
        image_prompt = f"{base}, {', '.join(prompt_parts)}"
    else:
        image_prompt = base
    
    # Clean and validate
    image_prompt = clean_prompt_text(image_prompt)
    return image_prompt


async def generate_image_prompt_for_lore_item(lore_item: LoreItem) -> str:
    """Generate an AI image prompt for a lore item based on their existing data."""
    prompt_parts = []
    
    # Start with item name and basic descriptor
    if lore_item.category and lore_item.category.value == 'ARTIFACT':
        base = f"Detailed view of {lore_item.title}"
    elif lore_item.category and lore_item.category.value == 'CREATURE':
        base = f"Artistic depiction of {lore_item.title}"
    else:
        base = f"Concept art of {lore_item.title}"
    
    if lore_item.description:
        # Extract key visual details from description
        desc = lore_item.description.strip()
        if '.' in desc:
            first_sentence = desc.split('.')[0] + '.'
            if len(first_sentence) < 200:
                prompt_parts.append(first_sentence)
            else:
                prompt_parts.append(desc[:150] + "...")
        else:
            prompt_parts.append(desc[:150] + "..." if len(desc) > 150 else desc)
    
    if lore_item.category:
        category = lore_item.category.value.replace('_', ' ').lower()
        if category not in ['other lore', 'culture']:  # Skip generic categories
            prompt_parts.append(f"({category} style)")
    
    # Combine parts cleanly
    if prompt_parts:
        image_prompt = f"{base}, {', '.join(prompt_parts)}"
    else:
        image_prompt = base
    
    # Clean and validate
    image_prompt = clean_prompt_text(image_prompt)
    return image_prompt


async def find_elements_without_image_prompts(db: AsyncSession, world_id: Optional[int] = None, force_regenerate: bool = False):
    """Find all elements that need image prompts generated."""
    
    # Build base filters
    if force_regenerate:
        # Get ALL elements regardless of whether they have image prompts
        char_filter = Character.id.isnot(None)  # Get all characters
        loc_filter = Location.id.isnot(None)    # Get all locations
        lore_filter = LoreItem.id.isnot(None)   # Get all lore items
    else:
        # Build base filters for missing prompts only
        char_filter = Character.image_prompt_definition.is_(None) | (Character.image_prompt_definition == '')
        loc_filter = Location.image_prompt_definition.is_(None) | (Location.image_prompt_definition == '')
        lore_filter = LoreItem.image_prompt_definition.is_(None) | (LoreItem.image_prompt_definition == '')
    
    if world_id:
        char_filter = and_(char_filter, Character.world_id == world_id)
        loc_filter = and_(loc_filter, Location.world_id == world_id)
        lore_filter = and_(lore_filter, LoreItem.world_id == world_id)
    
    # Query for elements missing image prompts
    characters_result = await db.execute(select(Character).filter(char_filter))
    locations_result = await db.execute(select(Location).filter(loc_filter))
    lore_items_result = await db.execute(select(LoreItem).filter(lore_filter))
    
    characters = characters_result.scalars().all()
    locations = locations_result.scalars().all()
    lore_items = lore_items_result.scalars().all()
    
    return characters, locations, lore_items


async def update_image_prompts(dry_run: bool = False, world_id: Optional[int] = None, force_regenerate: bool = False):
    """Update image prompts for all elements that need them."""
    
    async with async_session_local() as db:
        if force_regenerate:
            logger.info(f"Finding ALL elements to regenerate image prompts{f' in world {world_id}' if world_id else ''}...")
        else:
            logger.info(f"Finding elements without image prompts{f' in world {world_id}' if world_id else ''}...")
        
        characters, locations, lore_items = await find_elements_without_image_prompts(db, world_id, force_regenerate)
        
        total_elements = len(characters) + len(locations) + len(lore_items)
        logger.info(f"Found {total_elements} elements needing image prompts:")
        logger.info(f"  - {len(characters)} characters")
        logger.info(f"  - {len(locations)} locations") 
        logger.info(f"  - {len(lore_items)} lore items")
        
        if total_elements == 0:
            logger.info("No elements need image prompt generation!")
            return
        
        if force_regenerate:
            logger.info("FORCE REGENERATE MODE - All existing prompts will be replaced!")
        
        if dry_run:
            logger.info("DRY RUN MODE - No changes will be made")
            
            # Show examples
            if characters:
                sample_char = characters[0]
                sample_prompt = await generate_image_prompt_for_character(sample_char)
                logger.info(f"Example character prompt for '{sample_char.name}': {sample_prompt}")
            
            if locations:
                sample_loc = locations[0]
                sample_prompt = await generate_image_prompt_for_location(sample_loc)
                logger.info(f"Example location prompt for '{sample_loc.name}': {sample_prompt}")
                
            if lore_items:
                sample_lore = lore_items[0]
                sample_prompt = await generate_image_prompt_for_lore_item(sample_lore)
                logger.info(f"Example lore item prompt for '{sample_lore.title}': {sample_prompt}")
            
            return
        
        # Process characters
        logger.info("Processing characters...")
        for i, character in enumerate(characters, 1):
            try:
                image_prompt = await generate_image_prompt_for_character(character)
                character.image_prompt_definition = image_prompt
                logger.info(f"  {i}/{len(characters)}: Updated '{character.name}' -> '{image_prompt[:100]}...'")
            except Exception as e:
                logger.error(f"  {i}/{len(characters)}: Failed to update '{character.name}': {e}")
        
        # Process locations
        logger.info("Processing locations...")
        for i, location in enumerate(locations, 1):
            try:
                image_prompt = await generate_image_prompt_for_location(location)
                location.image_prompt_definition = image_prompt
                logger.info(f"  {i}/{len(locations)}: Updated '{location.name}' -> '{image_prompt[:100]}...'")
            except Exception as e:
                logger.error(f"  {i}/{len(locations)}: Failed to update '{location.name}': {e}")
        
        # Process lore items
        logger.info("Processing lore items...")
        for i, lore_item in enumerate(lore_items, 1):
            try:
                image_prompt = await generate_image_prompt_for_lore_item(lore_item)
                lore_item.image_prompt_definition = image_prompt
                logger.info(f"  {i}/{len(lore_items)}: Updated '{lore_item.title}' -> '{image_prompt[:100]}...'")
            except Exception as e:
                logger.error(f"  {i}/{len(lore_items)}: Failed to update '{lore_item.title}': {e}")
        
        # Commit all changes
        try:
            await db.commit()
            logger.info(f"✅ Successfully updated {total_elements} elements with image prompts!")
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Failed to commit changes: {e}")
            raise


async def main():
    parser = argparse.ArgumentParser(description="Generate missing AI image prompts for world elements")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be updated without making changes")
    parser.add_argument("--world-id", type=int, help="Only process elements from a specific world ID")
    parser.add_argument("--force", action="store_true", help="Force regeneration of ALL image prompts, even existing ones")
    
    args = parser.parse_args()
    
    try:
        await update_image_prompts(dry_run=args.dry_run, world_id=args.world_id, force_regenerate=args.force)
    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())