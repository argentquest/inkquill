"""Blog subscription service for newsletter functionality."""
import logging
import secrets
import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, update, delete
from sqlalchemy.orm import selectinload

from app.models.blog_subscription import (
    BlogSubscription, SubscriptionStatus, SubscriptionFrequency
)
from app.models.user import User

logger = logging.getLogger(__name__)


class BlogSubscriptionService:
    """Service for managing blog subscriptions and newsletters."""
    
    async def subscribe(
        self,
        db: AsyncSession,
        email: str,
        user_id: Optional[int] = None,
        frequency: SubscriptionFrequency = SubscriptionFrequency.WEEKLY,
        source: str = "website",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        require_confirmation: bool = True
    ) -> BlogSubscription:
        """
        Subscribe an email to the blog newsletter.
        
        Args:
            db: Database session
            email: Email address to subscribe
            user_id: User ID if they're registered
            frequency: How often to send emails
            source: Where they subscribed from
            ip_address: IP address of subscriber
            user_agent: User agent string
            require_confirmation: Whether to require email confirmation
            
        Returns:
            BlogSubscription object
        """
        try:
            # Check if already subscribed
            existing_result = await db.execute(
                select(BlogSubscription).where(
                    and_(
                        BlogSubscription.email == email.lower(),
                        BlogSubscription.status.in_([
                            SubscriptionStatus.ACTIVE,
                            SubscriptionStatus.PENDING
                        ])
                    )
                )
            )
            existing = existing_result.scalar_one_or_none()
            
            if existing:
                if existing.status == SubscriptionStatus.ACTIVE:
                    logger.info(f"Email {email} already has active subscription")
                    return existing
                elif existing.status == SubscriptionStatus.PENDING:
                    # Resend confirmation if pending
                    logger.info(f"Resending confirmation for {email}")
                    return existing
            
            # Create new subscription
            subscription = BlogSubscription(
                email=email.lower(),
                user_id=user_id,
                frequency=frequency,
                status=SubscriptionStatus.PENDING if require_confirmation else SubscriptionStatus.ACTIVE,
                confirmation_token=secrets.token_urlsafe(32) if require_confirmation else None,
                unsubscribe_token=secrets.token_urlsafe(32),
                source=source,
                ip_address=ip_address,
                user_agent=user_agent,
                confirmed_at=None if require_confirmation else datetime.utcnow()
            )
            
            db.add(subscription)
            await db.commit()
            await db.refresh(subscription)
            
            logger.info(f"Created subscription for {email} with status {subscription.status}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating subscription for {email}: {e}")
            await db.rollback()
            raise
    
    async def confirm_subscription(
        self,
        db: AsyncSession,
        confirmation_token: str
    ) -> Optional[BlogSubscription]:
        """
        Confirm a subscription using the confirmation token.
        
        Args:
            db: Database session
            confirmation_token: The confirmation token
            
        Returns:
            BlogSubscription if confirmed, None if token invalid
        """
        try:
            result = await db.execute(
                select(BlogSubscription).where(
                    and_(
                        BlogSubscription.confirmation_token == confirmation_token,
                        BlogSubscription.status == SubscriptionStatus.PENDING
                    )
                )
            )
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                logger.warning(f"Invalid confirmation token: {confirmation_token}")
                return None
            
            # Confirm the subscription
            await db.execute(
                update(BlogSubscription)
                .where(BlogSubscription.id == subscription.id)
                .values(
                    status=SubscriptionStatus.ACTIVE,
                    confirmed_at=datetime.utcnow(),
                    confirmation_token=None
                )
            )
            await db.commit()
            
            # Refresh the object
            await db.refresh(subscription)
            
            logger.info(f"Confirmed subscription for {subscription.email}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error confirming subscription: {e}")
            await db.rollback()
            return None
    
    async def unsubscribe(
        self,
        db: AsyncSession,
        unsubscribe_token: str
    ) -> Optional[BlogSubscription]:
        """
        Unsubscribe using the unsubscribe token.
        
        Args:
            db: Database session
            unsubscribe_token: The unsubscribe token
            
        Returns:
            BlogSubscription if unsubscribed, None if token invalid
        """
        try:
            result = await db.execute(
                select(BlogSubscription).where(
                    BlogSubscription.unsubscribe_token == unsubscribe_token
                )
            )
            subscription = result.scalar_one_or_none()
            
            if not subscription:
                logger.warning(f"Invalid unsubscribe token: {unsubscribe_token}")
                return None
            
            # Unsubscribe
            await db.execute(
                update(BlogSubscription)
                .where(BlogSubscription.id == subscription.id)
                .values(
                    status=SubscriptionStatus.UNSUBSCRIBED,
                    unsubscribed_at=datetime.utcnow()
                )
            )
            await db.commit()
            
            logger.info(f"Unsubscribed {subscription.email}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error unsubscribing: {e}")
            await db.rollback()
            return None
    
    async def get_active_subscriptions(
        self,
        db: AsyncSession,
        frequency: Optional[SubscriptionFrequency] = None,
        skip: int = 0,
        limit: int = 1000
    ) -> List[BlogSubscription]:
        """
        Get active subscriptions, optionally filtered by frequency.
        
        Args:
            db: Database session
            frequency: Filter by frequency
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of active subscriptions
        """
        try:
            query = select(BlogSubscription).where(
                BlogSubscription.status == SubscriptionStatus.ACTIVE
            )
            
            if frequency:
                query = query.where(BlogSubscription.frequency == frequency)
            
            query = query.offset(skip).limit(limit).order_by(BlogSubscription.created_at)
            
            result = await db.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error getting active subscriptions: {e}")
            return []
    
    async def get_subscription_by_email(
        self,
        db: AsyncSession,
        email: str
    ) -> Optional[BlogSubscription]:
        """
        Get subscription by email address.
        
        Args:
            db: Database session
            email: Email address
            
        Returns:
            BlogSubscription if found, None otherwise
        """
        try:
            result = await db.execute(
                select(BlogSubscription).where(
                    BlogSubscription.email == email.lower()
                )
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting subscription for {email}: {e}")
            return None
    
    async def update_subscription_preferences(
        self,
        db: AsyncSession,
        subscription_id: int,
        frequency: Optional[SubscriptionFrequency] = None,
        include_categories: Optional[List[int]] = None,
        include_tags: Optional[List[int]] = None
    ) -> Optional[BlogSubscription]:
        """
        Update subscription preferences.
        
        Args:
            db: Database session
            subscription_id: Subscription ID
            frequency: New frequency preference
            include_categories: List of category IDs to include
            include_tags: List of tag IDs to include
            
        Returns:
            Updated subscription or None if not found
        """
        try:
            # Build update values
            update_values = {"updated_at": datetime.utcnow()}
            
            if frequency is not None:
                update_values["frequency"] = frequency
            
            if include_categories is not None:
                update_values["include_categories"] = json.dumps(include_categories)
            
            if include_tags is not None:
                update_values["include_tags"] = json.dumps(include_tags)
            
            # Update subscription
            await db.execute(
                update(BlogSubscription)
                .where(BlogSubscription.id == subscription_id)
                .values(**update_values)
            )
            await db.commit()
            
            # Get updated subscription
            result = await db.execute(
                select(BlogSubscription).where(BlogSubscription.id == subscription_id)
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error updating subscription {subscription_id}: {e}")
            await db.rollback()
            return None
    
    async def record_email_sent(
        self,
        db: AsyncSession,
        subscription_id: int
    ) -> bool:
        """
        Record that an email was sent to a subscription.
        
        Args:
            db: Database session
            subscription_id: Subscription ID
            
        Returns:
            True if recorded successfully
        """
        try:
            await db.execute(
                update(BlogSubscription)
                .where(BlogSubscription.id == subscription_id)
                .values(
                    last_sent_at=datetime.utcnow(),
                    total_emails_sent=BlogSubscription.total_emails_sent + 1
                )
            )
            await db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error recording email sent for subscription {subscription_id}: {e}")
            await db.rollback()
            return False
    
    async def record_email_opened(
        self,
        db: AsyncSession,
        subscription_id: int
    ) -> bool:
        """
        Record that an email was opened.
        
        Args:
            db: Database session
            subscription_id: Subscription ID
            
        Returns:
            True if recorded successfully
        """
        try:
            await db.execute(
                update(BlogSubscription)
                .where(BlogSubscription.id == subscription_id)
                .values(
                    last_opened_at=datetime.utcnow(),
                    open_count=BlogSubscription.open_count + 1
                )
            )
            await db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error recording email opened for subscription {subscription_id}: {e}")
            await db.rollback()
            return False
    
    async def get_subscription_stats(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Get subscription statistics.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with subscription stats
        """
        try:
            # Count by status
            status_counts = {}
            for status in SubscriptionStatus:
                result = await db.execute(
                    select(func.count(BlogSubscription.id))
                    .where(BlogSubscription.status == status)
                )
                status_counts[status.value] = result.scalar() or 0
            
            # Count by frequency
            frequency_counts = {}
            for frequency in SubscriptionFrequency:
                result = await db.execute(
                    select(func.count(BlogSubscription.id))
                    .where(
                        and_(
                            BlogSubscription.frequency == frequency,
                            BlogSubscription.status == SubscriptionStatus.ACTIVE
                        )
                    )
                )
                frequency_counts[frequency.value] = result.scalar() or 0
            
            # Recent subscriptions (last 30 days)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            result = await db.execute(
                select(func.count(BlogSubscription.id))
                .where(BlogSubscription.created_at >= thirty_days_ago)
            )
            recent_subscriptions = result.scalar() or 0
            
            return {
                "total_subscriptions": sum(status_counts.values()),
                "active_subscriptions": status_counts.get("active", 0),
                "pending_confirmations": status_counts.get("pending", 0),
                "unsubscribed": status_counts.get("unsubscribed", 0),
                "by_frequency": frequency_counts,
                "recent_subscriptions_30d": recent_subscriptions
            }
            
        except Exception as e:
            logger.error(f"Error getting subscription stats: {e}")
            return {
                "error": "Failed to get subscription stats"
            }


# Global instance
blog_subscription_service = BlogSubscriptionService()