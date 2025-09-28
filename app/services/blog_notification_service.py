"""Blog notification service for managing subscriptions and notifications."""
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.blog_follow import BlogFollow
from app.models.blog_post import BlogPost
from app.models.user import User
from app.services.email_service import email_service

logger = logging.getLogger(__name__)


class BlogNotificationService:
    """Service for managing blog notifications and subscriptions."""
    
    async def notify_followers_of_new_post(
        self,
        db: AsyncSession,
        post: BlogPost
    ) -> None:
        """Notify followers when author publishes a new post."""
        try:
            # Get all followers of the author
            followers_result = await db.execute(
                select(BlogFollow, User)
                .join(User, BlogFollow.follower_id == User.id)
                .where(and_(
                    BlogFollow.author_id == post.author_id,
                    BlogFollow.notification_enabled == True,
                    User.is_active == True
                ))
            )
            followers = followers_result.fetchall()
            
            if not followers:
                return
            
            # Get author info
            author_result = await db.execute(
                select(User).where(User.id == post.author_id)
            )
            author = author_result.scalar_one_or_none()
            
            if not author:
                return
            
            # Send email notifications
            for follow, follower in followers:
                try:
                    await self._send_new_post_email(
                        follower_email=follower.email,
                        follower_name=follower.display_name or follower.username,
                        author_name=author.display_name or author.username,
                        post_title=post.title,
                        post_slug=post.slug,
                        post_excerpt=post.excerpt
                    )
                except Exception as e:
                    logger.error(f"Failed to send notification to {follower.email}: {e}")
            
            logger.info(f"Sent new post notifications to {len(followers)} followers")
            
        except Exception as e:
            logger.error(f"Error notifying followers of new post: {e}")
    
    async def _send_new_post_email(
        self,
        follower_email: str,
        follower_name: str,
        author_name: str,
        post_title: str,
        post_slug: str,
        post_excerpt: Optional[str] = None
    ) -> None:
        """Send new post notification email."""
        try:
            subject = f"New post from {author_name}: {post_title}"
            
            # Create email content
            excerpt_text = post_excerpt or "Check out this new blog post!"
            post_url = f"https://yoursite.com/blog/{post_slug}"  # Replace with actual domain
            
            html_content = f"""
            <h2>New Blog Post from {author_name}</h2>
            <h3>{post_title}</h3>
            <p>{excerpt_text}</p>
            <p><a href="{post_url}">Read the full post</a></p>
            <hr>
            <p><small>You're receiving this because you follow {author_name}. 
            <a href="{post_url}">Unsubscribe</a></small></p>
            """
            
            text_content = f"""
            New Blog Post from {author_name}
            
            {post_title}
            
            {excerpt_text}
            
            Read the full post: {post_url}
            
            You're receiving this because you follow {author_name}.
            """
            
            await email_service.send_email(
                to_email=follower_email,
                subject=subject,
                html_content=html_content,
                text_content=text_content
            )
            
        except Exception as e:
            logger.error(f"Error sending new post email: {e}")
            raise


# Create service instance
blog_notification_service = BlogNotificationService()