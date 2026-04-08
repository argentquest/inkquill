"""Blog comments API endpoints."""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db_session, get_current_user, get_current_active_user
from app.models.user import User
from app.services.blog_comment_service import blog_comment_service
from app.schemas.base import ApiResponse
from app.schemas.blog import (
    BlogCommentCreate, BlogCommentUpdate, BlogCommentRead,
    CommentStatus, BlogCommentWithReplies
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog", tags=["blog-comments"])


def _serialize_comment(comment) -> dict:
    """Provide internal router support for serialize comment."""
    return {
        "id": comment.id,
        "content": comment.content,
        "author_id": comment.author_id,
        "post_id": comment.post_id,
        "parent_comment_id": comment.parent_comment_id,
        "status": comment.status.value,
        "like_count": comment.like_count,
        "reply_count": comment.reply_count,
        "is_author_reply": comment.is_author_reply,
        "created_at": comment.created_at.isoformat(),
        "updated_at": comment.updated_at.isoformat(),
    }


@router.post("/posts/{post_id}/comments", status_code=status.HTTP_201_CREATED)
async def create_comment(
    post_id: int,
    comment_data: BlogCommentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new comment on a blog post."""
    try:
        # Check if the post exists
        from app.services.blog_service import blog_service
        post = await blog_service.get_post_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        # Check if comments are allowed on this post
        if not post.allow_comments:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Comments are not allowed on this post"
            )
        
        comment = await blog_comment_service.create_comment(
            db=db,
            comment_data=comment_data,
            user_id=current_user.id,
            post_id=post_id,
            parent_comment_id=comment_data.parent_comment_id
        )
        
        return ApiResponse.success_response(data=_serialize_comment(comment))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating comment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create comment"
        )


@router.get("/posts/{post_id}/comments")
async def get_post_comments(
    post_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("newest", pattern="^(newest|oldest|popular)$"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get comments for a blog post with nested replies."""
    try:
        comments = await blog_comment_service.get_post_comments(
            db=db,
            post_id=post_id,
            skip=skip,
            limit=limit,
            include_replies=True
        )
        
        # Convert to simple dict structure to avoid SQLAlchemy issues
        result = []
        for comment in comments:
            comment_dict = {
                "id": comment.id,
                "content": comment.content,
                "author_id": comment.author_id,
                "like_count": comment.like_count,
                "reply_count": comment.reply_count,
                "created_at": comment.created_at.isoformat(),
                "updated_at": comment.updated_at.isoformat(),
                "is_author_reply": comment.is_author_reply,
                "author": {
                    "id": comment.author.id if comment.author else None,
                    "username": comment.author.username if comment.author else "Unknown",
                    "display_name": comment.author.display_name if comment.author else None,
                    "profile_picture_url": getattr(comment.author, 'profile_picture_url', None) if comment.author else None
                },
                "replies": []
            }
            
            # Add replies if they exist
            if hasattr(comment, '_manual_replies'):
                for reply in comment._manual_replies:
                    reply_dict = {
                        "id": reply.id,
                        "content": reply.content,
                        "author_id": reply.author_id,
                        "like_count": reply.like_count,
                        "created_at": reply.created_at.isoformat(),
                        "updated_at": reply.updated_at.isoformat(),
                        "is_author_reply": reply.is_author_reply,
                        "author": {
                            "id": reply.author.id if reply.author else None,
                            "username": reply.author.username if reply.author else "Unknown",
                            "display_name": reply.author.display_name if reply.author else None,
                            "profile_picture_url": getattr(reply.author, 'profile_picture_url', None) if reply.author else None
                        }
                    }
                    comment_dict["replies"].append(reply_dict)
            
            result.append(comment_dict)
        
        # Sort based on preference
        if sort_by == "newest":
            result.sort(key=lambda x: x["created_at"], reverse=True)
        elif sort_by == "oldest":
            result.sort(key=lambda x: x["created_at"])
        elif sort_by == "popular":
            result.sort(key=lambda x: x["like_count"], reverse=True)
        
        return ApiResponse.success_response(data=result)
        
    except Exception as e:
        logger.error(f"Error getting comments for post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve comments"
        )


@router.put("/comments/{comment_id}")
async def update_comment(
    comment_id: int,
    comment_update: BlogCommentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update a comment (only by the author)."""
    try:
        comment = await blog_comment_service.get_comment(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        if comment.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own comments"
            )
        
        updated_comment = await blog_comment_service.update_comment(
            db=db,
            comment_id=comment_id,
            comment_data=comment_update,
            user_id=current_user.id
        )
        
        return ApiResponse.success_response(data=_serialize_comment(updated_comment))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update comment"
        )


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a comment (soft delete)."""
    try:
        comment = await blog_comment_service.get_comment(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Allow deletion by comment author or post author
        from app.services.blog_service import blog_service
        post = await blog_service.get_post_by_id(db, comment.post_id)
        
        if comment.author_id != current_user.id and post.author_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own comments or comments on your posts"
            )
        
        await blog_comment_service.delete_comment(
            db=db,
            comment_id=comment_id,
            user_id=current_user.id,
            is_admin=bool(current_user.is_admin or post.author_id == current_user.id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete comment"
        )


@router.post("/comments/{comment_id}/like", response_model=ApiResponse)
async def like_comment(
    comment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Like or unlike a comment."""
    try:
        # This would integrate with the blog_engagement_service
        # For now, we'll implement basic like functionality
        comment = await blog_comment_service.get_comment(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Toggle like (simplified implementation)
        # In a full implementation, you'd track individual user likes
        comment.like_count = (comment.like_count or 0) + 1
        await db.commit()
        
        return ApiResponse.success_response(
            data={"liked": True, "like_count": comment.like_count}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error liking comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to like comment"
        )


@router.post("/comments/{comment_id}/report", status_code=status.HTTP_201_CREATED)
async def report_comment(
    comment_id: int,
    reason: str = Query(..., min_length=10, max_length=500),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Report a comment for moderation."""
    try:
        comment = await blog_comment_service.get_comment(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found"
            )
        
        # Report the comment
        await blog_comment_service.report_comment(
            db=db,
            comment_id=comment_id,
            reporter_id=current_user.id,
            reason=reason
        )
        
        return ApiResponse.success_response(data={"message": "Comment reported successfully"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reporting comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to report comment"
        )


@router.put("/comments/{comment_id}/moderate")
async def moderate_comment(
    comment_id: int,
    status: CommentStatus,
    reason: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Moderate a comment (admin/moderator only)."""
    try:
        # Check if user is admin or moderator
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can moderate comments"
            )
        
        comment = await blog_comment_service.moderate_comment(
            db=db,
            comment_id=comment_id,
            moderator_id=current_user.id,
            status=status,
            reason=reason,
        )
        
        return ApiResponse.success_response(data=_serialize_comment(comment))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error moderating comment {comment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to moderate comment"
        )


@router.get("/comments/pending")
async def get_pending_comments(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get comments pending moderation (admin/moderator only)."""
    try:
        # Check if user is admin or moderator
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view pending comments"
            )
        
        comments = await blog_comment_service.get_pending_comments(
            db=db,
            skip=skip,
            limit=limit
        )
        
        # Convert to dict to avoid SQLAlchemy serialization issues
        result = []
        for comment in comments:
            comment_dict = {
                "id": comment.id,
                "content": comment.content,
                "author_id": comment.author_id,
                "post_id": comment.post_id,
                "parent_comment_id": comment.parent_comment_id,
                "status": comment.status.value,
                "like_count": comment.like_count,
                "reply_count": comment.reply_count,
                "is_author_reply": comment.is_author_reply,
                "created_at": comment.created_at.isoformat(),
                "updated_at": comment.updated_at.isoformat(),
                "author": {
                    "id": comment.author.id if comment.author else None,
                    "username": comment.author.username if comment.author else "Unknown",
                    "display_name": comment.author.display_name if comment.author else None,
                    "profile_picture_url": getattr(comment.author, 'profile_picture_url', None) if comment.author else None
                }
            }
            result.append(comment_dict)
        
        return ApiResponse.success_response(data=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pending comments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve pending comments"
        )
