"""
Referral tracking and analytics API endpoints.
"""
import logging
from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db_session, get_current_active_user, get_current_user
from app.models.user import User
from app.models.referral import Referral, ReferralReward
from app.services.referral_service import referral_service
from app.schemas.base import ApiResponse
from app.schemas.referral import (
    ReferralStats, ReferralHistory, ReferralRewardResponse,
    ReferralTrackingRequest, ReferralTrackingResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/referrals", tags=["referrals"])


@router.get("/stats", response_model=ApiResponse)
async def get_referral_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get referral statistics for the current user."""
    try:
        stats = await referral_service.get_user_referral_stats(db, current_user.id)
        return ApiResponse.success_response(data=ReferralStats(**stats))
    except Exception as e:
        logger.error(f"Error getting referral stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving referral statistics"
        )


@router.get("/history")
async def get_referral_history(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get referral history for the current user."""
    try:
        # Get referrals
        referrals = await db.execute(
            select(Referral)
            .where(Referral.referrer_user_id == current_user.id)
            .order_by(Referral.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        referral_list = referrals.scalars().all()
        
        # Convert to response format
        history = []
        for ref in referral_list:
            history.append({
                'id': ref.id,
                'referred_user_id': ref.referred_user_id,
                'is_anonymous': ref.referred_user_id is None,
                'source_platform': ref.source_platform,
                'source_content_type': ref.source_content_type,
                'is_converted': ref.is_converted,
                'converted_at': ref.converted_at,
                'has_created_story': ref.has_created_story,
                'has_published_story': ref.has_published_story,
                'created_at': ref.created_at
            })
        
        return ApiResponse.success_response(data={
            'referrals': history,
            'total': len(history),
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Error getting referral history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving referral history"
        )


@router.get("/rewards")
async def get_referral_rewards(
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get referral reward history for the current user."""
    try:
        # Get rewards
        rewards = await db.execute(
            select(ReferralReward)
            .where(ReferralReward.user_id == current_user.id)
            .order_by(ReferralReward.awarded_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        reward_list = rewards.scalars().all()
        
        # Convert to response format
        history = []
        for reward in reward_list:
            history.append({
                'id': reward.id,
                'referral_id': reward.referral_id,
                'reward_type': reward.reward_type,
                'coin_amount': reward.coin_amount,
                'awarded_at': reward.awarded_at
            })
        
        return ApiResponse.success_response(data={
            'rewards': history,
            'total': len(history),
            'limit': limit,
            'offset': offset
        })
        
    except Exception as e:
        logger.error(f"Error getting referral rewards: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving referral rewards"
        )


@router.post("/track", response_model=ApiResponse)
async def track_referral_visit(
    request: Request,
    tracking_data: ReferralTrackingRequest,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Track a referral visit (called by frontend when ref parameter detected)."""
    try:
        logger.info(f"🔍 REFERRAL DEBUG: Starting referral tracking with data: {tracking_data}")
        
        # Parse referral code
        try:
            referrer_user_id = int(tracking_data.referral_code)
            logger.info(f"🔍 REFERRAL DEBUG: Parsed referrer_user_id: {referrer_user_id}")
        except ValueError:
            logger.error(f"🔍 REFERRAL DEBUG: Invalid referral code: {tracking_data.referral_code}")
            return ApiResponse.success_response(data=ReferralTrackingResponse(
                success=False,
                message="Invalid referral code"
            ))
        
        # Get user info
        user_id = current_user.id if current_user else None
        anonymous_session_id = None
        
        logger.info(f"🔍 REFERRAL DEBUG: Current user: {current_user}")
        logger.info(f"🔍 REFERRAL DEBUG: User ID: {user_id}")
        
        if not user_id:
            # Get anonymous session from cookies, or create a temporary one
            anonymous_session_id = request.cookies.get("anon_session")
            logger.info(f"🔍 REFERRAL DEBUG: Anonymous session from cookies: {anonymous_session_id}")
            if not anonymous_session_id:
                # Create a temporary session ID for tracking
                import secrets
                anonymous_session_id = f"temp_{secrets.token_hex(16)}"
                logger.info(f"🔍 REFERRAL DEBUG: Created temporary session ID: {anonymous_session_id}")
        
        logger.info(f"🔍 REFERRAL DEBUG: Final anonymous_session_id: {anonymous_session_id}")
        
        # Don't allow self-referrals
        if user_id and user_id == referrer_user_id:
            logger.warning(f"🔍 REFERRAL DEBUG: Self-referral blocked - user {user_id} referring themselves")
            return ApiResponse.success_response(data=ReferralTrackingResponse(
                success=False,
                message="Self-referrals are not allowed"
            ))
        
        # Get IP address
        ip_address = request.client.host
        if request.headers.get("X-Forwarded-For"):
            ip_address = request.headers.get("X-Forwarded-For").split(",")[0].strip()
        
        logger.info(f"🔍 REFERRAL DEBUG: IP address: {ip_address}")
        
        # Use user agent from tracking data or fall back to headers
        user_agent = tracking_data.user_agent or request.headers.get("User-Agent", "")
        logger.info(f"🔍 REFERRAL DEBUG: User agent: {user_agent[:100]}...")
        
        # Track the referral
        logger.info(f"🔍 REFERRAL DEBUG: Calling referral_service.track_referral_visit with:")
        logger.info(f"🔍 REFERRAL DEBUG: - referrer_user_id: {referrer_user_id}")
        logger.info(f"🔍 REFERRAL DEBUG: - referred_user_id: {user_id}")
        logger.info(f"🔍 REFERRAL DEBUG: - anonymous_session_id: {anonymous_session_id}")
        logger.info(f"🔍 REFERRAL DEBUG: - source_platform: {tracking_data.source_platform}")
        logger.info(f"🔍 REFERRAL DEBUG: - landing_page: {tracking_data.landing_page}")
        
        result = await referral_service.track_referral_visit(
            db=db,
            referrer_user_id=referrer_user_id,
            referred_user_id=user_id,
            anonymous_session_id=anonymous_session_id,
            source_platform=tracking_data.source_platform,
            source_content_type=tracking_data.source_content_type,
            source_content_id=tracking_data.source_content_id,
            ip_address=ip_address,
            user_agent=user_agent,
            referral_url=tracking_data.landing_page or str(request.url)
        )
        
        logger.info(f"🔍 REFERRAL DEBUG: Service returned result: {result}")
        
        if result:
            # Check if a reward was given
            reward_given = False
            reward_amount = 0
            
            reward_result = await db.execute(
                select(ReferralReward)
                .where(ReferralReward.referral_id == result.id)
                .order_by(ReferralReward.awarded_at.desc())
            )
            latest_reward = reward_result.scalars().first()
            if latest_reward:
                reward_given = True
                reward_amount = latest_reward.coin_amount
            
            return ApiResponse.success_response(data=ReferralTrackingResponse(
                success=True,
                message="Referral tracked successfully",
                reward_given=reward_given,
                reward_amount=reward_amount,
                referral_id=result.id
            ))
        else:
            return ApiResponse.success_response(data=ReferralTrackingResponse(
                success=True,
                message="Referral already tracked",
                reward_given=False,
                reward_amount=0
            ))
            
    except Exception as e:
        logger.error(f"Error tracking referral: {e}")
        return ApiResponse.success_response(data=ReferralTrackingResponse(
            success=False,
            message="Error tracking referral"
        ))
