"""Blog engagement service for likes and follows."""
import logging
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update, and_, func

from app.models.blog_like import BlogLike
from app.models.blog_follow import BlogFollow
from app.models.blog_post import BlogPost
from app.models.blog_view import BlogView

logger = logging.getLogger(__name__)


class BlogEngagementService:
    """Service for managing blog engagement (likes, follows, views)."""
    
    async def like_post(
        self,
        db: AsyncSession,
        post_id: int,
        user_id: int
    ) -> bool:
        """Like or unlike a blog post. Returns True if liked, False if unliked."""
        try:
            # Check if already liked
            existing_like_result = await db.execute(
                select(BlogLike).where(
                    and_(BlogLike.post_id == post_id, BlogLike.user_id == user_id)
                )
            )
            existing_like = existing_like_result.scalar_one_or_none()
            
            if existing_like:
                # Unlike - remove the like
                await db.delete(existing_like)
                
                # Decrease like count
                await db.execute(
                    update(BlogPost)
                    .where(BlogPost.id == post_id)
                    .values(like_count=BlogPost.like_count - 1)
                )
                
                await db.commit()
                logger.info(f"User {user_id} unliked post {post_id}")
                return False
            else:
                # Like - create new like
                like = BlogLike(post_id=post_id, user_id=user_id)
                db.add(like)
                
                # Increase like count
                await db.execute(
                    update(BlogPost)
                    .where(BlogPost.id == post_id)
                    .values(like_count=BlogPost.like_count + 1)
                )
                
                await db.commit()
                logger.info(f"User {user_id} liked post {post_id}")
                return True
                
        except Exception as e:
            await db.rollback()
            logger.error(f"Error toggling like for post {post_id} by user {user_id}: {e}")
            raise
    
    async def is_post_liked(
        self,
        db: AsyncSession,
        post_id: int,
        user_id: int
    ) -> bool:
        """Check if user has liked a post."""
        try:
            result = await db.execute(
                select(BlogLike).where(
                    and_(BlogLike.post_id == post_id, BlogLike.user_id == user_id)
                )
            )
            return result.scalar_one_or_none() is not None
            
        except Exception as e:
            logger.error(f"Error checking if post {post_id} is liked by user {user_id}: {e}")
            raise
    
    async def follow_author(
        self,
        db: AsyncSession,
        author_id: int,
        follower_id: int
    ) -> bool:
        """Follow or unfollow a blog author. Returns True if followed, False if unfollowed."""
        try:
            if author_id == follower_id:
                raise ValueError("Cannot follow yourself")
            
            # Check if already following
            existing_follow_result = await db.execute(
                select(BlogFollow).where(
                    and_(BlogFollow.author_id == author_id, BlogFollow.follower_id == follower_id)
                )
            )
            existing_follow = existing_follow_result.scalar_one_or_none()
            
            if existing_follow:
                # Unfollow - remove the follow
                await db.delete(existing_follow)
                
                # Decrease follower count in author profile
                from app.models.blog_author_profile import BlogAuthorProfile
                await db.execute(
                    update(BlogAuthorProfile)
                    .where(BlogAuthorProfile.user_id == author_id)
                    .values(follower_count=BlogAuthorProfile.follower_count - 1)
                )
                
                await db.commit()
                logger.info(f"User {follower_id} unfollowed author {author_id}")
                return False
            else:
                # Follow - create new follow
                follow = BlogFollow(
                    author_id=author_id, 
                    follower_id=follower_id,
                    notification_enabled=True
                )
                db.add(follow)
                
                # Increase follower count in author profile
                from app.models.blog_author_profile import BlogAuthorProfile
                await db.execute(
                    update(BlogAuthorProfile)
                    .where(BlogAuthorProfile.user_id == author_id)
                    .values(follower_count=BlogAuthorProfile.follower_count + 1)
                )
                
                await db.commit()
                logger.info(f"User {follower_id} followed author {author_id}")
                return True
                
        except Exception as e:
            await db.rollback()
            logger.error(f"Error toggling follow for author {author_id} by user {follower_id}: {e}")
            raise
    
    async def is_following_author(
        self,
        db: AsyncSession,
        author_id: int,
        follower_id: int
    ) -> bool:
        """Check if user is following an author."""
        try:
            result = await db.execute(
                select(BlogFollow).where(
                    and_(BlogFollow.author_id == author_id, BlogFollow.follower_id == follower_id)
                )
            )
            return result.scalar_one_or_none() is not None
            
        except Exception as e:
            logger.error(f"Error checking if user {follower_id} follows author {author_id}: {e}")
            raise
    
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
        """Track blog post view for analytics."""
        try:
            # Create view record
            view = BlogView(
                post_id=post_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer_url=referrer_url,
                session_id=session_id
            )
            db.add(view)
            
            # Increment view count on post
            await db.execute(
                update(BlogPost)
                .where(BlogPost.id == post_id)
                .values(view_count=BlogPost.view_count + 1)
            )
            
            await db.commit()
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error tracking view for post {post_id}: {e}")
            # Don't raise - view tracking failures shouldn't break the request
            return False
    
    async def get_engagement_metrics(
        self,
        db: AsyncSession,
        post_id: int
    ) -> dict:
        """Get engagement metrics for a post."""
        try:
            # Get post with current counts
            post_result = await db.execute(
                select(BlogPost).where(BlogPost.id == post_id)
            )
            post = post_result.scalar_one_or_none()
            
            if not post:
                return {}
            
            # Get additional metrics
            unique_views_result = await db.execute(
                select(func.count(func.distinct(BlogView.user_id)))
                .where(and_(BlogView.post_id == post_id, BlogView.user_id.is_not(None)))
            )
            unique_views = unique_views_result.scalar() or 0
            
            return {
                "post_id": post_id,
                "view_count": post.view_count,
                "unique_views": unique_views,
                "like_count": post.like_count,
                "comment_count": post.comment_count,
                "engagement_rate": (post.like_count + post.comment_count) / max(post.view_count, 1) * 100
            }
            
        except Exception as e:
            logger.error(f"Error getting engagement metrics for post {post_id}: {e}")
            raise
    
    async def get_user_engagement_summary(
        self,
        db: AsyncSession,
        user_id: int
    ) -> dict:
        """Get engagement summary for a user's posts."""
        try:
            # Get total metrics for user's posts
            metrics_result = await db.execute(
                select(
                    func.count(BlogPost.id).label('total_posts'),
                    func.sum(BlogPost.view_count).label('total_views'),
                    func.sum(BlogPost.like_count).label('total_likes'),
                    func.sum(BlogPost.comment_count).label('total_comments')
                )
                .where(and_(
                    BlogPost.author_id == user_id,
                    BlogPost.deleted_at.is_(None)
                ))
            )
            metrics = metrics_result.first()
            
            # Get follower count
            follower_count_result = await db.execute(
                select(func.count(BlogFollow.id))
                .where(BlogFollow.author_id == user_id)
            )
            follower_count = follower_count_result.scalar() or 0
            
            total_posts = metrics.total_posts or 0
            total_views = metrics.total_views or 0
            total_likes = metrics.total_likes or 0
            total_comments = metrics.total_comments or 0
            
            return {
                "user_id": user_id,
                "total_posts": total_posts,
                "total_views": total_views,
                "total_likes": total_likes,
                "total_comments": total_comments,
                "follower_count": follower_count,
                "avg_views_per_post": total_views / max(total_posts, 1),
                "avg_engagement_per_post": (total_likes + total_comments) / max(total_posts, 1),
                "overall_engagement_rate": (total_likes + total_comments) / max(total_views, 1) * 100
            }
            
        except Exception as e:
            logger.error(f"Error getting user engagement summary for user {user_id}: {e}")
            raise


# Create service instance
blog_engagement_service = BlogEngagementService()