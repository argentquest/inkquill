"""Blog analytics summary service."""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.blog_post import BlogPost, BlogPostStatus
from app.models.blog_comment import BlogComment, CommentStatus
from app.models.blog_subscription import BlogSubscription, SubscriptionStatus
from app.models.user import User

logger = logging.getLogger(__name__)


class BlogAnalyticsSummaryService:
    """Service for generating blog analytics summaries."""
    
    async def get_dashboard_summary(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get a comprehensive dashboard summary.
        
        Args:
            db: Database session
            user_id: User ID for user-specific stats, None for site-wide
            days: Number of days to look back
            
        Returns:
            Dictionary with analytics summary
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Build base queries
            post_query = select(BlogPost)
            comment_query = select(BlogComment)
            
            if user_id:
                post_query = post_query.where(BlogPost.author_id == user_id)
                # For comments, get comments on user's posts
                user_post_ids = await db.execute(
                    select(BlogPost.id).where(BlogPost.author_id == user_id)
                )
                user_post_ids = [row[0] for row in user_post_ids.fetchall()]
                if user_post_ids:
                    comment_query = comment_query.where(BlogComment.post_id.in_(user_post_ids))
                else:
                    comment_query = comment_query.where(False)  # No posts, no comments
            
            # Posts analytics
            posts_summary = await self._get_posts_summary(db, post_query, start_date, end_date)
            
            # Comments analytics
            comments_summary = await self._get_comments_summary(db, comment_query, start_date, end_date)
            
            # Subscription analytics (site-wide only for now)
            subscriptions_summary = {}
            if not user_id:
                subscriptions_summary = await self._get_subscriptions_summary(db, start_date, end_date)
            
            # Top performing content
            top_posts = await self._get_top_posts(db, user_id, days)
            
            # Recent activity
            recent_activity = await self._get_recent_activity(db, user_id, days=7)
            
            return {
                "period": {
                    "days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "posts": posts_summary,
                "comments": comments_summary,
                "subscriptions": subscriptions_summary,
                "top_posts": top_posts,
                "recent_activity": recent_activity,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {e}")
            return {"error": "Failed to generate analytics summary"}
    
    async def _get_posts_summary(
        self,
        db: AsyncSession,
        base_query: select,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get posts analytics summary."""
        try:
            # Total posts
            total_result = await db.execute(
                base_query.where(BlogPost.deleted_at.is_(None))
                .with_only_columns(func.count(BlogPost.id))
            )
            total_posts = total_result.scalar() or 0
            
            # Published posts
            published_result = await db.execute(
                base_query.where(
                    and_(
                        BlogPost.status == BlogPostStatus.PUBLISHED,
                        BlogPost.deleted_at.is_(None)
                    )
                ).with_only_columns(func.count(BlogPost.id))
            )
            published_posts = published_result.scalar() or 0
            
            # Draft posts
            draft_result = await db.execute(
                base_query.where(
                    and_(
                        BlogPost.status == BlogPostStatus.DRAFT,
                        BlogPost.deleted_at.is_(None)
                    )
                ).with_only_columns(func.count(BlogPost.id))
            )
            draft_posts = draft_result.scalar() or 0
            
            # Posts in period
            period_result = await db.execute(
                base_query.where(
                    and_(
                        BlogPost.created_at >= start_date,
                        BlogPost.created_at <= end_date,
                        BlogPost.deleted_at.is_(None)
                    )
                ).with_only_columns(func.count(BlogPost.id))
            )
            posts_in_period = period_result.scalar() or 0
            
            # Total views
            views_result = await db.execute(
                base_query.where(
                    and_(
                        BlogPost.status == BlogPostStatus.PUBLISHED,
                        BlogPost.deleted_at.is_(None)
                    )
                ).with_only_columns(func.sum(BlogPost.view_count))
            )
            total_views = views_result.scalar() or 0
            
            # Total likes
            likes_result = await db.execute(
                base_query.where(
                    and_(
                        BlogPost.status == BlogPostStatus.PUBLISHED,
                        BlogPost.deleted_at.is_(None)
                    )
                ).with_only_columns(func.sum(BlogPost.like_count))
            )
            total_likes = likes_result.scalar() or 0
            
            return {
                "total_posts": total_posts,
                "published_posts": published_posts,
                "draft_posts": draft_posts,
                "posts_in_period": posts_in_period,
                "total_views": total_views,
                "total_likes": total_likes,
                "avg_views_per_post": round(total_views / max(published_posts, 1), 1)
            }
            
        except Exception as e:
            logger.error(f"Error getting posts summary: {e}")
            return {}
    
    async def _get_comments_summary(
        self,
        db: AsyncSession,
        base_query: select,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get comments analytics summary."""
        try:
            # Total comments
            total_result = await db.execute(
                base_query.where(BlogComment.deleted_at.is_(None))
                .with_only_columns(func.count(BlogComment.id))
            )
            total_comments = total_result.scalar() or 0
            
            # Approved comments
            approved_result = await db.execute(
                base_query.where(
                    and_(
                        BlogComment.status == CommentStatus.APPROVED,
                        BlogComment.deleted_at.is_(None)
                    )
                ).with_only_columns(func.count(BlogComment.id))
            )
            approved_comments = approved_result.scalar() or 0
            
            # Pending comments
            pending_result = await db.execute(
                base_query.where(
                    and_(
                        BlogComment.status == CommentStatus.PENDING,
                        BlogComment.deleted_at.is_(None)
                    )
                ).with_only_columns(func.count(BlogComment.id))
            )
            pending_comments = pending_result.scalar() or 0
            
            # Comments in period
            period_result = await db.execute(
                base_query.where(
                    and_(
                        BlogComment.created_at >= start_date,
                        BlogComment.created_at <= end_date,
                        BlogComment.deleted_at.is_(None)
                    )
                ).with_only_columns(func.count(BlogComment.id))
            )
            comments_in_period = period_result.scalar() or 0
            
            return {
                "total_comments": total_comments,
                "approved_comments": approved_comments,
                "pending_comments": pending_comments,
                "comments_in_period": comments_in_period
            }
            
        except Exception as e:
            logger.error(f"Error getting comments summary: {e}")
            return {}
    
    async def _get_subscriptions_summary(
        self,
        db: AsyncSession,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Get subscriptions analytics summary."""
        try:
            # Total active subscriptions
            active_result = await db.execute(
                select(func.count(BlogSubscription.id))
                .where(BlogSubscription.status == SubscriptionStatus.ACTIVE)
            )
            active_subscriptions = active_result.scalar() or 0
            
            # New subscriptions in period
            new_result = await db.execute(
                select(func.count(BlogSubscription.id))
                .where(
                    and_(
                        BlogSubscription.created_at >= start_date,
                        BlogSubscription.created_at <= end_date
                    )
                )
            )
            new_subscriptions = new_result.scalar() or 0
            
            # Unsubscribes in period
            unsubscribed_result = await db.execute(
                select(func.count(BlogSubscription.id))
                .where(
                    and_(
                        BlogSubscription.unsubscribed_at >= start_date,
                        BlogSubscription.unsubscribed_at <= end_date
                    )
                )
            )
            unsubscribed = unsubscribed_result.scalar() or 0
            
            return {
                "active_subscriptions": active_subscriptions,
                "new_subscriptions": new_subscriptions,
                "unsubscribes": unsubscribed,
                "net_growth": new_subscriptions - unsubscribed
            }
            
        except Exception as e:
            logger.error(f"Error getting subscriptions summary: {e}")
            return {}
    
    async def _get_top_posts(
        self,
        db: AsyncSession,
        user_id: Optional[int],
        days: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Get top performing posts."""
        try:
            query = select(BlogPost).where(
                and_(
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.deleted_at.is_(None)
                )
            )
            
            if user_id:
                query = query.where(BlogPost.author_id == user_id)
            
            # Order by view count
            query = query.order_by(BlogPost.view_count.desc()).limit(limit)
            
            result = await db.execute(query)
            posts = result.scalars().all()
            
            return [
                {
                    "id": post.id,
                    "title": post.title,
                    "slug": post.slug,
                    "view_count": post.view_count or 0,
                    "like_count": post.like_count or 0,
                    "comment_count": post.comment_count or 0,
                    "published_at": post.published_at.isoformat() if post.published_at else None
                }
                for post in posts
            ]
            
        except Exception as e:
            logger.error(f"Error getting top posts: {e}")
            return []
    
    async def _get_recent_activity(
        self,
        db: AsyncSession,
        user_id: Optional[int],
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get recent activity."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            activities = []
            
            # Recent posts
            post_query = select(BlogPost).where(
                and_(
                    BlogPost.created_at >= start_date,
                    BlogPost.deleted_at.is_(None)
                )
            )
            
            if user_id:
                post_query = post_query.where(BlogPost.author_id == user_id)
            
            post_query = post_query.order_by(BlogPost.created_at.desc()).limit(10)
            
            post_result = await db.execute(post_query)
            recent_posts = post_result.scalars().all()
            
            for post in recent_posts:
                activities.append({
                    "type": "post_created",
                    "title": f"Created post: {post.title}",
                    "timestamp": post.created_at.isoformat(),
                    "data": {
                        "post_id": post.id,
                        "post_title": post.title,
                        "status": post.status.value
                    }
                })
            
            # Recent comments (on user's posts if user_id provided)
            comment_query = select(BlogComment).where(
                and_(
                    BlogComment.created_at >= start_date,
                    BlogComment.deleted_at.is_(None)
                )
            )
            
            if user_id:
                # Get comments on user's posts
                user_post_ids = await db.execute(
                    select(BlogPost.id).where(BlogPost.author_id == user_id)
                )
                user_post_ids = [row[0] for row in user_post_ids.fetchall()]
                if user_post_ids:
                    comment_query = comment_query.where(BlogComment.post_id.in_(user_post_ids))
                else:
                    comment_query = comment_query.where(False)
            
            comment_query = comment_query.options(selectinload(BlogComment.post)).order_by(BlogComment.created_at.desc()).limit(10)
            
            comment_result = await db.execute(comment_query)
            recent_comments = comment_result.scalars().all()
            
            for comment in recent_comments:
                activities.append({
                    "type": "comment_received",
                    "title": f"New comment on: {comment.post.title}",
                    "timestamp": comment.created_at.isoformat(),
                    "data": {
                        "comment_id": comment.id,
                        "post_id": comment.post_id,
                        "post_title": comment.post.title,
                        "author_id": comment.author_id
                    }
                })
            
            # Sort all activities by timestamp
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return activities[:20]  # Return top 20 recent activities
            
        except Exception as e:
            logger.error(f"Error getting recent activity: {e}")
            return []
    
    async def get_engagement_metrics(
        self,
        db: AsyncSession,
        user_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get detailed engagement metrics."""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Base query for posts
            post_query = select(BlogPost).where(
                and_(
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.deleted_at.is_(None)
                )
            )
            
            if user_id:
                post_query = post_query.where(BlogPost.author_id == user_id)
            
            # Get engagement data
            result = await db.execute(post_query)
            posts = result.scalars().all()
            
            if not posts:
                return {
                    "total_posts": 0,
                    "avg_engagement_rate": 0,
                    "top_engaging_posts": []
                }
            
            # Calculate engagement metrics
            total_views = sum(post.view_count or 0 for post in posts)
            total_likes = sum(post.like_count or 0 for post in posts)
            total_comments = sum(post.comment_count or 0 for post in posts)
            
            engagement_rate = ((total_likes + total_comments) / max(total_views, 1)) * 100
            
            # Top engaging posts
            engaging_posts = sorted(
                posts,
                key=lambda p: ((p.like_count or 0) + (p.comment_count or 0)) / max(p.view_count or 1, 1),
                reverse=True
            )[:5]
            
            return {
                "total_posts": len(posts),
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "avg_engagement_rate": round(engagement_rate, 2),
                "top_engaging_posts": [
                    {
                        "id": post.id,
                        "title": post.title,
                        "slug": post.slug,
                        "engagement_rate": round(((post.like_count or 0) + (post.comment_count or 0)) / max(post.view_count or 1, 1) * 100, 2),
                        "views": post.view_count or 0,
                        "likes": post.like_count or 0,
                        "comments": post.comment_count or 0
                    }
                    for post in engaging_posts
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting engagement metrics: {e}")
            return {"error": "Failed to get engagement metrics"}


# Global instance
blog_analytics_summary_service = BlogAnalyticsSummaryService()