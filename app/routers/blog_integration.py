"""Blog integration with storytelling features API endpoints."""
import logging
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_active_user, get_db_session
from app.models.blog_post import BlogPost
from app.models.blog_post_association import AssociationType, BlogPostAssociation
from app.models.character import Character
from app.models.location import Location
from app.models.lore_item import LoreItem
from app.models.story import Story
from app.models.user import User
from app.models.world import World
from app.schemas.base import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog/integration", tags=["blog-integration"])


CONTENT_MODEL_MAP = {
    "story": (AssociationType.STORY, Story, "title"),
    "world": (AssociationType.WORLD, World, "name"),
    "character": (AssociationType.CHARACTER, Character, "name"),
    "location": (AssociationType.LOCATION, Location, "name"),
    "lore_item": (AssociationType.LORE_ITEM, LoreItem, "title"),
}


async def _get_user_world_ids(db: AsyncSession, user_id: int) -> List[int]:
    """Provide internal router support for get user world ids."""
    result = await db.execute(select(World.id).where(World.user_id == user_id))
    return [row[0] for row in result.fetchall()]


async def _get_owned_content(
    db: AsyncSession,
    *,
    current_user: User,
    content_type: str,
    content_id: int,
):
    """Provide internal router support for get owned content."""
    config = CONTENT_MODEL_MAP.get(content_type)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content_type. Must be one of: {', '.join(CONTENT_MODEL_MAP.keys())}",
        )

    _, model, title_attr = config
    query = select(model).where(model.id == content_id)
    if model in (Story, World):
        query = query.where(model.user_id == current_user.id)
    else:
        world_ids = await _get_user_world_ids(db, current_user.id)
        query = query.where(model.world_id.in_(world_ids if world_ids else [-1]))

    result = await db.execute(query)
    content = result.scalar_one_or_none()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{content_type.title()} not found or access denied",
        )
    return content, getattr(content, title_attr, str(content))


def _serialize_association(link: BlogPostAssociation) -> Dict[str, Any]:
    """Provide internal router support for serialize association."""
    return {
        "link_id": link.id,
        "content_type": link.association_type.value,
        "content_id": link.association_id,
        "title": link.association_title,
        "linked_at": link.created_at.isoformat(),
    }


def _get_content_summary(content: Any, *candidates: str) -> Optional[str]:
    """Provide internal router support for get content summary."""
    for field in candidates:
        value = getattr(content, field, None)
        if value:
            return value
    return None


