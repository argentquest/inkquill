"""API routes for published stories."""

# /story_app/app/routers/published_stories.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging

from app.core.deps import get_db_session, get_current_user
from app.models.user import User
from app.models.published_story import PublishedStory
from app.models.story import Story
from app.models.story_rating import StoryRating
from app.models.story_comment import StoryComment
from app.schemas.base import ApiResponse
from app.schemas.published_story import (
    PublishedStoryRead, 
    PublishedStoryList,
    PublishedStoryDetail,
    StoryCommentCreate,
    StoryCommentRead,
    StoryRatingCreate,
    StoryRatingRead,
    StoryRatingStats
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/published-stories",
    tags=["published-stories"]
)


def _build_published_story_read(story: PublishedStory) -> PublishedStoryRead:
    """Provide internal router support for build published story read."""
    story_read = PublishedStoryRead(
        id=story.id,
        story_id=story.story_id,
        user_id=story.user_id,
        published_url=story.published_url,
        filename=story.filename,
        title=story.title,
        description=story.description,
        word_count=story.word_count,
        is_public=story.is_public,
        is_featured=story.is_featured,
        view_count=story.view_count,
        like_count=story.like_count,
        comment_count=story.comment_count,
        average_rating=story.average_rating,
        published_at=story.published_at,
        updated_at=story.updated_at or story.published_at,
    )
    story_read.publisher_username = story.publisher.username if story.publisher else None
    story_read.publisher_display_name = story.publisher.display_name if story.publisher else None
    if story.story and story.story.world:
        story_read.world_name = story.story.world.name
    return story_read


def _build_published_story_detail(story: PublishedStory) -> PublishedStoryDetail:
    """Provide internal router support for build published story detail."""
    story_detail = PublishedStoryDetail(
        id=story.id,
        story_id=story.story_id,
        user_id=story.user_id,
        published_url=story.published_url,
        filename=story.filename,
        title=story.title,
        description=story.description,
        word_count=story.word_count,
        is_public=story.is_public,
        is_featured=story.is_featured,
        view_count=story.view_count,
        like_count=story.like_count,
        comment_count=story.comment_count,
        average_rating=story.average_rating,
        published_at=story.published_at,
        updated_at=story.updated_at or story.published_at,
    )
    story_detail.publisher_username = story.publisher.username if story.publisher else None
    story_detail.publisher_display_name = story.publisher.display_name if story.publisher else None
    if story.story:
        story_detail.story_title = story.story.title
        story_detail.story_short_description = story.story.short_description
        if story.story.world:
            story_detail.world_name = story.story.world.name
    return story_detail

@router.get("/", response_model=ApiResponse, name="list_published_stories")
async def list_published_stories(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    sort_by: str = Query("recent", pattern="^(recent|popular|rating|title)$"),
    is_featured: Optional[bool] = None,
    db: AsyncSession = Depends(get_db_session)
):
    """List all public published stories with pagination and filtering"""
    
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
    
    # Apply featured filter
    if is_featured is not None:
        query = query.where(PublishedStory.is_featured == is_featured)
    
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
    
    # Apply pagination
    offset = (page - 1) * per_page
    query = query.offset(offset).limit(per_page)
    
    # Load with relationships
    query = query.options(
        selectinload(PublishedStory.publisher),
        selectinload(PublishedStory.story).selectinload(Story.world)
    )
    
    # Execute query
    result = await db.execute(query)
    stories = result.scalars().all()
    
    # Transform to response model
    story_reads = []
    for story in stories:
        story_reads.append(_build_published_story_read(story))
    
    return ApiResponse.success_response(data=PublishedStoryList(
        stories=story_reads,
        total=total,
        page=page,
        per_page=per_page
    ))

@router.get("/{story_id}", response_model=ApiResponse, name="get_published_story")
async def get_published_story(
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get details of a specific published story"""
    
    # Get story with relationships
    result = await db.execute(
        select(PublishedStory)
        .where(PublishedStory.id == story_id)
        .where(PublishedStory.is_public == True)
        .options(
            selectinload(PublishedStory.publisher),
            selectinload(PublishedStory.story).selectinload(Story.world)
        )
    )
    story = result.scalar_one_or_none()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Published story not found"
        )
    
    # Increment view count
    story.view_count += 1
    await db.commit()
    
    await db.refresh(story)

    refreshed_result = await db.execute(
        select(PublishedStory)
        .where(PublishedStory.id == story_id)
        .options(
            selectinload(PublishedStory.publisher),
            selectinload(PublishedStory.story).selectinload(Story.world)
        )
    )
    refreshed_story = refreshed_result.scalar_one()

    # Create response
    story_detail = _build_published_story_detail(refreshed_story)
    
    # Check if user has rated
    if current_user:
        rating_result = await db.execute(
            select(StoryRating)
            .where(StoryRating.published_story_id == story_id)
            .where(StoryRating.user_id == current_user.id)
        )
        user_rating = rating_result.scalar_one_or_none()
        if user_rating:
            story_detail.has_user_rated = True
            story_detail.user_rating = user_rating.rating
    
    return ApiResponse.success_response(data=story_detail)

@router.post("/{story_id}/rate", response_model=ApiResponse, name="rate_published_story")
async def rate_published_story(
    story_id: int,
    rating_data: StoryRatingCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Rate a published story (1-5 stars)"""
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Must be logged in to rate stories"
        )
    
    # Verify story exists
    story_result = await db.execute(
        select(PublishedStory)
        .where(PublishedStory.id == story_id)
        .where(PublishedStory.is_public == True)
    )
    story = story_result.scalar_one_or_none()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Published story not found"
        )
    
    # Check for existing rating
    existing_result = await db.execute(
        select(StoryRating)
        .where(StoryRating.published_story_id == story_id)
        .where(StoryRating.user_id == current_user.id)
    )
    existing_rating = existing_result.scalar_one_or_none()
    
    if existing_rating:
        # Update existing rating
        existing_rating.rating = rating_data.rating
        db.add(existing_rating)
        rating = existing_rating
    else:
        # Create new rating
        rating = StoryRating(
            published_story_id=story_id,
            user_id=current_user.id,
            rating=rating_data.rating
        )
        db.add(rating)
    
    await db.commit()
    
    # Update story statistics after commit
    await _update_story_rating_stats(db, story_id)
    
    # Reload rating with fresh data to avoid detached object issues
    result = await db.execute(
        select(StoryRating)
        .where(StoryRating.id == rating.id)
    )
    fresh_rating = result.scalar_one()
    
    # Create response manually to avoid validation issues
    rating_read = StoryRatingRead(
        id=fresh_rating.id,
        published_story_id=fresh_rating.published_story_id,
        user_id=fresh_rating.user_id,
        rating=fresh_rating.rating,
        created_at=fresh_rating.created_at,
        updated_at=fresh_rating.updated_at
    )
    
    return ApiResponse.success_response(data=rating_read)

