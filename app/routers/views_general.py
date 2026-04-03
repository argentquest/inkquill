"""API routes for views general."""

# /story_app/app/routers/views_general.py

from fastapi import APIRouter, Request, Depends, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Optional, Dict, Any 
import logging 

# --- Core Application Imports ---
from app.core.deps import get_db_session, get_current_user_with_anonymous_support, get_current_active_user 
from app.models.user import User
from app.models.world import World
from app.models.story import Story
from app.core.config import settings
from app.core import security as core_security 
from app.crud import user as crud_user

logger = logging.getLogger(__name__) 

router = APIRouter(
    prefix="/ui", 
    tags=["ui-general-views"], 
)

# Create templates instance with proper globals
templates = Jinja2Templates(directory="app/templates")
templates.env.globals["google_analytics_id"] = settings.GOOGLE_ANALYTICS_ID
templates.env.globals["google_analytics_consent_mode"] = settings.GOOGLE_ANALYTICS_CONSENT_MODE
templates.env.globals["cookie_consent_required"] = settings.COOKIE_CONSENT_REQUIRED


# --- General UI Page Endpoints ---

@router.get("/", response_class=HTMLResponse, name="ui_home") 
async def home_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support),
    db: AsyncSession = Depends(get_db_session)
):
    """Handle GET /."""
    logger.info(f"Serving home page. User: {current_user.username if current_user else 'Anonymous'}")
    
    # Get latest news articles
    news_articles = []
    try:
        # Import here to avoid circular imports
        from app.crud import forum_category as crud_category
        from app.crud import forum_thread as crud_thread
        from app.crud import forum_post as crud_post
        
        # Get the news category
        news_category = await crud_category.get_forum_category_by_slug(db, "news")
        if news_category:
            # Get latest 10 news threads
            news_threads = await crud_thread.get_forum_threads(
                db,
                category_id=news_category.id,
                order_by="recent",
                limit=10
            )
            
            # Get first post content for each thread
            for thread in news_threads:
                posts = await crud_post.get_thread_posts(db, thread.id, limit=1)
                content = posts[0].content if posts else ""
                # Limit content to first 200 characters for preview
                content_preview = content[:200] + "..." if len(content) > 200 else content
                
                news_articles.append({
                    "id": thread.id,
                    "title": thread.title,
                    "content_preview": content_preview,
                    "created_at": thread.created_at,
                    "author": thread.user.username if thread.user else "Admin",
                    "is_pinned": thread.is_pinned,
                    "view_count": thread.view_count
                })
        
    except Exception as e:
        logger.warning(f"Error fetching news articles for home page: {e}")
        # Continue without news if there's an error
    
    # Get AI Chat Worlds (worlds available for public chat)
    ai_chat_worlds = []
    try:
        from sqlalchemy import func
        
        # Get 3 random worlds that are available for public chat
        result = await db.execute(
            select(World)
            .options(
                selectinload(World.current_image),
                selectinload(World.characters),
                selectinload(World.locations),
                selectinload(World.lore_items)
            )
            .where(World.is_free_chat_enabled == True)
            .order_by(func.random())  # Random selection for variety
            .limit(3)
        )
        worlds = result.scalars().all()
        
        for world in worlds:
            ai_chat_worlds.append({
                "id": world.id,
                "name": world.name,
                "description": world.description,
                "image_url": world.current_image.blob_url if world.current_image else None,
                "element_count": {
                    "characters": len(world.characters) if world.characters else 0,
                    "locations": len(world.locations) if world.locations else 0,
                    "lore_items": len(world.lore_items) if world.lore_items else 0
                },
                "created_at": world.created_at
            })
        
        logger.info(f"Found {len(ai_chat_worlds)} AI Chat Worlds for home page")
        if ai_chat_worlds:
            logger.info(f"AI Chat Worlds: {[world['name'] for world in ai_chat_worlds]}")
        else:
            logger.warning("No AI Chat Worlds found - check if any worlds have is_free_chat_enabled=True")
        
    except Exception as e:
        logger.warning(f"Error fetching AI Chat Worlds for home page: {e}")
        # Continue without AI Chat Worlds if there's an error
    
    # Get recent published stories
    recent_published_stories = []
    try:
        from app.models.published_story import PublishedStory
        from app.models.story import Story  # Add this import!
        from sqlalchemy import func
        
        logger.info("Starting to fetch published stories for home page")
        
        # First, let's check how many published stories exist in total
        count_all = await db.execute(
            select(func.count()).select_from(PublishedStory).where(PublishedStory.is_public == True)
        )
        total_published = count_all.scalar()
        logger.info(f"Total public published stories: {total_published}")
        
        # Count stories with images
        count_with_images = await db.execute(
            select(func.count())
            .select_from(PublishedStory)
            .join(PublishedStory.story)
            .where(
                PublishedStory.is_public == True,
                Story.current_image_id.isnot(None)
            )
        )
        total_with_images = count_with_images.scalar()
        logger.info(f"Published stories with images: {total_with_images}")
        
        # Get 5 random stories that have images
        stories_query = (
            select(PublishedStory)
            .join(PublishedStory.story)
            .options(
                selectinload(PublishedStory.story).selectinload(Story.current_image), 
                selectinload(PublishedStory.publisher),
                selectinload(PublishedStory.ratings)
            )
            .where(
                PublishedStory.is_public == True,
                Story.current_image_id.isnot(None)  # Only stories with images
            )
            .order_by(func.random())
            .limit(5)
        )
        
        # Execute query
        result = await db.execute(stories_query)
        published_stories = result.scalars().all()
        
        logger.info(f"Found {len(published_stories)} published stories with images")
        
        for published_story in published_stories:
            # Get story image URL - we know current_image exists because of our query filter
            # Use the image_url property from the Story model
            story_image_url = None
            if published_story.story and published_story.story.current_image:
                story_image_url = published_story.story.current_image.blob_url
                logger.debug(f"Story {published_story.id} has image URL: {story_image_url}")
            
            # Get rating count
            rating_count = len(published_story.ratings) if published_story.ratings else 0
            
            recent_published_stories.append({
                "id": published_story.id,
                "title": published_story.title,
                "description": published_story.description,
                "published_url": published_story.published_url,
                "published_at": published_story.published_at,
                "author": published_story.publisher.username if published_story.publisher else "Anonymous",
                "view_count": published_story.view_count,
                "word_count": published_story.word_count,
                "image_url": story_image_url,
                "average_rating": published_story.average_rating,
                "rating_count": rating_count
            })
        
        logger.info(f"Processed {len(recent_published_stories)} stories for display")
        
    except Exception as e:
        logger.error(f"Error fetching recent published stories for home page: {e}", exc_info=True)
        # Continue without published stories if there's an error
    
    # Get recent generated images with randomization
    recent_images = []
    try:
        from app.models.generated_image import GeneratedImage
        from app.models.character import Character
        from app.models.location import Location
        from app.models.lore_item import LoreItem
        from app.models.act import Act
        from app.models.scene import Scene
        from app.models.story import Story
        from sqlalchemy import union_all
        import random as py_random
        
        # Get images and randomize the order
        result = await db.execute(
            select(GeneratedImage)
            .options(selectinload(GeneratedImage.owner))
            .order_by(func.random())  # Randomize order
            .limit(10)
        )
        images = result.scalars().all()
        
        for image in images:
            # Get element details based on type
            element_title = "Unknown"
            element_context = None
            
            try:
                if image.element_type == "character":
                    char_result = await db.execute(
                        select(Character)
                        .options(selectinload(Character.world))
                        .where(Character.id == image.associated_element_id)
                    )
                    character = char_result.scalar_one_or_none()
                    if character:
                        element_title = character.name
                        element_context = f"Character from {character.world.name}" if character.world else "Character"
                
                elif image.element_type == "location":
                    loc_result = await db.execute(
                        select(Location)
                        .options(selectinload(Location.world))
                        .where(Location.id == image.associated_element_id)
                    )
                    location = loc_result.scalar_one_or_none()
                    if location:
                        element_title = location.name
                        element_context = f"Location from {location.world.name}" if location.world else "Location"
                
                elif image.element_type == "lore_item":
                    lore_result = await db.execute(
                        select(LoreItem)
                        .options(selectinload(LoreItem.world))
                        .where(LoreItem.id == image.associated_element_id)
                    )
                    lore_item = lore_result.scalar_one_or_none()
                    if lore_item:
                        element_title = lore_item.title
                        element_context = f"Lore from {lore_item.world.name}" if lore_item.world else "Lore Item"
                
                elif image.element_type == "act":
                    act_result = await db.execute(
                        select(Act)
                        .options(selectinload(Act.story))
                        .where(Act.id == image.associated_element_id)
                    )
                    act = act_result.scalar_one_or_none()
                    if act:
                        element_title = act.title or f"Act {act.act_number}"
                        element_context = f"Act from {act.story.title}" if act.story else "Story Act"
                
                elif image.element_type == "scene":
                    scene_result = await db.execute(
                        select(Scene)
                        .options(selectinload(Scene.act).selectinload(Act.story))
                        .where(Scene.id == image.associated_element_id)
                    )
                    scene = scene_result.scalar_one_or_none()
                    if scene:
                        element_title = scene.title or f"Scene {scene.scene_number}"
                        element_context = f"Scene from {scene.act.story.title}" if scene.act and scene.act.story else "Story Scene"
                
            except Exception as e:
                logger.warning(f"Error fetching element details for image {image.id}: {e}")
            
            recent_images.append({
                "id": image.id,
                "image_url": image.blob_url,
                "prompt": image.prompt,
                "element_type": image.element_type,
                "element_title": element_title,
                "element_context": element_context,
                "created_at": image.created_at,
                "owner": image.owner.username if image.owner else "Anonymous"
            })
        
    except Exception as e:
        logger.warning(f"Error fetching recent images for home page: {e}")
        # Continue without images if there's an error
    
    # Get recent forum posts
    recent_forum_posts = []
    try:
        from app.models.forum import ForumPost, ForumThread, ForumCategory
        
        # Get 5 most recent forum posts with thread and category info
        result = await db.execute(
            select(ForumPost)
            .join(ForumThread)
            .join(ForumCategory)
            .where(ForumPost.is_deleted == False)
            .where(ForumThread.is_deleted == False)
            .where(ForumCategory.is_active == True)
            .options(
                selectinload(ForumPost.user),
                selectinload(ForumPost.thread).selectinload(ForumThread.category),
                selectinload(ForumPost.thread).selectinload(ForumThread.user)
            )
            .order_by(ForumPost.created_at.desc())
            .limit(5)
        )
        posts = result.scalars().all()
        
        for post in posts:
            # Get content preview
            content_preview = post.content[:200] + "..." if len(post.content) > 200 else post.content
            
            recent_forum_posts.append({
                "id": post.id,
                "content_preview": content_preview,
                "created_at": post.created_at,
                "author": post.user.username if post.user else "Anonymous",
                "thread_id": post.thread.id if post.thread else None,
                "thread_title": post.thread.title if post.thread else "Unknown Thread",
                "thread_is_pinned": post.thread.is_pinned if post.thread else False,
                "category_name": post.thread.category.name if post.thread and post.thread.category else "General"
            })
        
    except Exception as e:
        logger.warning(f"Error fetching recent forum posts for home page: {e}")
        # Continue without forum posts if there's an error
    
    # Get recent blog posts
    blog_posts = []
    try:
        from app.services.blog_service import blog_service
        
        # Get 5 most recent published blog posts
        blog_posts = await blog_service.get_published_posts(
            db=db,
            skip=0,
            limit=5
        )
        
        logger.info(f"Found {len(blog_posts)} blog posts for home page")
        
    except Exception as e:
        logger.warning(f"Error fetching blog posts for home page: {e}")
        # Continue without blog posts if there's an error
    
    # Get CTA content for all home page positions
    home_ctas = {}
    try:
        from app.crud.cta_content import get_active_ctas_for_position
        from app.models.cta_content import CTAPosition
        
        # Define all home page positions
        home_positions = [
            CTAPosition.HOME_MAIN_TOP,
            CTAPosition.HOME_WELCOME_TOP,
            CTAPosition.HOME_WELCOME_BOTTOM,
            CTAPosition.HOME_QUICK_ACTIONS_TOP,
            CTAPosition.HOME_QUICK_ACTIONS_BOTTOM,
            CTAPosition.HOME_LOGIN_REGISTER_TOP,
            CTAPosition.HOME_LOGIN_REGISTER_BOTTOM,
            CTAPosition.HOME_BLOG_SECTION_TOP,
            CTAPosition.HOME_BLOG_SECTION_BOTTOM,
            CTAPosition.HOME_MAIN_BOTTOM,
            CTAPosition.HOME_SIDEBAR_TOP,
            CTAPosition.HOME_SIDEBAR_BOTTOM,
            CTAPosition.HOME_AI_CHAT_WORLDS_TOP,
            CTAPosition.HOME_AI_CHAT_WORLDS_BOTTOM,
            CTAPosition.HOME_PUBLISHED_STORIES_TOP,
            CTAPosition.HOME_PUBLISHED_STORIES_BOTTOM,
            CTAPosition.HOME_GENERATED_IMAGES_TOP,
            CTAPosition.HOME_GENERATED_IMAGES_BOTTOM
        ]
        
        # Fetch CTAs for each position
        for position in home_positions:
            try:
                ctas = await get_active_ctas_for_position(
                    db=db,
                    position=position,
                    user=current_user
                )
                
                # Convert to dict for template rendering
                position_key = position.value.lower()
                home_ctas[position_key] = [cta.to_dict() for cta in ctas]
                logger.info(f"Found {len(ctas)} CTAs for position {position.value}")
                
            except Exception as e:
                logger.warning(f"Error fetching CTAs for position {position.value}: {e}")
                home_ctas[position.value.lower()] = []
        
        logger.info(f"Loaded CTA content for home page: {list(home_ctas.keys())}")
        
    except Exception as e:
        logger.warning(f"Error fetching CTA content for home page: {e}")
        # Continue without CTAs if there's an error
        home_ctas = {
            "home_sidebar_top": [],
            "home_main_top": [],
            "home_main_bottom": [],
            "home_sidebar_bottom": []
        }
    
    return templates.TemplateResponse(
        "pages/index.html",
        {
            "request": request, 
            "current_user": current_user, 
            "project_name": settings.APP_PROJECT_NAME,
            "news_articles": news_articles,
            "ai_chat_worlds": ai_chat_worlds,
            "recent_published_stories": recent_published_stories,
            "recent_images": recent_images,
            "recent_forum_posts": recent_forum_posts,
            "blog_posts": blog_posts,
            "home_ctas": home_ctas
        }
    )

