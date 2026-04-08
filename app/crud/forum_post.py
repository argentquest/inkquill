"""CRUD operations for forum posts."""
from typing import List, Optional
from datetime import UTC, datetime
from sqlalchemy import select, func, desc, and_, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.forum import ForumPost, ForumThread, ForumVote, VoteType
from app.schemas.forum import ForumPostCreate, ForumPostUpdate
from app.crud.forum_thread import update_thread_last_post


async def get_forum_post(
    db: AsyncSession, 
    post_id: int,
    include_deleted: bool = False
) -> Optional[ForumPost]:
    """Get a single forum post by ID."""
    query = select(ForumPost).where(ForumPost.id == post_id)
    
    if not include_deleted:
        query = query.where(ForumPost.is_deleted == False)
    
    query = query.options(
        selectinload(ForumPost.user),
        selectinload(ForumPost.thread),
        selectinload(ForumPost.character),
        selectinload(ForumPost.location),
        selectinload(ForumPost.parent_post),
        selectinload(ForumPost.edited_by)
    )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_thread_posts(
    db: AsyncSession,
    thread_id: int,
    skip: int = 0,
    limit: int = 50,
    order: str = "asc",  # asc or desc
    include_deleted: bool = False
) -> List[ForumPost]:
    """Get all posts for a thread with pagination."""
    query = select(ForumPost).where(ForumPost.thread_id == thread_id)
    
    if not include_deleted:
        query = query.where(ForumPost.is_deleted == False)
    
    # Order by creation time
    if order == "desc":
        query = query.order_by(desc(ForumPost.created_at))
    else:
        query = query.order_by(ForumPost.created_at)
    
    query = query.offset(skip).limit(limit)
    query = query.options(
        selectinload(ForumPost.user),
        selectinload(ForumPost.character),
        selectinload(ForumPost.location),
        selectinload(ForumPost.parent_post),
        selectinload(ForumPost.votes)
    )
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_user_posts(
    db: AsyncSession,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    include_deleted: bool = False
) -> List[ForumPost]:
    """Get all posts by a user."""
    query = select(ForumPost).where(ForumPost.user_id == user_id)
    
    if not include_deleted:
        query = query.where(ForumPost.is_deleted == False)
    
    query = query.order_by(desc(ForumPost.created_at))
    query = query.offset(skip).limit(limit)
    query = query.options(
        selectinload(ForumPost.thread).selectinload(ForumThread.category),
        selectinload(ForumPost.parent_post)
    )
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_forum_post(
    db: AsyncSession,
    post: ForumPostCreate,
    user_id: int
) -> ForumPost:
    """Create a new forum post."""
    # Check if thread exists and is not locked
    thread = await db.get(ForumThread, post.thread_id)
    if not thread or thread.is_deleted or thread.is_locked:
        raise ValueError("Thread not available for posting")
    
    # Verify parent post exists if replying
    if post.parent_post_id:
        parent = await db.get(ForumPost, post.parent_post_id)
        if not parent or parent.thread_id != post.thread_id:
            raise ValueError("Invalid parent post")
    
    db_post = ForumPost(
        content=post.content,
        content_html=post.content_html,
        thread_id=post.thread_id,
        user_id=user_id,
        parent_post_id=post.parent_post_id,
        character_id=post.character_id,
        location_id=post.location_id
    )
    
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)
    
    # Update thread's last post info
    await update_thread_last_post(db, post.thread_id, user_id)
    
    return db_post


async def update_forum_post(
    db: AsyncSession,
    post_id: int,
    post_update: ForumPostUpdate,
    user_id: int,
    is_admin: bool = False
) -> Optional[ForumPost]:
    """Update an existing forum post."""
    db_post = await get_forum_post(db, post_id)
    if not db_post:
        return None
    
    # Check permissions
    if not is_admin and db_post.user_id != user_id:
        return None
    
    # Check if thread is locked
    if db_post.thread.is_locked and not is_admin:
        return None
    
    update_data = post_update.model_dump(exclude_unset=True)
    
    # Track edits
    if "content" in update_data:
        db_post.edit_count += 1
        db_post.edited_at = datetime.now(UTC)
        db_post.edited_by_id = user_id
    
    for field, value in update_data.items():
        setattr(db_post, field, value)
    
    await db.commit()
    await db.refresh(db_post)
    return db_post


