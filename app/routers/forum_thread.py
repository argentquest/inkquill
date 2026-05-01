"""API endpoints for forum threads."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db_session, get_current_user
from app.models.user import User
from app.models.forum import ThreadStatus
from app.schemas.base import ApiResponse
from app.schemas.forum import (
    ForumThreadCreate,
    ForumThreadUpdate,
    ForumThreadListResponse,
    ForumThreadDetailResponse,
    ForumPostResponse
)
from app.crud import forum_thread as crud_thread
from app.crud import forum_post as crud_post

router = APIRouter(prefix="/api/forum/threads", tags=["forum_threads"])


def _build_thread_list_response(thread) -> ForumThreadListResponse:
    """Provide internal router support for build thread list response."""
    return ForumThreadListResponse(
        id=thread.id,
        title=thread.title,
        slug=thread.slug,
        status=thread.status,
        category_id=thread.category_id,
        category_name=thread.category.name if thread.category else None,
        user_id=thread.user_id,
        username=thread.user.username if thread.user else "Unknown",
        world_id=thread.world_id,
        world_name=thread.world.name if thread.world else None,
        story_id=thread.story_id,
        story_title=thread.story.title if thread.story else None,
        view_count=thread.view_count,
        post_count=thread.post_count,
        last_post_at=thread.last_post_at,
        last_post_by_username=thread.last_post_by.username if thread.last_post_by else None,
        is_pinned=thread.is_pinned,
        is_locked=thread.is_locked,
        created_at=thread.created_at,
        app_source=getattr(thread, "app_source", "storytelling"),
    )


def _build_post_response(post, user_vote=None) -> ForumPostResponse:
    """Provide internal router support for build post response."""
    user = post.__dict__.get("user")
    character = post.__dict__.get("character")
    location = post.__dict__.get("location")
    edited_by = post.__dict__.get("edited_by")
    return ForumPostResponse(
        id=post.id,
        content=post.content,
        content_html=post.content_html,
        thread_id=post.thread_id,
        user_id=post.user_id,
        username=user.username if user else "Unknown",
        user_display_name=user.display_name if user else None,
        parent_post_id=post.parent_post_id,
        character_id=post.character_id,
        character_name=character.name if character else None,
        location_id=post.location_id,
        location_name=location.name if location else None,
        upvote_count=post.upvote_count,
        downvote_count=post.downvote_count,
        score=post.score,
        user_vote=user_vote,
        edit_count=post.edit_count,
        edited_at=post.edited_at,
        edited_by_username=edited_by.username if edited_by else None,
        is_deleted=post.is_deleted,
        deleted_at=post.deleted_at,
        deletion_reason=post.deletion_reason,
        created_at=post.created_at,
        updated_at=post.updated_at,
    )


@router.get("/", response_model=ApiResponse)
async def get_threads(
    category_id: Optional[int] = None,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[ThreadStatus] = None,
    app_source: Optional[str] = Query(None, pattern="^(storytelling|care-circle)$"),
    order_by: str = Query("recent", pattern="^(recent|popular|updated)$"),
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db_session)
):
    """Get forum threads with optional filters."""
    threads = await crud_thread.get_forum_threads(
        db,
        category_id=category_id,
        world_id=world_id,
        story_id=story_id,
        user_id=user_id,
        status=status,
        app_source=app_source,
        order_by=order_by,
        skip=skip,
        limit=limit
    )
    
    # Convert to response format
    response_threads = [_build_thread_list_response(thread) for thread in threads]
    return ApiResponse.success_response(data=response_threads)


@router.get("/{thread_id}", response_model=ApiResponse)
async def get_thread(
    thread_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific forum thread with posts."""
    thread = await crud_thread.get_forum_thread(db, thread_id, increment_view=True)
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # Get posts for the thread
    posts = await crud_post.get_thread_posts(db, thread_id, limit=50)
    
    # Check if user is subscribed
    is_subscribed = False
    if current_user:
        is_subscribed = await crud_thread.is_thread_subscribed(
            db, thread_id, current_user.id
        )
    
    # Convert posts to response format
    response_posts = []
    for post in posts:
        user_vote = None
        if current_user:
            user_vote = await crud_post.get_user_vote_on_post(
                db, post.id, current_user.id
            )
        
        response_posts.append(_build_post_response(post, user_vote))
    
    # Convert thread to response format
    thread_response = ForumThreadDetailResponse(
        id=thread.id,
        title=thread.title,
        slug=thread.slug,
        status=thread.status,
        category_id=thread.category_id,
        category_name=thread.category.name if thread.category else None,
        user_id=thread.user_id,
        username=thread.user.username if thread.user else "Unknown",
        world_id=thread.world_id,
        world_name=thread.world.name if thread.world else None,
        story_id=thread.story_id,
        story_title=thread.story.title if thread.story else None,
        view_count=thread.view_count,
        post_count=thread.post_count,
        last_post_at=thread.last_post_at,
        last_post_by_username=thread.last_post_by.username if thread.last_post_by else None,
        is_pinned=thread.is_pinned,
        is_locked=thread.is_locked,
        created_at=thread.created_at,
        updated_at=thread.updated_at,
        app_source=getattr(thread, "app_source", "storytelling"),
        is_subscribed=is_subscribed,
        posts=response_posts
    )
    
    return ApiResponse.success_response(data=thread_response)


