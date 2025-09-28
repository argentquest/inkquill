"""Blog author profile service."""
import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.models.blog_author_profile import BlogAuthorProfile
from app.models.user import User
from app.schemas.blog import BlogAuthorProfileCreate, BlogAuthorProfileUpdate

logger = logging.getLogger(__name__)


class BlogAuthorService:
    """Service for managing blog author profiles."""
    
    async def get_or_create_profile(
        self,
        db: AsyncSession,
        user_id: int
    ) -> BlogAuthorProfile:
        """Get existing profile or create new one."""
        try:
            result = await db.execute(
                select(BlogAuthorProfile).where(BlogAuthorProfile.user_id == user_id)
            )
            profile = result.scalar_one_or_none()
            
            if not profile:
                profile = BlogAuthorProfile(user_id=user_id)
                db.add(profile)
                await db.commit()
                await db.refresh(profile)
                logger.info(f"Created blog author profile for user {user_id}")
            
            return profile
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error getting/creating author profile for user {user_id}: {e}")
            raise
    
    async def update_profile(
        self,
        db: AsyncSession,
        user_id: int,
        profile_data: BlogAuthorProfileUpdate
    ) -> Optional[BlogAuthorProfile]:
        """Update blog author profile."""
        try:
            profile = await self.get_or_create_profile(db, user_id)
            
            # Update fields
            update_data = profile_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(profile, field, value)
            
            await db.commit()
            await db.refresh(profile)
            
            logger.info(f"Updated blog author profile for user {user_id}")
            return profile
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating author profile for user {user_id}: {e}")
            raise
    
    async def update_stats(
        self,
        db: AsyncSession,
        user_id: int,
        stats: dict
    ) -> None:
        """Update cached statistics for author profile."""
        try:
            await db.execute(
                update(BlogAuthorProfile)
                .where(BlogAuthorProfile.user_id == user_id)
                .values(**stats)
            )
            await db.commit()
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating author stats for user {user_id}: {e}")
            raise


# Create service instance
blog_author_service = BlogAuthorService()