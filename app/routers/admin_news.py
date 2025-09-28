"""Admin routes for news management and public news display."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db_session, get_current_user
from app.models.user import User

templates = Jinja2Templates(directory="app/templates")

# Create separate routers for admin and public routes
admin_router = APIRouter(prefix="/admin/news", tags=["Admin News"])
public_router = APIRouter(tags=["News"])

# We'll use the main router for public routes and include admin_router separately
router = public_router


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin privileges."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


# ==================== PUBLIC NEWS ROUTES ====================

@router.get("/news", response_class=HTMLResponse, name="ui_news_list")
async def ui_news_list(
    request: Request,
    page: int = 1,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Display paginated list of all news articles."""
    
    # Import here to avoid circular imports
    from app.crud import forum_category as crud_category
    from app.crud import forum_thread as crud_thread
    from app.crud import forum_post as crud_post
    
    # Get the news category
    news_category = await crud_category.get_forum_category_by_slug(db, "news")
    if not news_category:
        return templates.TemplateResponse(
            "pages/news_list.html",
            {
                "request": request,
                "current_user": current_user,
                "pinned_articles": [],
                "recent_articles": [],
                "page": page,
                "has_next": False,
                "total_pages": 0,
                "page_title": "News & Updates"
            }
        )
    
    # Pagination settings
    per_page = 12
    skip = (page - 1) * per_page
    
    # Get pinned articles (only on first page)
    pinned_articles = []
    if page == 1:
        pinned_threads = await crud_thread.get_forum_threads(
            db,
            category_id=news_category.id,
            order_by="recent",
            limit=10  # Get more to filter pinned ones
        )
        
        for thread in pinned_threads:
            if thread.is_pinned:
                posts = await crud_post.get_thread_posts(db, thread.id, limit=1)
                if posts:
                    content = posts[0].content
                    content_preview = content[:200] + "..." if len(content) > 200 else content
                    
                    # Count replies
                    all_posts = await crud_post.get_thread_posts(db, thread.id)
                    reply_count = len(all_posts) - 1
                    
                    pinned_articles.append({
                        "id": thread.id,
                        "title": thread.title,
                        "content_preview": content_preview,
                        "created_at": thread.created_at,
                        "author": thread.user.username if thread.user else "Admin",
                        "view_count": thread.view_count,
                        "reply_count": reply_count
                    })
                    
                    if len(pinned_articles) >= 4:  # Limit pinned articles
                        break
    
    # Get recent articles (non-pinned or all if not first page)
    all_threads = await crud_thread.get_forum_threads(
        db,
        category_id=news_category.id,
        order_by="recent",
        skip=skip,
        limit=per_page + 1  # Get one extra to check if there's a next page
    )
    
    # Filter out pinned articles for recent section (only on first page)
    filtered_threads = []
    for thread in all_threads:
        if page == 1 and thread.is_pinned:
            continue  # Skip pinned on first page as they're shown separately
        filtered_threads.append(thread)
    
    # Check if there's a next page
    has_next = len(filtered_threads) > per_page
    if has_next:
        filtered_threads = filtered_threads[:per_page]
    
    # Process recent articles
    recent_articles = []
    for thread in filtered_threads:
        posts = await crud_post.get_thread_posts(db, thread.id, limit=1)
        if posts:
            content = posts[0].content
            content_preview = content[:250] + "..." if len(content) > 250 else content
            
            # Count replies
            all_posts = await crud_post.get_thread_posts(db, thread.id)
            reply_count = len(all_posts) - 1
            
            recent_articles.append({
                "id": thread.id,
                "title": thread.title,
                "content_preview": content_preview,
                "created_at": thread.created_at,
                "author": thread.user.username if thread.user else "Admin",
                "view_count": thread.view_count,
                "reply_count": reply_count
            })
    
    # Calculate total pages (rough estimate)
    total_articles = await crud_thread.get_forum_threads(
        db,
        category_id=news_category.id,
        order_by="recent",
        limit=1000  # Large number to get count
    )
    total_count = len(total_articles)
    total_pages = (total_count + per_page - 1) // per_page
    
    return templates.TemplateResponse(
        "pages/news_list.html",
        {
            "request": request,
            "current_user": current_user,
            "pinned_articles": pinned_articles,
            "recent_articles": recent_articles,
            "page": page,
            "has_next": has_next,
            "total_pages": total_pages,
            "page_title": "News & Updates"
        }
    )


