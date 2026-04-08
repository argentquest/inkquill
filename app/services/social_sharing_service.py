"""
Social Sharing Service with coin rewards and analytics tracking.
"""
import uuid
from datetime import UTC, date, datetime
from typing import Optional, Dict, Any, List
from urllib.parse import quote_plus
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.models.social_share import SocialShare, SocialShareDailySummary
from app.models.user import User
from app.schemas.social_share import (
    SocialShareCreate, SocialShareResponse, 
    ShareUrlRequest, ShareUrlResponse,
    SocialShareAnalytics
)
from app.services.billing_service import BillingService


class SocialSharingService:
    """Service for handling social media sharing with coin rewards."""
    
    # Maximum coins per day per user
    MAX_DAILY_COINS = 10
    COINS_PER_SHARE = 1

    @staticmethod
    def _naive_utc_now() -> datetime:
        """Return UTC as a naive datetime for legacy TIMESTAMP WITHOUT TIME ZONE columns."""
        return datetime.now(UTC).replace(tzinfo=None)
    
    # Social platform configurations (popup dimensions increased by 75%)
    PLATFORM_CONFIGS = {
        'facebook': {
            'url_template': 'https://www.facebook.com/sharer/sharer.php?u={url}&quote={title}',
            'popup_width': 1050,
            'popup_height': 700
        },
        'twitter': {
            'url_template': 'https://twitter.com/intent/tweet?url={url}&text={title}&hashtags={hashtags}',
            'popup_width': 1050,
            'popup_height': 700
        },
        'linkedin': {
            'url_template': 'https://www.linkedin.com/sharing/share-offsite/?url={url}',
            'popup_width': 1050,
            'popup_height': 875
        },
        'reddit': {
            'url_template': 'https://reddit.com/submit?url={url}&title={title}',
            'popup_width': 1050,
            'popup_height': 875
        },
        'whatsapp': {
            'url_template': 'https://wa.me/?text={title}%20{url}',
            'popup_width': 1050,
            'popup_height': 700
        },
        'email': {
            'url_template': 'mailto:?subject={title}&body={description}%0A%0A{url}',
            'popup_width': 1050,
            'popup_height': 700
        },
        'pinterest': {
            'url_template': 'https://pinterest.com/pin/create/button/?url={url}&description={title}&media={image}',
            'popup_width': 1312,
            'popup_height': 612
        },
        'telegram': {
            'url_template': 'https://t.me/share/url?url={url}&text={title}',
            'popup_width': 1050,
            'popup_height': 700
        }
    }
    
    def __init__(self, db: AsyncSession, billing_service: BillingService):
        self.db = db
        self.billing_service = billing_service
    
    async def generate_share_url(self, request: ShareUrlRequest, user_id: Optional[int] = None, **kwargs) -> ShareUrlResponse:
        """Generate a share URL for the specified platform."""
        platform = request.platform.lower()
        
        if platform not in self.PLATFORM_CONFIGS:
            raise ValueError(f"Unsupported platform: {platform}")
        
        config = self.PLATFORM_CONFIGS[platform]
        
        # Get the base URL
        base_url = kwargs.get('url', '')
        
        # Add referral ID if user is authenticated
        if user_id:
            # Check if URL already has query parameters
            separator = '&' if '?' in base_url else '?'
            base_url = f"{base_url}{separator}ref={user_id}"
        
        # Prepare parameters
        params = {
            'url': quote_plus(base_url),
            'title': quote_plus(kwargs.get('title', '')),
            'description': quote_plus(kwargs.get('description', '')),
            'hashtags': quote_plus(kwargs.get('hashtags', '').replace('#', '')),
            'image': quote_plus(kwargs.get('image', ''))
        }
        
        # Generate share URL
        share_url = config['url_template'].format(**params)
        
        return ShareUrlResponse(
            share_url=share_url,
            popup_width=config['popup_width'],
            popup_height=config['popup_height']
        )
    
    async def track_share(
        self, 
        share_data: SocialShareCreate, 
        user_id: Optional[int] = None
    ) -> SocialShareResponse:
        """Track a social media share and award coins if applicable."""
        
        # Create share record
        share_record = SocialShare(
            user_id=user_id,
            content_type=share_data.content_type,
            content_id=share_data.content_id,
            content_title=share_data.content_title,
            content_url=share_data.content_url,
            platform=share_data.platform,
            shared_text=share_data.shared_text,
            shared_hashtags=share_data.shared_hashtags,
            ip_address=share_data.ip_address,
            user_agent=share_data.user_agent,
            referrer=share_data.referrer
        )
        
        coin_awarded = False
        coin_amount = 0
        daily_shares = 1
        remaining_coin_shares = self.MAX_DAILY_COINS
        message = "Share tracked successfully!"
        
        if user_id:
            # Check daily coin limit for registered users
            today = date.today()
            daily_summary = await self._get_or_create_daily_summary(user_id, today)
            
            daily_shares = daily_summary.total_shares + 1
            
            # Award coin if under daily limit
            if daily_summary.coins_earned < self.MAX_DAILY_COINS:
                coin_awarded = True
                coin_amount = self.COINS_PER_SHARE
                
                # Award the coin through billing service
                # Note: BillingService doesn't have add_coins, need to use billing_crud directly
                from app.crud.billing import billing_crud
                from app.models.user_transaction import TransactionType
                from app.schemas.billing import UserTransactionCreate
                from decimal import Decimal
                
                account = await billing_crud.get_or_create_user_account(self.db, user_id)
                new_balance = account.current_balance + Decimal(str(coin_amount))
                
                transaction_data = UserTransactionCreate(
                    user_account_id=account.id,
                    transaction_type=TransactionType.MONTHLY_BONUS,  # Using existing bonus type for social rewards
                    amount=Decimal(str(coin_amount)),
                    balance_after=new_balance,
                    description=f"Social sharing reward - {share_data.platform}"
                )
                
                await billing_crud.create_transaction(self.db, transaction_data)
                
                # Update account balance
                account.current_balance = new_balance
                await self.db.commit()
                
                share_record.coin_awarded = True
                share_record.coin_amount = coin_amount
                
                # Update daily summary
                daily_summary.coins_earned += coin_amount
                daily_summary.total_shares = daily_shares
                
                if daily_summary.coins_earned >= self.MAX_DAILY_COINS:
                    daily_summary.max_coins_reached = True
                
                # Update platform-specific counter
                platform_field = f"{share_data.platform}_shares"
                if hasattr(daily_summary, platform_field):
                    current_count = getattr(daily_summary, platform_field)
                    setattr(daily_summary, platform_field, current_count + 1)
                
                # Update content type counter
                content_field = f"{share_data.content_type}_shares"
                if hasattr(daily_summary, content_field):
                    current_count = getattr(daily_summary, content_field)
                    setattr(daily_summary, content_field, current_count + 1)
                
                daily_summary.updated_at = self._naive_utc_now()
                
                message = f"Share tracked! You earned {coin_amount} coin. Keep sharing!"
            else:
                daily_summary.total_shares = daily_shares
                message = "Share tracked! Daily coin limit reached, but thanks for sharing!"
            
            remaining_coin_shares = max(0, self.MAX_DAILY_COINS - daily_summary.coins_earned)
        
        # Save to database
        self.db.add(share_record)
        await self.db.commit()
        
        return SocialShareResponse(
            success=True,
            coin_awarded=coin_awarded,
            coin_amount=coin_amount,
            daily_shares=daily_shares,
            remaining_coin_shares=remaining_coin_shares,
            message=message
        )
    
    async def _get_or_create_daily_summary(
        self, 
        user_id: int, 
        target_date: date
    ) -> SocialShareDailySummary:
        """Get or create daily summary for user and date."""
        
        # Convert date to datetime for comparison
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())
        
        # Try to find existing summary
        result = await self.db.execute(
            select(SocialShareDailySummary).where(
                and_(
                    SocialShareDailySummary.user_id == user_id,
                    SocialShareDailySummary.date >= start_of_day,
                    SocialShareDailySummary.date <= end_of_day
                )
            )
        )
        summary = result.scalar_one_or_none()
        
        if not summary:
            # Create new summary
            summary = SocialShareDailySummary(
                user_id=user_id,
                date=start_of_day
            )
            self.db.add(summary)
            await self.db.flush()  # Get the ID
        
        return summary
    
    async def get_user_daily_stats(self, user_id: int, target_date: Optional[date] = None) -> Dict[str, Any]:
        """Get daily sharing statistics for a user."""
        if not target_date:
            target_date = date.today()
        
        summary = await self._get_or_create_daily_summary(user_id, target_date)
        
        return {
            'date': target_date.isoformat(),
            'total_shares': summary.total_shares,
            'coins_earned': summary.coins_earned,
            'remaining_coin_shares': max(0, self.MAX_DAILY_COINS - summary.coins_earned),
            'max_coins_reached': summary.max_coins_reached,
            'platform_breakdown': {
                'facebook': summary.facebook_shares,
                'twitter': summary.twitter_shares,
                'linkedin': summary.linkedin_shares,
                'reddit': summary.reddit_shares,
                'whatsapp': summary.whatsapp_shares,
                'email': summary.email_shares,
                'copy_link': summary.copy_link_shares,
                'pinterest': summary.pinterest_shares,
                'telegram': summary.telegram_shares,
            },
            'content_type_breakdown': {
                'image_preview': summary.image_preview_shares,
                'published_story': summary.published_story_shares,
                'ai_public_chat': summary.ai_public_chat_shares,
            }
        }
    
    async def get_analytics(
        self, 
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100
    ) -> SocialShareAnalytics:
        """Get comprehensive analytics for social sharing."""
        
        # Base query
        query = select(SocialShare)
        
        if user_id:
            query = query.where(SocialShare.user_id == user_id)
        
        if start_date:
            query = query.where(SocialShare.created_at >= start_date)
        
        if end_date:
            query = query.where(SocialShare.created_at <= end_date)
        
        # Get total shares and coins
        result = await self.db.execute(query)
        shares = result.scalars().all()
        
        total_shares = len(shares)
        total_coins = sum(share.coin_amount for share in shares)
        
        # Platform stats
        platform_stats = {}
        for share in shares:
            platform_stats[share.platform] = platform_stats.get(share.platform, 0) + 1
        
        # Content type stats
        content_type_stats = {}
        for share in shares:
            content_type_stats[share.content_type] = content_type_stats.get(share.content_type, 0) + 1
        
        # Daily stats (last 30 days)
        daily_query = select(SocialShareDailySummary).where(
            SocialShareDailySummary.date >= self._naive_utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        ).order_by(SocialShareDailySummary.date.desc()).limit(30)
        
        if user_id:
            daily_query = daily_query.where(SocialShareDailySummary.user_id == user_id)
        
        daily_result = await self.db.execute(daily_query)
        daily_summaries = daily_result.scalars().all()
        
        daily_stats = [
            {
                'date': summary.date.date().isoformat(),
                'shares': summary.total_shares,
                'coins': summary.coins_earned
            }
            for summary in daily_summaries
        ]
        
        # Top shared content
        content_query = (
            select(
                SocialShare.content_type,
                SocialShare.content_id,
                SocialShare.content_title,
                func.count(SocialShare.id).label('share_count')
            )
            .group_by(SocialShare.content_type, SocialShare.content_id, SocialShare.content_title)
            .order_by(func.count(SocialShare.id).desc())
            .limit(10)
        )
        
        if user_id:
            content_query = content_query.where(SocialShare.user_id == user_id)
        
        content_result = await self.db.execute(content_query)
        top_content = [
            {
                'content_type': row.content_type,
                'content_id': row.content_id,
                'content_title': row.content_title,
                'share_count': row.share_count
            }
            for row in content_result
        ]
        
        return SocialShareAnalytics(
            total_shares=total_shares,
            total_coins_awarded=total_coins,
            platform_stats=platform_stats,
            content_type_stats=content_type_stats,
            daily_stats=daily_stats,
            top_shared_content=top_content
        )
