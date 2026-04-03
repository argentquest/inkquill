#!/usr/bin/env python
"""
Simple script to refresh AI summaries with better error handling and connection diagnostics.
Usage: python scripts/refresh_summaries_simple.py [--test-only]
"""

import asyncio
import logging
import argparse
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import app modules after setting up logging
try:
    from app.core.config import settings
    from app.db.database import async_session_local
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select, text
    from app.models.user import User
    from app.models.act import Act
    from app.models.scene import Scene
    from app.services.summary_generation_service import (
        generate_ai_summary_for_act,
        generate_ai_summary_for_scene
    )
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    logger.error("Make sure you're running from the project root and the environment is activated")
    sys.exit(1)


async def test_database_connection():
    """Test if we can connect to the database"""
    try:
        logger.info("Testing database connection...")
        
        from app.core.config import SQLALCHEMY_DATABASE_URI
        
        # Parse the URL to hide password in logs
        database_url = SQLALCHEMY_DATABASE_URI
        if '@' in database_url:
            before_at, after_at = database_url.split('@', 1)
            if ':' in before_at:
                protocol_user, password = before_at.rsplit(':', 1)
                safe_url = f"{protocol_user}:[HIDDEN]@{after_at}"
            else:
                safe_url = database_url
        else:
            safe_url = database_url
        
        logger.info(f"Database URL configured: {safe_url}")
        
        # Try to create a session and run a simple query
        async with async_session_local() as db:
            result = await db.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            
            if test_value == 1:
                logger.info("✓ Database connection successful")
                return True
            else:
                logger.error("✗ Database query returned unexpected result")
                return False
                
    except Exception as e:
        logger.error(f"✗ Database connection failed: {e}")
        logger.error("Common causes:")
        logger.error("  1. PostgreSQL server is not running")
        logger.error("  2. Database credentials are incorrect")
        logger.error("  3. Database server is unreachable")
        logger.error("  4. Firewall blocking connection")
        logger.error("  5. Azure PostgreSQL firewall blocking your IP")
        return False


async def get_user_count():
    """Get the number of users in the database"""
    try:
        async with async_session_local() as db:
            result = await db.execute(select(User).limit(5))
            users = result.scalars().all()
            logger.info(f"Found {len(users)} users in database")
            for user in users:
                logger.info(f"  User {user.id}: {user.email}")
            return len(users) > 0
    except Exception as e:
        logger.error(f"Failed to query users: {e}")
        return False


async def get_content_stats():
    """Get statistics about acts and scenes"""
    try:
        async with async_session_local() as db:
            # Count acts
            result = await db.execute(select(Act))
            acts = result.scalars().all()
            acts_with_content = [a for a in acts if a.description and a.description.strip()]
            acts_with_summary = [a for a in acts if a.ai_summary and a.ai_summary.strip()]
            
            # Count scenes
            result = await db.execute(select(Scene))
            scenes = result.scalars().all()
            scenes_with_content = [s for s in scenes if s.content and s.content.strip()]
            scenes_with_summary = [s for s in scenes if s.ai_summary and s.ai_summary.strip()]
            
            logger.info("Content Statistics:")
            logger.info(f"  Acts: {len(acts)} total, {len(acts_with_content)} with content, {len(acts_with_summary)} with AI summary")
            logger.info(f"  Scenes: {len(scenes)} total, {len(scenes_with_content)} with content, {len(scenes_with_summary)} with AI summary")
            
            return {
                "acts_total": len(acts),
                "acts_with_content": len(acts_with_content),
                "acts_with_summary": len(acts_with_summary),
                "scenes_total": len(scenes),
                "scenes_with_content": len(scenes_with_content),
                "scenes_with_summary": len(scenes_with_summary)
            }
    except Exception as e:
        logger.error(f"Failed to get content stats: {e}")
        return None