@router.get("/login", response_class=HTMLResponse, name="ui_login_form") 
async def login_form(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    user: Optional[User] = Depends(get_current_user_with_anonymous_support)
): 
    """Handle GET /login."""
    if user:
        logger.info(f"User {user.username} already logged in, redirecting to stories from login page.")
        try:
            redirect_url = str(request.url_for('ui_list_stories'))
        except Exception: 
            logger.error("CRITICAL: Could not find route named 'ui_list_stories' for redirect.")
            redirect_url = "/ui/stories"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    logger.info("Serving login page for anonymous user.")
    return templates.TemplateResponse("pages/login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse, name="ui_register_form") 
async def register_form(request: Request, next: Optional[str] = Query(None)):
    """Handle GET /register."""
    logger.info("Serving registration page.")
    return templates.TemplateResponse("pages/register.html", {"request": request, "next_step": next})

@router.get("/forgot-password", response_class=HTMLResponse, name="ui_forgot_password_form") 
async def forgot_password_form(request: Request):
    """Handle GET /forgot-password."""
    logger.info("Serving forgot password page.")
    return templates.TemplateResponse("pages/forgot_password.html", {"request": request})

@router.get("/reset-password", response_class=HTMLResponse, name="ui_reset_password_form") 
async def reset_password_form(request: Request, token: str = Query(...)):
    """Handle GET /reset-password."""
    logger.info(f"Serving reset password page for token: {token[:8]}...")
    return templates.TemplateResponse("pages/reset_password.html", {"request": request, "token": token})

@router.get("/user-guide", response_class=HTMLResponse, name="ui_user_guide")
async def user_guide_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support)
):
    """Handle GET /user-guide."""
    logger.info(f"User '{current_user.username if current_user else 'Anonymous'}' accessing user guide - redirecting to help popup.")
    
    # Return a page that automatically opens the help popup with the introduction topic
    return templates.TemplateResponse(
        "pages/user_guide_redirect.html",
        {
            "request": request, 
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME
        }
    )

