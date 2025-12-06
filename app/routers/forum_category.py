"""API endpoints for forum categories."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db_session, get_current_user
from app.models.user import User
from app.schemas.base import ApiResponse
from app.schemas.forum import (
    ForumCategoryCreate,
    ForumCategoryUpdate,
    ForumCategoryResponse
)
from app.crud import forum_category as crud_category

router = APIRouter(prefix="/api/forum/categories", tags=["forum_categories"])


@router.get("/", response_model=ApiResponse)
async def get_categories(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db_session)
):
    """Get all forum categories."""
    categories = await crud_category.get_forum_categories(
        db, skip=skip, limit=limit, include_inactive=include_inactive
    )
    
    # Add thread counts
    response_categories = []
    for category in categories:
        category_dict = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "slug": category.slug,
            "sort_order": category.sort_order,
            "is_active": category.is_active,
            "icon": category.icon,
            "thread_count": len([t for t in category.threads if not t.is_deleted]),
            "created_at": category.created_at,
            "updated_at": category.updated_at
        }
        response_categories.append(ForumCategoryResponse(**category_dict))
    
    return response_categories


@router.get("/{category_id}", response_model=ApiResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific forum category."""
    category = await crud_category.get_forum_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return ForumCategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        slug=category.slug,
        sort_order=category.sort_order,
        is_active=category.is_active,
        icon=category.icon,
        thread_count=len([t for t in category.threads if not t.is_deleted]),
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@router.get("/slug/{slug}", response_model=ApiResponse)
async def get_category_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific forum category by slug."""
    category = await crud_category.get_forum_category_by_slug(db, slug)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return ForumCategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        slug=category.slug,
        sort_order=category.sort_order,
        is_active=category.is_active,
        icon=category.icon,
        thread_count=len([t for t in category.threads if not t.is_deleted]),
        created_at=category.created_at,
        updated_at=category.updated_at
    )


@router.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: ForumCategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new forum category. (Admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create categories"
        )
    
    try:
        new_category = await crud_category.create_forum_category(db, category)
        return ForumCategoryResponse(
            id=new_category.id,
            name=new_category.name,
            description=new_category.description,
            slug=new_category.slug,
            sort_order=new_category.sort_order,
            is_active=new_category.is_active,
            icon=new_category.icon,
            thread_count=0,
            created_at=new_category.created_at,
            updated_at=new_category.updated_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{category_id}", response_model=ApiResponse)
async def update_category(
    category_id: int,
    category_update: ForumCategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update a forum category. (Admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update categories"
        )
    
    try:
        updated_category = await crud_category.update_forum_category(
            db, category_id, category_update
        )
        if not updated_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        return ForumCategoryResponse(
            id=updated_category.id,
            name=updated_category.name,
            description=updated_category.description,
            slug=updated_category.slug,
            sort_order=updated_category.sort_order,
            is_active=updated_category.is_active,
            icon=updated_category.icon,
            thread_count=len([t for t in updated_category.threads if not t.is_deleted]),
            created_at=updated_category.created_at,
            updated_at=updated_category.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a forum category. (Admin only)"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete categories"
        )
    
    success = await crud_category.delete_forum_category(db, category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return None