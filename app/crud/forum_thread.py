"""CRUD operations for forum threads."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.models.forum import ForumThread, ForumPost, ForumSubscription, ThreadStatus
from app.models.user import User
from app.schemas.forum import ForumThreadCreate, ForumThreadUpdate


async def get_forum_thread(
    db: AsyncSession, 
    thread_id: int,
    increment_view: bool = False
) -> Optional[ForumThread]:
    """Get a single forum thread by ID."""
    result = await db.execute(
        select(ForumThread)
        .where(ForumThread.id == thread_id)
        .where(ForumThread.is_deleted == False)
        .options(
            selectinload(ForumThread.category),
            selectinload(ForumThread.user),
            selectinload(ForumThread.world),
            selectinload(ForumThread.story),
            selectinload(ForumThread.posts).selectinload(ForumPost.user)
        )
    )
    thread = result.scalar_one_or_none()
    
    if thread and increment_view:
        thread.view_count += 1
        await db.commit()
        await db.refresh(thread)

    return thread


async def get_forum_threads(
    db: AsyncSession,
    category_id: Optional[int] = None,
    world_id: Optional[int] = None,
    story_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[ThreadStatus] = None,
    skip: int = 0,
    limit: int = 20,
    order_by: str = "recent"  # recent, popular, updated
) -> List[ForumThread]:
    """Get forum threads with filtering and pagination."""
    query = select(ForumThread).where(ForumThread.is_deleted == False)
    
    # Apply filters
    if category_id:
        query = query.where(ForumThread.category_id == category_id)
    if world_id:
        query = query.where(ForumThread.world_id == world_id)
    if story_id:
        query = query.where(ForumThread.story_id == story_id)
    if user_id:
        query = query.where(ForumThread.user_id == user_id)
    if status:
        query = query.where(ForumThread.status == status)
    
    # Apply ordering
    if order_by == "popular":
        query = query.order_by(
            desc(ForumThread.is_pinned),
            desc(ForumThread.view_count)
        )
    elif order_by == "updated":
        query = query.order_by(
            desc(ForumThread.is_pinned),
            desc(ForumThread.last_post_at)
        )
    else:  # recent
        query = query.order_by(
            desc(ForumThread.is_pinned),
            desc(ForumThread.created_at)
        )
    
    query = query.offset(skip).limit(limit)
    query = query.options(
        selectinload(ForumThread.category),
        selectinload(ForumThread.user),
        selectinload(ForumThread.last_post_by),
        selectinload(ForumThread.world),
        selectinload(ForumThread.story)
    )
    
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_forum_thread(
    db: AsyncSession,
    thread: ForumThreadCreate,
    user_id: int
) -> ForumThread:
    """Create a new forum thread."""
    # Generate slug from title
    slug = thread.title.lower().replace(" ", "-").replace("_", "-")
    slug = "".join(c for c in slug if c.isalnum() or c == "-")[:255]
    
    # Ensure slug is unique within category
    counter = 0
    original_slug = slug
    while True:
        existing = await db.execute(
            select(ForumThread)
            .where(ForumThread.category_id == thread.category_id)
            .where(ForumThread.slug == slug)
        )
        if not existing.scalar_one_or_none():
            break
        counter += 1
        slug = f"{original_slug}-{counter}"
    
    db_thread = ForumThread(
        title=thread.title,
        slug=slug,
        category_id=thread.category_id,
        user_id=user_id,
        world_id=thread.world_id,
        story_id=thread.story_id,
        status=ThreadStatus.OPEN
    )
    
    db.add(db_thread)
    await db.commit()
    await db.refresh(db_thread)
    
    # Auto-subscribe creator to thread
    subscription = ForumSubscription(
        thread_id=db_thread.id,
        user_id=user_id
    )
    db.add(subscription)
    await db.commit()
    
    return db_thread


async def update_forum_thread(
    db: AsyncSession,
    thread_id: int,
    thread_update: ForumThreadUpdate,
    user_id: int,
    is_admin: bool = False
) -> Optional[ForumThread]:
    """Update an existing forum thread."""
    db_thread = await get_forum_thread(db, thread_id)
    if not db_thread:
        return None
    
    # Check permissions
    if not is_admin and db_thread.user_id != user_id:
        # Regular users can only edit their own threads
        return None
    
    update_data = thread_update.model_dump(exclude_unset=True)
    
    # Handle special admin-only fields
    if not is_admin:
        update_data.pop("is_pinned", None)
        update_data.pop("is_locked", None)
        update_data.pop("status", None)
    
    for field, value in update_data.items():
        setattr(db_thread, field, value)
    
    db_thread.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(db_thread)
    return db_thread


async def delete_forum_thread(
    db: AsyncSession,
    thread_id: int,
    user_id: int,
    is_admin: bool = False,
    hard_delete: bool = False
) -> bool:
    """Delete a forum thread (soft delete by default)."""
    db_thread = await get_forum_thread(db, thread_id)
    if not db_thread:
        return False
    
    # Check permissions
    if not is_admin and db_thread.user_id != user_id:
        return False
    
    if hard_delete and is_admin:
        await db.delete(db_thread)
    else:
        db_thread.is_deleted = True
        db_thread.deleted_at = datetime.utcnow()
        db_thread.deleted_by_id = user_id
    
    await db.commit()
    return True


async def toggle_thread_lock(
    db: AsyncSession,
    thread_id: int,
    is_admin: bool = False
) -> Optional[ForumThread]:
    """Toggle the locked status of a thread."""
    if not is_admin:
        return None
        
    db_thread = await get_forum_thread(db, thread_id)
    if not db_thread:
        return None
    
    db_thread.is_locked = not db_thread.is_locked
    if db_thread.is_locked:
        db_thread.status = ThreadStatus.LOCKED
    else:
        db_thread.status = ThreadStatus.OPEN
    
    await db.commit()
    await db.refresh(db_thread)
    return db_thread


async def toggle_thread_pin(
    db: AsyncSession,
    thread_id: int,
    is_admin: bool = False
) -> Optional[ForumThread]:
    """Toggle the pinned status of a thread."""
    if not is_admin:
        return None
        
    db_thread = await get_forum_thread(db, thread_id)
    if not db_thread:
        return None
    
    db_thread.is_pinned = not db_thread.is_pinned
    if db_thread.is_pinned:
        db_thread.status = ThreadStatus.PINNED
    elif not db_thread.is_locked:
        db_thread.status = ThreadStatus.OPEN
    
    await db.commit()
    await db.refresh(db_thread)
    return db_thread


async def update_thread_last_post(
    db: AsyncSession,
    thread_id: int,
    user_id: int
) -> None:
    """Update thread's last post information."""
    db_thread = await db.get(ForumThread, thread_id)
    if db_thread:
        db_thread.last_post_at = datetime.utcnow()
        db_thread.last_post_by_id = user_id
        db_thread.post_count += 1
        await db.commit()


async def is_thread_subscribed(
    db: AsyncSession,
    thread_id: int,
    user_id: int
) -> bool:
    """Check if a user is subscribed to a thread."""
    result = await db.execute(
        select(ForumSubscription)
        .where(ForumSubscription.thread_id == thread_id)
        .where(ForumSubscription.user_id == user_id)
    )
    return result.scalar_one_or_none() is not None


async def toggle_thread_subscription(
    db: AsyncSession,
    thread_id: int,
    user_id: int
) -> bool:
    """Toggle thread subscription for a user."""
    existing = await db.execute(
        select(ForumSubscription)
        .where(ForumSubscription.thread_id == thread_id)
        .where(ForumSubscription.user_id == user_id)
    )
    subscription = existing.scalar_one_or_none()
    
    if subscription:
        await db.delete(subscription)
        await db.commit()
        return False
    else:
        new_subscription = ForumSubscription(
            thread_id=thread_id,
            user_id=user_id
        )
        db.add(new_subscription)
        await db.commit()
        return True