@router.get("/terms-of-service", response_class=HTMLResponse, name="ui_terms_of_service")
async def terms_of_service_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support)
):
    """Handle GET /terms-of-service."""
    logger.info(f"User '{current_user.username if current_user else 'Anonymous'}' accessing terms of service.")
    return templates.TemplateResponse(
        "pages/terms_of_service.html",
        {
            "request": request, 
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME
        }
    )

@router.get("/my-account", response_class=HTMLResponse, name="ui_my_account")
async def my_account_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support),
    db: AsyncSession = Depends(get_db_session)
):
    """User account management page."""
    if not current_user:
        logger.warning("Anonymous user attempted to access my account page")
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    # Get user statistics
    from app.crud.user import get_user_statistics
    user_stats = await get_user_statistics(db, current_user.id)
    
    logger.info(f"User '{current_user.username}' accessing my account page")
    return templates.TemplateResponse(
        "pages/my_account.html",
        {
            "request": request, 
            "current_user": current_user,
            "user_stats": user_stats,
            "project_name": settings.APP_PROJECT_NAME
        }
    )

@router.post("/my-account/update-profile")
async def update_profile(
    request: Request,
    profile_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update user profile information"""
    from app.crud.user import update_user, get_user_by_username, get_user_by_email
    from app.schemas.user import UserUpdate
    
    try:
        # Validate username uniqueness if being changed
        if "username" in profile_data and profile_data["username"] != current_user.username:
            existing_user = await get_user_by_username(db, profile_data["username"])
            if existing_user:
                return {"success": False, "message": "Username already taken"}
        
        # Validate email uniqueness if being changed
        if "email" in profile_data and profile_data["email"] != current_user.email:
            existing_user = await get_user_by_email(db, profile_data["email"])
            if existing_user:
                return {"success": False, "message": "Email already in use"}
        
        # Update user profile
        user_update = UserUpdate(**profile_data)
        updated_user = await update_user(db, current_user, user_update)
        await db.commit()
        
        logger.info(f"User '{current_user.username}' updated profile")
        return {"success": True, "message": "Profile updated successfully"}
        
    except Exception as e:
        logger.error(f"Error updating profile for user {current_user.username}: {str(e)}")
        await db.rollback()
        return {"success": False, "message": "Failed to update profile"}

@router.post("/my-account/change-password")
async def change_password(
    request: Request,
    password_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Change user password"""
    from app.core.security import verify_password, get_password_hash
    from app.crud.user import update_user
    from app.schemas.user import UserUpdate
    
    try:
        # Verify current password
        if not verify_password(password_data["current_password"], current_user.hashed_password):
            return {"success": False, "message": "Current password is incorrect"}
        
        # Verify new passwords match
        if password_data["new_password"] != password_data["confirm_password"]:
            return {"success": False, "message": "New passwords do not match"}
        
        # Update password
        user_update = UserUpdate(password=password_data["new_password"])
        updated_user = await update_user(db, current_user, user_update)
        await db.commit()
        
        logger.info(f"User '{current_user.username}' changed password")
        return {"success": True, "message": "Password changed successfully"}
        
    except Exception as e:
        logger.error(f"Error changing password for user {current_user.username}: {str(e)}")
        await db.rollback()
        return {"success": False, "message": "Failed to change password"}

@router.get("/admin", response_class=HTMLResponse, name="ui_admin_dashboard")
async def admin_dashboard_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support)
):
    """Admin dashboard - main admin page with overview and quick access."""
    if not current_user:
        logger.warning("Anonymous user attempted to access admin dashboard")
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    if not current_user.is_admin:
        logger.warning(f"Non-admin user '{current_user.username}' attempted to access admin dashboard")
        return RedirectResponse(url="/ui/", status_code=status.HTTP_303_SEE_OTHER)
    
    logger.info(f"Admin user '{current_user.username}' accessing admin dashboard")
    return templates.TemplateResponse(
        "pages/admin_dashboard.html",
        {
            "request": request, 
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME
        }
    )

