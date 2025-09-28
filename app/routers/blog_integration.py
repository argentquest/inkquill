"""Blog integration with storytelling features API endpoints."""
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.models.blog_post import BlogPost, BlogPostStatus
from app.models.blog_content_link import BlogContentLink
from app.models.story import Story
from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.models.world import World
from app.services.blog_service import blog_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog/integration", tags=["blog-integration"])


@router.post("/link-content")
async def link_blog_to_content(
    blog_post_id: int,
    content_id: int,
    content_type: str = Query(..., regex="^(story|character|location|lore_item|world)$"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Link a blog post to storytelling content."""
    try:
        # Verify blog post ownership
        post_result = await db.execute(
            select(BlogPost).where(
                and_(
                    BlogPost.id == blog_post_id,
                    BlogPost.author_id == current_user.id
                )
            )
        )
        post = post_result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found or access denied"
            )
        
        # Verify content exists and user has access
        content = None
        if content_type == "story":
            content_result = await db.execute(
                select(Story).where(
                    and_(
                        Story.id == content_id,
                        Story.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
        elif content_type == "character":
            content_result = await db.execute(
                select(Character).where(
                    and_(
                        Character.id == content_id,
                        Character.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
        elif content_type == "location":
            content_result = await db.execute(
                select(Location).where(
                    and_(
                        Location.id == content_id,
                        Location.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
        elif content_type == "lore_item":
            content_result = await db.execute(
                select(LoreItem).where(
                    and_(
                        LoreItem.id == content_id,
                        LoreItem.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
        elif content_type == "world":
            content_result = await db.execute(
                select(World).where(
                    and_(
                        World.id == content_id,
                        World.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{content_type.title()} not found or access denied"
            )
        
        # Check if link already exists
        existing_link_result = await db.execute(
            select(BlogContentLink).where(
                and_(
                    BlogContentLink.post_id == blog_post_id,
                    BlogContentLink.content_type == content_type,
                    BlogContentLink.content_id == content_id
                )
            )
        )
        existing_link = existing_link_result.scalar_one_or_none()
        
        if existing_link:
            return {
                "linked": True,
                "message": "Content already linked to blog post",
                "link_id": existing_link.id
            }
        
        # Create new link
        link = BlogContentLink(
            post_id=blog_post_id,
            content_type=content_type,
            content_id=content_id,
            title=getattr(content, 'name', getattr(content, 'title', str(content)))
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)
        
        return {
            "linked": True,
            "message": f"Blog post linked to {content_type} successfully",
            "link_id": link.id,
            "content": {
                "type": content_type,
                "id": content_id,
                "title": link.title
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking blog post {blog_post_id} to {content_type} {content_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link content"
        )


@router.delete("/unlink-content/{link_id}")
async def unlink_blog_content(
    link_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Remove a content link from a blog post."""
    try:
        # Get link and verify ownership through post
        link_result = await db.execute(
            select(BlogContentLink)
            .join(BlogPost, BlogContentLink.post_id == BlogPost.id)
            .where(
                and_(
                    BlogContentLink.id == link_id,
                    BlogPost.author_id == current_user.id
                )
            )
        )
        link = link_result.scalar_one_or_none()
        
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content link not found or access denied"
            )
        
        await db.delete(link)
        await db.commit()
        
        return {
            "unlinked": True,
            "message": "Content unlinked from blog post successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlinking content link {link_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlink content"
        )


@router.get("/blog-links/{blog_post_id}")
async def get_blog_content_links(
    blog_post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get all content links for a blog post."""
    try:
        # Verify blog post ownership
        post_result = await db.execute(
            select(BlogPost).where(
                and_(
                    BlogPost.id == blog_post_id,
                    BlogPost.author_id == current_user.id
                )
            )
        )
        post = post_result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found or access denied"
            )
        
        # Get all links for this post
        links_result = await db.execute(
            select(BlogContentLink)
            .where(BlogContentLink.post_id == blog_post_id)
            .order_by(BlogContentLink.created_at)
        )
        links = links_result.scalars().all()
        
        # Group links by content type
        linked_content = {
            "stories": [],
            "characters": [],
            "locations": [],
            "lore_items": [],
            "worlds": []
        }
        
        for link in links:
            content_info = {
                "link_id": link.id,
                "content_id": link.content_id,
                "title": link.title,
                "linked_at": link.created_at.isoformat()
            }
            
            if link.content_type == "story":
                linked_content["stories"].append(content_info)
            elif link.content_type == "character":
                linked_content["characters"].append(content_info)
            elif link.content_type == "location":
                linked_content["locations"].append(content_info)
            elif link.content_type == "lore_item":
                linked_content["lore_items"].append(content_info)
            elif link.content_type == "world":
                linked_content["worlds"].append(content_info)
        
        return {
            "blog_post": {
                "id": post.id,
                "title": post.title
            },
            "linked_content": linked_content,
            "total_links": len(links)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content links for blog post {blog_post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get content links"
        )


@router.get("/content-blogs/{content_type}/{content_id}")
async def get_content_blog_posts(
    content_type: str,
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get all blog posts linked to specific content."""
    try:
        # Validate content_type
        valid_content_types = ["story", "character", "location", "lore_item", "world"]
        if content_type not in valid_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content_type. Must be one of: {', '.join(valid_content_types)}"
            )
        
        # Verify content ownership
        content = None
        if content_type == "story":
            content_result = await db.execute(
                select(Story).where(
                    and_(
                        Story.id == content_id,
                        Story.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
        elif content_type == "character":
            content_result = await db.execute(
                select(Character).where(
                    and_(
                        Character.id == content_id,
                        Character.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
        elif content_type == "location":
            content_result = await db.execute(
                select(Location).where(
                    and_(
                        Location.id == content_id,
                        Location.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
        elif content_type == "lore_item":
            content_result = await db.execute(
                select(LoreItem).where(
                    and_(
                        LoreItem.id == content_id,
                        LoreItem.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
        elif content_type == "world":
            content_result = await db.execute(
                select(World).where(
                    and_(
                        World.id == content_id,
                        World.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{content_type.title()} not found or access denied"
            )
        
        # Get blog posts linked to this content
        links_result = await db.execute(
            select(BlogContentLink, BlogPost)
            .join(BlogPost, BlogContentLink.post_id == BlogPost.id)
            .where(
                and_(
                    BlogContentLink.content_type == content_type,
                    BlogContentLink.content_id == content_id,
                    BlogPost.author_id == current_user.id,
                    BlogPost.deleted_at.is_(None)
                )
            )
            .order_by(BlogPost.updated_at.desc())
        )
        links_data = links_result.fetchall()
        
        blog_posts = []
        for link, post in links_data:
            blog_posts.append({
                "link_id": link.id,
                "post": {
                    "id": post.id,
                    "title": post.title,
                    "slug": post.slug,
                    "status": post.status.value,
                    "published_at": post.published_at.isoformat() if post.published_at else None,
                    "updated_at": post.updated_at.isoformat(),
                    "view_count": post.view_count,
                    "like_count": post.like_count
                },
                "linked_at": link.created_at.isoformat()
            })
        
        return {
            "content": {
                "type": content_type,
                "id": content_id,
                "title": getattr(content, 'name', getattr(content, 'title', str(content)))
            },
            "blog_posts": blog_posts,
            "total_posts": len(blog_posts)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting blog posts for {content_type} {content_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get linked blog posts"
        )


@router.get("/user-content")
async def get_user_linkable_content(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get all user content that can be linked to blog posts."""
    try:
        # Get user's stories
        stories_result = await db.execute(
            select(Story)
            .where(Story.user_id == current_user.id)
            .order_by(Story.updated_at.desc())
            .limit(50)
        )
        stories = stories_result.scalars().all()
        
        # Get user's characters
        characters_result = await db.execute(
            select(Character)
            .where(Character.user_id == current_user.id)
            .order_by(Character.updated_at.desc())
            .limit(50)
        )
        characters = characters_result.scalars().all()
        
        # Get user's locations
        locations_result = await db.execute(
            select(Location)
            .where(Location.user_id == current_user.id)
            .order_by(Location.updated_at.desc())
            .limit(50)
        )
        locations = locations_result.scalars().all()
        
        # Get user's lore items
        lore_items_result = await db.execute(
            select(LoreItem)
            .where(LoreItem.user_id == current_user.id)
            .order_by(LoreItem.updated_at.desc())
            .limit(50)
        )
        lore_items = lore_items_result.scalars().all()
        
        # Get user's worlds
        worlds_result = await db.execute(
            select(World)
            .where(World.user_id == current_user.id)
            .order_by(World.updated_at.desc())
            .limit(50)
        )
        worlds = worlds_result.scalars().all()
        
        return {
            "stories": [
                {
                    "id": story.id,
                    "title": story.title,
                    "description": story.description,
                    "updated_at": story.updated_at.isoformat()
                }
                for story in stories
            ],
            "characters": [
                {
                    "id": char.id,
                    "name": char.name,
                    "description": char.description,
                    "updated_at": char.updated_at.isoformat()
                }
                for char in characters
            ],
            "locations": [
                {
                    "id": loc.id,
                    "name": loc.name,
                    "description": loc.description,
                    "updated_at": loc.updated_at.isoformat()
                }
                for loc in locations
            ],
            "lore_items": [
                {
                    "id": lore.id,
                    "name": lore.name,
                    "description": lore.description,
                    "updated_at": lore.updated_at.isoformat()
                }
                for lore in lore_items
            ],
            "worlds": [
                {
                    "id": world.id,
                    "name": world.name,
                    "description": world.description,
                    "updated_at": world.updated_at.isoformat()
                }
                for world in worlds
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting user linkable content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get linkable content"
        )


@router.post("/generate-blog-from-content")
async def generate_blog_from_content(
    content_id: int,
    content_type: str = Query(..., regex="^(story|character|location|lore_item|world)$"),
    blog_style: str = Query("informative", regex="^(informative|creative|behind_scenes|guide)$"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Generate a blog post draft from existing storytelling content."""
    try:
        # Validate content_type
        valid_content_types = ["story", "character", "location", "lore_item", "world"]
        if content_type not in valid_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid content_type. Must be one of: {', '.join(valid_content_types)}"
            )
        
        # Validate blog_style
        valid_blog_styles = ["informative", "creative", "behind_scenes", "guide"]
        if blog_style not in valid_blog_styles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid blog_style. Must be one of: {', '.join(valid_blog_styles)}"
            )
        
        # Verify content ownership and get content
        content = None
        content_data = {}
        
        if content_type == "story":
            content_result = await db.execute(
                select(Story).where(
                    and_(
                        Story.id == content_id,
                        Story.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
            if content:
                content_data = {
                    "title": content.title,
                    "description": content.description,
                    "content": getattr(content, 'content', ''),
                    "type": "story"
                }
        elif content_type == "character":
            content_result = await db.execute(
                select(Character).where(
                    and_(
                        Character.id == content_id,
                        Character.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
            if content:
                content_data = {
                    "title": content.name,
                    "description": content.description,
                    "content": getattr(content, 'background', ''),
                    "type": "character"
                }
        elif content_type == "location":
            content_result = await db.execute(
                select(Location).where(
                    and_(
                        Location.id == content_id,
                        Location.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
            if content:
                content_data = {
                    "title": content.name,
                    "description": content.description,
                    "content": getattr(content, 'details', ''),
                    "type": "location"
                }
        elif content_type == "lore_item":
            content_result = await db.execute(
                select(LoreItem).where(
                    and_(
                        LoreItem.id == content_id,
                        LoreItem.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
            if content:
                content_data = {
                    "title": content.name,
                    "description": content.description,
                    "content": getattr(content, 'content', ''),
                    "type": "lore_item"
                }
        elif content_type == "world":
            content_result = await db.execute(
                select(World).where(
                    and_(
                        World.id == content_id,
                        World.user_id == current_user.id
                    )
                )
            )
            content = content_result.scalar_one_or_none()
            if content:
                content_data = {
                    "title": content.name,
                    "description": content.description,
                    "content": getattr(content, 'overview', ''),
                    "type": "world"
                }
        
        if not content:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"{content_type.title()} not found or access denied"
            )
        
        # Generate blog post suggestions based on style
        blog_suggestions = {
            "informative": {
                "title": f"Understanding {content_data['title']}: A Deep Dive",
                "excerpt": f"An informative exploration of {content_data['title']} and its significance in storytelling.",
                "content_outline": [
                    "Introduction and overview",
                    "Key characteristics and features", 
                    "Role in the broader narrative",
                    "Creative inspiration and process",
                    "Conclusion and takeaways"
                ]
            },
            "creative": {
                "title": f"The Story Behind {content_data['title']}",
                "excerpt": f"Discover the creative journey and inspiration that brought {content_data['title']} to life.",
                "content_outline": [
                    "Creative inspiration",
                    "Development process",
                    "Challenges and breakthroughs",
                    "Personal reflections",
                    "What's next"
                ]
            },
            "behind_scenes": {
                "title": f"Behind the Scenes: Creating {content_data['title']}",
                "excerpt": f"A behind-the-scenes look at the creation process of {content_data['title']}.",
                "content_outline": [
                    "Initial concept",
                    "Research and development",
                    "Design decisions",
                    "Iterations and refinements",
                    "Final thoughts"
                ]
            },
            "guide": {
                "title": f"Writer's Guide: Crafting {content_type.replace('_', ' ').title()}s Like {content_data['title']}",
                "excerpt": f"Learn the techniques and principles used to create compelling {content_type.replace('_', ' ')}s.",
                "content_outline": [
                    "Key principles",
                    "Step-by-step process",
                    "Common pitfalls to avoid",
                    "Tips and best practices",
                    "Resources for further learning"
                ]
            }
        }
        
        suggestion = blog_suggestions[blog_style]
        
        return {
            "source_content": {
                "type": content_type,
                "id": content_id,
                "title": content_data["title"],
                "description": content_data["description"]
            },
            "blog_suggestion": {
                "style": blog_style,
                "title": suggestion["title"],
                "excerpt": suggestion["excerpt"],
                "content_outline": suggestion["content_outline"],
                "suggested_tags": [
                    content_type.replace('_', ' '),
                    "writing",
                    "storytelling",
                    "creative process"
                ]
            },
            "next_steps": [
                "Copy the suggested title and excerpt",
                "Use the content outline as a structure",
                "Write the blog post in the editor",
                "Link the blog post back to this content"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating blog from {content_type} {content_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate blog suggestion"
        )