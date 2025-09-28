"""Blog category service for managing blog categories."""
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func

from app.models.blog_category import BlogCategory
from app.schemas.blog import BlogCategoryCreate, BlogCategoryUpdate

logger = logging.getLogger(__name__)


class BlogCategoryService:
    """Service for managing blog categories."""
    
    async def create_category(
        self, 
        db: AsyncSession, 
        category_data: BlogCategoryCreate
    ) -> BlogCategory:
        """Create a new blog category."""
        try:
            category = BlogCategory(**category_data.dict())
            db.add(category)
            await db.commit()
            await db.refresh(category)
            
            logger.info(f"Created blog category: {category.name}")
            return category
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating blog category: {e}")
            raise
    
    async def get_categories(
        self, 
        db: AsyncSession, 
        active_only: bool = True
    ) -> List[BlogCategory]:
        """Get all blog categories."""
        try:
            query = select(BlogCategory).order_by(BlogCategory.display_order, BlogCategory.name)
            
            if active_only:
                query = query.where(BlogCategory.is_active == True)
            
            result = await db.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error getting blog categories: {e}")
            raise
    
    async def get_category_by_id(
        self, 
        db: AsyncSession, 
        category_id: int
    ) -> Optional[BlogCategory]:
        """Get blog category by ID."""
        try:
            result = await db.execute(
                select(BlogCategory).where(BlogCategory.id == category_id)
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting blog category {category_id}: {e}")
            raise
    
    async def get_category_by_slug(
        self, 
        db: AsyncSession, 
        slug: str
    ) -> Optional[BlogCategory]:
        """Get blog category by slug."""
        try:
            result = await db.execute(
                select(BlogCategory).where(BlogCategory.slug == slug)
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting blog category by slug {slug}: {e}")
            raise
    
    async def update_category(
        self, 
        db: AsyncSession, 
        category_id: int, 
        category_data: BlogCategoryUpdate
    ) -> Optional[BlogCategory]:
        """Update blog category."""
        try:
            result = await db.execute(
                select(BlogCategory).where(BlogCategory.id == category_id)
            )
            category = result.scalar_one_or_none()
            
            if not category:
                return None
            
            # Update fields
            update_data = category_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(category, field, value)
            
            await db.commit()
            await db.refresh(category)
            
            logger.info(f"Updated blog category: {category.name}")
            return category
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating blog category {category_id}: {e}")
            raise
    
    async def delete_category(
        self, 
        db: AsyncSession, 
        category_id: int
    ) -> bool:
        """Delete blog category."""
        try:
            result = await db.execute(
                select(BlogCategory).where(BlogCategory.id == category_id)
            )
            category = result.scalar_one_or_none()
            
            if not category:
                return False
            
            await db.delete(category)
            await db.commit()
            
            logger.info(f"Deleted blog category: {category.name}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error deleting blog category {category_id}: {e}")
            raise


# Create service instance
blog_category_service = BlogCategoryService()