@router.get("/admin/users", response_class=HTMLResponse, name="ui_admin_users")
async def admin_users_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support)
):
    """Admin-only page for managing users and impersonation."""
    if not current_user:
        logger.warning("Anonymous user attempted to access admin users page")
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    if not current_user.is_admin:
        logger.warning(f"Non-admin user '{current_user.username}' attempted to access admin users page")
        return RedirectResponse(url="/ui/", status_code=status.HTTP_303_SEE_OTHER)
    
    logger.info(f"Admin user '{current_user.username}' accessing admin users page")
    return templates.TemplateResponse(
        "pages/admin_users.html",
        {
            "request": request, 
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME
        }
    )

@router.get("/analytics-test", response_class=HTMLResponse, name="ui_analytics_test")
async def analytics_test_page(
    request: Request,
    nav_layout: Optional[str] = None,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support)
):
    """Analytics testing page - for testing GA4 implementation"""
    logger.info(f"User '{current_user.username if current_user else 'Anonymous'}' accessing analytics test page")
    
    # Handle navigation layout parameter
    response = templates.TemplateResponse(
        "pages/analytics_test.html",
        {
            "request": request, 
            "current_user": current_user,
            "project_name": settings.APP_PROJECT_NAME,
            "google_analytics_id": settings.GOOGLE_ANALYTICS_ID
        }
    )
    
    # Set nav_layout cookie if parameter is provided
    if nav_layout in ['topbar', 'sidebar']:
        response.set_cookie(
            key="nav_layout", 
            value=nav_layout, 
            max_age=30*24*60*60,  # 30 days
            httponly=False,  # Allow JavaScript access
            secure=False,  # Set to True in production with HTTPS
            samesite="lax"
        )
        logger.info(f"Set nav_layout cookie to: {nav_layout}")
    
    return response

