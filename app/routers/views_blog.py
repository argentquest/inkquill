"""Blog view routes for frontend templates."""
import logging
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, Request, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.deps import get_db_session
from app.core.config import settings
from app.models.user import User
from app.models.blog_post import BlogPost, BlogPostStatus
from app.models.blog_category import BlogCategory
from app.models.blog_tag import BlogTag
from app.services.blog_service import blog_service
from app.schemas.blog import BlogPostCreate, BlogPostUpdate

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/blog",
    tags=["blog-views"],
    include_in_schema=False
)

# Create templates instance with blog-specific directory
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["google_analytics_id"] = settings.GOOGLE_ANALYTICS_ID
templates.env.globals["google_analytics_consent_mode"] = settings.GOOGLE_ANALYTICS_CONSENT_MODE
templates.env.globals["cookie_consent_required"] = settings.COOKIE_CONSENT_REQUIRED


async def get_optional_current_user_for_blog_views(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """Get current user for blog views - supports anonymous users."""
    from app.core import security as core_security
    from app.crud import user as crud_user
    
    token = request.cookies.get("access_token")
    if not token:
        logger.debug("No access_token cookie found in request for blog views.")
        return None
    
    try:
        payload: Optional[Dict[str, Any]] = await core_security.decode_access_token(token=token)
        if payload is None:
            logger.warning("Token decoding returned None for blog views.")
            return None
        
        username_from_payload: Optional[str] = payload.get("sub")
        if username_from_payload is None:
            logger.warning("Username (sub) not found in token payload for blog views.")
            return None
        
        user = await crud_user.get_user_by_username(db, username=username_from_payload)
        if user is None:
            logger.warning(f"User not found in database for username '{username_from_payload}' for blog views.")
            return None
        
        return user
    
    except Exception as e:
        logger.error(f"Error retrieving user for blog views: {e}")
        return None


@router.get("/", response_class=HTMLResponse, name="blog_home")
async def blog_home(
    request: Request,
    page: int = Query(1, ge=1),
    category_id: Optional[int] = Query(None),
    tag_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    q: Optional[str] = Query(None),  # Alternative search parameter
    trending: Optional[bool] = Query(None),  # Show trending posts
    current_user: Optional[User] = Depends(get_optional_current_user_for_blog_views),
    db: AsyncSession = Depends(get_db_session)
):
    """Blog home page with post listing."""
    try:
        # Calculate pagination
        limit = 12  # Posts per page
        skip = (page - 1) * limit
        
        # Parse tag_id into list if provided
        tag_ids = [tag_id] if tag_id else None
        
        # Use q parameter if search is not provided
        search_query = search or q
        
        # Get posts based on request type
        if trending:
            # Get trending posts using weighted algorithm
            posts = await blog_service.get_trending_posts(
                db=db,
                limit=limit,
                days_back=30
            )
        else:
            # Get regular published posts
            posts = await blog_service.get_published_posts(
                db=db,
                skip=skip,
                limit=limit,
                category_id=category_id,
                tag_ids=tag_ids,
                search_query=search_query
            )
        
        # Get categories for sidebar
        categories_result = await db.execute(
            select(BlogCategory)
            .where(BlogCategory.is_active == True)
            .order_by(BlogCategory.display_order, BlogCategory.name)
        )
        categories = categories_result.scalars().all()
        
        # Get popular tags
        popular_tags_result = await db.execute(
            select(BlogTag)
            .order_by(BlogTag.usage_count.desc())
            .limit(20)
        )
        popular_tags = popular_tags_result.scalars().all()
        
        # Get featured posts for hero section
        featured_posts_result = await db.execute(
            select(BlogPost)
            .where(
                and_(
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.is_featured == True,
                    BlogPost.deleted_at.is_(None)
                )
            )
            .order_by(BlogPost.published_at.desc())
            .limit(5)  # Get up to 5 featured posts for rotation
        )
        featured_posts = featured_posts_result.scalars().all()
        
        # Calculate total posts for pagination
        from sqlalchemy import func
        total_query = select(func.count(BlogPost.id)).where(
            and_(
                BlogPost.status == BlogPostStatus.PUBLISHED,
                BlogPost.deleted_at.is_(None)
            )
        )
        
        if category_id:
            total_query = total_query.where(BlogPost.category_id == category_id)
        if search_query:
            from sqlalchemy import or_
            search_filter = or_(
                BlogPost.title.ilike(f"%{search_query}%"),
                BlogPost.content.ilike(f"%{search_query}%"),
                BlogPost.excerpt.ilike(f"%{search_query}%")
            )
            total_query = total_query.where(search_filter)
        
        total_result = await db.execute(total_query)
        total_posts = total_result.scalar()
        total_pages = (total_posts + limit - 1) // limit
        
        return templates.TemplateResponse(
            "blog/home_modern.html",
            {
                "request": request,
                "current_user": current_user,
                "posts": posts,
                "categories": categories,
                "popular_tags": popular_tags,
                "featured_posts": featured_posts,
                "current_page": page,
                "total_pages": total_pages,
                "total_posts": total_posts,
                "current_category_id": category_id,
                "current_tag_id": tag_id,
                "current_search": search_query or "",
                "is_trending": trending or False,
                "page_title": "Trending Posts" if trending else "Blog",
                "meta_description": "Discover storytelling insights, writing tips, and creative inspiration from our community of writers.",
                "breadcrumb_active": "Trending" if trending else "Home"
            }
        )
        
    except Exception as e:
        logger.error(f"Error rendering blog home: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load blog home page"
        )


@router.get("/post/{slug}", response_class=HTMLResponse, name="blog_post_detail")
async def blog_post_detail(
    request: Request,
    slug: str,
    current_user: Optional[User] = Depends(get_optional_current_user_for_blog_views),
    db: AsyncSession = Depends(get_db_session)
):
    """Individual blog post detail page."""
    try:
        # Get post by slug
        post = await blog_service.get_post_by_slug(db, slug)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        # Check if post is published or user is author
        if post.status != BlogPostStatus.PUBLISHED:
            if not current_user or current_user.id != post.author_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Blog post not found"
                )
        
        # Get related posts by category
        related_posts = []
        if post.category_id:
            related_posts = await blog_service.get_published_posts(
                db=db,
                category_id=post.category_id,
                limit=3
            )
            # Remove current post from related posts
            related_posts = [p for p in related_posts if p.id != post.id]
        
        # TODO: Track view for analytics
        
        # Calculate reading time (rough estimate: 200 words per minute)
        word_count = len(post.content.split())
        reading_time = max(1, round(word_count / 200))
        
        # Get categories for navigation
        categories_result = await db.execute(
            select(BlogCategory)
            .where(BlogCategory.is_active == True)
            .order_by(BlogCategory.display_order, BlogCategory.name)
        )
        categories = categories_result.scalars().all()
        
        # Get popular tags for sidebar
        popular_tags_result = await db.execute(
            select(BlogTag)
            .order_by(BlogTag.usage_count.desc())
            .limit(15)
        )
        popular_tags = popular_tags_result.scalars().all()
        
        # Get comments for this post
        comments = []
        if post.allow_comments:
            from app.services.blog_comment_service import blog_comment_service
            comments = await blog_comment_service.get_post_comments(
                db=db,
                post_id=post.id,
                skip=0,
                limit=50,
                include_replies=True
            )
            
            # Process comments to create a proper nested structure for the template
            processed_comments = []
            for comment in comments:
                # Convert to a dict-like structure that the template can easily work with
                comment_dict = {
                    'id': comment.id,
                    'content': comment.content,
                    'created_at': comment.created_at,
                    'author': comment.author,
                    'replies': []
                }
                
                # Add replies if they exist
                if hasattr(comment, '_manual_replies') and comment._manual_replies:
                    for reply in comment._manual_replies:
                        reply_dict = {
                            'id': reply.id,
                            'content': reply.content,
                            'created_at': reply.created_at,
                            'author': reply.author
                        }
                        comment_dict['replies'].append(reply_dict)
                
                processed_comments.append(comment_dict)
            
            comments = processed_comments
        
        return templates.TemplateResponse(
            "blog/post_detail_modern.html",
            {
                "request": request,
                "current_user": current_user,
                "post": post,
                "comments": comments,
                "related_posts": related_posts,
                "categories": categories,
                "popular_tags": popular_tags,
                "reading_time": reading_time,
                "page_title": post.meta_title or post.title,
                "meta_description": post.meta_description or post.excerpt or post.title,
                "og_title": post.title,
                "og_description": post.excerpt or post.title,
                "og_image": post.featured_image_url,
                "breadcrumb_active": post.title[:50] + "..." if len(post.title) > 50 else post.title
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rendering blog post {slug}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load blog post"
        )


@router.get("/category/{category_slug}", response_class=HTMLResponse, name="blog_category")
async def blog_category(
    request: Request,
    category_slug: str,
    page: int = Query(1, ge=1),
    current_user: Optional[User] = Depends(get_optional_current_user_for_blog_views),
    db: AsyncSession = Depends(get_db_session)
):
    """Blog posts filtered by category."""
    try:
        # Get category by slug
        category_result = await db.execute(
            select(BlogCategory).where(BlogCategory.slug == category_slug)
        )
        category = category_result.scalar_one_or_none()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        
        # Redirect to home with category filter
        return RedirectResponse(
            url=f"/blog/?category_id={category.id}&page={page}",
            status_code=status.HTTP_302_FOUND
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling category {category_slug}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load category"
        )


@router.get("/tag/{tag_slug}", response_class=HTMLResponse, name="blog_tag")
async def blog_tag(
    request: Request,
    tag_slug: str,
    page: int = Query(1, ge=1),
    current_user: Optional[User] = Depends(get_optional_current_user_for_blog_views),
    db: AsyncSession = Depends(get_db_session)
):
    """Blog posts filtered by tag."""
    try:
        # Get tag by slug
        tag_result = await db.execute(
            select(BlogTag).where(BlogTag.slug == tag_slug)
        )
        tag = tag_result.scalar_one_or_none()
        
        if not tag:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tag not found"
            )
        
        # Redirect to home with tag filter
        return RedirectResponse(
            url=f"/blog/?tag_id={tag.id}&page={page}",
            status_code=status.HTTP_302_FOUND
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling tag {tag_slug}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load tag"
        )