@router.get("/{story_id}/comments", response_model=ApiResponse, name="get_story_comments")
async def get_story_comments(
    story_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get all approved comments for a published story"""
    
    # Get top-level comments with user info
    result = await db.execute(
        select(StoryComment)
        .where(StoryComment.published_story_id == story_id)
        .where(StoryComment.parent_comment_id == None)
        .where(StoryComment.is_approved == True)
        .where(StoryComment.is_deleted == False)
        .options(selectinload(StoryComment.commenter))
        .order_by(StoryComment.created_at.desc())
    )
    comments = result.scalars().all()
    
    # Transform to response model
    comment_reads = []
    for comment in comments:
        comment_read = StoryCommentRead(
            id=comment.id,
            published_story_id=comment.published_story_id,
            user_id=comment.user_id,
            content=comment.content,
            parent_comment_id=comment.parent_comment_id,
            is_approved=comment.is_approved,
            is_deleted=comment.is_deleted,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
            commenter_username=comment.commenter.username,
            commenter_display_name=comment.commenter.display_name,
            replies=[]  # TODO: Load nested replies if needed
        )
        comment_reads.append(comment_read)
    
    return ApiResponse.success_response(data=comment_reads)

@router.post("/{story_id}/comments", response_model=ApiResponse, name="create_story_comment")
async def create_story_comment(
    story_id: int,
    comment_data: StoryCommentCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new comment on a published story"""
    
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Must be logged in to comment"
        )
    
    # Verify story exists
    story_result = await db.execute(
        select(PublishedStory)
        .where(PublishedStory.id == story_id)
        .where(PublishedStory.is_public == True)
    )
    story = story_result.scalar_one_or_none()
    
    if not story:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Published story not found"
        )
    
    # Create comment
    comment = StoryComment(
        published_story_id=story_id,
        user_id=current_user.id,
        content=comment_data.content,
        parent_comment_id=comment_data.parent_comment_id,
        is_approved=True  # Auto-approve for now, can add moderation later
    )
    db.add(comment)
    
    # Update comment count
    story.comment_count += 1
    
    await db.commit()
    
    # Reload comment with proper eager loading
    result = await db.execute(
        select(StoryComment)
        .options(selectinload(StoryComment.commenter))
        .where(StoryComment.id == comment.id)
    )
    comment_with_user = result.scalar_one()
    
    # Create response with user info
    comment_read = StoryCommentRead(
        id=comment_with_user.id,
        published_story_id=comment_with_user.published_story_id,
        user_id=comment_with_user.user_id,
        content=comment_with_user.content,
        parent_comment_id=comment_with_user.parent_comment_id,
        is_approved=comment_with_user.is_approved,
        is_deleted=comment_with_user.is_deleted,
        created_at=comment_with_user.created_at,
        updated_at=comment_with_user.updated_at,
        commenter_username=comment_with_user.commenter.username,
        commenter_display_name=comment_with_user.commenter.display_name,
        replies=[]  # New comments don't have replies yet
    )
    
    return ApiResponse.success_response(data=comment_read)

async def _update_story_rating_stats(db: AsyncSession, story_id: int):
    """Update the average rating and like count for a story"""
    
    # Calculate average rating
    result = await db.execute(
        select(
            func.avg(StoryRating.rating).label("avg_rating"),
            func.count(StoryRating.id).label("count")
        )
        .where(StoryRating.published_story_id == story_id)
    )
    stats = result.first()
    
    # Update story
    story_result = await db.execute(
        select(PublishedStory).where(PublishedStory.id == story_id)
    )
    story = story_result.scalar_one()
    
    story.average_rating = float(stats.avg_rating) if stats.avg_rating else None
    story.like_count = stats.count or 0
    
    db.add(story)
    await db.commit()