@router.get("/admin/users/{user_id}/edit", response_class=HTMLResponse, name="ui_edit_user")
async def edit_user_page(
    user_id: int,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support),
    db: AsyncSession = Depends(get_db_session)
):
    """Admin-only page for editing a specific user."""
    if not current_user:
        logger.warning("Anonymous user attempted to access edit user page")
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    if not current_user.is_admin:
        logger.warning(f"Non-admin user '{current_user.username}' attempted to access edit user page")
        return RedirectResponse(url="/ui/", status_code=status.HTTP_303_SEE_OTHER)
    
    # Get the user to edit
    user = await crud_user.get_user(db, user_id=user_id)
    if not user:
        logger.warning(f"Admin '{current_user.username}' tried to edit non-existent user ID: {user_id}")
        return RedirectResponse(url="/ui/admin/users", status_code=status.HTTP_303_SEE_OTHER)
    
    # Load relationship counts to avoid lazy loading in template
    from sqlalchemy import func
    from app.models.story import Story
    from app.models.uploaded_document import UploadedDocument
    from app.models.ai_cost_log import AICallLog
    from datetime import datetime, timedelta, timezone
    
    # Get user's stories with world information to avoid lazy loading
    user_stories = await db.execute(
        select(Story).options(selectinload(Story.world)).where(Story.user_id == user_id).order_by(Story.updated_at.desc()).limit(10)
    )
    stories_list = user_stories.scalars().all()
    
    user_worlds = await db.execute(
        select(World).where(World.user_id == user_id).order_by(World.updated_at.desc()).limit(10)
    )
    worlds_list = user_worlds.scalars().all()
    
    # Get total counts
    stories_count = await db.scalar(
        select(func.count(Story.id)).where(Story.user_id == user_id)
    ) or 0
    
    worlds_count = await db.scalar(
        select(func.count(World.id)).where(World.user_id == user_id)
    ) or 0
    
    documents_count = await db.scalar(
        select(func.count(UploadedDocument.id)).where(UploadedDocument.user_id == user_id)
    ) or 0
    
    # Get AI usage statistics for different time periods, grouped by call_type
    now = datetime.now(timezone.utc)
    
    async def get_ai_stats_by_period_and_type(time_filter):
        stats = await db.execute(
            select(
                AICallLog.call_type,
                func.sum(AICallLog.total_tokens).label('total_tokens'),
                func.sum(AICallLog.calculated_cost_usd).label('total_cost'),
                func.count(AICallLog.id).label('call_count')
            ).where(
                AICallLog.user_id == user_id,
                AICallLog.created_at >= time_filter
            ).group_by(AICallLog.call_type)
        )
        
        result = {}
        total_tokens = 0
        total_cost = 0.0
        total_calls = 0
        
        for row in stats:
            call_type = row.call_type
            tokens = int(row.total_tokens or 0)
            cost = float(row.total_cost or 0.0)
            calls = int(row.call_count or 0)
            
            result[call_type] = {
                'tokens': tokens,
                'cost': cost,
                'calls': calls
            }
            
            total_tokens += tokens
            total_cost += cost
            total_calls += calls
        
        # Add totals
        result['_totals'] = {
            'tokens': total_tokens,
            'cost': total_cost,
            'calls': total_calls
        }
        
        return result
    
    # Get statistics for each time period
    last_24h = now - timedelta(hours=24)
    last_7d = now - timedelta(days=7)
    last_30d = now - timedelta(days=30)
    
    ai_usage_stats = {
        '24h': await get_ai_stats_by_period_and_type(last_24h),
        '7d': await get_ai_stats_by_period_and_type(last_7d),
        '30d': await get_ai_stats_by_period_and_type(last_30d)
    }
    
    # Add period totals for easy access in template
    period_totals = {
        '24h': ai_usage_stats['24h']['_totals'] if '_totals' in ai_usage_stats['24h'] else {'tokens': 0, 'cost': 0.0, 'calls': 0},
        '7d': ai_usage_stats['7d']['_totals'] if '_totals' in ai_usage_stats['7d'] else {'tokens': 0, 'cost': 0.0, 'calls': 0},
        '30d': ai_usage_stats['30d']['_totals'] if '_totals' in ai_usage_stats['30d'] else {'tokens': 0, 'cost': 0.0, 'calls': 0}
    }
    
    logger.info(f"Admin user '{current_user.username}' accessing edit page for user '{user.username}'")
    return templates.TemplateResponse(
        "pages/edit_user.html",
        {
            "request": request, 
            "current_user": current_user,
            "user": user,
            "stories_list": stories_list,
            "worlds_list": worlds_list,
            "stories_count": stories_count,
            "worlds_count": worlds_count,
            "documents_count": documents_count,
            "ai_usage_stats": ai_usage_stats,
            "period_totals": period_totals,
            "project_name": settings.APP_PROJECT_NAME
        }
    )

