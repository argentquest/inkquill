"""
Referral tracking and reward service.
"""
import logging
from datetime import UTC, date, datetime
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.exc import IntegrityError

from app.models.referral import Referral, ReferralReward, ReferralLimit
from app.models.user import User
from app.crud import billing as billing_crud
from app.services.billing_service import billing_service

logger = logging.getLogger(__name__)

# Referral reward configuration
REFERRAL_REWARDS = {
    'visit': 5,           # New visitor clicks link
    'registration': 50,   # Visitor registers
    'first_story': 25,    # Referral creates first story
    'first_publish': 50   # Referral publishes first story
}

# Daily limits configuration
DAILY_LIMITS = {
    'total_coins': 500,
    'visit_rewards': 10,
    'registration_rewards': 5,
    'story_rewards': 3,
    'publish_rewards': 3
}


class ReferralService:
    """Service for managing referrals and rewards."""

    @staticmethod
    def _naive_utc_now() -> datetime:
        """Return UTC as a naive datetime for legacy TIMESTAMP WITHOUT TIME ZONE columns."""
        return datetime.now(UTC).replace(tzinfo=None)
    
    async def track_referral_visit(
        self,
        db: AsyncSession,
        referrer_user_id: int,
        referred_user_id: Optional[int] = None,
        anonymous_session_id: Optional[str] = None,
        source_platform: Optional[str] = None,
        source_content_type: Optional[str] = None,
        source_content_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referral_url: Optional[str] = None
    ) -> Optional[Referral]:
        """Track a new referral visit."""
        try:
            logger.info(f"🔍 SERVICE DEBUG: Starting track_referral_visit with:")
            logger.info(f"🔍 SERVICE DEBUG: - referrer_user_id: {referrer_user_id}")
            logger.info(f"🔍 SERVICE DEBUG: - referred_user_id: {referred_user_id}")
            logger.info(f"🔍 SERVICE DEBUG: - anonymous_session_id: {anonymous_session_id}")
            logger.info(f"🔍 SERVICE DEBUG: - ip_address: {ip_address}")
            logger.info(f"🔍 SERVICE DEBUG: - referral_url: {referral_url}")
            # Check if this referral already exists
            existing_query = select(Referral).where(
                Referral.referrer_user_id == referrer_user_id
            )
            
            logger.info(f"🔍 SERVICE DEBUG: Building existing query for referrer {referrer_user_id}")
            
            if referred_user_id:
                existing_query = existing_query.where(Referral.referred_user_id == referred_user_id)
                logger.info(f"🔍 SERVICE DEBUG: Adding referred_user_id filter: {referred_user_id}")
            elif anonymous_session_id:
                existing_query = existing_query.where(Referral.anonymous_session_id == anonymous_session_id)
                logger.info(f"🔍 SERVICE DEBUG: Adding anonymous_session_id filter: {anonymous_session_id}")
            else:
                logger.warning("🔍 SERVICE DEBUG: No referred user ID or anonymous session ID provided, treating as anonymous visit")
                # For anonymous visits without session, use IP address as identifier
                anonymous_session_id = f"ip_{ip_address}_{referrer_user_id}" if ip_address else f"anon_{referrer_user_id}"
                existing_query = existing_query.where(Referral.anonymous_session_id == anonymous_session_id)
                logger.info(f"🔍 SERVICE DEBUG: Created fallback anonymous_session_id: {anonymous_session_id}")
            
            logger.info(f"🔍 SERVICE DEBUG: Executing existing referral query...")
            existing = await db.execute(existing_query)
            existing_referral = existing.scalar_one_or_none()
            
            if existing_referral:
                logger.info(f"🔍 SERVICE DEBUG: Found existing referral {existing_referral.id} for referrer {referrer_user_id}")
                return existing_referral
            
            logger.info(f"🔍 SERVICE DEBUG: No existing referral found, creating new one...")
            
            # Create new referral
            logger.info(f"🔍 SERVICE DEBUG: Creating new Referral object...")
            referral = Referral(
                referrer_user_id=referrer_user_id,
                referred_user_id=referred_user_id,
                anonymous_session_id=anonymous_session_id,
                referral_code=str(referrer_user_id),
                source_platform=source_platform,
                source_content_type=source_content_type,
                source_content_id=source_content_id,
                ip_address=ip_address,
                user_agent=user_agent,
                referral_url=referral_url
            )
            
            logger.info(f"🔍 SERVICE DEBUG: Adding referral to database session...")
            db.add(referral)
            logger.info(f"🔍 SERVICE DEBUG: Flushing database session...")
            await db.flush()
            logger.info(f"🔍 SERVICE DEBUG: Referral created with ID: {referral.id}")
            
            # Try to award visit reward
            logger.info(f"🔍 SERVICE DEBUG: Attempting to award visit reward...")
            reward_result = await self._try_award_reward(db, referral, 'visit')
            logger.info(f"🔍 SERVICE DEBUG: Reward result: {reward_result}")
            
            logger.info(f"🔍 SERVICE DEBUG: Committing transaction...")
            await db.commit()
            logger.info(f"🔍 SERVICE DEBUG: Transaction committed successfully")
            logger.info(f"🔍 SERVICE DEBUG: Created new referral {referral.id} from user {referrer_user_id}")
            return referral
            
        except Exception as e:
            logger.error(f"Error tracking referral visit: {e}")
            await db.rollback()
            return None
    
    async def convert_anonymous_referral(
        self,
        db: AsyncSession,
        anonymous_session_id: str,
        registered_user_id: int
    ) -> bool:
        """Convert an anonymous referral to a registered user referral."""
        try:
            # Find the anonymous referral
            result = await db.execute(
                select(Referral).where(
                    Referral.anonymous_session_id == anonymous_session_id,
                    Referral.referred_user_id.is_(None)
                )
            )
            referral = result.scalar_one_or_none()
            
            if not referral:
                logger.info(f"No anonymous referral found for session {anonymous_session_id}")
                return False
            
            # Update the referral
            referral.referred_user_id = registered_user_id
            referral.is_converted = True
            referral.converted_at = self._naive_utc_now()
            
            # Update the referred user
            user_result = await db.execute(
                select(User).where(User.id == registered_user_id)
            )
            user = user_result.scalar_one_or_none()
            if user and not user.referred_by_user_id:
                user.referred_by_user_id = referral.referrer_user_id
            
            # Try to award registration reward
            await self._try_award_reward(db, referral, 'registration')
            
            # Update referrer's referral count
            referrer_result = await db.execute(
                select(User).where(User.id == referral.referrer_user_id)
            )
            referrer = referrer_result.scalar_one_or_none()
            if referrer:
                referrer.referral_count += 1
            
            await db.commit()
            logger.info(f"Converted anonymous referral to user {registered_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting anonymous referral: {e}")
            await db.rollback()
            return False
    
    async def track_referral_action(
        self,
        db: AsyncSession,
        user_id: int,
        action: str  # 'first_story' or 'first_publish'
    ) -> bool:
        """Track when a referred user completes an action."""
        try:
            # Find the referral for this user
            result = await db.execute(
                select(Referral).where(
                    Referral.referred_user_id == user_id
                )
            )
            referral = result.scalar_one_or_none()
            
            if not referral:
                logger.info(f"No referral found for user {user_id}")
                return False
            
            # Update the referral based on action
            if action == 'first_story' and not referral.has_created_story:
                referral.has_created_story = True
                referral.first_story_at = self._naive_utc_now()
                await self._try_award_reward(db, referral, 'first_story')
            elif action == 'first_publish' and not referral.has_published_story:
                referral.has_published_story = True
                referral.first_publish_at = self._naive_utc_now()
                await self._try_award_reward(db, referral, 'first_publish')
            else:
                logger.info(f"Action {action} already completed or invalid for user {user_id}")
                return False
            
            await db.commit()
            logger.info(f"Tracked referral action {action} for user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking referral action: {e}")
            await db.rollback()
            return False
    
    async def _try_award_reward(
        self,
        db: AsyncSession,
        referral: Referral,
        reward_type: str
    ) -> bool:
        """Try to award a referral reward, checking daily limits."""
        try:
            logger.info(f"🔍 REWARD DEBUG: Starting _try_award_reward for referral {referral.id}, reward_type: {reward_type}")
            
            # Check if reward already given
            logger.info(f"🔍 REWARD DEBUG: Checking for existing reward...")
            existing_reward = await db.execute(
                select(ReferralReward).where(
                    ReferralReward.referral_id == referral.id,
                    ReferralReward.reward_type == reward_type
                )
            )
            existing_reward_obj = existing_reward.scalar_one_or_none()
            if existing_reward_obj:
                logger.info(f"🔍 REWARD DEBUG: Reward {reward_type} already given for referral {referral.id}")
                return False
            
            logger.info(f"🔍 REWARD DEBUG: No existing reward found, proceeding...")
            
            # Get or create today's limit record
            today = date.today()
            logger.info(f"🔍 REWARD DEBUG: Getting daily limit record for user {referral.referrer_user_id}, date: {today}")
            limit_result = await db.execute(
                select(ReferralLimit).where(
                    ReferralLimit.user_id == referral.referrer_user_id,
                    func.date(ReferralLimit.date) == today
                )
            )
            limit = limit_result.scalar_one_or_none()
            
            if not limit:
                logger.info(f"🔍 REWARD DEBUG: No daily limit record found, creating new one...")
                limit = ReferralLimit(
                    user_id=referral.referrer_user_id,
                    date=datetime.combine(today, datetime.min.time())
                )
                db.add(limit)
                await db.flush()
                logger.info(f"🔍 REWARD DEBUG: Created new daily limit record with ID: {limit.id}")
            else:
                logger.info(f"🔍 REWARD DEBUG: Found existing daily limit record: {limit.id}")
            
            # Check daily limits
            reward_amount = REFERRAL_REWARDS.get(reward_type, 0)
            logger.info(f"🔍 REWARD DEBUG: Reward amount for {reward_type}: {reward_amount}")
            logger.info(f"🔍 REWARD DEBUG: Current total coins earned today: {limit.total_coins_earned}")
            
            # Check total daily coin limit
            if limit.total_coins_earned + reward_amount > DAILY_LIMITS['total_coins']:
                logger.info(f"🔍 REWARD DEBUG: Daily coin limit reached for user {referral.referrer_user_id}")
                return False
            
            # Check per-reward-type limits
            limit_key = f"{reward_type.replace('first_', '')}_rewards"
            current_count = getattr(limit, f"{limit_key}_count", 0)
            max_count = DAILY_LIMITS.get(limit_key, float('inf'))
            
            logger.info(f"🔍 REWARD DEBUG: Checking {limit_key} limits: current={current_count}, max={max_count}")
            
            if current_count >= max_count:
                logger.info(f"🔍 REWARD DEBUG: Daily {reward_type} limit reached for user {referral.referrer_user_id}")
                return False
            
            # Award the reward
            logger.info(f"🔍 REWARD DEBUG: Creating reward record...")
            reward = ReferralReward(
                referral_id=referral.id,
                user_id=referral.referrer_user_id,
                reward_type=reward_type,
                coin_amount=reward_amount
            )
            db.add(reward)
            logger.info(f"🔍 REWARD DEBUG: Added reward to session")
            
            # Update limits
            logger.info(f"🔍 REWARD DEBUG: Updating limits...")
            limit.total_coins_earned += reward_amount
            setattr(limit, f"{limit_key}_count", current_count + 1)
            logger.info(f"🔍 REWARD DEBUG: Updated limits - total_coins_earned: {limit.total_coins_earned}, {limit_key}_count: {current_count + 1}")
            
            # Add coins to user's account
            logger.info(f"🔍 REWARD DEBUG: Calling billing service to add reward...")
            await billing_service.add_referral_reward(
                db,
                referral.referrer_user_id,
                reward_amount,
                f"Referral reward: {reward_type}"
            )
            logger.info(f"🔍 REWARD DEBUG: Billing service completed")
            
            await db.flush()
            logger.info(f"🔍 REWARD DEBUG: Flushed reward changes to database")
            logger.info(f"🔍 REWARD DEBUG: Awarded {reward_amount} coins for {reward_type} to user {referral.referrer_user_id}")
            return True
            
        except Exception as e:
            logger.error(f"🔍 REWARD DEBUG: Error awarding referral reward: {e}", exc_info=True)
            return False
    
    async def get_user_referral_stats(
        self,
        db: AsyncSession,
        user_id: int
    ) -> Dict[str, Any]:
        """Get referral statistics for a user."""
        try:
            # Get total referrals
            total_referrals = await db.execute(
                select(func.count(Referral.id)).where(
                    Referral.referrer_user_id == user_id
                )
            )
            total_count = total_referrals.scalar() or 0
            
            # Get converted referrals
            converted_referrals = await db.execute(
                select(func.count(Referral.id)).where(
                    Referral.referrer_user_id == user_id,
                    Referral.is_converted == True
                )
            )
            converted_count = converted_referrals.scalar() or 0
            
            # Get total coins earned
            total_coins = await db.execute(
                select(func.sum(ReferralReward.coin_amount)).where(
                    ReferralReward.user_id == user_id
                )
            )
            coins_earned = total_coins.scalar() or 0
            
            # Get today's stats
            today = date.today()
            today_limit = await db.execute(
                select(ReferralLimit).where(
                    ReferralLimit.user_id == user_id,
                    func.date(ReferralLimit.date) == today
                )
            )
            today_stats = today_limit.scalar_one_or_none()
            
            # Get platform breakdown
            platform_stats = await db.execute(
                select(
                    Referral.source_platform,
                    func.count(Referral.id).label('count')
                ).where(
                    Referral.referrer_user_id == user_id
                ).group_by(Referral.source_platform)
            )
            
            platforms = {
                row.source_platform or 'direct': row.count
                for row in platform_stats
            }
            
            return {
                'total_referrals': total_count,
                'converted_referrals': converted_count,
                'conversion_rate': (converted_count / total_count * 100) if total_count > 0 else 0,
                'total_coins_earned': coins_earned,
                'today': {
                    'coins_earned': today_stats.total_coins_earned if today_stats else 0,
                    'coins_remaining': DAILY_LIMITS['total_coins'] - (today_stats.total_coins_earned if today_stats else 0),
                    'visit_rewards': today_stats.visit_rewards_count if today_stats else 0,
                    'registration_rewards': today_stats.registration_rewards_count if today_stats else 0,
                    'story_rewards': today_stats.story_rewards_count if today_stats else 0,
                    'publish_rewards': today_stats.publish_rewards_count if today_stats else 0
                },
                'platform_breakdown': platforms,
                'limits': DAILY_LIMITS,
                'reward_amounts': REFERRAL_REWARDS
            }
            
        except Exception as e:
            logger.error(f"Error getting referral stats: {e}")
            return {
                'total_referrals': 0,
                'converted_referrals': 0,
                'conversion_rate': 0,
                'total_coins_earned': 0,
                'today': {
                    'coins_earned': 0,
                    'coins_remaining': DAILY_LIMITS['total_coins'],
                    'visit_rewards': 0,
                    'registration_rewards': 0,
                    'story_rewards': 0,
                    'publish_rewards': 0
                },
                'platform_breakdown': {},
                'limits': DAILY_LIMITS,
                'reward_amounts': REFERRAL_REWARDS
            }


# Singleton instance
referral_service = ReferralService()
