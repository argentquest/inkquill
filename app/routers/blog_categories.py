"""Blog category API endpoints."""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.services.blog_category_service import blog_category_service
from app.schemas.blog import BlogCategoryCreate, BlogCategoryUpdate, BlogCategoryRead
from app.schemas.base import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog/categories", tags=["blog-categories"])


@router.get("/", response_model=ApiResponse)
async def get_blog_categories(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db_session)
):
    """Get all blog categories."""
    try:
        categories = await blog_category_service.get_categories(db, active_only=active_only)
        return categories
    except Exception as e:
        logger.error(f"Error getting blog categories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve blog categories"
        )


@router.get("/{category_id}", response_model=ApiResponse)
async def get_blog_category(
    category_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get blog category by ID."""
    try:
        category = await blog_category_service.get_category_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog category not found"
            )
        return category
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting blog category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve blog category"
        )


@router.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_blog_category(
    category_data: BlogCategoryCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new blog category (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        category = await blog_category_service.create_category(db, category_data)
        return category
    except Exception as e:
        logger.error(f"Error creating blog category: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create blog category"
        )


@router.put("/{category_id}", response_model=ApiResponse)
async def update_blog_category(
    category_id: int,
    category_data: BlogCategoryUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update blog category (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        category = await blog_category_service.update_category(db, category_id, category_data)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog category not found"
            )
        return category
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating blog category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update blog category"
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog_category(
    category_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete blog category (admin only)."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    try:
        success = await blog_category_service.delete_category(db, category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog category not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting blog category {category_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete blog category"
        )