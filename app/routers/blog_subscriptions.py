"""Blog subscription API endpoints."""
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.deps import get_db_session, get_current_user, get_current_active_user
from app.models.user import User
from app.models.blog_subscription import SubscriptionFrequency, SubscriptionStatus
from app.services.blog_subscription_service import blog_subscription_service
from app.schemas.base import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog/subscriptions", tags=["blog-subscriptions"])


# Pydantic models
class SubscriptionRequest(BaseModel):
    email: EmailStr
    frequency: SubscriptionFrequency = SubscriptionFrequency.WEEKLY
    source: str = "website"


class SubscriptionResponse(BaseModel):
    id: int
    email: str
    status: SubscriptionStatus
    frequency: SubscriptionFrequency
    confirmed_at: Optional[str]
    created_at: str


class SubscriptionUpdateRequest(BaseModel):
    frequency: Optional[SubscriptionFrequency] = None
    include_categories: Optional[List[int]] = None
    include_tags: Optional[List[int]] = None


@router.post("/subscribe", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_to_newsletter(
    subscription_data: SubscriptionRequest,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Subscribe to the blog newsletter."""
    try:
        # Get IP address for tracking
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        subscription = await blog_subscription_service.subscribe(
            db=db,
            email=subscription_data.email,
            user_id=current_user.id if current_user else None,
            frequency=subscription_data.frequency,
            source=subscription_data.source,
            ip_address=ip_address,
            user_agent=user_agent,
            require_confirmation=True
        )
        
        if subscription.status == SubscriptionStatus.PENDING:
            message = "Please check your email to confirm your subscription."
        else:
            message = "Successfully subscribed to the newsletter!"
        
        return {
            "message": message,
            "subscription": {
                "id": subscription.id,
                "email": subscription.email,
                "status": subscription.status.value,
                "frequency": subscription.frequency.value,
                "needs_confirmation": subscription.needs_confirmation
            }
        }
        
    except Exception as e:
        logger.error(f"Error subscribing {subscription_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to subscribe to newsletter"
        )


@router.get("/confirm/{token}")
async def confirm_subscription(
    token: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Confirm a subscription using the confirmation token."""
    try:
        subscription = await blog_subscription_service.confirm_subscription(db, token)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid or expired confirmation token"
            )
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Subscription Confirmed</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .success {{ color: #28a745; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="success">✅ Subscription Confirmed!</h1>
                <p>Thank you for confirming your subscription to our blog newsletter.</p>
                <p>Email: <strong>{subscription.email}</strong></p>
                <p>Frequency: <strong>{subscription.frequency.value.title()}</strong></p>
                <p>You'll start receiving our newsletter according to your preferences.</p>
                <a href="/blog" style="color: #007bff; text-decoration: none;">← Back to Blog</a>
            </div>
        </body>
        </html>
        """)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error confirming subscription with token {token}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to confirm subscription"
        )


@router.get("/unsubscribe/{token}")
async def unsubscribe_from_newsletter(
    token: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Unsubscribe from the newsletter using the unsubscribe token."""
    try:
        subscription = await blog_subscription_service.unsubscribe(db, token)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid unsubscribe token"
            )
        
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Unsubscribed</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                .info {{ color: #17a2b8; }}
                .container {{ max-width: 600px; margin: 0 auto; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="info">📧 Successfully Unsubscribed</h1>
                <p>You have been unsubscribed from our blog newsletter.</p>
                <p>Email: <strong>{subscription.email}</strong></p>
                <p>You will no longer receive newsletter emails from us.</p>
                <p>If you change your mind, you can always subscribe again from our blog.</p>
                <a href="/blog" style="color: #007bff; text-decoration: none;">← Back to Blog</a>
            </div>
        </body>
        </html>
        """)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unsubscribing with token {token}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsubscribe"
        )


@router.get("/my-subscription", response_model=ApiResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user's subscription status."""
    try:
        subscription = await blog_subscription_service.get_subscription_by_email(
            db, current_user.email
        )
        
        if not subscription:
            return {
                "subscribed": False,
                "message": "You are not currently subscribed to the newsletter."
            }
        
        return {
            "subscribed": True,
            "subscription": {
                "id": subscription.id,
                "email": subscription.email,
                "status": subscription.status.value,
                "frequency": subscription.frequency.value,
                "confirmed_at": subscription.confirmed_at.isoformat() if subscription.confirmed_at else None,
                "created_at": subscription.created_at.isoformat(),
                "total_emails_sent": subscription.total_emails_sent,
                "open_count": subscription.open_count
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting subscription for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription status"
        )


@router.put("/my-subscription", response_model=ApiResponse)
async def update_my_subscription(
    update_data: SubscriptionUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update current user's subscription preferences."""
    try:
        subscription = await blog_subscription_service.get_subscription_by_email(
            db, current_user.email
        )
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You are not currently subscribed to the newsletter"
            )
        
        updated_subscription = await blog_subscription_service.update_subscription_preferences(
            db=db,
            subscription_id=subscription.id,
            frequency=update_data.frequency,
            include_categories=update_data.include_categories,
            include_tags=update_data.include_tags
        )
        
        if not updated_subscription:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update subscription preferences"
            )
        
        return {
            "message": "Subscription preferences updated successfully",
            "subscription": {
                "frequency": updated_subscription.frequency.value,
                "include_categories": updated_subscription.include_categories,
                "include_tags": updated_subscription.include_tags
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscription for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription preferences"
        )


@router.delete("/my-subscription", status_code=status.HTTP_204_NO_CONTENT)
async def unsubscribe_current_user(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Unsubscribe the current user from the newsletter."""
    try:
        subscription = await blog_subscription_service.get_subscription_by_email(
            db, current_user.email
        )
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="You are not currently subscribed to the newsletter"
            )
        
        await blog_subscription_service.unsubscribe(db, subscription.unsubscribe_token)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unsubscribing user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unsubscribe from newsletter"
        )


# Admin endpoints
@router.get("/stats", response_model=ApiResponse)
async def get_subscription_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get subscription statistics (admin only)."""
    try:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view subscription statistics"
            )
        
        stats = await blog_subscription_service.get_subscription_stats(db)
        return stats
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting subscription stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get subscription statistics"
        )


@router.get("/list", response_model=ApiResponse)
async def list_subscriptions(
    status_filter: Optional[SubscriptionStatus] = Query(None),
    frequency_filter: Optional[SubscriptionFrequency] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List subscriptions (admin only)."""
    try:
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can list subscriptions"
            )
        
        # For now, just get active subscriptions
        # TODO: Add filtering by status and frequency
        subscriptions = await blog_subscription_service.get_active_subscriptions(
            db=db,
            frequency=frequency_filter,
            skip=skip,
            limit=limit
        )
        
        return [
            {
                "id": sub.id,
                "email": sub.email,
                "status": sub.status.value,
                "frequency": sub.frequency.value,
                "created_at": sub.created_at.isoformat(),
                "confirmed_at": sub.confirmed_at.isoformat() if sub.confirmed_at else None,
                "total_emails_sent": sub.total_emails_sent,
                "open_count": sub.open_count
            }
            for sub in subscriptions
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing subscriptions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list subscriptions"
        )