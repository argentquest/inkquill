"""API endpoints for forum posts."""
from typing import List, Optional
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
            
            reply_dict = {
                "id": reply.id,
                "content": reply.content,
                "content_html": reply.content_html,
                "thread_id": reply.thread_id,
                "user_id": reply.user_id,
                "username": reply.user.username if reply.user else "Unknown",
                "user_display_name": reply.user.display_name if reply.user else None,
                "parent_post_id": reply.parent_post_id,
                "character_id": reply.character_id,
                "character_name": reply.character.name if reply.character else None,
                "location_id": reply.location_id,
                "location_name": reply.location.name if reply.location else None,
                "upvote_count": reply.upvote_count,
                "downvote_count": reply.downvote_count,
                "score": reply.score,
                "user_vote": reply_vote,
                "edit_count": reply.edit_count,
                "edited_at": reply.edited_at,
                "edited_by_username": reply.edited_by.username if reply.edited_by else None,
                "is_deleted": reply.is_deleted,
                "deleted_at": reply.deleted_at,
                "deletion_reason": reply.deletion_reason,
                "created_at": reply.created_at,
                "updated_at": reply.updated_at,
                "replies": []
            }
            reply_responses.append(ForumPostResponse(**reply_dict))
        
        post_dict = {
            "id": post.id,
            "content": post.content,
            "content_html": post.content_html,
            "thread_id": post.thread_id,
            "thread_title": post.thread.title if post.thread else None,
            "user_id": post.user_id,
            "username": post.user.username if post.user else "Unknown",
            "user_display_name": post.user.display_name if post.user else None,
            "parent_post_id": post.parent_post_id,
            "character_id": post.character_id,
            "character_name": post.character.name if post.character else None,
            "location_id": post.location_id,
            "location_name": post.location.name if post.location else None,
            "upvote_count": post.upvote_count,
            "downvote_count": post.downvote_count,
            "score": post.score,
            "user_vote": user_vote,
            "edit_count": post.edit_count,
            "edited_at": post.edited_at,
            "edited_by_username": post.edited_by.username if post.edited_by else None,
            "is_deleted": post.is_deleted,
            "deleted_at": post.deleted_at,
            "deletion_reason": post.deletion_reason,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "replies": reply_responses
        }
        response_posts.append(ForumPostResponse(**post_dict))
    
    return response_posts


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
        post_dict = {
            "id": post.id,
            "content": post.content,
            "content_html": post.content_html,
            "thread_id": post.thread_id,
            "thread_title": post.thread.title if post.thread else None,
            "user_id": post.user_id,
            "username": post.user.username if post.user else "Unknown",
            "user_display_name": post.user.display_name if post.user else None,
            "parent_post_id": post.parent_post_id,
            "character_id": post.character_id,
            "location_id": post.location_id,
            "upvote_count": post.upvote_count,
            "downvote_count": post.downvote_count,
            "score": post.score,
            "user_vote": None,
            "edit_count": post.edit_count,
            "edited_at": post.edited_at,
            "is_deleted": post.is_deleted,
            "deleted_at": post.deleted_at,
            "deletion_reason": post.deletion_reason,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "replies": []
        }
        response_posts.append(ForumPostResponse(**post_dict))
    
    return response_posts


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
    
    return ForumPostResponse(
        id=post.id,
        content=post.content,
        content_html=post.content_html,
        thread_id=post.thread_id,
        thread_title=post.thread.title if post.thread else None,
        user_id=post.user_id,
        username=post.user.username if post.user else "Unknown",
        user_display_name=post.user.display_name if post.user else None,
        parent_post_id=post.parent_post_id,
        character_id=post.character_id,
        character_name=post.character.name if post.character else None,
        location_id=post.location_id,
        location_name=post.location.name if post.location else None,
        upvote_count=post.upvote_count,
        downvote_count=post.downvote_count,
        score=post.score,
        user_vote=user_vote,
        edit_count=post.edit_count,
        edited_at=post.edited_at,
        edited_by_username=post.edited_by.username if post.edited_by else None,
        is_deleted=post.is_deleted,
        deleted_at=post.deleted_at,
        deletion_reason=post.deletion_reason,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


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
        
        await db.refresh(new_post)
        
        return ForumPostResponse(
            id=new_post.id,
            content=new_post.content,
            content_html=new_post.content_html,
            thread_id=new_post.thread_id,
            thread_title=new_post.thread.title if new_post.thread else None,
            user_id=new_post.user_id,
            username=current_user.username,
            user_display_name=current_user.display_name,
            parent_post_id=new_post.parent_post_id,
            character_id=new_post.character_id,
            character_name=new_post.character.name if new_post.character else None,
            location_id=new_post.location_id,
            location_name=new_post.location.name if new_post.location else None,
            upvote_count=0,
            downvote_count=0,
            score=0,
            user_vote=None,
            edit_count=0,
            edited_at=None,
            is_deleted=False,
            deleted_at=None,
            deletion_reason=None,
            created_at=new_post.created_at,
            updated_at=new_post.updated_at,
            replies=[]
        )
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
    
    return ForumPostResponse(
        id=updated_post.id,
        content=updated_post.content,
        content_html=updated_post.content_html,
        thread_id=updated_post.thread_id,
        thread_title=updated_post.thread.title if updated_post.thread else None,
        user_id=updated_post.user_id,
        username=updated_post.user.username if updated_post.user else "Unknown",
        user_display_name=updated_post.user.display_name if updated_post.user else None,
        parent_post_id=updated_post.parent_post_id,
        character_id=updated_post.character_id,
        character_name=updated_post.character.name if updated_post.character else None,
        location_id=updated_post.location_id,
        location_name=updated_post.location.name if updated_post.location else None,
        upvote_count=updated_post.upvote_count,
        downvote_count=updated_post.downvote_count,
        score=updated_post.score,
        user_vote=user_vote,
        edit_count=updated_post.edit_count,
        edited_at=updated_post.edited_at,
        edited_by_username=updated_post.edited_by.username if updated_post.edited_by else None,
        is_deleted=updated_post.is_deleted,
        deleted_at=updated_post.deleted_at,
        deletion_reason=updated_post.deletion_reason,
        created_at=updated_post.created_at,
        updated_at=updated_post.updated_at
    )


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
        
        return {
            "post_id": post.id,
            "upvote_count": post.upvote_count,
            "downvote_count": post.downvote_count,
            "score": post.score,
            "user_vote": vote.vote_type
        }
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
    
    return UserForumStats(
        user_id=user_id,
        username=user.username,
        post_count=post_count,
        thread_count=thread_count,
        total_karma=total_karma,
        joined_date=user.created_at
    )