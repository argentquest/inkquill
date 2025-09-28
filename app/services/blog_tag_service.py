"""Blog tag service for managing blog tags."""
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.models.blog_tag import BlogTag
from app.schemas.blog import BlogTagCreate

logger = logging.getLogger(__name__)


class BlogTagService:
    """Service for managing blog tags."""
    
    def _generate_slug(self, name: str) -> str:
        """Generate SEO-friendly slug from tag name."""
        import re
        slug = re.sub(r'[^\w\s-]', '', name.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        return slug
    
    async def get_or_create_tag(
        self, 
        db: AsyncSession, 
        tag_name: str
    ) -> BlogTag:
        """Get existing tag or create new one."""
        try:
            tag_name = tag_name.strip().lower()
            
            # Try to get existing tag
            result = await db.execute(
                select(BlogTag).where(BlogTag.name == tag_name)
            )
            tag = result.scalar_one_or_none()
            
            if not tag:
                # Create new tag
                slug = self._generate_slug(tag_name)
                tag = BlogTag(name=tag_name, slug=slug)
                db.add(tag)
                await db.flush()
                logger.info(f"Created new blog tag: {tag_name}")
            
            return tag
            
        except Exception as e:
            logger.error(f"Error getting/creating blog tag {tag_name}: {e}")
            raise
    
    async def get_popular_tags(
        self, 
        db: AsyncSession, 
        limit: int = 20
    ) -> List[BlogTag]:
        """Get most popular tags by usage count."""
        try:
            result = await db.execute(
                select(BlogTag)
                .where(BlogTag.usage_count > 0)
                .order_by(desc(BlogTag.usage_count))
                .limit(limit)
            )
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error getting popular tags: {e}")
            raise
    
    async def search_tags(
        self, 
        db: AsyncSession, 
        query: str, 
        limit: int = 10
    ) -> List[BlogTag]:
        """Search tags by name for auto-completion."""
        try:
            result = await db.execute(
                select(BlogTag)
                .where(BlogTag.name.ilike(f"%{query.lower()}%"))
                .order_by(desc(BlogTag.usage_count))
                .limit(limit)
            )
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error searching tags with query '{query}': {e}")
            raise
    
    async def get_all_tags(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[BlogTag]:
        """Get all tags with pagination."""
        try:
            result = await db.execute(
                select(BlogTag)
                .order_by(BlogTag.name)
                .offset(skip)
                .limit(limit)
            )
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error getting all tags: {e}")
            raise
    
    async def get_tag_by_slug(
        self, 
        db: AsyncSession, 
        slug: str
    ) -> Optional[BlogTag]:
        """Get tag by slug."""
        try:
            result = await db.execute(
                select(BlogTag).where(BlogTag.slug == slug)
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting tag by slug {slug}: {e}")
            raise
    
    async def update_tag_usage_counts(self, db: AsyncSession) -> None:
        """Update usage counts for all tags based on actual usage."""
        try:
            # This would typically be run as a background task
            from app.models.blog_tag import blog_post_tags
            
            # Update usage counts based on actual associations
            result = await db.execute(
                select(
                    blog_post_tags.c.tag_id,
                    func.count(blog_post_tags.c.post_id).label('count')
                )
                .group_by(blog_post_tags.c.tag_id)
            )
            
            usage_counts = {row.tag_id: row.count for row in result.fetchall()}
            
            # Update all tags
            tags_result = await db.execute(select(BlogTag))
            tags = tags_result.scalars().all()
            
            for tag in tags:
                tag.usage_count = usage_counts.get(tag.id, 0)
            
            await db.commit()
            logger.info("Updated tag usage counts")
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating tag usage counts: {e}")
            raise


# Create service instance
blog_tag_service = BlogTagService()