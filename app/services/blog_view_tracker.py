"""Blog view tracking service."""
import logging
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, update
from sqlalchemy.dialects.postgresql import insert

from app.models.blog_post import BlogPost

logger = logging.getLogger(__name__)


class BlogViewTracker:
    """Service for tracking blog post views."""
    
    async def track_view(
        self,
        db: AsyncSession,
        post_id: int,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> bool:
        """
        Track a view for a blog post.
        
        Args:
            db: Database session
            post_id: ID of the blog post
            user_id: ID of the user viewing (if authenticated)
            ip_address: IP address of the viewer
            user_agent: User agent string
            
        Returns:
            True if view was tracked (not a duplicate), False if duplicate
        """
        try:
            # Check if this is a valid post
            post_result = await db.execute(
                select(BlogPost).where(BlogPost.id == post_id)
            )
            post = post_result.scalar_one_or_none()
            
            if not post:
                logger.warning(f"Attempted to track view for non-existent post {post_id}")
                return False
            
            # Simple view tracking - just increment the view count
            # In a more sophisticated system, you might:
            # 1. Create a separate blog_post_views table
            # 2. Track unique views per IP/user within time window
            # 3. Store additional analytics data
            
            # For now, just increment the view count
            await db.execute(
                update(BlogPost)
                .where(BlogPost.id == post_id)
                .values(
                    view_count=BlogPost.view_count + 1,
                    last_viewed_at=func.now()
                )
            )
            await db.commit()
            
            logger.debug(f"Tracked view for post {post_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking view for post {post_id}: {e}")
            await db.rollback()
            return False
    
    async def get_view_stats(
        self,
        db: AsyncSession,
        post_id: int
    ) -> dict:
        """
        Get view statistics for a blog post.
        
        Args:
            db: Database session
            post_id: ID of the blog post
            
        Returns:
            Dictionary with view statistics
        """
        try:
            post_result = await db.execute(
                select(BlogPost).where(BlogPost.id == post_id)
            )
            post = post_result.scalar_one_or_none()
            
            if not post:
                return {"error": "Post not found"}
            
            return {
                "post_id": post_id,
                "total_views": post.view_count or 0,
                "last_viewed_at": post.last_viewed_at,
                "views_today": 0,  # TODO: Implement when we have detailed view tracking
                "unique_viewers": 0  # TODO: Implement when we have detailed view tracking
            }
            
        except Exception as e:
            logger.error(f"Error getting view stats for post {post_id}: {e}")
            return {"error": "Failed to get view stats"}
    
    async def get_popular_posts(
        self,
        db: AsyncSession,
        limit: int = 10,
        days: int = 30
    ) -> list:
        """
        Get most popular posts by view count.
        
        Args:
            db: Database session
            limit: Number of posts to return
            days: Number of days to look back (not implemented yet)
            
        Returns:
            List of popular posts
        """
        try:
            # For now, just get posts ordered by total view count
            # TODO: Implement time-based filtering when we have detailed view tracking
            result = await db.execute(
                select(BlogPost)
                .where(
                    and_(
                        BlogPost.status == "published",
                        BlogPost.deleted_at.is_(None)
                    )
                )
                .order_by(BlogPost.view_count.desc())
                .limit(limit)
            )
            
            posts = result.scalars().all()
            return [
                {
                    "id": post.id,
                    "title": post.title,
                    "slug": post.slug,
                    "view_count": post.view_count or 0,
                    "published_at": post.published_at,
                    "author_id": post.author_id
                }
                for post in posts
            ]
            
        except Exception as e:
            logger.error(f"Error getting popular posts: {e}")
            return []


# Global instance
blog_view_tracker = BlogViewTracker()