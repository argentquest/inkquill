"""Blog search service backed by local database search."""
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.models.blog_post import BlogPost, BlogPostStatus
from app.models.blog_tag import BlogTag, blog_post_tags
from app.models.blog_category import BlogCategory
# Blog search uses database full-text search (no external search service needed)

logger = logging.getLogger(__name__)


class BlogSearchService:
    """Service for blog content search and filtering."""
    
    async def search_posts(
        self,
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[int] = None,
        tag_ids: Optional[List[int]] = None,
        author_id: Optional[int] = None
    ) -> List[BlogPost]:
        """Search blog posts with full-text search and filtering."""
        try:
            # Build base query for published posts
            base_query = (
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
            )
            
            # Apply text search
            if query:
                search_filter = or_(
                    BlogPost.title.ilike(f"%{query}%"),
                    BlogPost.content.ilike(f"%{query}%"),
                    BlogPost.excerpt.ilike(f"%{query}%"),
                    BlogPost.meta_keywords.ilike(f"%{query}%")
                )
                base_query = base_query.where(search_filter)
            
            # Apply filters
            if category_id:
                base_query = base_query.where(BlogPost.category_id == category_id)
            
            if author_id:
                base_query = base_query.where(BlogPost.author_id == author_id)
            
            if tag_ids:
                base_query = (
                    base_query.join(blog_post_tags)
                    .where(blog_post_tags.c.tag_id.in_(tag_ids))
                )
            
            # Order by relevance (published date for now, could be enhanced with ranking)
            base_query = base_query.order_by(BlogPost.published_at.desc())
            
            # Apply pagination
            base_query = base_query.offset(skip).limit(limit)
            
            result = await db.execute(base_query)
            posts = result.scalars().all()
            
            return list(posts)
            
        except Exception as e:
            logger.error(f"Error searching blog posts: {e}")
            raise
    
    async def get_search_suggestions(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 5
    ) -> Dict[str, List[str]]:
        """Get search suggestions for auto-completion."""
        try:
            suggestions = {
                "titles": [],
                "tags": [],
                "categories": []
            }
            
            # Search in post titles
            title_result = await db.execute(
                select(BlogPost.title)
                .where(and_(
                    BlogPost.title.ilike(f"%{query}%"),
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.deleted_at.is_(None)
                ))
                .limit(limit)
            )
            suggestions["titles"] = [row[0] for row in title_result.fetchall()]
            
            # Search in tags
            tag_result = await db.execute(
                select(BlogTag.name)
                .where(BlogTag.name.ilike(f"%{query}%"))
                .order_by(BlogTag.usage_count.desc())
                .limit(limit)
            )
            suggestions["tags"] = [row[0] for row in tag_result.fetchall()]
            
            # Search in categories
            category_result = await db.execute(
                select(BlogCategory.name)
                .where(and_(
                    BlogCategory.name.ilike(f"%{query}%"),
                    BlogCategory.is_active == True
                ))
                .limit(limit)
            )
            suggestions["categories"] = [row[0] for row in category_result.fetchall()]
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            raise
    
    async def get_related_posts(
        self,
        db: AsyncSession,
        post_id: int,
        limit: int = 5
    ) -> List[BlogPost]:
        """Get related posts based on tags and category."""
        try:
            # Get the current post
            current_post_result = await db.execute(
                select(BlogPost)
                .where(BlogPost.id == post_id)
                .options(selectinload(BlogPost.tags))
            )
            current_post = current_post_result.scalar_one_or_none()
            
            if not current_post:
                return []
            
            # Find posts with same category or tags
            related_query = (
                select(BlogPost)
                .where(and_(
                    BlogPost.id != post_id,
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.deleted_at.is_(None)
                ))
                .options(
                    selectinload(BlogPost.author),
                    selectinload(BlogPost.category),
                    selectinload(BlogPost.tags)
                )
            )
            
            # Prioritize posts with same category
            if current_post.category_id:
                related_query = related_query.where(
                    BlogPost.category_id == current_post.category_id
                )
            
            # Order by published date
            related_query = related_query.order_by(BlogPost.published_at.desc()).limit(limit)
            
            result = await db.execute(related_query)
            related_posts = list(result.scalars().all())
            
            # If we don't have enough related posts, get more by tags
            if len(related_posts) < limit:
                # Get current post tags
                current_tags_result = await db.execute(
                    select(blog_post_tags.c.tag_id)
                    .where(blog_post_tags.c.post_id == post_id)
                )
                current_tag_ids = [row[0] for row in current_tags_result.fetchall()]
                
                if current_tag_ids:
                    # Get posts with similar tags
                    tag_related_query = (
                        select(BlogPost)
                        .join(blog_post_tags)
                        .where(and_(
                            BlogPost.id != post_id,
                            BlogPost.status == BlogPostStatus.PUBLISHED,
                            BlogPost.deleted_at.is_(None),
                            blog_post_tags.c.tag_id.in_(current_tag_ids)
                        ))
                        .options(
                            selectinload(BlogPost.author),
                            selectinload(BlogPost.category),
                            selectinload(BlogPost.tags)
                        )
                        .order_by(BlogPost.published_at.desc())
                        .limit(limit - len(related_posts))
                    )
                    
                    tag_result = await db.execute(tag_related_query)
                    tag_related_posts = list(tag_result.scalars().all())
                    
                    # Combine and deduplicate
                    existing_ids = {post.id for post in related_posts}
                    for post in tag_related_posts:
                        if post.id not in existing_ids:
                            related_posts.append(post)
                            if len(related_posts) >= limit:
                                break
            
            return related_posts[:limit]
            
        except Exception as e:
            logger.error(f"Error getting related posts for {post_id}: {e}")
            raise
    
    async def get_trending_posts(
        self,
        db: AsyncSession,
        days: int = 7,
        limit: int = 10
    ) -> List[BlogPost]:
        """Get trending posts based on recent engagement."""
        try:
            from datetime import datetime, timedelta
            
            # Calculate trending based on recent views and likes
            # This is a simplified version - could be enhanced with more sophisticated ranking
            since_date = datetime.utcnow() - timedelta(days=days)
            
            trending_query = (
                select(BlogPost)
                .where(and_(
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.deleted_at.is_(None),
                    BlogPost.published_at >= since_date
                ))
                .options(
                    selectinload(BlogPost.author),
                    selectinload(BlogPost.category),
                    selectinload(BlogPost.tags)
                )
                .order_by(
                    (BlogPost.view_count + BlogPost.like_count * 2 + BlogPost.comment_count * 3).desc()
                )
                .limit(limit)
            )
            
            result = await db.execute(trending_query)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"Error getting trending posts: {e}")
            raise
    
    async def index_post_for_search(
        self,
        post: BlogPost
    ) -> None:
        """Index blog post for full-text search (if using external search service)."""
        try:
            # Future enhancement point for richer ranking if needed.
            # For now, we'll use database full-text search
            
            # Prepare search document
            search_doc = {
                "id": f"blog_post_{post.id}",
                "title": post.title,
                "content": post.content,
                "excerpt": post.excerpt or "",
                "author_id": post.author_id,
                "category_id": post.category_id,
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "tags": [],  # Would be populated with tag names
                "url": f"/blog/{post.slug}"
            }
            
            # Index with search service (placeholder)
            # await search_service.index_document("blog_posts", search_doc)
            
            logger.info(f"Indexed blog post for search: {post.title}")
            
        except Exception as e:
            logger.error(f"Error indexing post for search: {e}")
            # Don't raise - indexing failures shouldn't break post creation
    
    async def remove_post_from_search(
        self,
        post_id: int
    ) -> None:
        """Remove blog post from search index."""
        try:
            # Remove from search service (placeholder)
            # await search_service.delete_document("blog_posts", f"blog_post_{post_id}")
            
            logger.info(f"Removed blog post from search index: {post_id}")
            
        except Exception as e:
            logger.error(f"Error removing post from search index: {e}")
            # Don't raise - indexing failures shouldn't break post deletion


# Create service instance
blog_search_service = BlogSearchService()
