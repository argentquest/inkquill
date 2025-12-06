"""Blog API endpoints."""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db_session, get_current_active_user, get_current_user
from app.models.user import User
from app.services.blog_service import blog_service
from app.schemas.base import ApiResponse
from app.schemas.blog import (
    BlogPostCreate, BlogPostUpdate, BlogPostRead, BlogPostSummary,
    BlogCategoryRead, BlogTagRead
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog", tags=["blog"])


@router.post("/posts", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_blog_post(
    post_data: BlogPostCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new blog post."""
    try:
        post = await blog_service.create_post(db, post_data, current_user.id)
        return post
    except Exception as e:
        logger.error(f"Error creating blog post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create blog post"
        )


@router.get("/posts", response_model=ApiResponse)
async def get_blog_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = Query(None),
    tag_ids: Optional[str] = Query(None, description="Comma-separated tag IDs"),
    search: Optional[str] = Query(None, min_length=1),
    author_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db_session)
):
    """Get published blog posts with filtering and pagination."""
    try:
        # Parse tag IDs
        tag_id_list = None
        if tag_ids:
            try:
                tag_id_list = [int(tid.strip()) for tid in tag_ids.split(",") if tid.strip()]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tag IDs format"
                )
        
        posts = await blog_service.get_published_posts(
            db=db,
            skip=skip,
            limit=limit,
            category_id=category_id,
            tag_ids=tag_id_list,
            search_query=search,
            author_id=author_id
        )
        return posts
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting blog posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve blog posts"
        )


@router.get("/posts/{slug}", response_model=ApiResponse)
async def get_blog_post(
    slug: str,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get blog post by slug."""
    try:
        post = await blog_service.get_post_by_slug(db, slug)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        # Check if post is published or user is author/admin
        if post.status.value != "published" and (not current_user or (current_user.id != post.author_id and not getattr(current_user, 'is_admin', False))):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        # Track view for analytics
        from app.services.blog_view_tracker import blog_view_tracker
        await blog_view_tracker.track_view(
            db=db,
            post_id=post.id,
            user_id=current_user.id if current_user else None
        )
        
        return post
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting blog post {slug}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve blog post"
        )


@router.put("/posts/{post_id}", response_model=ApiResponse)
async def update_blog_post(
    post_id: int,
    post_data: BlogPostUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update blog post."""
    try:
        post = await blog_service.update_post(db, post_id, post_data, current_user)
        return post
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating blog post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update blog post"
        )


@router.post("/posts/{post_id}/publish", response_model=ApiResponse)
async def publish_blog_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Publish a draft blog post."""
    try:
        post = await blog_service.publish_post(db, post_id, current_user)
        return post
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error publishing blog post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to publish blog post"
        )


@router.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Soft delete blog post."""
    try:
        success = await blog_service.soft_delete_post(db, post_id, current_user)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found or access denied"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting blog post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete blog post"
        )


@router.get("/my-posts", response_model=ApiResponse)
async def get_my_blog_posts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    include_drafts: bool = Query(True),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user's blog posts."""
    try:
        posts = await blog_service.get_user_posts(
            db=db,
            user_id=current_user.id,
            include_drafts=include_drafts,
            skip=skip,
            limit=limit
        )
        return posts
    except Exception as e:
        logger.error(f"Error getting user posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user posts"
        )