@router.get("/news/{article_id}", response_class=HTMLResponse, name="ui_news_detail")
async def ui_news_detail(
    request: Request,
    article_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Display a news article in a dedicated news format."""
    
    # Import here to avoid circular imports
    from app.crud import forum_thread as crud_thread
    from app.crud import forum_post as crud_post
    from app.crud import forum_category as crud_category
    
    # Get the thread (this will increment view count)
    thread = await crud_thread.get_forum_thread(db, article_id, increment_view=True)
    if not thread:
        raise HTTPException(status_code=404, detail="News article not found")
    
    # Verify this is actually a news article (in news category)
    news_category = await crud_category.get_forum_category_by_slug(db, "news")
    if not news_category or thread.category_id != news_category.id:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Get the first post (the article content)
    posts = await crud_post.get_thread_posts(db, article_id, limit=1)
    if not posts:
        raise HTTPException(status_code=404, detail="Article content not found")
    
    first_post = posts[0]
    
    # Count replies (excluding the first post)
    all_posts = await crud_post.get_thread_posts(db, article_id)
    reply_count = len(all_posts) - 1  # Subtract the original post
    
    # Get related articles (other recent news, excluding current)
    related_threads = await crud_thread.get_forum_threads(
        db,
        category_id=news_category.id,
        order_by="recent",
        limit=6
    )
    
    related_articles = []
    for related_thread in related_threads:
        if related_thread.id != article_id:  # Exclude current article
            # Get first post for preview
            related_posts = await crud_post.get_thread_posts(db, related_thread.id, limit=1)
            if related_posts:
                content = related_posts[0].content
                content_preview = content[:150] + "..." if len(content) > 150 else content
                
                related_articles.append({
                    "id": related_thread.id,
                    "title": related_thread.title,
                    "content_preview": content_preview,
                    "created_at": related_thread.created_at
                })
                
                if len(related_articles) >= 4:  # Limit to 4 related articles
                    break
    
    # Prepare article data
    article_data = {
        "id": thread.id,
        "title": thread.title,
        "content": first_post.content,
        "created_at": thread.created_at,
        "updated_at": first_post.edited_at or thread.updated_at,
        "author_username": thread.user.username if thread.user else "Admin",
        "author_display_name": thread.user.display_name if thread.user else None,
        "is_pinned": thread.is_pinned,
        "view_count": thread.view_count,
        "reply_count": reply_count
    }
    
    return templates.TemplateResponse(
        "pages/news_detail.html",
        {
            "request": request,
            "current_user": current_user,
            "article": article_data,
            "related_articles": related_articles,
            "page_title": f"{thread.title} - News"
        }
    )


# ==================== ADMIN NEWS ROUTES ====================

@admin_router.get("/", response_class=HTMLResponse)
async def admin_news_list(
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)
):
    """Admin news management page."""
    
    # Import here to avoid circular imports
    from app.crud import forum_category as crud_category
    from app.crud import forum_thread as crud_thread
    
    # Get the news category
    news_category = await crud_category.get_forum_category_by_slug(db, "news")
    if not news_category:
        # Create news category if it doesn't exist
        from app.schemas.forum import ForumCategoryCreate
        category_data = ForumCategoryCreate(
            name="News & Announcements",
            description="Official news, updates, and announcements from the AI Story App team.",
            slug="news",
            sort_order=5,
            icon="📰"
        )
        news_category = await crud_category.create_forum_category(db, category_data)
    
    # Get all news threads (sorted by latest)
    news_threads = await crud_thread.get_forum_threads(
        db,
        category_id=news_category.id,
        order_by="recent",
        limit=50
    )
    
    return templates.TemplateResponse(
        "pages/admin_news.html",
        {
            "request": request,
            "current_user": current_user,
            "news_category": news_category,
            "news_threads": news_threads,
            "page_title": "News Management - Admin"
        }
    )


@admin_router.get("/new", response_class=HTMLResponse)
async def admin_news_create_form(
    request: Request,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)
):
    """Admin create news article form."""
    
    from datetime import datetime
    
    return templates.TemplateResponse(
        "pages/admin_news_form.html",
        {
            "request": request,
            "current_user": current_user,
            "page_title": "Create News Article - Admin",
            "is_edit": False,
            "current_datetime": datetime.now()
        }
    )


@admin_router.post("/new", response_class=HTMLResponse)
async def admin_news_create(
    request: Request,
    title: str = Form(..., min_length=3, max_length=255),
    content: str = Form(..., min_length=10),
    is_pinned: bool = Form(False),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new news article."""
    
    try:
        # Import here to avoid circular imports
        from app.crud import forum_category as crud_category
        from app.schemas.forum import ForumThreadCreate
        from app.crud import forum_thread as crud_thread
        from app.crud import forum_post as crud_post
        from datetime import datetime
        
        # Get the news category
        news_category = await crud_category.get_forum_category_by_slug(db, "news")
        if not news_category:
            raise HTTPException(status_code=404, detail="News category not found")
        
        # Create the news thread
        thread_data = ForumThreadCreate(
            title=title.strip(),
            category_id=news_category.id,
            world_id=None,
            story_id=None,
            initial_post_content=content.strip(),
            initial_post_content_html=None
        )
        
        new_thread = await crud_thread.create_forum_thread(
            db, thread_data, current_user.id
        )
        
        # Pin the thread if requested
        if is_pinned:
            await crud_thread.toggle_thread_pin(db, new_thread.id, True)
        
        # Create the initial post
        from app.schemas.forum import ForumPostCreate
        initial_post = ForumPostCreate(
            content=content.strip(),
            content_html=None,
            thread_id=new_thread.id
        )
        
        await crud_post.create_forum_post(
            db, initial_post, current_user.id
        )
        
        return RedirectResponse(
            url="/admin/news?success=created",
            status_code=302
        )
        
    except Exception as e:
        return templates.TemplateResponse(
            "pages/admin_news_form.html",
            {
                "request": request,
                "current_user": current_user,
                "page_title": "Create News Article - Admin",
                "is_edit": False,
                "current_datetime": datetime.now(),
                "error_message": f"Error creating news article: {str(e)}",
                "form_data": {
                    "title": title,
                    "content": content,
                    "is_pinned": is_pinned
                }
            }
        )


@admin_router.get("/{thread_id}/edit", response_class=HTMLResponse)
async def admin_news_edit_form(
    request: Request,
    thread_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)
):
    """Admin edit news article form."""
    
    # Import here to avoid circular imports
    from app.crud import forum_thread as crud_thread
    from app.crud import forum_post as crud_post
    from datetime import datetime
    
    # Get the thread
    thread = await crud_thread.get_forum_thread(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="News article not found")
    
    # Get the first post (news content)
    posts = await crud_post.get_thread_posts(db, thread_id, limit=1)
    if not posts:
        raise HTTPException(status_code=404, detail="News content not found")
    
    first_post = posts[0]
    
    return templates.TemplateResponse(
        "pages/admin_news_form.html",
        {
            "request": request,
            "current_user": current_user,
            "page_title": f"Edit: {thread.title} - Admin",
            "is_edit": True,
            "thread": thread,
            "post": first_post,
            "current_datetime": datetime.now(),
            "form_data": {
                "title": thread.title,
                "content": first_post.content,
                "is_pinned": thread.is_pinned
            }
        }
    )


