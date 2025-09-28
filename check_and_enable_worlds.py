#!/usr/bin/env python3
"""
Quick script to check and enable worlds for free chat
"""
import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

# Add the project root to the path
sys.path.append('.')

from app.db.database import get_async_session
from app.models.world import World


async def check_and_enable_worlds():
    """Check existing worlds and enable some for free chat"""
    
    async for db in get_async_session():
        try:
            # Check current worlds
            result = await db.execute(select(World))
            all_worlds = result.scalars().all()
            
            print(f"Found {len(all_worlds)} total worlds:")
            for world in all_worlds:
                print(f"  - {world.name} (ID: {world.id}) - Free chat enabled: {world.is_free_chat_enabled}")
            
            # Check how many are enabled for free chat
            enabled_result = await db.execute(
                select(World).where(World.is_free_chat_enabled == True)
            )
            enabled_worlds = enabled_result.scalars().all()
            print(f"\n{len(enabled_worlds)} worlds enabled for free chat")
            
            # If no worlds are enabled, enable some good ones for testing
            if len(enabled_worlds) == 0 and len(all_worlds) > 0:
                print("\nNo worlds enabled for free chat. Enabling some good worlds for testing...")
                
                # Enable some specific interesting worlds for free chat
                good_world_ids = [28, 55, 78, 81]  # Little Prince, Star Wars, Bikini Bottom, Peanuts
                worlds_to_enable = [w for w in all_worlds if w.id in good_world_ids]
                
                for world in worlds_to_enable:
                    world.is_free_chat_enabled = True
                    print(f"  - Enabled: {world.name}")
                
                await db.commit()
                print(f"\nEnabled {len(worlds_to_enable)} worlds for free chat testing")
            
            elif len(enabled_worlds) > 0:
                print("\nWorlds available for free chat:")
                for world in enabled_worlds:
                    print(f"  - {world.name} (ID: {world.id})")
            
            break
            
        except Exception as e:
            print(f"Error: {e}")
            await db.rollback()
            break


if __name__ == "__main__":
    asyncio.run(check_and_enable_worlds())