# --- FIX: Moved logout endpoint here from auth.py ---
@router.post("/logout", name="logout", summary="Logout user by clearing the access token cookie.")
async def logout(request: Request): 
    """Handle POST /logout."""
    logger.info("User logging out via UI router.")
    try: 
        home_url = str(request.url_for('ui_home')) + "?logged_out=true"
    except Exception: 
        home_url = "/ui/?logged_out=true"
        logger.warning("Could not resolve 'ui_home' for logout redirect, defaulting to '/ui/'.")
    
    response = RedirectResponse(url=home_url, status_code=status.HTTP_303_SEE_OTHER)
    logger.info(f"Deleting access_token cookie. Path: '/', Secure: {settings.APP_ENV.lower() == 'production'}")
    response.delete_cookie(
        key="access_token", 
        path="/", 
        domain=None,
        secure=settings.APP_ENV.lower() == "production", 
        httponly=True, 
        samesite="Lax"
    )
    
    # Also clear anonymous user cookies to ensure fresh anonymous session
    logger.info("Clearing anonymous user cookies to ensure fresh session")
    response.delete_cookie(
        key="anon_user_id",
        path="/",
        domain=None,
        secure=settings.APP_ENV.lower() == "production",
        httponly=True,
        samesite="Lax"
    )
    response.delete_cookie(
        key="anon_session",
        path="/",
        domain=None,
        secure=settings.APP_ENV.lower() == "production", 
        httponly=True,
        samesite="Lax"
    )
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    logger.info(f"Logout successful. Redirecting to: {home_url}")
    return response
# --- END FIX ---

@router.get("/privacy", response_class=HTMLResponse, name="ui_privacy")
async def privacy_page(request: Request):
    """Privacy Policy page"""
    return templates.TemplateResponse(
        "pages/privacy.html",
        {
            "request": request,
            "project_name": settings.APP_PROJECT_NAME
        }
    )

@router.get("/terms", response_class=HTMLResponse, name="ui_terms")
async def terms_page(request: Request):
    """Terms of Service page"""
    return templates.TemplateResponse(
        "pages/terms.html",
        {
            "request": request,
            "project_name": settings.APP_PROJECT_NAME
        }
    )


@router.get("/do_interview", response_class=HTMLResponse, name="ui_do_interview")
async def do_interview(
    request: Request, 
    id: str = Query(..., description="Interview ID to trigger"),
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support)
):
    """Trigger interview modal with specific interview ID"""
    context = {
        "request": request,
        "current_user": current_user,
        "trigger_interview": True,
        "interview_id": id,
        "page_title": f"Interview: {id}"
    }
    return templates.TemplateResponse("pages/interview_trigger.html", context)


@router.get("/components-demo", response_class=HTMLResponse, name="ui_components_demo")
async def components_demo(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support)
):
    """Demo page showcasing Tabler UI components"""
    context = {
        "request": request,
        "current_user": current_user,
        "page_title": "Tabler Components Demo"
    }
    return templates.TemplateResponse("components/examples/component_demo.html", context)


@router.get("/welcome-interview", response_class=HTMLResponse, name="ui_welcome_interview")
async def welcome_interview_page(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support)
):
    """Welcome interview page for new users"""
    logger.info(f"User '{current_user.username if current_user else 'Anonymous'}' accessing welcome interview page")
    
    context = {
        "request": request,
        "current_user": current_user,
        "project_name": settings.APP_PROJECT_NAME
    }
    return templates.TemplateResponse("pages/welcome_interview.html", context)


