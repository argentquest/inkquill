"""CRUD operations for forum categories."""
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.forum import ForumCategory, ForumThread
from app.schemas.forum import ForumCategoryCreate, ForumCategoryUpdate


async def get_forum_category(db: AsyncSession, category_id: int) -> Optional[ForumCategory]:
    """Get a single forum category by ID."""
    result = await db.execute(
        select(ForumCategory)
        .where(ForumCategory.id == category_id)
        .options(selectinload(ForumCategory.threads))
    )
    return result.scalar_one_or_none()


async def get_forum_category_by_slug(db: AsyncSession, slug: str) -> Optional[ForumCategory]:
    """Get a single forum category by slug."""
    result = await db.execute(
        select(ForumCategory)
        .where(ForumCategory.slug == slug)
        .options(selectinload(ForumCategory.threads))
    )
    return result.scalar_one_or_none()


async def get_forum_categories(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False
) -> List[ForumCategory]:
    """Get all forum categories with pagination."""
    query = select(ForumCategory).options(
        selectinload(ForumCategory.threads).selectinload(ForumThread.user),
        selectinload(ForumCategory.threads).selectinload(ForumThread.last_post_by)
    )
    
    if not include_inactive:
        query = query.where(ForumCategory.is_active == True)
    
    query = query.order_by(ForumCategory.sort_order, ForumCategory.name)
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_forum_category(
    db: AsyncSession,
    category: ForumCategoryCreate
) -> ForumCategory:
    """Create a new forum category."""
    # Generate slug from name if not provided
    slug = category.slug or category.name.lower().replace(" ", "-").replace("_", "-")
    
    # Ensure slug is unique
    existing = await get_forum_category_by_slug(db, slug)
    if existing:
        # Add a number suffix to make it unique
        counter = 1
        while existing:
            new_slug = f"{slug}-{counter}"
            existing = await get_forum_category_by_slug(db, new_slug)
            counter += 1
        slug = new_slug
    
    db_category = ForumCategory(
        name=category.name,
        description=category.description,
        slug=slug,
        sort_order=category.sort_order or 0,
        is_active=category.is_active if category.is_active is not None else True,
        icon=category.icon
    )
    
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def update_forum_category(
    db: AsyncSession,
    category_id: int,
    category_update: ForumCategoryUpdate
) -> Optional[ForumCategory]:
    """Update an existing forum category."""
    db_category = await get_forum_category(db, category_id)
    if not db_category:
        return None
    
    update_data = category_update.model_dump(exclude_unset=True)
    
    # If updating slug, ensure it's unique
    if "slug" in update_data and update_data["slug"] != db_category.slug:
        existing = await get_forum_category_by_slug(db, update_data["slug"])
        if existing and existing.id != category_id:
            raise ValueError("Slug already exists")
    
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def delete_forum_category(db: AsyncSession, category_id: int) -> bool:
    """Delete a forum category."""
    db_category = await get_forum_category(db, category_id)
    if not db_category:
        return False

    for thread in list(db_category.threads):
        await db.delete(thread)

    await db.delete(db_category)
    await db.commit()
    return True


async def get_category_thread_count(db: AsyncSession, category_id: int) -> int:
    """Get the count of threads in a category."""
    result = await db.execute(
        select(func.count())
        .select_from(ForumThread)
        .where(ForumThread.category_id == category_id)
        .where(ForumThread.is_deleted == False)
    )
    return result.scalar() or 0
