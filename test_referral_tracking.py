#!/usr/bin/env python3
"""
Test script to validate referral tracking system.
This script tests the anonymous user referral tracking flow.
"""

import asyncio
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_referral_tracking():
    """Test the referral tracking system."""
    try:
        # Import after setting up logging
        from app.db.database import async_session_local
        from app.services.referral_service import referral_service
        from app.models.referral import Referral, ReferralReward
        from app.models.user import User
        
        logger.info("=== Starting Referral Tracking Test ===")
        
        async with async_session_local() as db:
            # Test 1: Check if we can create a referral record
            logger.info("Test 1: Creating anonymous referral record...")
            
            # First, let's check if we have any users to test with
            result = await db.execute(select(User).limit(1))
            test_user = result.scalar_one_or_none()
            
            if not test_user:
                logger.error("No users found in database. Cannot test referral system.")
                return False
                
            logger.info(f"Using test user: {test_user.username} (ID: {test_user.id})")
            
            # Test anonymous referral creation
            referral = await referral_service.track_referral_visit(
                db=db,
                referrer_user_id=test_user.id,
                referred_user_id=None,  # Anonymous
                anonymous_session_id="test_session_123",
                source_platform="test",
                source_content_type="direct_link",
                ip_address="127.0.0.1",
                user_agent="Test Agent",
                referral_url="http://localhost:8000/?ref=" + str(test_user.id)
            )
            
            if referral:
                logger.info(f"✅ Successfully created referral record with ID: {referral.id}")
                
                # Test 2: Check if referral reward was created
                logger.info("Test 2: Checking if visit reward was created...")
                
                reward_result = await db.execute(
                    select(ReferralReward).where(
                        ReferralReward.referral_id == referral.id,
                        ReferralReward.reward_type == "visit"
                    )
                )
                reward = reward_result.scalar_one_or_none()
                
                if reward:
                    logger.info(f"✅ Visit reward created: {reward.coin_amount} coins")
                else:
                    logger.warning("⚠️ No visit reward found")
                
                # Test 3: Check database record directly
                logger.info("Test 3: Verifying database record...")
                
                db_referral = await db.execute(
                    select(Referral).where(Referral.id == referral.id)
                )
                db_ref = db_referral.scalar_one_or_none()
                
                if db_ref:
                    logger.info(f"✅ Database record found:")
                    logger.info(f"   - Referrer: {db_ref.referrer_user_id}")
                    logger.info(f"   - Anonymous session: {db_ref.anonymous_session_id}")
                    logger.info(f"   - Is converted: {db_ref.is_converted}")
                    logger.info(f"   - Created: {db_ref.created_at}")
                else:
                    logger.error("❌ Database record not found")
                    
                return True
                
            else:
                logger.error("❌ Failed to create referral record")
                return False
                
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}", exc_info=True)
        return False

async def main():
    """Main test function."""
    success = await test_referral_tracking()
    if success:
        logger.info("=== Referral tracking test PASSED ===")
    else:
        logger.error("=== Referral tracking test FAILED ===")

if __name__ == "__main__":
    asyncio.run(main())