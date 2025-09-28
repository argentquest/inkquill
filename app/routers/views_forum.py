"""UI view routes for forum functionality."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.core.deps import get_db_session, get_current_user
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(tags=["Forum Views"])


@router.get("/forum", response_class=HTMLResponse, name="ui_forum_home")
async def ui_forum_home(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Display the forum home page with categories."""
    
    # Import here to avoid circular imports
    from app.crud import forum_category as crud_category
    
    # Get all active categories
    categories = await crud_category.get_forum_categories(db, include_inactive=False)
    
    # Calculate thread counts for each category
    category_data = []
    for category in categories:
        category_info = {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "slug": category.slug,
            "icon": category.icon,
            "thread_count": len([t for t in category.threads if not t.is_deleted]),
            "post_count": sum(t.post_count for t in category.threads if not t.is_deleted),
            "latest_thread": None
        }
        
        # Get latest thread in category
        if category.threads:
            active_threads = [t for t in category.threads if not t.is_deleted]
            if active_threads:
                latest_thread = max(active_threads, key=lambda x: x.last_post_at or x.created_at)
                category_info["latest_thread"] = {
                    "id": latest_thread.id,
                    "title": latest_thread.title,
                    "last_post_at": latest_thread.last_post_at or latest_thread.created_at,
                    "last_post_by": latest_thread.last_post_by.username if latest_thread.last_post_by else latest_thread.user.username
                }
        
        category_data.append(category_info)
    
    return templates.TemplateResponse(
        "pages/forum_home.html",
        {
            "request": request,
            "current_user": current_user,
            "categories": category_data,
            "page_title": "Community Forum"
        }
    )