@router.get("/author/{username}", response_class=HTMLResponse, name="blog_author")
async def blog_author(
    request: Request,
    username: str,
    page: int = Query(1, ge=1),
    current_user: Optional[User] = Depends(get_optional_current_user_for_blog_views),
    db: AsyncSession = Depends(get_db_session)
):
    """Blog posts by specific author."""
    try:
        # Get author by username
        from app.crud import user as crud_user
        author = await crud_user.get_user_by_username(db, username)
        
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found"
            )
        
        # Calculate pagination
        limit = 12
        skip = (page - 1) * limit
        
        # Get author's published posts
        posts = await blog_service.get_published_posts(
            db=db,
            author_id=author.id,
            skip=skip,
            limit=limit
        )
        
        # Calculate total posts for pagination
        from sqlalchemy import func
        total_result = await db.execute(
            select(func.count(BlogPost.id)).where(
                and_(
                    BlogPost.author_id == author.id,
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.deleted_at.is_(None)
                )
            )
        )
        total_posts = total_result.scalar()
        total_pages = (total_posts + limit - 1) // limit
        
        return templates.TemplateResponse(
            "blog/author.html",
            {
                "request": request,
                "current_user": current_user,
                "author": author,
                "posts": posts,
                "current_page": page,
                "total_pages": total_pages,
                "total_posts": total_posts,
                "page_title": f"Posts by {author.display_name or author.username}",
                "meta_description": f"Read blog posts by {author.display_name or author.username}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rendering author page {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load author page"
        )


@router.get("/editor", response_class=HTMLResponse, name="blog_editor")
async def blog_editor(
    request: Request,
    post_id: Optional[int] = Query(None),
    current_user: Optional[User] = Depends(get_optional_current_user_for_blog_views),
    db: AsyncSession = Depends(get_db_session)
):
    """Blog post editor page."""
    try:
        # Require authentication for editor
        if not current_user:
            return RedirectResponse(
                url="/auth/login?next=/blog/editor",
                status_code=status.HTTP_302_FOUND
            )
        
        # Load existing post if post_id is provided
        post_data = None
        if post_id:
            post = await blog_service.get_post_by_id(db, post_id)
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Blog post not found"
                )
            
            # Check if current user is the author or admin
            if post.author_id != current_user.id and not current_user.is_admin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only edit your own posts"
                )
            
            # Convert post to dict for template
            post_data = {
                "id": post.id,
                "title": post.title,
                "content": post.content,
                "excerpt": post.excerpt,
                "category_id": post.category_id,
                "status": post.status.value if post.status else 'draft',
                "is_featured": post.is_featured,
                "tags": [tag.name for tag in post.tags] if post.tags else []
            }
        
        # Get categories for dropdown
        categories_result = await db.execute(
            select(BlogCategory)
            .where(BlogCategory.is_active == True)
            .order_by(BlogCategory.display_order, BlogCategory.name)
        )
        categories = categories_result.scalars().all()
        
        return templates.TemplateResponse(
            "blog/editor.html",
            {
                "request": request,
                "current_user": current_user,
                "categories": categories,
                "post_data": post_data,
                "page_title": "Edit Post" if post_data else "Blog Editor",
                "meta_description": "Create and edit blog posts with AI assistance",
                "breadcrumb_active": "Editor"
            }
        )
        
    except Exception as e:
        logger.error(f"Error rendering blog editor: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load blog editor"
        )


@router.get("/dashboard", response_class=HTMLResponse, name="blog_dashboard")
async def blog_dashboard(
    request: Request,
    current_user: Optional[User] = Depends(get_optional_current_user_for_blog_views),
    db: AsyncSession = Depends(get_db_session)
):
    """Blog author dashboard page."""
    try:
        # Require authentication for dashboard
        if not current_user:
            return RedirectResponse(
                url="/auth/login?next=/blog/dashboard",
                status_code=status.HTTP_302_FOUND
            )
        
        return templates.TemplateResponse(
            "blog/dashboard.html",
            {
                "request": request,
                "current_user": current_user,
                "page_title": "My Blog Dashboard",
                "meta_description": "Manage your blog posts and track performance"
            }
        )
        
    except Exception as e:
        logger.error(f"Error rendering blog dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load blog dashboard"
        )