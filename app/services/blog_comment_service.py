"""Blog comment service for managing threaded comments."""
import logging
from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, func
from sqlalchemy.orm import selectinload

from app.models.blog_comment import BlogComment, CommentStatus
from app.models.blog_post import BlogPost
from app.schemas.blog import BlogCommentCreate, BlogCommentUpdate

logger = logging.getLogger(__name__)


class BlogCommentService:
    """Service for managing threaded blog comments."""
    
    async def create_comment(
        self,
        db: AsyncSession,
        comment_data: BlogCommentCreate,
        user_id: int,
        post_id: int,
        parent_comment_id: Optional[int] = None
    ) -> BlogComment:
        """Create a new comment or reply."""
        try:
            # Verify post exists and allows comments
            post_result = await db.execute(
                select(BlogPost).where(BlogPost.id == post_id)
            )
            post = post_result.scalar_one_or_none()
            
            if not post:
                raise ValueError("Blog post not found")
            
            if not post.allow_comments:
                raise ValueError("Comments are disabled for this post")
            
            # Verify parent comment exists if specified
            if parent_comment_id:
                parent_result = await db.execute(
                    select(BlogComment).where(
                        and_(
                            BlogComment.id == parent_comment_id,
                            BlogComment.post_id == post_id
                        )
                    )
                )
                parent_comment = parent_result.scalar_one_or_none()
                if not parent_comment:
                    raise ValueError("Parent comment not found")
            
            # Check if this is a reply from the post author
            is_author_reply = user_id == post.author_id
            
            # Create comment
            comment = BlogComment(
                post_id=post_id,
                author_id=user_id,
                parent_comment_id=parent_comment_id,
                content=comment_data.content,
                status=CommentStatus.APPROVED,  # Auto-approve for now
                is_author_reply=is_author_reply
            )
            
            db.add(comment)
            await db.flush()
            
            # Update post comment count
            post.comment_count += 1
            
            # Update parent comment reply count if this is a reply
            if parent_comment_id:
                await db.execute(
                    update(BlogComment)
                    .where(BlogComment.id == parent_comment_id)
                    .values(reply_count=BlogComment.reply_count + 1)
                )
            
            await db.commit()
            await db.refresh(comment)
            
            logger.info(f"Created comment on post {post_id} by user {user_id}")
            return comment
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating comment: {e}")
            raise
    
    async def get_post_comments(
        self,
        db: AsyncSession,
        post_id: int,
        skip: int = 0,
        limit: int = 50,
        include_replies: bool = True
    ) -> List[BlogComment]:
        """Get comments for a blog post with threading."""
        try:
            # Get top-level comments first
            top_level_query = (
                select(BlogComment)
                .where(and_(
                    BlogComment.post_id == post_id,
                    BlogComment.parent_comment_id.is_(None),
                    BlogComment.status == CommentStatus.APPROVED
                ))
                .options(selectinload(BlogComment.author))
                .order_by(BlogComment.created_at.asc())
                .offset(skip)
                .limit(limit)
            )
            
            result = await db.execute(top_level_query)
            top_level_comments = list(result.scalars().all())
            
            if include_replies and top_level_comments:
                # Get all replies for these top-level comments
                comment_ids = [comment.id for comment in top_level_comments]
                
                replies_query = (
                    select(BlogComment)
                    .where(and_(
                        BlogComment.parent_comment_id.in_(comment_ids),
                        BlogComment.status == CommentStatus.APPROVED
                    ))
                    .options(selectinload(BlogComment.author))
                    .order_by(BlogComment.created_at.asc())
                )
                
                replies_result = await db.execute(replies_query)
                all_replies = list(replies_result.scalars().all())
                
                # Group replies by parent comment ID
                replies_by_parent = {}
                for reply in all_replies:
                    parent_id = reply.parent_comment_id
                    if parent_id not in replies_by_parent:
                        replies_by_parent[parent_id] = []
                    replies_by_parent[parent_id].append(reply)
                
                # Manually set replies for each top-level comment
                # We'll use a custom attribute to avoid SQLAlchemy relationship issues
                for comment in top_level_comments:
                    # Explicitly set the replies list to avoid lazy loading
                    comment_replies = replies_by_parent.get(comment.id, [])
                    # Store replies in a way that won't trigger lazy loading
                    setattr(comment, '_manual_replies', comment_replies)
            
            return top_level_comments
            
        except Exception as e:
            logger.error(f"Error getting post comments: {e}")
            raise
    
    async def get_comment(
        self,
        db: AsyncSession,
        comment_id: int
    ) -> Optional[BlogComment]:
        """Get a single comment by ID."""
        try:
            result = await db.execute(
                select(BlogComment)
                .where(BlogComment.id == comment_id)
                .options(selectinload(BlogComment.author))
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting comment {comment_id}: {e}")
            raise
    
    async def update_comment(
        self,
        db: AsyncSession,
        comment_id: int,
        comment_data: BlogCommentUpdate,
        user_id: int
    ) -> Optional[BlogComment]:
        """Update comment (author only)."""
        try:
            result = await db.execute(
                select(BlogComment)
                .where(and_(
                    BlogComment.id == comment_id,
                    BlogComment.author_id == user_id
                ))
            )
            comment = result.scalar_one_or_none()
            
            if not comment:
                return None
            
            # Update content
            if comment_data.content:
                comment.content = comment_data.content
                comment.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(comment)
            
            logger.info(f"Updated comment {comment_id}")
            return comment
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating comment {comment_id}: {e}")
            raise
    
    async def delete_comment(
        self,
        db: AsyncSession,
        comment_id: int,
        user_id: int,
        is_admin: bool = False
    ) -> bool:
        """Delete comment (author or admin only)."""
        try:
            query = select(BlogComment).where(BlogComment.id == comment_id)
            
            if not is_admin:
                query = query.where(BlogComment.author_id == user_id)
            
            result = await db.execute(query)
            comment = result.scalar_one_or_none()
            
            if not comment:
                return False
            
            # Soft delete
            comment.status = CommentStatus.DELETED
            comment.deleted_at = datetime.utcnow()
            
            # Update post comment count
            await db.execute(
                update(BlogPost)
                .where(BlogPost.id == comment.post_id)
                .values(comment_count=BlogPost.comment_count - 1)
            )
            
            # Update parent reply count if this is a reply
            if comment.parent_comment_id:
                await db.execute(
                    update(BlogComment)
                    .where(BlogComment.id == comment.parent_comment_id)
                    .values(reply_count=BlogComment.reply_count - 1)
                )
            
            await db.commit()
            
            logger.info(f"Deleted comment {comment_id}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting comment {comment_id}: {e}")
            raise
    
    async def moderate_comment(
        self,
        db: AsyncSession,
        comment_id: int,
        status: CommentStatus,
        moderator_id: int,
        reason: Optional[str] = None
    ) -> Optional[BlogComment]:
        """Moderate comment (admin only)."""
        try:
            result = await db.execute(
                select(BlogComment).where(BlogComment.id == comment_id)
            )
            comment = result.scalar_one_or_none()
            
            if not comment:
                return None
            
            old_status = comment.status
            comment.status = status
            comment.updated_at = datetime.utcnow()
            
            # Update post comment count if status changed from/to approved
            if old_status == CommentStatus.APPROVED and status != CommentStatus.APPROVED:
                # Comment was approved, now it's not
                await db.execute(
                    update(BlogPost)
                    .where(BlogPost.id == comment.post_id)
                    .values(comment_count=BlogPost.comment_count - 1)
                )
            elif old_status != CommentStatus.APPROVED and status == CommentStatus.APPROVED:
                # Comment was not approved, now it is
                await db.execute(
                    update(BlogPost)
                    .where(BlogPost.id == comment.post_id)
                    .values(comment_count=BlogPost.comment_count + 1)
                )
            
            await db.commit()
            await db.refresh(comment)
            
            logger.info(f"Moderated comment {comment_id} to status {status}")
            return comment
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error moderating comment {comment_id}: {e}")
            raise
    
    async def report_comment(
        self,
        db: AsyncSession,
        comment_id: int,
        reporter_id: int,
        reason: str
    ) -> bool:
        """Report inappropriate comment."""
        try:
            # Verify comment exists
            result = await db.execute(
                select(BlogComment).where(BlogComment.id == comment_id)
            )
            comment = result.scalar_one_or_none()
            
            if not comment:
                return False
            
            # For now, just flag for moderation
            # In a full implementation, you'd create a reports table
            comment.status = CommentStatus.PENDING
            await db.commit()
            
            logger.info(f"Reported comment {comment_id} by user {reporter_id}: {reason}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error reporting comment {comment_id}: {e}")
            raise
    
    async def get_pending_comments(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 50
    ) -> List[BlogComment]:
        """Get comments pending moderation."""
        try:
            query = (
                select(BlogComment)
                .where(BlogComment.status == CommentStatus.PENDING)
                .options(selectinload(BlogComment.author))
                .order_by(BlogComment.created_at.desc())
                .offset(skip)
                .limit(limit)
            )
            
            result = await db.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error getting pending comments: {e}")
            raise


# Create service instance
blog_comment_service = BlogCommentService()
