"""Blog analytics service for tracking and reporting."""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from decimal import Decimal

from app.models.blog_view import BlogView
from app.models.blog_post import BlogPost
from app.models.blog_analytics_summary import BlogAnalyticsSummary
from app.models.blog_like import BlogLike
from app.models.blog_comment import BlogComment

logger = logging.getLogger(__name__)


class BlogAnalyticsService:
    """Service for blog analytics and reporting."""
    
    async def track_view(
        self,
        db: AsyncSession,
        post_id: int,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        referrer_url: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> bool:
        """Track blog post view."""
        try:
            view = BlogView(
                post_id=post_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer_url=referrer_url,
                session_id=session_id
            )
            db.add(view)
            await db.commit()
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error tracking view: {e}")
            return False
    
    async def get_post_analytics(
        self,
        db: AsyncSession,
        post_id: int,
        user_id: int,
        date_range: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """Get detailed analytics for a specific post."""
        try:
            # Verify post ownership
            post_result = await db.execute(
                select(BlogPost).where(
                    and_(BlogPost.id == post_id, BlogPost.author_id == user_id)
                )
            )
            post = post_result.scalar_one_or_none()
            
            if not post:
                raise ValueError("Post not found or access denied")
            
            # Base query for views
            view_query = select(BlogView).where(BlogView.post_id == post_id)
            
            if date_range:
                start_date, end_date = date_range
                view_query = view_query.where(
                    and_(
                        BlogView.created_at >= start_date,
                        BlogView.created_at <= end_date
                    )
                )
            
            # Get view metrics
            total_views_result = await db.execute(
                select(func.count(BlogView.id)).select_from(view_query.subquery())
            )
            total_views = total_views_result.scalar() or 0
            
            unique_views_result = await db.execute(
                select(func.count(func.distinct(BlogView.user_id)))
                .select_from(view_query.subquery())
                .where(BlogView.user_id.is_not(None))
            )
            unique_views = unique_views_result.scalar() or 0
            
            # Get engagement metrics
            likes_result = await db.execute(
                select(func.count(BlogLike.id))
                .where(BlogLike.post_id == post_id)
            )
            total_likes = likes_result.scalar() or 0
            
            comments_result = await db.execute(
                select(func.count(BlogComment.id))
                .where(BlogComment.post_id == post_id)
            )
            total_comments = comments_result.scalar() or 0
            
            # Calculate engagement rate
            engagement_rate = 0
            if total_views > 0:
                engagement_rate = ((total_likes + total_comments) / total_views) * 100
            
            return {
                "post_id": post_id,
                "title": post.title,
                "total_views": total_views,
                "unique_views": unique_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "engagement_rate": round(engagement_rate, 2),
                "published_at": post.published_at,
                "reading_time_minutes": post.reading_time_minutes
            }
            
        except Exception as e:
            logger.error(f"Error getting post analytics: {e}")
            raise
    
    async def get_author_dashboard(
        self,
        db: AsyncSession,
        author_id: int,
        date_range: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """Get author dashboard with all posts analytics."""
        try:
            # Get author's posts
            posts_query = select(BlogPost).where(
                and_(
                    BlogPost.author_id == author_id,
                    BlogPost.deleted_at.is_(None)
                )
            )
            
            if date_range:
                start_date, end_date = date_range
                posts_query = posts_query.where(
                    and_(
                        BlogPost.created_at >= start_date,
                        BlogPost.created_at <= end_date
                    )
                )
            
            posts_result = await db.execute(posts_query)
            posts = list(posts_result.scalars().all())
            
            if not posts:
                return {
                    "author_id": author_id,
                    "total_posts": 0,
                    "total_views": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "avg_engagement_rate": 0,
                    "top_posts": []
                }
            
            post_ids = [post.id for post in posts]
            
            # Get aggregated metrics
            total_views = sum(post.view_count for post in posts)
            total_likes = sum(post.like_count for post in posts)
            total_comments = sum(post.comment_count for post in posts)
            
            # Calculate average engagement rate
            avg_engagement_rate = 0
            if total_views > 0:
                avg_engagement_rate = ((total_likes + total_comments) / total_views) * 100
            
            # Get top performing posts
            top_posts = sorted(
                posts,
                key=lambda p: p.view_count + (p.like_count * 2) + (p.comment_count * 3),
                reverse=True
            )[:5]
            
            top_posts_data = [
                {
                    "id": post.id,
                    "title": post.title,
                    "slug": post.slug,
                    "views": post.view_count,
                    "likes": post.like_count,
                    "comments": post.comment_count,
                    "published_at": post.published_at
                }
                for post in top_posts
            ]
            
            return {
                "author_id": author_id,
                "total_posts": len(posts),
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "avg_engagement_rate": round(avg_engagement_rate, 2),
                "top_posts": top_posts_data
            }
            
        except Exception as e:
            logger.error(f"Error getting author dashboard: {e}")
            raise
    
    async def get_trending_posts(
        self,
        db: AsyncSession,
        time_period: str = "week",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get trending blog posts."""
        try:
            # Calculate date range
            now = datetime.utcnow()
            if time_period == "day":
                since_date = now - timedelta(days=1)
            elif time_period == "week":
                since_date = now - timedelta(days=7)
            elif time_period == "month":
                since_date = now - timedelta(days=30)
            else:
                since_date = now - timedelta(days=7)
            
            # Get trending posts based on recent engagement
            trending_query = (
                select(BlogPost)
                .where(and_(
                    BlogPost.published_at >= since_date,
                    BlogPost.deleted_at.is_(None)
                ))
                .order_by(
                    desc(BlogPost.view_count + BlogPost.like_count * 2 + BlogPost.comment_count * 3)
                )
                .limit(limit)
            )
            
            result = await db.execute(trending_query)
            posts = list(result.scalars().all())
            
            trending_data = [
                {
                    "id": post.id,
                    "title": post.title,
                    "slug": post.slug,
                    "author_id": post.author_id,
                    "views": post.view_count,
                    "likes": post.like_count,
                    "comments": post.comment_count,
                    "published_at": post.published_at,
                    "trending_score": post.view_count + (post.like_count * 2) + (post.comment_count * 3)
                }
                for post in posts
            ]
            
            return trending_data
            
        except Exception as e:
            logger.error(f"Error getting trending posts: {e}")
            raise
    
    async def generate_daily_summary(
        self,
        db: AsyncSession,
        post_id: int,
        target_date: date
    ) -> Optional[BlogAnalyticsSummary]:
        """Generate daily analytics summary for a post."""
        try:
            # Check if summary already exists
            existing_result = await db.execute(
                select(BlogAnalyticsSummary).where(
                    and_(
                        BlogAnalyticsSummary.post_id == post_id,
                        BlogAnalyticsSummary.date == target_date
                    )
                )
            )
            existing_summary = existing_result.scalar_one_or_none()
            
            if existing_summary:
                return existing_summary
            
            # Calculate metrics for the day
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())
            
            # Views
            views_result = await db.execute(
                select(
                    func.count(BlogView.id).label('total_views'),
                    func.count(func.distinct(BlogView.user_id)).label('unique_views')
                )
                .where(and_(
                    BlogView.post_id == post_id,
                    BlogView.created_at >= start_datetime,
                    BlogView.created_at <= end_datetime
                ))
            )
            view_metrics = views_result.first()
            
            # Likes
            likes_result = await db.execute(
                select(func.count(BlogLike.id))
                .where(and_(
                    BlogLike.post_id == post_id,
                    BlogLike.created_at >= start_datetime,
                    BlogLike.created_at <= end_datetime
                ))
            )
            new_likes = likes_result.scalar() or 0
            
            # Comments
            comments_result = await db.execute(
                select(func.count(BlogComment.id))
                .where(and_(
                    BlogComment.post_id == post_id,
                    BlogComment.created_at >= start_datetime,
                    BlogComment.created_at <= end_datetime
                ))
            )
            new_comments = comments_result.scalar() or 0
            
            # Create summary
            summary = BlogAnalyticsSummary(
                post_id=post_id,
                date=target_date,
                unique_views=view_metrics.unique_views or 0,
                total_views=view_metrics.total_views or 0,
                new_likes=new_likes,
                new_comments=new_comments,
                avg_read_time=0,  # Would need to track reading time
                bounce_rate=Decimal('0.00'),  # Would need to calculate
                social_shares=0  # Would need to track social shares
            )
            
            db.add(summary)
            await db.commit()
            await db.refresh(summary)
            
            return summary
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error generating daily summary: {e}")
            raise


# Create service instance
blog_analytics_service = BlogAnalyticsService()