@router.get("/forum/category/{category_slug}", response_class=HTMLResponse, name="ui_forum_category")
async def ui_forum_category(
    request: Request,
    category_slug: str,
    page: int = 1,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Display threads for a specific category."""
    
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Forum category route accessed: category_slug='{category_slug}', page={page}")
    
    # Import here to avoid circular imports
    from app.crud import forum_category as crud_category
    from app.crud import forum_thread as crud_thread
    
    try:
        # Get category
        category = await crud_category.get_forum_category_by_slug(db, category_slug)
        if not category:
            logger.warning(f"Category not found: '{category_slug}'")
            raise HTTPException(status_code=404, detail="Category not found")
        
        logger.info(f"Found category: {category.name} (id={category.id})")
    except Exception as e:
        logger.error(f"Error fetching category '{category_slug}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    try:
        # Get threads with pagination
        limit = 20
        skip = (page - 1) * limit
        threads = await crud_thread.get_forum_threads(
            db, 
            category_id=category.id, 
            skip=skip, 
            limit=limit,
            order_by="updated"
        )
        logger.info(f"Found {len(threads)} threads for category '{category_slug}'")
        
        # Prepare thread data
        thread_data = []
        for thread in threads:
            thread_info = {
                "id": thread.id,
                "title": thread.title,
                "slug": thread.slug,
                "user": thread.user.username if thread.user else "Unknown",
                "created_at": thread.created_at,
                "post_count": thread.post_count,
                "view_count": thread.view_count,
                "last_post_at": thread.last_post_at,
                "last_post_by": thread.last_post_by.username if thread.last_post_by else None,
                "is_pinned": thread.is_pinned,
                "is_locked": thread.is_locked,
                "world_name": thread.world.name if thread.world else None,
                "story_title": thread.story.title if thread.story else None
            }
            thread_data.append(thread_info)
    
    except Exception as e:
        logger.error(f"Error fetching threads for category '{category_slug}': {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
    logger.info(f"Successfully prepared {len(thread_data)} threads for display")
    
    return templates.TemplateResponse(
        "pages/forum_category.html",
        {
            "request": request,
            "current_user": current_user,
            "category": category,
            "threads": thread_data,
            "page": page,
            "has_next": len(threads) == limit,
            "page_title": f"{category.name} - Forum"
        }
    )


@router.get("/forum/thread/{thread_id}", response_class=HTMLResponse)
async def ui_forum_thread(
    request: Request,
    thread_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Display a forum thread with posts."""
    
    # Import here to avoid circular imports
    from app.crud import forum_thread as crud_thread
    from app.crud import forum_post as crud_post
    
    # Get thread (this will increment view count)
    thread = await crud_thread.get_forum_thread(db, thread_id, increment_view=True)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    
    # Get posts
    posts = await crud_post.get_thread_posts(db, thread_id, limit=100)
    
    # Check if user is subscribed
    is_subscribed = False
    if current_user:
        is_subscribed = await crud_thread.is_thread_subscribed(db, thread_id, current_user.id)
    
    # Get characters and locations from the linked world (if any) for reply form
    world_characters = []
    world_locations = []
    if thread.world_id and current_user:
        try:
            from app.crud import character as crud_character
            from app.crud import location as crud_location
            
            # Get characters and locations from the world
            world_characters = await crud_character.get_characters_by_world(db, thread.world_id)
            world_locations = await crud_location.get_locations_by_world(db, thread.world_id)
        except Exception:
            # If there's an error fetching world data, just continue without it
            pass
    
    # Prepare post data
    post_data = []
    for post in posts:
        user_vote = None
        if current_user:
            user_vote = await crud_post.get_user_vote_on_post(db, post.id, current_user.id)
        
        post_info = {
            "id": post.id,
            "content": post.content,
            "user": post.user.username if post.user else "Unknown",
            "user_display_name": post.user.display_name if post.user else None,
            "created_at": post.created_at,
            "edited_at": post.edited_at,
            "edit_count": post.edit_count,
            "upvote_count": post.upvote_count,
            "downvote_count": post.downvote_count,
            "score": post.score,
            "user_vote": user_vote.value if user_vote else None,
            "character_name": post.character.name if post.character else None,
            "location_name": post.location.name if post.location else None,
            "parent_post_id": post.parent_post_id,
            "can_edit": current_user and (current_user.id == post.user_id or current_user.is_admin),
            "can_delete": current_user and (current_user.id == post.user_id or current_user.is_admin)
        }
        post_data.append(post_info)
    
    return templates.TemplateResponse(
        "pages/forum_thread.html",
        {
            "request": request,
            "current_user": current_user,
            "thread": thread,
            "posts": post_data,
            "is_subscribed": is_subscribed,
            "can_edit_thread": current_user and (current_user.id == thread.user_id or current_user.is_admin),
            "can_post": current_user and not thread.is_locked,
            "world_characters": world_characters,
            "world_locations": world_locations,
            "page_title": f"{thread.title} - Forum"
        }
    )


@router.get("/forum/new-thread", response_class=HTMLResponse)
async def ui_new_thread_form(
    request: Request,
    category_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Display the new thread creation form."""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Import here to avoid circular imports
    from app.crud import forum_category as crud_category
    from app.crud import world as crud_world
    from app.crud import story as crud_story
    
    # Get all categories
    categories = await crud_category.get_forum_categories(db, include_inactive=False)
    
    # Get user's worlds and stories for optional linking
    user_worlds = await crud_world.get_worlds_by_user(db, current_user.id)
    user_stories = await crud_story.get_stories_by_user(db, current_user.id)
    
    return templates.TemplateResponse(
        "pages/forum_new_thread.html",
        {
            "request": request,
            "current_user": current_user,
            "categories": categories,
            "selected_category_id": category_id,
            "user_worlds": user_worlds,
            "user_stories": user_stories,
            "page_title": "Create New Thread - Forum"
        }
    )


@router.post("/forum/new-thread", response_class=HTMLResponse)
async def ui_create_thread(
    request: Request,
    category_id: int = Form(...),
    title: str = Form(..., min_length=3, max_length=255),
    content: str = Form(..., min_length=10),
    world_id: str = Form(""),
    story_id: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Handle thread creation form submission."""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    try:
        # Import here to avoid circular imports
        from app.schemas.forum import ForumThreadCreate
        from app.crud import forum_thread as crud_thread
        from app.crud import forum_post as crud_post
        
        # Convert empty strings to None for optional foreign keys
        world_id_int = None
        story_id_int = None
        
        try:
            if world_id and world_id.strip():
                world_id_int = int(world_id)
        except (ValueError, TypeError):
            world_id_int = None
            
        try:
            if story_id and story_id.strip():
                story_id_int = int(story_id)
        except (ValueError, TypeError):
            story_id_int = None
        
        # Create thread data
        thread_data = ForumThreadCreate(
            title=title.strip(),
            category_id=category_id,
            world_id=world_id_int,
            story_id=story_id_int,
            initial_post_content=content.strip(),
            initial_post_content_html=None
        )
        
        # Create the thread
        new_thread = await crud_thread.create_forum_thread(
            db, thread_data, current_user.id
        )
        
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
        
        # Redirect to the new thread
        return RedirectResponse(
            url=f"/forum/thread/{new_thread.id}",
            status_code=302
        )
        
    except Exception as e:
        # Import here to avoid circular imports
        from app.crud import forum_category as crud_category
        from app.crud import world as crud_world
        from app.crud import story as crud_story
        
        # Get data for re-rendering form
        categories = await crud_category.get_forum_categories(db, include_inactive=False)
        user_worlds = await crud_world.get_worlds_by_user(db, current_user.id)
        user_stories = await crud_story.get_stories_by_user(db, current_user.id)
        
        error_message = f"Error creating thread: {str(e)}"
        
        return templates.TemplateResponse(
            "pages/forum_new_thread.html",
            {
                "request": request,
                "current_user": current_user,
                "categories": categories,
                "selected_category_id": category_id,
                "user_worlds": user_worlds,
                "user_stories": user_stories,
                "error_message": error_message,
                "form_data": {
                    "title": title,
                    "content": content,
                    "world_id": world_id if world_id and world_id.strip() else "",
                    "story_id": story_id if story_id and story_id.strip() else ""
                },
                "page_title": "Create New Thread - Forum"
            }
        )


@router.get("/forum/category/{category_slug}/new-thread", response_class=HTMLResponse)
async def ui_new_thread_in_category(
    request: Request,
    category_slug: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Redirect to new thread form with category pre-selected."""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    # Import here to avoid circular imports
    from app.crud import forum_category as crud_category
    
    # Get category
    category = await crud_category.get_forum_category_by_slug(db, category_slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return RedirectResponse(
        url=f"/forum/new-thread?category_id={category.id}",
        status_code=302
    )


@router.post("/forum/thread/{thread_id}/reply", response_class=HTMLResponse)
async def ui_reply_to_thread(
    request: Request,
    thread_id: int,
    content: str = Form(..., min_length=3),
    parent_post_id: str = Form(""),
    character_id: str = Form(""),
    location_id: str = Form(""),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Handle reply form submission."""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=302)
    
    try:
        # Import here to avoid circular imports
        from app.schemas.forum import ForumPostCreate
        from app.crud import forum_post as crud_post
        from app.crud import forum_thread as crud_thread
        
        # Check if thread exists and is not locked
        thread = await crud_thread.get_forum_thread(db, thread_id)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        
        if thread.is_locked:
            raise HTTPException(status_code=403, detail="Thread is locked")
        
        # Convert empty strings to None for optional foreign keys
        parent_post_id_int = None
        character_id_int = None
        location_id_int = None
        
        try:
            if parent_post_id and parent_post_id.strip():
                parent_post_id_int = int(parent_post_id)
        except (ValueError, TypeError):
            parent_post_id_int = None
            
        try:
            if character_id and character_id.strip():
                character_id_int = int(character_id)
        except (ValueError, TypeError):
            character_id_int = None
            
        try:
            if location_id and location_id.strip():
                location_id_int = int(location_id)
        except (ValueError, TypeError):
            location_id_int = None
        
        # Create the post
        post_data = ForumPostCreate(
            content=content.strip(),
            content_html=None,
            thread_id=thread_id,
            parent_post_id=parent_post_id_int,
            character_id=character_id_int,
            location_id=location_id_int
        )
        
        new_post = await crud_post.create_forum_post(
            db, post_data, current_user.id
        )
        
        # Redirect to the thread with an anchor to the new post
        return RedirectResponse(
            url=f"/forum/thread/{thread_id}#post-{new_post.id}",
            status_code=302
        )
        
    except Exception as e:
        # Redirect back to thread with error (we'll add error handling to the thread view)
        return RedirectResponse(
            url=f"/forum/thread/{thread_id}?error=reply_failed",
            status_code=302
        )