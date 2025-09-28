"""Blog service for managing blog posts and related operations."""
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models.blog_post import BlogPost, BlogPostStatus
from app.models.blog_category import BlogCategory
from app.models.blog_tag import BlogTag, blog_post_tags
from app.models.user import User
from app.schemas.blog import BlogPostCreate, BlogPostUpdate, BlogPostRead

logger = logging.getLogger(__name__)


class BlogService:
    """Core blog management service."""
    
    def _generate_slug(self, title: str, existing_slugs: List[str] = None) -> str:
        """Generate SEO-friendly slug from title."""
        import re
        
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', title.lower())
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        
        # Handle duplicates
        if existing_slugs and slug in existing_slugs:
            counter = 1
            base_slug = slug
            while f"{base_slug}-{counter}" in existing_slugs:
                counter += 1
            slug = f"{base_slug}-{counter}"
        
        return slug
    
    async def create_post(
        self, 
        db: AsyncSession, 
        post_data: BlogPostCreate, 
        user_id: int
    ) -> BlogPost:
        """Create a new blog post with draft status."""
        try:
            # Generate unique slug
            existing_slugs_result = await db.execute(
                select(BlogPost.slug).where(BlogPost.deleted_at.is_(None))
            )
            existing_slugs = [row[0] for row in existing_slugs_result.fetchall()]
            slug = self._generate_slug(post_data.title, existing_slugs)
            
            # Create blog post
            blog_post = BlogPost(
                title=post_data.title,
                slug=slug,
                content=post_data.content,
                excerpt=post_data.excerpt,
                featured_image_url=post_data.featured_image_url,
                author_id=user_id,
                category_id=post_data.category_id,
                meta_title=post_data.meta_title,
                meta_description=post_data.meta_description,
                meta_keywords=post_data.meta_keywords,
                allow_comments=post_data.allow_comments,
                is_ai_generated=post_data.is_ai_generated or False,
                is_featured=post_data.is_featured or False,
                status=BlogPostStatus.DRAFT
            )
            
            db.add(blog_post)
            await db.flush()
            
            # Handle tags
            if post_data.tags:
                await self._handle_post_tags(db, blog_post.id, post_data.tags)
            
            await db.commit()
            await db.refresh(blog_post)
            
            logger.info(f"Created blog post: {blog_post.title} (ID: {blog_post.id})")
            return blog_post
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating blog post: {e}")
            raise
    
    async def publish_post(
        self, 
        db: AsyncSession, 
        post_id: int, 
        current_user: 'User'
    ) -> BlogPost:
        """Publish a draft blog post."""
        try:
            # Get post and verify ownership or admin access
            result = await db.execute(
                select(BlogPost)
                .where(BlogPost.id == post_id)
                .options(selectinload(BlogPost.tags))
            )
            post = result.scalar_one_or_none()
            
            if not post:
                raise ValueError("Blog post not found")
            
            # Check permissions: owner or admin can publish
            if post.author_id != current_user.id and not getattr(current_user, 'is_admin', False):
                raise ValueError("Blog post not found or access denied")
            
            if post.status == BlogPostStatus.PUBLISHED:
                return post
            
            # Update post status and published timestamp
            post.status = BlogPostStatus.PUBLISHED
            post.published_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(post)
            
            logger.info(f"Published blog post: {post.title} (ID: {post.id})")
            return post
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error publishing blog post {post_id}: {e}")
            raise
    
    async def get_published_posts(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 20,
        category_id: Optional[int] = None,
        tag_ids: Optional[List[int]] = None,
        search_query: Optional[str] = None,
        author_id: Optional[int] = None,
        author_ids: Optional[List[int]] = None
    ) -> List[BlogPost]:
        """Get published blog posts with filtering and pagination."""
        try:
            query = (
                select(BlogPost)
                .where(and_(
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.deleted_at.is_(None)
                ))
                .options(
                    selectinload(BlogPost.author),
                    selectinload(BlogPost.category),
                    selectinload(BlogPost.tags)
                )
                .order_by(BlogPost.published_at.desc())
            )
            
            # Apply filters
            if category_id:
                query = query.where(BlogPost.category_id == category_id)
            
            if author_id:
                query = query.where(BlogPost.author_id == author_id)
            
            if author_ids:
                query = query.where(BlogPost.author_id.in_(author_ids))
            
            if search_query:
                search_filter = or_(
                    BlogPost.title.ilike(f"%{search_query}%"),
                    BlogPost.content.ilike(f"%{search_query}%"),
                    BlogPost.excerpt.ilike(f"%{search_query}%")
                )
                query = query.where(search_filter)
            
            if tag_ids:
                query = (
                    query.join(blog_post_tags)
                    .where(blog_post_tags.c.tag_id.in_(tag_ids))
                )
            
            # Apply pagination
            query = query.offset(skip).limit(limit)
            
            result = await db.execute(query)
            posts = result.scalars().all()
            
            return list(posts)
            
        except Exception as e:
            logger.error(f"Error getting published posts: {e}")
            raise
    
    async def get_post_by_id(
        self, 
        db: AsyncSession, 
        post_id: int
    ) -> Optional[BlogPost]:
        """Get blog post by ID."""
        try:
            result = await db.execute(
                select(BlogPost)
                .where(and_(
                    BlogPost.id == post_id,
                    BlogPost.deleted_at.is_(None)
                ))
                .options(
                    selectinload(BlogPost.author),
                    selectinload(BlogPost.category),
                    selectinload(BlogPost.tags)
                )
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting post by ID {post_id}: {e}")
            raise

    async def get_post_by_slug(
        self, 
        db: AsyncSession, 
        slug: str
    ) -> Optional[BlogPost]:
        """Get blog post by SEO-friendly slug."""
        try:
            result = await db.execute(
                select(BlogPost)
                .where(and_(
                    BlogPost.slug == slug,
                    BlogPost.deleted_at.is_(None)
                ))
                .options(
                    selectinload(BlogPost.author),
                    selectinload(BlogPost.category),
                    selectinload(BlogPost.tags)
                )
            )
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error getting post by slug {slug}: {e}")
            raise
    
    async def update_post(
        self, 
        db: AsyncSession, 
        post_id: int, 
        post_data: BlogPostUpdate, 
        current_user: 'User'
    ) -> BlogPost:
        """Update blog post with version tracking."""
        try:
            # Get post and verify ownership or admin access
            result = await db.execute(
                select(BlogPost)
                .where(BlogPost.id == post_id)
                .options(selectinload(BlogPost.tags))
            )
            post = result.scalar_one_or_none()
            
            if not post:
                raise ValueError("Blog post not found")
            
            # Check permissions: owner or admin can edit
            if post.author_id != current_user.id and not getattr(current_user, 'is_admin', False):
                raise ValueError("Blog post not found or access denied")
            
            # Update fields
            if post_data.title and post_data.title != post.title:
                # Generate new slug if title changed
                existing_slugs_result = await db.execute(
                    select(BlogPost.slug).where(
                        and_(BlogPost.id != post_id, BlogPost.deleted_at.is_(None))
                    )
                )
                existing_slugs = [row[0] for row in existing_slugs_result.fetchall()]
                post.slug = self._generate_slug(post_data.title, existing_slugs)
                post.title = post_data.title
            
            if post_data.content is not None:
                post.content = post_data.content
            if post_data.excerpt is not None:
                post.excerpt = post_data.excerpt
            if post_data.featured_image_url is not None:
                post.featured_image_url = post_data.featured_image_url
            if post_data.category_id is not None:
                post.category_id = post_data.category_id
            if post_data.meta_title is not None:
                post.meta_title = post_data.meta_title
            if post_data.meta_description is not None:
                post.meta_description = post_data.meta_description
            if post_data.allow_comments is not None:
                post.allow_comments = post_data.allow_comments
            if post_data.is_featured is not None:
                post.is_featured = post_data.is_featured
            if post_data.status is not None:
                post.status = post_data.status
                # Update published_at timestamp when publishing
                if post_data.status == BlogPostStatus.PUBLISHED and post.published_at is None:
                    post.published_at = datetime.utcnow()
            
            # Handle tags update
            if post_data.tags is not None:
                await self._handle_post_tags(db, post.id, post_data.tags)
            
            post.updated_at = datetime.utcnow()
            
            await db.commit()
            await db.refresh(post)
            
            logger.info(f"Updated blog post: {post.title} (ID: {post.id})")
            return post
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error updating blog post {post_id}: {e}")
            raise
    
    async def soft_delete_post(
        self, 
        db: AsyncSession, 
        post_id: int, 
        current_user: 'User'
    ) -> bool:
        """Soft delete blog post."""
        try:
            result = await db.execute(
                select(BlogPost)
                .where(BlogPost.id == post_id)
            )
            post = result.scalar_one_or_none()
            
            if not post:
                return False
            
            # Check permissions: owner or admin can delete
            if post.author_id != current_user.id and not getattr(current_user, 'is_admin', False):
                return False
            
            post.deleted_at = datetime.utcnow()
            await db.commit()
            
            logger.info(f"Soft deleted blog post: {post.title} (ID: {post.id})")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Error soft deleting blog post {post_id}: {e}")
            raise
    
    async def get_user_posts(
        self,
        db: AsyncSession,
        user_id: int,
        include_drafts: bool = True,
        skip: int = 0,
        limit: int = 20
    ) -> List[BlogPost]:
        """Get all posts for a specific user."""
        try:
            query = (
                select(BlogPost)
                .where(and_(
                    BlogPost.author_id == user_id,
                    BlogPost.deleted_at.is_(None)
                ))
                .options(
                    selectinload(BlogPost.category),
                    selectinload(BlogPost.tags)
                )
                .order_by(BlogPost.updated_at.desc())
            )
            
            if not include_drafts:
                query = query.where(BlogPost.status == BlogPostStatus.PUBLISHED)
            
            query = query.offset(skip).limit(limit)
            
            result = await db.execute(query)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error getting user posts for user {user_id}: {e}")
            raise
    
    async def _handle_post_tags(
        self, 
        db: AsyncSession, 
        post_id: int, 
        tag_names: List[str]
    ) -> None:
        """Handle post tags - create new tags if needed and associate with post."""
        try:
            # Remove existing tag associations
            await db.execute(
                delete(blog_post_tags).where(blog_post_tags.c.post_id == post_id)
            )
            
            for tag_name in tag_names:
                tag_name = tag_name.strip().lower()
                if not tag_name:
                    continue
                
                # Get or create tag
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
                
                # Create association
                await db.execute(
                    blog_post_tags.insert().values(
                        post_id=post_id,
                        tag_id=tag.id
                    )
                )
                
                # Update tag usage count
                tag.usage_count += 1
            
        except Exception as e:
            logger.error(f"Error handling post tags: {e}")
            raise
    
    async def get_trending_posts(
        self,
        db: AsyncSession,
        limit: int = 10,
        days_back: int = 30
    ) -> List[BlogPost]:
        """Get trending posts based on weighted algorithm considering views, likes, comments, and recency."""
        try:
            from datetime import datetime, timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            
            # Weighted trending algorithm:
            # Score = (view_count * 1.0) + (like_count * 2.0) + (comment_count * 3.0) + (recency_boost)
            # Recency boost: newer posts get higher score (max 50 points for posts < 7 days old)
            
            query = select(
                BlogPost,
                (
                    (BlogPost.view_count * 1.0) +
                    (BlogPost.like_count * 2.0) +
                    (BlogPost.comment_count * 3.0) +
                    # Recency boost: 50 points for posts < 7 days, decreasing linearly
                    func.greatest(
                        0,
                        50 - (func.extract('epoch', func.now() - BlogPost.published_at) / 86400 / 7 * 50)
                    )
                ).label('trending_score')
            ).where(
                and_(
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.published_at >= cutoff_date,
                    BlogPost.deleted_at.is_(None)
                )
            ).options(
                selectinload(BlogPost.author),
                selectinload(BlogPost.category),
                selectinload(BlogPost.tags)
            ).order_by(
                func.desc('trending_score')
            ).limit(limit)
            
            result = await db.execute(query)
            posts_with_scores = result.all()
            
            # Extract just the posts
            trending_posts = [row[0] for row in posts_with_scores]
            
            logger.info(f"Retrieved {len(trending_posts)} trending posts")
            return trending_posts
            
        except Exception as e:
            logger.error(f"Error getting trending posts: {e}")
            # Fallback to most viewed posts
            try:
                result = await db.execute(
                    select(BlogPost)
                    .where(and_(
                        BlogPost.status == BlogPostStatus.PUBLISHED,
                        BlogPost.deleted_at.is_(None)
                    ))
                    .options(
                        selectinload(BlogPost.author),
                        selectinload(BlogPost.category),
                        selectinload(BlogPost.tags)
                    )
                    .order_by(BlogPost.view_count.desc())
                    .limit(limit)
                )
                return list(result.scalars().all())
            except Exception as fallback_error:
                logger.error(f"Error in trending posts fallback: {fallback_error}")
                return []


# Create service instance
blog_service = BlogService()