@router.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_thread(
    thread: ForumThreadCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new forum thread with initial post."""
    try:
        # Create thread
        new_thread = await crud_thread.create_forum_thread(
            db, thread, current_user.id
        )
        
        # Create initial post
        from app.schemas.forum import ForumPostCreate
        initial_post = ForumPostCreate(
            content=thread.initial_post_content,
            content_html=thread.initial_post_content_html,
            thread_id=new_thread.id
        )
        
        first_post = await crud_post.create_forum_post(
            db, initial_post, current_user.id
        )
        new_thread = await crud_thread.get_forum_thread(db, new_thread.id)
        first_post = await crud_post.get_forum_post(db, first_post.id)

        return ApiResponse.success_response(
            data=ForumThreadDetailResponse(
            id=new_thread.id,
            title=new_thread.title,
            slug=new_thread.slug,
            status=new_thread.status,
            category_id=new_thread.category_id,
            category_name=new_thread.category.name if new_thread.category else None,
            user_id=new_thread.user_id,
            username=current_user.username,
            world_id=new_thread.world_id,
            world_name=new_thread.world.name if new_thread.world else None,
            story_id=new_thread.story_id,
            story_title=new_thread.story.title if new_thread.story else None,
            view_count=0,
            post_count=1,
            last_post_at=first_post.created_at,
            last_post_by_username=current_user.username,
            is_pinned=False,
            is_locked=False,
            created_at=new_thread.created_at,
            updated_at=new_thread.updated_at,
            app_source=getattr(new_thread, "app_source", "storytelling"),
            is_subscribed=True,
            posts=[
                ForumPostResponse(
                    id=first_post.id,
                    content=first_post.content,
                    content_html=first_post.content_html,
                    thread_id=first_post.thread_id,
                    user_id=first_post.user_id,
                    username=current_user.username,
                    user_display_name=current_user.display_name,
                    parent_post_id=None,
                    character_id=first_post.character_id,
                    location_id=first_post.location_id,
                    upvote_count=0,
                    downvote_count=0,
                    score=0,
                    user_vote=None,
                    edit_count=0,
                    edited_at=None,
                    is_deleted=False,
                    deleted_at=None,
                    deletion_reason=None,
                    created_at=first_post.created_at,
                    updated_at=first_post.updated_at,
                )
            ],
            ),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{thread_id}", response_model=ApiResponse)
async def update_thread(
    thread_id: int,
    thread_update: ForumThreadUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update a forum thread."""
    updated_thread = await crud_thread.update_forum_thread(
        db, thread_id, thread_update, current_user.id, current_user.is_admin
    )
    
    if not updated_thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found or you don't have permission to edit it"
        )
    
    await db.refresh(updated_thread)
    
    return ApiResponse.success_response(data=_build_thread_list_response(updated_thread))


@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(
    thread_id: int,
    hard_delete: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a forum thread."""
    success = await crud_thread.delete_forum_thread(
        db, thread_id, current_user.id, current_user.is_admin, hard_delete
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found or you don't have permission to delete it"
        )
    
    return None


@router.post("/{thread_id}/toggle-lock", response_model=ApiResponse)
async def toggle_thread_lock(
    thread_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Toggle thread lock status. (Admin only)"""
    thread = await crud_thread.toggle_thread_lock(
        db, thread_id, current_user.is_admin
    )
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can lock/unlock threads"
        )
    
    await db.refresh(thread)
    
    return ApiResponse.success_response(data=_build_thread_list_response(thread))


@router.post("/{thread_id}/toggle-pin", response_model=ApiResponse)
async def toggle_thread_pin(
    thread_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Toggle thread pin status. (Admin only)"""
    thread = await crud_thread.toggle_thread_pin(
        db, thread_id, current_user.is_admin
    )
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can pin/unpin threads"
        )
    
    await db.refresh(thread)
    
    return ApiResponse.success_response(data=_build_thread_list_response(thread))


@router.post("/{thread_id}/subscribe")
async def toggle_subscription(
    thread_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Toggle subscription to a thread."""
    is_subscribed = await crud_thread.toggle_thread_subscription(
        db, thread_id, current_user.id
    )
    
    return ApiResponse.success_response(data={"subscribed": is_subscribed})