@router.post("/link-content", response_model=ApiResponse)
async def link_blog_to_content(
    blog_post_id: int,
    content_id: int,
    content_type: str = Query(..., pattern="^(story|character|location|lore_item|world)$"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Link a blog post to storytelling content."""
    try:
        post_result = await db.execute(
            select(BlogPost).where(and_(BlogPost.id == blog_post_id, BlogPost.author_id == current_user.id))
        )
        post = post_result.scalar_one_or_none()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found or access denied",
            )

        content, title = await _get_owned_content(
            db,
            current_user=current_user,
            content_type=content_type,
            content_id=content_id,
        )
        association_type = CONTENT_MODEL_MAP[content_type][0]

        existing_link_result = await db.execute(
            select(BlogPostAssociation).where(
                and_(
                    BlogPostAssociation.post_id == blog_post_id,
                    BlogPostAssociation.association_type == association_type,
                    BlogPostAssociation.association_id == content_id,
                )
            )
        )
        existing_link = existing_link_result.scalar_one_or_none()
        if existing_link:
            return ApiResponse.success_response(
                data={
                    "linked": True,
                    "message": "Content already linked to blog post",
                    "link": _serialize_association(existing_link),
                }
            )

        link = BlogPostAssociation(
            post_id=blog_post_id,
            association_type=association_type,
            association_id=content_id,
            association_title=title,
        )
        db.add(link)
        await db.commit()
        await db.refresh(link)

        return ApiResponse.success_response(
            data={
                "linked": True,
                "message": f"Blog post linked to {content_type} successfully",
                "link": _serialize_association(link),
                "content": {
                    "type": content_type,
                    "id": content_id,
                    "title": title,
                },
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error linking blog post {blog_post_id} to {content_type} {content_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link content",
        )


@router.delete("/unlink-content/{link_id}", response_model=ApiResponse)
async def unlink_blog_content(
    link_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Remove a content link from a blog post."""
    try:
        link_result = await db.execute(
            select(BlogPostAssociation)
            .join(BlogPost, BlogPostAssociation.post_id == BlogPost.id)
            .where(and_(BlogPostAssociation.id == link_id, BlogPost.author_id == current_user.id))
        )
        link = link_result.scalar_one_or_none()
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Content link not found or access denied",
            )

        await db.delete(link)
        await db.commit()

        return ApiResponse.success_response(
            data={"unlinked": True, "message": "Content unlinked from blog post successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unlinking content link {link_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to unlink content",
        )


@router.get("/blog-links/{blog_post_id}", response_model=ApiResponse)
async def get_blog_content_links(
    blog_post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all content links for a blog post."""
    try:
        post_result = await db.execute(
            select(BlogPost).where(and_(BlogPost.id == blog_post_id, BlogPost.author_id == current_user.id))
        )
        post = post_result.scalar_one_or_none()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found or access denied",
            )

        links_result = await db.execute(
            select(BlogPostAssociation)
            .where(BlogPostAssociation.post_id == blog_post_id)
            .order_by(BlogPostAssociation.created_at)
        )
        links = links_result.scalars().all()

        grouped = {"stories": [], "characters": [], "locations": [], "lore_items": [], "worlds": []}
        for link in links:
            serialized = _serialize_association(link)
            if link.association_type == AssociationType.STORY:
                grouped["stories"].append(serialized)
            elif link.association_type == AssociationType.CHARACTER:
                grouped["characters"].append(serialized)
            elif link.association_type == AssociationType.LOCATION:
                grouped["locations"].append(serialized)
            elif link.association_type == AssociationType.LORE_ITEM:
                grouped["lore_items"].append(serialized)
            elif link.association_type == AssociationType.WORLD:
                grouped["worlds"].append(serialized)

        return ApiResponse.success_response(
            data={
                "blog_post": {"id": post.id, "title": post.title},
                "linked_content": grouped,
                "total_links": len(links),
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting content links for blog post {blog_post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get content links",
        )


@router.get("/content-blogs/{content_type}/{content_id}", response_model=ApiResponse)
async def get_content_blog_posts(
    content_type: str,
    content_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all blog posts linked to specific content."""
    try:
        content, title = await _get_owned_content(
            db,
            current_user=current_user,
            content_type=content_type,
            content_id=content_id,
        )
        association_type = CONTENT_MODEL_MAP[content_type][0]

        links_result = await db.execute(
            select(BlogPostAssociation, BlogPost)
            .join(BlogPost, BlogPostAssociation.post_id == BlogPost.id)
            .where(
                and_(
                    BlogPostAssociation.association_type == association_type,
                    BlogPostAssociation.association_id == content_id,
                    BlogPost.author_id == current_user.id,
                    BlogPost.deleted_at.is_(None),
                )
            )
            .order_by(BlogPost.updated_at.desc())
        )
        links_data = links_result.fetchall()

        blog_posts = [
            {
                "link_id": link.id,
                "post": {
                    "id": post.id,
                    "title": post.title,
                    "slug": post.slug,
                    "status": post.status.value,
                    "published_at": post.published_at.isoformat() if post.published_at else None,
                    "updated_at": post.updated_at.isoformat(),
                    "view_count": post.view_count,
                    "like_count": post.like_count,
                },
                "linked_at": link.created_at.isoformat(),
            }
            for link, post in links_data
        ]

        return ApiResponse.success_response(
            data={
                "content": {"type": content_type, "id": content_id, "title": title},
                "blog_posts": blog_posts,
                "total_posts": len(blog_posts),
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting blog posts for {content_type} {content_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get linked blog posts",
        )


@router.get("/user-content", response_model=ApiResponse)
async def get_user_linkable_content(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Get all user content that can be linked to blog posts."""
    try:
        world_ids = await _get_user_world_ids(db, current_user.id)
        stories = (
            await db.execute(select(Story).where(Story.user_id == current_user.id).order_by(Story.updated_at.desc()).limit(50))
        ).scalars().all()
        characters = (
            await db.execute(
                select(Character).where(Character.world_id.in_(world_ids if world_ids else [-1])).order_by(Character.updated_at.desc()).limit(50)
            )
        ).scalars().all()
        locations = (
            await db.execute(
                select(Location).where(Location.world_id.in_(world_ids if world_ids else [-1])).order_by(Location.updated_at.desc()).limit(50)
            )
        ).scalars().all()
        lore_items = (
            await db.execute(
                select(LoreItem).where(LoreItem.world_id.in_(world_ids if world_ids else [-1])).order_by(LoreItem.updated_at.desc()).limit(50)
            )
        ).scalars().all()
        worlds = (
            await db.execute(select(World).where(World.user_id == current_user.id).order_by(World.updated_at.desc()).limit(50))
        ).scalars().all()

        return ApiResponse.success_response(
            data={
                "stories": [
                    {
                        "id": story.id,
                        "title": story.title,
                        "description": _get_content_summary(story, "short_description", "description"),
                        "updated_at": story.updated_at.isoformat(),
                    }
                    for story in stories
                ],
                "characters": [
                    {"id": char.id, "name": char.name, "description": _get_content_summary(char, "description"), "updated_at": char.updated_at.isoformat()}
                    for char in characters
                ],
                "locations": [
                    {"id": loc.id, "name": loc.name, "description": _get_content_summary(loc, "description"), "updated_at": loc.updated_at.isoformat()}
                    for loc in locations
                ],
                "lore_items": [
                    {"id": lore.id, "title": lore.title, "description": _get_content_summary(lore, "description"), "updated_at": lore.updated_at.isoformat()}
                    for lore in lore_items
                ],
                "worlds": [
                    {"id": world.id, "name": world.name, "description": _get_content_summary(world, "short_description", "description"), "updated_at": world.updated_at.isoformat()}
                    for world in worlds
                ],
            }
        )
    except Exception as e:
        logger.error(f"Error getting user linkable content: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get linkable content",
        )


@router.post("/generate-blog-from-content", response_model=ApiResponse)
async def generate_blog_from_content(
    content_id: int,
    content_type: str = Query(..., pattern="^(story|character|location|lore_item|world)$"),
    blog_style: str = Query("informative", pattern="^(informative|creative|behind_scenes|guide)$"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """Generate a blog post draft suggestion from existing storytelling content."""
    try:
        content, title = await _get_owned_content(
            db,
            current_user=current_user,
            content_type=content_type,
            content_id=content_id,
        )

        content_body = ""
        if content_type == "story":
            content_body = getattr(content, "content", "") or ""
        elif content_type == "character":
            content_body = getattr(content, "background", "") or ""
        elif content_type == "location":
            content_body = getattr(content, "details", "") or ""
        elif content_type == "lore_item":
            content_body = getattr(content, "content", "") or ""
        elif content_type == "world":
            content_body = getattr(content, "overview", "") or ""

        description = _get_content_summary(content, "short_description", "description")

        blog_suggestions = {
            "informative": {
                "title": f"Understanding {title}: A Deep Dive",
                "excerpt": f"An informative exploration of {title} and its significance in storytelling.",
                "content_outline": [
                    "Introduction and overview",
                    "Key characteristics and features",
                    "Role in the broader narrative",
                    "Creative inspiration and process",
                    "Conclusion and takeaways",
                ],
            },
            "creative": {
                "title": f"The Story Behind {title}",
                "excerpt": f"Discover the creative journey and inspiration that brought {title} to life.",
                "content_outline": [
                    "Creative inspiration",
                    "Development process",
                    "Challenges and breakthroughs",
                    "Personal reflections",
                    "What's next",
                ],
            },
            "behind_scenes": {
                "title": f"Behind the Scenes: Creating {title}",
                "excerpt": f"A behind-the-scenes look at the creation process of {title}.",
                "content_outline": [
                    "Initial concept",
                    "Research and development",
                    "Design decisions",
                    "Iterations and refinements",
                    "Final thoughts",
                ],
            },
            "guide": {
                "title": f"Writer's Guide: Crafting {content_type.replace('_', ' ').title()}s Like {title}",
                "excerpt": f"Learn the techniques and principles used to create compelling {content_type.replace('_', ' ')}s.",
                "content_outline": [
                    "Key principles",
                    "Step-by-step process",
                    "Common pitfalls to avoid",
                    "Tips and best practices",
                    "Resources for further learning",
                ],
            },
        }
        suggestion = blog_suggestions[blog_style]

        return ApiResponse.success_response(
            data={
                "source_content": {
                    "type": content_type,
                    "id": content_id,
                    "title": title,
                    "description": description,
                    "content_preview": content_body[:300],
                },
                "blog_suggestion": {
                    "style": blog_style,
                    "title": suggestion["title"],
                    "excerpt": suggestion["excerpt"],
                    "content_outline": suggestion["content_outline"],
                    "suggested_tags": [
                        content_type.replace("_", " "),
                        "writing",
                        "storytelling",
                        "creative process",
                    ],
                },
                "next_steps": [
                    "Copy the suggested title and excerpt",
                    "Use the content outline as a structure",
                    "Write the blog post in the editor",
                    "Link the blog post back to this content",
                ],
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating blog from {content_type} {content_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate blog suggestion",
        )
