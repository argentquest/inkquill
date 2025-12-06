"""Blog search API endpoints."""
import logging
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db_session
from app.services.blog_search_service import blog_search_service
from app.schemas.blog import BlogPostRead
from app.schemas.base import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog/search", tags=["blog-search"])


@router.get("/", response_model=ApiResponse)
async def search_blog_posts(
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: int = Query(None),
    tag_ids: str = Query(None, description="Comma-separated tag IDs"),
    author_id: int = Query(None),
    db: AsyncSession = Depends(get_db_session)
):
    """Search blog posts with full-text search and filtering."""
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
        
        posts = await blog_search_service.search_posts(
            db=db,
            query=q,
            skip=skip,
            limit=limit,
            category_id=category_id,
            tag_ids=tag_id_list,
            author_id=author_id
        )
        return posts
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching blog posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search blog posts"
        )


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, List[str]]:
    """Get search suggestions for auto-completion."""
    try:
        suggestions = await blog_search_service.get_search_suggestions(db, q, limit)
        return suggestions
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get search suggestions"
        )


@router.get("/related/{post_id}", response_model=ApiResponse)
async def get_related_posts(
    post_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db_session)
):
    """Get related posts based on tags and category."""
    try:
        posts = await blog_search_service.get_related_posts(db, post_id, limit)
        return posts
    except Exception as e:
        logger.error(f"Error getting related posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get related posts"
        )


@router.get("/trending", response_model=ApiResponse)
async def get_trending_posts(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db_session)
):
    """Get trending posts based on recent engagement."""
    try:
        posts = await blog_search_service.get_trending_posts(db, days, limit)
        return posts
    except Exception as e:
        logger.error(f"Error getting trending posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trending posts"
        )