@router.get("/search", response_class=HTMLResponse, name="ui_global_search")
async def global_search(
    request: Request,
    q: Optional[str] = Query(None, description="Search query"),
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support),
    db: AsyncSession = Depends(get_db_session)
):
    """Global search across all content types"""
    logger.info(f"Global search query: '{q}' by user: {current_user.username if current_user else 'Anonymous'}")
    
    search_results = {
        "stories": [],
        "worlds": [],
        "characters": [],
        "locations": [],
        "lore_items": [],
        "blog_posts": [],
        "forum_threads": []
    }
    
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        
        try:
            # Search Stories
            if current_user:
                story_result = await db.execute(
                    select(Story)
                    .where(
                        (Story.title.ilike(search_term) | Story.description.ilike(search_term)) &
                        (Story.user_id == current_user.id)
                    )
                    .options(selectinload(Story.world))
                    .limit(10)
                )
                search_results["stories"] = story_result.scalars().all()
            
            # Search Worlds
            if current_user:
                world_result = await db.execute(
                    select(World)
                    .where(
                        (World.name.ilike(search_term) | World.description.ilike(search_term)) &
                        (World.user_id == current_user.id)
                    )
                    .limit(10)
                )
                search_results["worlds"] = world_result.scalars().all()
            
            # Search Blog Posts
            from app.models.blog_post import BlogPost, BlogPostStatus
            blog_result = await db.execute(
                select(BlogPost)
                .where(
                    (BlogPost.title.ilike(search_term) | BlogPost.content.ilike(search_term)) &
                    (BlogPost.status == BlogPostStatus.PUBLISHED)
                )
                .options(selectinload(BlogPost.author))
                .limit(10)
            )
            search_results["blog_posts"] = blog_result.scalars().all()
            
        except Exception as e:
            logger.error(f"Error performing global search: {e}")
    
    context = {
        "request": request,
        "current_user": current_user,
        "search_query": q,
        "search_results": search_results,
        "page_title": f"Search Results for '{q}'" if q else "Global Search"
    }
    return templates.TemplateResponse("pages/global_search.html", context)


@router.get("/basic-story-editor", response_class=HTMLResponse, name="ui_basic_story_editor")
async def basic_story_editor(
    request: Request,
    story_id: int = Query(..., description="ID of the basic story to edit"),
    act_id: int = Query(None, description="ID of the act to edit (optional)"),
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support),
    db: AsyncSession = Depends(get_db_session)
):
    """Basic Story Editor Page"""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    try:
        # Get the story
        from app.crud import story as story_crud
        from app.crud import act as act_crud
        
        story = await story_crud.get_story_for_user(db, story_id, current_user.id)
        if not story:
            return RedirectResponse(url="/ui/stories", status_code=status.HTTP_302_FOUND)
        
        # Verify it's a basic story
        if story.story_type != 'basic':
            return RedirectResponse(url=f"/ui/stories/{story_id}", status_code=status.HTTP_302_FOUND)
        
        # Get the first act (basic stories have only one act)
        acts = await act_crud.get_acts_by_story(db, story_id, limit=1)
        act = acts[0] if acts else None
        
        if not act:
            # Create the first act if it doesn't exist
            from app.models.act import Act
            act = Act(
                title="Act 1",
                act_number=1,
                story_id=story.id,
                description=""
            )
            db.add(act)
            await db.commit()
            await db.refresh(act)
        
        context = {
            "request": request,
            "current_user": current_user,
            "story": story,
            "act": act,
            "page_title": f"Edit {story.title} - Basic Story Editor"
        }
        
        return templates.TemplateResponse("pages/basic_story_editor.html", context)
        
    except Exception as e:
        logger.error(f"Error loading basic story editor for story {story_id}: {e}")
        return RedirectResponse(url="/ui/stories", status_code=status.HTTP_302_FOUND)