async def test_summary_generation():
    """Test summary generation on a single act/scene"""
    try:
        logger.info("Testing AI summary generation...")
        
        async with async_session_local() as db:
            # Find an act with content but no summary
            result = await db.execute(
                select(Act)
                .where(Act.description.isnot(None))
                .where(Act.description != "")
                .limit(1)
            )
            test_act = result.scalar_one_or_none()
            
            if test_act:
                logger.info(f"Testing with Act {test_act.id}: '{test_act.title}'")
                logger.info(f"Content length: {len(test_act.description)} characters")
                
                # Test summary generation (using user ID 1)
                summary = await generate_ai_summary_for_act(db, test_act, 1)
                
                if summary:
                    logger.info(f"✓ Summary generated successfully: {summary[:100]}...")
                    return True
                else:
                    logger.error("✗ Summary generation returned None")
                    return False
            else:
                logger.warning("No acts with content found for testing")
                return False
                
    except Exception as e:
        logger.error(f"✗ Summary generation test failed: {e}")
        return False


async def refresh_missing_summaries(user_id: int = 1, limit: int = 5):
    """Refresh summaries for a limited number of items missing summaries"""
    try:
        logger.info(f"Refreshing missing summaries (limit: {limit})...")
        
        async with async_session_local() as db:
            # Get acts without summaries
            result = await db.execute(
                select(Act)
                .where(Act.description.isnot(None))
                .where(Act.description != "")
                .where((Act.ai_summary.is_(None)) | (Act.ai_summary == ""))
                .order_by(Act.story_id, Act.act_number)
                .limit(limit)
            )
            acts_to_process = result.scalars().all()
            
            logger.info(f"Found {len(acts_to_process)} acts needing summaries")
            
            for i, act in enumerate(acts_to_process, 1):
                try:
                    logger.info(f"[{i}/{len(acts_to_process)}] Processing act {act.id}: '{act.title}'")
                    summary = await generate_ai_summary_for_act(db, act, user_id)
                    
                    if summary:
                        logger.info(f"✓ Generated summary: {summary[:50]}...")
                        await db.commit()
                    else:
                        logger.warning(f"✗ Failed to generate summary")
                        
                except Exception as e:
                    logger.error(f"Error processing act {act.id}: {e}")
                    await db.rollback()
            
            # Get scenes without summaries
            result = await db.execute(
                select(Scene)
                .where(Scene.content.isnot(None))
                .where(Scene.content != "")
                .where((Scene.ai_summary.is_(None)) | (Scene.ai_summary == ""))
                .order_by(Scene.act_id, Scene.scene_number)
                .limit(limit)
            )
            scenes_to_process = result.scalars().all()
            
            logger.info(f"Found {len(scenes_to_process)} scenes needing summaries")
            
            for i, scene in enumerate(scenes_to_process, 1):
                try:
                    logger.info(f"[{i}/{len(scenes_to_process)}] Processing scene {scene.id}: '{scene.title}'")
                    summary = await generate_ai_summary_for_scene(db, scene, user_id)
                    
                    if summary:
                        logger.info(f"✓ Generated summary: {summary[:50]}...")
                        await db.commit()
                    else:
                        logger.warning(f"✗ Failed to generate summary")
                        
                except Exception as e:
                    logger.error(f"Error processing scene {scene.id}: {e}")
                    await db.rollback()
            
            logger.info("Summary refresh completed")
            
    except Exception as e:
        logger.error(f"Failed to refresh summaries: {e}")


async def main(test_only: bool = False):
    """Main function with comprehensive diagnostics"""
    logger.info("=== AI Summary Refresh Tool ===")
    
    # Step 1: Test database connection
    if not await test_database_connection():
        logger.error("Cannot proceed without database connection")
        return
    
    # Step 2: Test user access
    if not await get_user_count():
        logger.error("No users found in database")
        return
    
    # Step 3: Get content statistics
    stats = await get_content_stats()
    if not stats:
        logger.error("Failed to get content statistics")
        return
    
    # Step 4: Test AI summary generation
    if not await test_summary_generation():
        logger.error("AI summary generation test failed")
        if test_only:
            return
        else:
            logger.warning("Continuing despite test failure...")
    
    # Step 5: If not test-only, do actual work
    if not test_only:
        await refresh_missing_summaries(user_id=1, limit=5)
    
    logger.info("=== Diagnostics Complete ===")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh AI summaries with diagnostics")
    parser.add_argument("--test-only", action="store_true", help="Run diagnostics only, don't process summaries")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args.test_only))
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)