@admin_router.post("/{thread_id}/edit", response_class=HTMLResponse)
async def admin_news_edit(
    request: Request,
    thread_id: int,
    title: str = Form(..., min_length=3, max_length=255),
    content: str = Form(..., min_length=10),
    is_pinned: bool = Form(False),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)
):
    """Update a news article."""
    
    try:
        # Import here to avoid circular imports
        from app.crud import forum_thread as crud_thread
        from app.crud import forum_post as crud_post
        from app.schemas.forum import ForumThreadUpdate, ForumPostUpdate
        from datetime import datetime
        
        # Get the thread
        thread = await crud_thread.get_forum_thread(db, thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="News article not found")
        
        # Update thread
        thread_update = ForumThreadUpdate(
            title=title.strip(),
            is_pinned=is_pinned
        )
        await crud_thread.update_forum_thread(
            db, thread_id, thread_update, current_user.id, True
        )
        
        # Update the first post content
        posts = await crud_post.get_thread_posts(db, thread_id, limit=1)
        if posts:
            post_update = ForumPostUpdate(
                content=content.strip()
            )
            await crud_post.update_forum_post(
                db, posts[0].id, post_update, current_user.id, True
            )
        
        return RedirectResponse(
            url="/admin/news?success=updated",
            status_code=302
        )
        
    except Exception as e:
        # Get the thread again for form re-rendering
        thread = await crud_thread.get_forum_thread(db, thread_id)
        posts = await crud_post.get_thread_posts(db, thread_id, limit=1)
        first_post = posts[0] if posts else None
        
        return templates.TemplateResponse(
            "pages/admin_news_form.html",
            {
                "request": request,
                "current_user": current_user,
                "page_title": f"Edit: {thread.title} - Admin",
                "is_edit": True,
                "thread": thread,
                "post": first_post,
                "current_datetime": datetime.now(),
                "error_message": f"Error updating news article: {str(e)}",
                "form_data": {
                    "title": title,
                    "content": content,
                    "is_pinned": is_pinned
                }
            }
        )


@admin_router.post("/{thread_id}/delete")
async def admin_news_delete(
    thread_id: int,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a news article."""
    
    # Import here to avoid circular imports
    from app.crud import forum_thread as crud_thread
    
    success = await crud_thread.delete_forum_thread(
        db, thread_id, current_user.id, True, hard_delete=True
    )
    
    if success:
        return RedirectResponse(
            url="/admin/news?success=deleted",
            status_code=302
        )
    else:
        return RedirectResponse(
            url="/admin/news?error=delete_failed",
            status_code=302
        )