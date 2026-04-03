"""API endpoints for forum posts."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db_session, get_current_user
from app.models.user import User
from app.models.forum import VoteType
from app.schemas.base import ApiResponse
from app.schemas.forum import (
    ForumPostCreate,
    ForumPostUpdate,
    ForumPostResponse,
    ForumVoteCreate,
    UserForumStats
)
from app.crud import forum_post as crud_post

router = APIRouter(prefix="/api/forum/posts", tags=["forum_posts"])


def _build_post_response(post, user_vote=None, replies=None) -> ForumPostResponse:
    """Provide internal router support for build post response."""
    thread = post.__dict__.get("thread")
    user = post.__dict__.get("user")
    character = post.__dict__.get("character")
    location = post.__dict__.get("location")
    edited_by = post.__dict__.get("edited_by")
    return ForumPostResponse(
        id=post.id,
        content=post.content,
        content_html=post.content_html,
        thread_id=post.thread_id,
        thread_title=thread.title if thread else None,
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
        replies=replies or [],
    )


@router.get("/thread/{thread_id}", response_model=ApiResponse)
async def get_thread_posts(
    thread_id: int,
    skip: int = 0,
    limit: int = 50,
    order: str = "asc",
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all posts for a thread."""
    posts = await crud_post.get_thread_posts(
        db, thread_id, skip=skip, limit=limit, order=order
    )
    
    # Convert to response format with user votes
    response_posts = []
    for post in posts:
        user_vote = None
        if current_user:
            user_vote = await crud_post.get_user_vote_on_post(
                db, post.id, current_user.id
            )
        
        # Get replies
        replies = await crud_post.get_post_replies(db, post.id)
        reply_responses = []
        for reply in replies:
            reply_vote = None
            if current_user:
                reply_vote = await crud_post.get_user_vote_on_post(
                    db, reply.id, current_user.id
                )
            
            reply_responses.append(_build_post_response(reply, reply_vote))

        response_posts.append(_build_post_response(post, user_vote, reply_responses))

    return ApiResponse.success_response(data=response_posts)


@router.get("/user/{user_id}", response_model=ApiResponse)
async def get_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db_session)
):
    """Get all posts by a specific user."""
    posts = await crud_post.get_user_posts(
        db, user_id, skip=skip, limit=limit
    )
    
    # Convert to response format
    response_posts = []
    for post in posts:
        response_posts.append(_build_post_response(post))

    return ApiResponse.success_response(data=response_posts)


@router.get("/{post_id}", response_model=ApiResponse)
async def get_post(
    post_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific forum post."""
    post = await crud_post.get_forum_post(db, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    user_vote = None
    if current_user:
        user_vote = await crud_post.get_user_vote_on_post(
            db, post.id, current_user.id
        )
    
    return ApiResponse.success_response(data=_build_post_response(post, user_vote))


@router.post("/", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    post: ForumPostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new forum post."""
    try:
        new_post = await crud_post.create_forum_post(
            db, post, current_user.id
        )
        new_post = await crud_post.get_forum_post(db, new_post.id)

        return ApiResponse.success_response(data=_build_post_response(new_post))
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{post_id}", response_model=ApiResponse)
async def update_post(
    post_id: int,
    post_update: ForumPostUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update a forum post."""
    updated_post = await crud_post.update_forum_post(
        db, post_id, post_update, current_user.id, current_user.is_admin
    )
    
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to edit it"
        )
    
    await db.refresh(updated_post)
    
    user_vote = await crud_post.get_user_vote_on_post(
        db, updated_post.id, current_user.id
    )
    
    return ApiResponse.success_response(data=_build_post_response(updated_post, user_vote))


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    deletion_reason: Optional[str] = None,
    hard_delete: bool = False,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a forum post."""
    success = await crud_post.delete_forum_post(
        db, post_id, current_user.id, current_user.is_admin,
        deletion_reason, hard_delete
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to delete it"
        )
    
    return None


@router.post("/{post_id}/vote")
async def vote_on_post(
    post_id: int,
    vote: ForumVoteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Vote on a forum post."""
    if vote.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post ID mismatch"
        )
    
    try:
        post = await crud_post.vote_on_post(
            db, post_id, current_user.id, vote.vote_type
        )
        
        return ApiResponse.success_response(
            data={
                "post_id": post.id,
                "upvote_count": post.upvote_count,
                "downvote_count": post.downvote_count,
                "score": post.score,
                "user_vote": vote.vote_type,
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/user/{user_id}/stats", response_model=ApiResponse)
async def get_user_forum_stats(
    user_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get forum statistics for a user."""
    # Get user
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get stats
    post_count = await crud_post.get_user_post_count(db, user_id)
    total_karma = await crud_post.get_user_karma(db, user_id)
    
    # Get thread count
    from app.crud import forum_thread as crud_thread
    threads = await crud_thread.get_forum_threads(db, user_id=user_id)
    thread_count = len(threads)
    
    return ApiResponse.success_response(
        data=UserForumStats(
            user_id=user_id,
            username=user.username,
            post_count=post_count,
            thread_count=thread_count,
            total_karma=total_karma,
            joined_date=user.created_at,
        )
    )