async def delete_forum_post(
    db: AsyncSession,
    post_id: int,
    user_id: int,
    is_admin: bool = False,
    deletion_reason: Optional[str] = None,
    hard_delete: bool = False
) -> bool:
    """Delete a forum post (soft delete by default)."""
    db_post = await get_forum_post(db, post_id)
    if not db_post:
        return False
    
    # Check permissions
    if not is_admin and db_post.user_id != user_id:
        return False
    
    if hard_delete and is_admin:
        await db.delete(db_post)
    else:
        db_post.is_deleted = True
        db_post.deleted_at = datetime.now(UTC)
        db_post.deleted_by_id = user_id
        db_post.deletion_reason = deletion_reason
    
    await db.commit()
    return True


async def vote_on_post(
    db: AsyncSession,
    post_id: int,
    user_id: int,
    vote_type: VoteType
) -> ForumPost:
    """Vote on a forum post."""
    # Check if post exists
    db_post = await get_forum_post(db, post_id)
    if not db_post:
        raise ValueError("Post not found")
    
    # Check existing vote
    existing_vote = await db.execute(
        select(ForumVote)
        .where(ForumVote.post_id == post_id)
        .where(ForumVote.user_id == user_id)
    )
    vote = existing_vote.scalar_one_or_none()
    
    if vote:
        if vote.vote_type == vote_type:
            # Remove vote if clicking same type
            await db.delete(vote)
            if vote_type == VoteType.UPVOTE:
                db_post.upvote_count -= 1
            else:
                db_post.downvote_count -= 1
        else:
            # Change vote type
            old_type = vote.vote_type
            vote.vote_type = vote_type
            vote.updated_at = datetime.now(UTC)
            
            if old_type == VoteType.UPVOTE:
                db_post.upvote_count -= 1
                db_post.downvote_count += 1
            else:
                db_post.downvote_count -= 1
                db_post.upvote_count += 1
    else:
        # Create new vote
        new_vote = ForumVote(
            post_id=post_id,
            user_id=user_id,
            vote_type=vote_type
        )
        db.add(new_vote)
        
        if vote_type == VoteType.UPVOTE:
            db_post.upvote_count += 1
        else:
            db_post.downvote_count += 1
    
    # Update score
    db_post.score = db_post.upvote_count - db_post.downvote_count
    
    await db.commit()
    await db.refresh(db_post)
    return db_post


async def get_user_vote_on_post(
    db: AsyncSession,
    post_id: int,
    user_id: int
) -> Optional[VoteType]:
    """Get a user's vote on a post."""
    result = await db.execute(
        select(ForumVote.vote_type)
        .where(ForumVote.post_id == post_id)
        .where(ForumVote.user_id == user_id)
    )
    vote_type = result.scalar_one_or_none()
    return vote_type


async def get_post_replies(
    db: AsyncSession,
    post_id: int,
    include_deleted: bool = False
) -> List[ForumPost]:
    """Get all direct replies to a post."""
    query = select(ForumPost).where(ForumPost.parent_post_id == post_id)
    
    if not include_deleted:
        query = query.where(ForumPost.is_deleted == False)
    
    query = query.order_by(ForumPost.created_at)
    query = query.options(
        selectinload(ForumPost.user),
        selectinload(ForumPost.votes)
    )
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_user_post_count(db: AsyncSession, user_id: int) -> int:
    """Get total post count for a user."""
    result = await db.execute(
        select(func.count())
        .select_from(ForumPost)
        .where(ForumPost.user_id == user_id)
        .where(ForumPost.is_deleted == False)
    )
    return result.scalar() or 0


async def get_user_karma(db: AsyncSession, user_id: int) -> int:
    """Calculate user's total karma from posts."""
    result = await db.execute(
        select(func.sum(ForumPost.score))
        .where(ForumPost.user_id == user_id)
        .where(ForumPost.is_deleted == False)
    )
    return result.scalar() or 0
