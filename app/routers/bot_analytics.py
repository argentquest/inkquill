# /ai_rag_story_app/app/routers/bot_analytics.py

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from app.core.deps import get_db_session, get_current_user
from app.models.user_activity import UserActivity
from app.utils.bot_detection import is_bot_request, get_bot_info
from app.core.config import settings
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/analytics", tags=["Bot Analytics"])

@router.get("/bot-detection-test")
async def test_bot_detection(request: Request):
    """Test endpoint to check if current request is detected as a bot"""
    is_bot = is_bot_request(request)
    bot_info = get_bot_info(request) if is_bot else None
    
    return {
        "is_bot": is_bot,
        "bot_info": bot_info,
        "user_agent": request.headers.get("user-agent", ""),
        "ip": request.client.host if request.client else None,
        "filter_enabled": settings.FILTER_BOT_ANALYTICS
    }

@router.get("/activity-stats")
async def get_activity_stats(
    hours: int = 24,
    db: AsyncSession = Depends(get_db_session)
):
    """Get activity statistics showing bot vs human traffic"""
    
    # Calculate time window
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Get total activity count
    total_query = select(func.count(UserActivity.id)).where(
        UserActivity.created_at >= since
    )
    total_result = await db.execute(total_query)
    total_count = total_result.scalar() or 0
    
    # Get activity by user agent patterns (to identify bot patterns that got through)
    bot_pattern_query = select(
        UserActivity.user_agent,
        func.count(UserActivity.id).label('count')
    ).where(
        and_(
            UserActivity.created_at >= since,
            or_(
                UserActivity.user_agent.ilike('%bot%'),
                UserActivity.user_agent.ilike('%crawler%'),
                UserActivity.user_agent.ilike('%spider%'),
                UserActivity.user_agent.ilike('%facebook%'),
                UserActivity.user_agent.ilike('%twitter%'),
                UserActivity.user_agent.ilike('%linkedin%'),
                UserActivity.user_agent.ilike('%discord%'),
                UserActivity.user_agent.ilike('%whatsapp%')
            )
        )
    ).group_by(UserActivity.user_agent).order_by(desc('count')).limit(10)
    
    bot_patterns_result = await db.execute(bot_pattern_query)
    bot_patterns = bot_patterns_result.fetchall()
    
    # Get activity by endpoint
    endpoint_query = select(
        UserActivity.endpoint,
        func.count(UserActivity.id).label('count')
    ).where(
        UserActivity.created_at >= since
    ).group_by(UserActivity.endpoint).order_by(desc('count')).limit(10)
    
    endpoint_result = await db.execute(endpoint_query)
    top_endpoints = endpoint_result.fetchall()
    
    # Get referrer statistics
    referrer_query = select(
        func.coalesce(UserActivity.request_data['referrer'].astext, 'Direct').label('referrer'),
        func.count(UserActivity.id).label('count')
    ).where(
        UserActivity.created_at >= since
    ).group_by('referrer').order_by(desc('count')).limit(10)
    
    try:
        referrer_result = await db.execute(referrer_query)
        top_referrers = referrer_result.fetchall()
    except Exception as e:
        logger.warning(f"Could not get referrer stats: {e}")
        top_referrers = []
    
    return {
        "time_window_hours": hours,
        "since": since.isoformat(),
        "total_activity_count": total_count,
        "bot_filtering_enabled": settings.FILTER_BOT_ANALYTICS,
        "detected_bot_patterns": [
            {"user_agent": pattern[0][:100], "count": pattern[1]} 
            for pattern in bot_patterns
        ],
        "top_endpoints": [
            {"endpoint": endpoint[0], "count": endpoint[1]} 
            for endpoint in top_endpoints
        ],
        "top_referrers": [
            {"referrer": ref[0] if ref[0] else "Direct", "count": ref[1]} 
            for ref in top_referrers
        ],
        "note": "If bot filtering is enabled, bot requests should not appear in user_activity logs",
        "configured_bot_patterns": settings.BOT_USER_AGENTS
    }

@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 50,
    db: AsyncSession = Depends(get_db_session)
):
    """Get recent activity with user agent analysis"""
    
    query = select(
        UserActivity.created_at,
        UserActivity.endpoint,
        UserActivity.method,
        UserActivity.ip_address,
        UserActivity.user_agent,
        UserActivity.status_code
    ).order_by(desc(UserActivity.created_at)).limit(limit)
    
    result = await db.execute(query)
    activities = result.fetchall()
    
    # Analyze each activity for bot patterns
    analyzed_activities = []
    for activity in activities:
        user_agent = activity.user_agent or ""
        
        # Simple bot detection on stored data
        likely_bot = any(
            pattern.lower() in user_agent.lower() 
            for pattern in settings.BOT_USER_AGENTS
        )
        
        analyzed_activities.append({
            "timestamp": activity.created_at.isoformat(),
            "endpoint": activity.endpoint,
            "method": activity.method,
            "ip": activity.ip_address,
            "user_agent": user_agent[:100] + "..." if len(user_agent) > 100 else user_agent,
            "status_code": activity.status_code,
            "likely_bot": likely_bot
        })
    
    return {
        "activities": analyzed_activities,
        "total_returned": len(analyzed_activities),
        "note": "likely_bot is based on user agent analysis of stored data"
    }