@router.get("/stories", response_class=HTMLResponse, name="ui_list_stories")
async def stories_list(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support),
    db: AsyncSession = Depends(get_db_session)
):
    """User's stories list page."""
    if not current_user:
        logger.warning("Anonymous user attempted to access stories list")
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    logger.info(f"User '{current_user.username}' (ID: {current_user.id}) accessing stories list")
    
    try:
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select, func
        
        # Debug: Log the query we're about to execute
        logger.info(f"Fetching stories for user_id={current_user.id}")
        
        # Get user's stories with ALL relationships to avoid lazy loading in template
        user_stories = await db.execute(
            select(Story)
            .filter(Story.user_id == current_user.id)
            .options(
                selectinload(Story.world),
                selectinload(Story.current_image),
                selectinload(Story.published_version)
            )
            .order_by(Story.updated_at.desc())
        )
        stories_list = user_stories.scalars().all()
        
        # Count total stories
        stories_count = await db.scalar(
            select(func.count(Story.id)).where(Story.user_id == current_user.id)
        )
        
        logger.info(f"Query completed: Found {len(stories_list)} stories for user {current_user.username} (ID: {current_user.id})")
        logger.info(f"Stories count from DB: {stories_count}")
        
        return templates.TemplateResponse(
            "pages/stories_list.html",
            {
                "request": request, 
                "current_user": current_user,
                "project_name": settings.APP_PROJECT_NAME,
                "stories": stories_list,
                "stories_count": stories_count or 0,
                "show_empty_state": len(stories_list) == 0
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading stories list for user {current_user.username}: {e}")
        return templates.TemplateResponse(
            "pages/stories_list.html",
            {
                "request": request, 
                "current_user": current_user,
                "project_name": settings.APP_PROJECT_NAME,
                "stories": [],
                "stories_count": 0,
                "show_empty_state": True,
                "error_message": "Unable to load stories. Please try again."
            }
        )


@router.get("/stories/new", response_class=HTMLResponse, name="ui_new_story")
async def new_story(
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support),
    db: AsyncSession = Depends(get_db_session)
):
    """Create new story page."""
    if not current_user:
        logger.warning("Anonymous user attempted to access new story page")
        return RedirectResponse(url="/ui/login", status_code=status.HTTP_303_SEE_OTHER)
    
    logger.info(f"User '{current_user.username}' accessing new story page")
    
    try:
        from app.crud import world as crud_world
        from app.schemas.world import WorldCreate
        
        # Get user's existing worlds
        available_worlds = await crud_world.get_worlds_by_user(db, current_user.id)
        
        # For first-time users, create a generic world if they don't have any
        pre_selected_world_id = None
        if not available_worlds:
            logger.info(f"First-time user {current_user.username} has no worlds, creating generic world")
            
            # Create a generic world for the user
            world_name = f"Untitled World by {current_user.username}"
            world_data = WorldCreate(
                name=world_name,
                description="A generic world created for your advanced stories. You can customize this world later.",
                short_description="Generic world for storytelling",
                is_free_chat_enabled=False
            )
            
            new_world = await crud_world.create_world(db=db, world_in=world_data, user_id=current_user.id)
            await db.commit()
            logger.info(f"Created generic world '{new_world.name}' (ID: {new_world.id}) for user {current_user.username}")
            
            available_worlds = [new_world]
            pre_selected_world_id = new_world.id
        
        return templates.TemplateResponse(
            "pages/story_form.html",
            {
                "request": request, 
                "current_user": current_user,
                "project_name": settings.APP_PROJECT_NAME,
                "available_worlds_for_story_form": available_worlds,
                "pre_selected_world_id": pre_selected_world_id,
                "no_worlds_exist_error": False,
                "form_action_url": "/api/v1/stories/",
                "story": None
            }
        )
        
    except Exception as e:
        logger.error(f"Error setting up new story form for user {current_user.username}: {e}")
        return templates.TemplateResponse(
            "pages/story_form.html",
            {
                "request": request, 
                "current_user": current_user,
                "project_name": settings.APP_PROJECT_NAME,
                "available_worlds_for_story_form": [],
                "pre_selected_world_id": None,
                "no_worlds_exist_error": True,
                "form_action_url": "/api/v1/stories/",
                "story": None
            }
        )


@router.get("/stories/{story_id}", response_class=HTMLResponse, name="ui_story_detail")
async def story_detail_redirect(
    story_id: int,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_with_anonymous_support),
    db: AsyncSession = Depends(get_db_session)
):
    """Story Detail - Detects story type and redirects to appropriate editor"""
    if not current_user:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)
    
    try:
        # Get the story
        from app.crud import story as story_crud
        
        logger.info(f"User {current_user.id} requesting story {story_id}")
        story = await story_crud.get_story_for_user(db, story_id, current_user.id)
        if not story:
            logger.warning(f"Story {story_id} not found or access denied for user {current_user.id} ({current_user.username})")
            # Try to check if story exists at all (for better logging)
            from sqlalchemy import select
            story_exists = await db.scalar(select(Story.id).where(Story.id == story_id))
            if story_exists:
                logger.warning(f"Story {story_id} exists but user {current_user.id} doesn't have access")
            else:
                logger.warning(f"Story {story_id} does not exist in database")
            # Redirect to stories list instead of home page
            return RedirectResponse(url="/ui/stories", status_code=status.HTTP_302_FOUND)
        
        # Detect story type and redirect to appropriate editor
        if story.story_type == 'basic':
            logger.info(f"Redirecting to basic story editor for story {story_id}")
            # Get the first act for the redirect
            from app.crud import act as act_crud
            acts = await act_crud.get_acts_by_story(db, story_id, limit=1)
            act_id = acts[0].id if acts else None
            
            if act_id:
                return RedirectResponse(
                    url=f"/ui/basic-story-editor?story_id={story_id}&act_id={act_id}",
                    status_code=status.HTTP_302_FOUND
                )
            else:
                return RedirectResponse(
                    url=f"/ui/basic-story-editor?story_id={story_id}",
                    status_code=status.HTTP_302_FOUND
                )
        else:
            # Advanced story - show story detail page
            logger.info(f"Loading story detail page for advanced story {story_id}")
            
            # Load the story with all necessary relationships for the template
            from sqlalchemy.orm import selectinload
            from sqlalchemy import select
            
            story_result = await db.execute(
                select(Story)
                .filter(Story.id == story_id, Story.user_id == current_user.id)
                .options(
                    selectinload(Story.world),
                    selectinload(Story.acts),
                    selectinload(Story.characters),
                    selectinload(Story.locations), 
                    selectinload(Story.lore_items),
                    selectinload(Story.current_image),
                    selectinload(Story.published_version)
                )
            )
            story_detail = story_result.scalar_one_or_none()
            
            if not story_detail:
                logger.warning(f"Story {story_id} not found for user {current_user.id} when loading detail")
                return RedirectResponse(url="/ui/stories", status_code=status.HTTP_302_FOUND)
            
            # Render the story detail template
            return templates.TemplateResponse(
                "pages/story_detail.html",
                {
                    "request": request,
                    "current_user": current_user,
                    "story": story_detail,
                    "acts": story_detail.acts,  # Add acts to template context
                    "project_name": settings.APP_PROJECT_NAME
                }
            )
        
    except Exception as e:
        logger.error(f"Error detecting story type for story {story_id}: {e}")
        # Fallback: redirect to stories list
        return RedirectResponse(url="/ui/stories", status_code=status.HTTP_302_FOUND)
