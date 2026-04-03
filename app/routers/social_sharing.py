"""
Social Sharing API endpoints for tracking shares and coin rewards.
"""
from datetime import datetime, date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db_session, get_current_user
from app.models.user import User
from app.schemas.base import ApiResponse
from app.schemas.social_share import (
    SocialShareCreate, SocialShareResponse,
    ShareUrlRequest, ShareUrlResponse,
    SocialShareAnalytics
)
from app.services.social_sharing_service import SocialSharingService
from app.services.billing_service import billing_service


router = APIRouter(prefix="/api/v1/social", tags=["social-sharing"])


def get_social_sharing_service(db: AsyncSession = Depends(get_db_session)) -> SocialSharingService:
    """Dependency to get social sharing service."""
    return SocialSharingService(db, billing_service)


@router.post("/share/url", response_model=ApiResponse)
async def generate_share_url(
    request: ShareUrlRequest,
    url: str,
    title: str,
    description: Optional[str] = None,
    image: Optional[str] = None,
    hashtags: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user),
    service: SocialSharingService = Depends(get_social_sharing_service)
):
    """Generate a share URL for the specified platform."""
    try:
        user_id = current_user.id if current_user else None
        response = await service.generate_share_url(
            request,
            user_id=user_id,
            url=url,
            title=title,
            description=description or "",
            image=image or "",
            hashtags=hashtags or ""
        )
        return ApiResponse.success_response(response.model_dump())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/share/track", response_model=ApiResponse)
async def track_share(
    share_data: SocialShareCreate,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    service: SocialSharingService = Depends(get_social_sharing_service)
):
    """Track a social media share and award coins if applicable."""
    
    # Add request metadata
    share_data.ip_address = request.client.host if request.client else None
    share_data.user_agent = request.headers.get("user-agent")
    share_data.referrer = request.headers.get("referer")
    
    user_id = current_user.id if current_user else None
    
    try:
        response = await service.track_share(share_data, user_id)
        return ApiResponse.success_response(response.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error tracking share: {str(e)}"
        )


@router.get("/share/stats/daily")
async def get_daily_stats(
    target_date: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user),
    service: SocialSharingService = Depends(get_social_sharing_service)
):
    """Get daily sharing statistics for the current user."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        parsed_date = None
        if target_date:
            parsed_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        
        return ApiResponse.success_response(
            await service.get_user_daily_stats(current_user.id, parsed_date)
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )


@router.get("/share/analytics", response_model=ApiResponse)
async def get_sharing_analytics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user),
    service: SocialSharingService = Depends(get_social_sharing_service)
):
    """Get comprehensive sharing analytics."""
    
    # Parse dates if provided
    parsed_start_date = None
    parsed_end_date = None
    
    try:
        if start_date:
            parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    user_id = current_user.id if current_user else None
    
    analytics = await service.get_analytics(
        user_id=user_id,
        start_date=parsed_start_date,
        end_date=parsed_end_date
    )
    if hasattr(analytics, "model_dump"):
        analytics = analytics.model_dump()
    return ApiResponse.success_response(analytics)


@router.get("/share/platforms")
async def get_supported_platforms():
    """Get list of supported social media platforms."""
    return ApiResponse.success_response({
        "platforms": [
            {
                "id": "facebook",
                "name": "Facebook",
                "icon": "fab fa-facebook-f",
                "color": "#1877f2"
            },
            {
                "id": "twitter",
                "name": "Twitter/X",
                "icon": "fab fa-twitter",
                "color": "#1da1f2"
            },
            {
                "id": "linkedin",
                "name": "LinkedIn",
                "icon": "fab fa-linkedin-in",
                "color": "#0077b5"
            },
            {
                "id": "reddit",
                "name": "Reddit",
                "icon": "fab fa-reddit-alien",
                "color": "#ff4500"
            },
            {
                "id": "whatsapp",
                "name": "WhatsApp",
                "icon": "fab fa-whatsapp",
                "color": "#25d366"
            },
            {
                "id": "email",
                "name": "Email",
                "icon": "fas fa-envelope",
                "color": "#6c757d"
            },
            {
                "id": "copy_link",
                "name": "Copy Link",
                "icon": "fas fa-link",
                "color": "#6c757d"
            },
            {
                "id": "pinterest",
                "name": "Pinterest",
                "icon": "fab fa-pinterest-p",
                "color": "#bd081c"
            },
            {
                "id": "telegram",
                "name": "Telegram",
                "icon": "fab fa-telegram-plane",
                "color": "#0088cc"
            }
        ]
    })


@router.get("/share/config")
async def get_sharing_config():
    """Get sharing configuration and limits."""
    return ApiResponse.success_response({
        "max_daily_coins": SocialSharingService.MAX_DAILY_COINS,
        "coins_per_share": SocialSharingService.COINS_PER_SHARE,
        "supported_content_types": [
            "image_preview",
            "published_story", 
            "ai_public_chat"
        ]
    })
