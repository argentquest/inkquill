# /ai_rag_story_app/app/routers/views_published_stories.py

from fastapi import APIRouter, Request, Depends, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from typing import Optional
import logging
import re

from app.core.deps import get_db_session, get_current_user
from app.models.user import User
from app.models.published_story import PublishedStory
from app.models.story import Story
from app.models.story_comment import StoryComment
from app.models.act import Act
from app.models.scene import Scene

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/published",
    tags=["published-views"],
)

templates = Jinja2Templates(directory="app/templates")

def extract_first_50_words(text: str) -> str:
    """Extract the first 50 words from text content."""
    if not text:
        return ""
    
    # Remove HTML tags and normalize whitespace
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # Split into words and take first 50
    words = clean_text.split()
    if len(words) <= 50:
        return ' '.join(words)
    else:
        return ' '.join(words[:50])

async def get_story_first_words(db: AsyncSession, story_id: int) -> str:
    """Get the first 50 words from a story's content."""
    try:
        logger.info(f"Getting first words for story ID: {story_id}")
        
        # Get the first act's content (lowest act_number)
        result = await db.execute(
            select(Act.description)
            .where(Act.story_id == story_id)
            .where(Act.description.isnot(None))
            .where(Act.description != '')
            .order_by(Act.act_number.asc())
            .limit(1)
        )
        
        act_content = result.scalar_one_or_none()
        logger.info(f"Act content found for story {story_id}: {bool(act_content)}")
        if act_content:
            first_words = extract_first_50_words(act_content)
            logger.info(f"Extracted first words from act for story {story_id}: {first_words[:100]}...")
            return first_words
            
        logger.info(f"No content found for story {story_id}")
        return ""
    except Exception as e:
        logger.error(f"Error getting first words for story {story_id}: {e}")
        return ""

@router.get("/stories", response_class=HTMLResponse, name="published_stories_gallery")
async def published_stories_gallery(
    request: Request,
    page: int = Query(1, ge=1),
    search: Optional[str] = None,
    sort_by: str = Query("recent", regex="^(recent|popular|rating|title)$"),
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Public gallery of all published stories"""
    
    per_page = 12  # Number of stories per page
    
    # Base query
    query = select(PublishedStory).where(PublishedStory.is_public == True)
    
    # Apply search filter
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                PublishedStory.title.ilike(search_term),
                PublishedStory.description.ilike(search_term)
            )
        )
    
    # Apply sorting
    if sort_by == "recent":
        query = query.order_by(PublishedStory.published_at.desc())
    elif sort_by == "popular":
        query = query.order_by(PublishedStory.view_count.desc())
    elif sort_by == "rating":
        query = query.order_by(PublishedStory.average_rating.desc().nullslast())
    elif sort_by == "title":
        query = query.order_by(PublishedStory.title)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) * per_page
    
    # Apply pagination
    query = query.offset(offset).limit(per_page)
    
    # Load with relationships
    query = query.options(
        selectinload(PublishedStory.publisher),
        selectinload(PublishedStory.story).selectinload(Story.world),
        selectinload(PublishedStory.story).selectinload(Story.current_image)
    )
    
    # Execute query
    result = await db.execute(query)
    stories = result.scalars().all()
    
    # Create enriched story data with first words
    enriched_stories = []
    for story in stories:
        # Create a dictionary with story data plus first words
        story_dict = {
            'story': story,
            'first_words': await get_story_first_words(db, story.story_id) if story.story_id else ""
        }
        enriched_stories.append(story_dict)
    
    return templates.TemplateResponse(
        "pages/published_stories_gallery.html",
        {
            "request": request,
            "current_user": current_user,
            "stories": enriched_stories,
            "page": page,
            "total_pages": total_pages,
            "total_stories": total,
            "search": search,
            "sort_by": sort_by
        }
    )

@router.get("/story/{story_id}", response_class=HTMLResponse, name="view_published_story")
async def view_published_story(
    request: Request,
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user)
):
    """View a specific published story with comments and ratings"""
    
    # Get story with relationships
    result = await db.execute(
        select(PublishedStory)
        .where(PublishedStory.id == story_id)
        .where(PublishedStory.is_public == True)
        .options(
            selectinload(PublishedStory.publisher),
            selectinload(PublishedStory.story).selectinload(Story.world),
            selectinload(PublishedStory.story).selectinload(Story.current_image),
            selectinload(PublishedStory.comments).selectinload(StoryComment.commenter)
        )
    )
    published_story = result.scalar_one_or_none()
    
    if not published_story:
        # Return 404 page
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request, "current_user": current_user},
            status_code=404
        )
    
    # Increment view count (non-blocking)
    published_story.view_count += 1
    await db.commit()
    
    # Get user's rating if logged in
    user_rating = None
    if current_user:
        from app.models.story_rating import StoryRating
        rating_result = await db.execute(
            select(StoryRating)
            .where(StoryRating.published_story_id == story_id)
            .where(StoryRating.user_id == current_user.id)
        )
        user_rating_obj = rating_result.scalar_one_or_none()
        if user_rating_obj:
            user_rating = user_rating_obj.rating
    
    # Filter approved comments
    approved_comments = [
        comment for comment in published_story.comments 
        if comment.is_approved and not comment.is_deleted
    ]
    
    return templates.TemplateResponse(
        "pages/view_published_story.html",
        {
            "request": request,
            "current_user": current_user,
            "published_story": published_story,
            "user_rating": user_rating,
            "comments": approved_comments
        }
    )

@router.get("/user/{username}", response_class=HTMLResponse, name="user_published_stories")
async def user_published_stories(
    request: Request,
    username: str,
    page: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user)
):
    """View all published stories by a specific user"""
    
    # Get the user
    user_result = await db.execute(
        select(User).where(User.username == username)
    )
    profile_user = user_result.scalar_one_or_none()
    
    if not profile_user:
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request, "current_user": current_user},
            status_code=404
        )
    
    per_page = 12
    
    # Query user's published stories
    query = (
        select(PublishedStory)
        .where(PublishedStory.user_id == profile_user.id)
        .where(PublishedStory.is_public == True)
        .order_by(PublishedStory.published_at.desc())
    )
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Calculate pagination
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) * per_page
    
    # Apply pagination and load relationships
    query = query.offset(offset).limit(per_page).options(
        selectinload(PublishedStory.story).selectinload(Story.world)
    )
    
    result = await db.execute(query)
    stories = result.scalars().all()
    
    return templates.TemplateResponse(
        "pages/user_published_stories.html",
        {
            "request": request,
            "current_user": current_user,
            "profile_user": profile_user,
            "stories": stories,
            "page": page,
            "total_pages": total_pages,
            "total_stories": total
        }
    )