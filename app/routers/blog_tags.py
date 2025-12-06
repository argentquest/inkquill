"""Blog tag API endpoints."""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db_session
from app.services.blog_tag_service import blog_tag_service
from app.schemas.blog import BlogTagRead
from app.schemas.base import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog/tags", tags=["blog-tags"])


@router.get("/", response_model=ApiResponse)
async def get_blog_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all blog tags."""
    try:
        tags = await blog_tag_service.get_all_tags(db, skip=skip, limit=limit)
        return tags
    except Exception as e:
        logger.error(f"Error getting blog tags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve blog tags"
        )


@router.get("/popular", response_model=ApiResponse)
async def get_popular_blog_tags(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db_session)
):
    """Get most popular blog tags."""
    try:
        tags = await blog_tag_service.get_popular_tags(db, limit=limit)
        return tags
    except Exception as e:
        logger.error(f"Error getting popular blog tags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve popular blog tags"
        )


@router.get("/search", response_model=ApiResponse)
async def search_blog_tags(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db_session)
):
    """Search blog tags for auto-completion."""
    try:
        tags = await blog_tag_service.search_tags(db, q, limit=limit)
        return tags
    except Exception as e:
        logger.error(f"Error searching blog tags: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search blog tags"
        )


@router.get("/{slug}", response_model=ApiResponse)
async def get_blog_tag_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get blog tag by slug."""
    try:
        tag = await blog_tag_service.get_tag_by_slug(db, slug)
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog tag not found"
            )
        return tag
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting blog tag by slug {slug}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve blog tag"
        )