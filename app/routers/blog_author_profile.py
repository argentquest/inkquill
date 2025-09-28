"""Blog author profile management API endpoints."""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.models.blog_post import BlogPost, BlogPostStatus
from app.models.blog_author_profile import BlogAuthorProfile
from app.models.blog_follow import BlogFollow
from app.models.blog_like import BlogLike
from app.schemas.blog import BlogAuthorProfileCreate, BlogAuthorProfileUpdate, BlogAuthorProfileRead

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog/author-profile", tags=["blog-author-profile"])


@router.get("/", response_model=BlogAuthorProfileRead)
async def get_my_author_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user's author profile."""
    try:
        # Get or create author profile
        profile_result = await db.execute(
            select(BlogAuthorProfile).where(BlogAuthorProfile.user_id == current_user.id)
        )
        profile = profile_result.scalar_one_or_none()
        
        if not profile:
            # Create default profile
            profile = BlogAuthorProfile(
                user_id=current_user.id,
                bio="",
                allow_comments_default=True,
                auto_publish=False,
                email_notifications=True
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)
        
        # Update statistics
        await update_profile_stats(db, profile)
        
        return profile
        
    except Exception as e:
        logger.error(f"Error getting author profile for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get author profile"
        )


@router.put("/", response_model=BlogAuthorProfileRead)
async def update_my_author_profile(
    profile_data: BlogAuthorProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Update current user's author profile."""
    try:
        # Get existing profile
        profile_result = await db.execute(
            select(BlogAuthorProfile).where(BlogAuthorProfile.user_id == current_user.id)
        )
        profile = profile_result.scalar_one_or_none()
        
        if not profile:
            # Create new profile
            profile = BlogAuthorProfile(user_id=current_user.id)
            db.add(profile)
        
        # Update fields
        for field, value in profile_data.model_dump(exclude_unset=True).items():
            setattr(profile, field, value)
        
        await db.commit()
        await db.refresh(profile)
        
        return profile
        
    except Exception as e:
        logger.error(f"Error updating author profile for user {current_user.id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update author profile"
        )


@router.get("/stats")
async def get_my_author_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get detailed author statistics."""
    try:
        # Get basic stats
        post_stats = await db.execute(
            select(
                func.count(BlogPost.id).label('total_posts'),
                func.sum(BlogPost.view_count).label('total_views'),
                func.sum(BlogPost.like_count).label('total_likes')
            )
            .where(
                and_(
                    BlogPost.author_id == current_user.id,
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.deleted_at.is_(None)
                )
            )
        )
        stats = post_stats.first()
        
        # Get follower count
        follower_count_result = await db.execute(
            select(func.count(BlogFollow.id))
            .where(BlogFollow.author_id == current_user.id)
        )
        follower_count = follower_count_result.scalar() or 0
        
        # Get draft count
        draft_count_result = await db.execute(
            select(func.count(BlogPost.id))
            .where(
                and_(
                    BlogPost.author_id == current_user.id,
                    BlogPost.status == BlogPostStatus.DRAFT,
                    BlogPost.deleted_at.is_(None)
                )
            )
        )
        draft_count = draft_count_result.scalar() or 0
        
        # Get recent engagement (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        recent_likes_result = await db.execute(
            select(func.count(BlogLike.id))
            .join(BlogPost, BlogLike.post_id == BlogPost.id)
            .where(
                and_(
                    BlogPost.author_id == current_user.id,
                    BlogLike.created_at >= thirty_days_ago
                )
            )
        )
        recent_likes = recent_likes_result.scalar() or 0
        
        recent_follows_result = await db.execute(
            select(func.count(BlogFollow.id))
            .where(
                and_(
                    BlogFollow.author_id == current_user.id,
                    BlogFollow.created_at >= thirty_days_ago
                )
            )
        )
        recent_follows = recent_follows_result.scalar() or 0
        
        return {
            "total_posts": stats.total_posts or 0,
            "total_views": stats.total_views or 0,
            "total_likes": stats.total_likes or 0,
            "follower_count": follower_count,
            "draft_count": draft_count,
            "recent_stats": {
                "likes_last_30_days": recent_likes,
                "follows_last_30_days": recent_follows
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting author stats for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get author statistics"
        )


@router.get("/dashboard")
async def get_author_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get author dashboard data."""
    try:
        from sqlalchemy.orm import selectinload
        
        # Check if user is admin to show all posts or just their own
        if current_user.is_admin:
            # Admin users see all posts from all users
            recent_posts_result = await db.execute(
                select(BlogPost)
                .options(selectinload(BlogPost.author))
                .where(BlogPost.deleted_at.is_(None))
                .order_by(BlogPost.updated_at.desc())
                .limit(20)  # Show more posts for admin view
            )
            recent_posts = recent_posts_result.scalars().all()
            
            # Get top performing posts from all users
            top_posts_result = await db.execute(
                select(BlogPost)
                .options(selectinload(BlogPost.author))
                .where(
                    and_(
                        BlogPost.status == BlogPostStatus.PUBLISHED,
                        BlogPost.deleted_at.is_(None)
                    )
                )
                .order_by(BlogPost.view_count.desc())
                .limit(10)
            )
            top_posts = top_posts_result.scalars().all()
        else:
            # Regular users see only their own posts
            recent_posts_result = await db.execute(
                select(BlogPost)
                .options(selectinload(BlogPost.author))
                .where(
                    and_(
                        BlogPost.author_id == current_user.id,
                        BlogPost.deleted_at.is_(None)
                    )
                )
                .order_by(BlogPost.updated_at.desc())
                .limit(5)
            )
            recent_posts = recent_posts_result.scalars().all()
            
            # Get top performing posts
            top_posts_result = await db.execute(
                select(BlogPost)
                .options(selectinload(BlogPost.author))
                .where(
                    and_(
                        BlogPost.author_id == current_user.id,
                        BlogPost.status == BlogPostStatus.PUBLISHED,
                        BlogPost.deleted_at.is_(None)
                    )
                )
                .order_by(BlogPost.view_count.desc())
                .limit(5)
            )
            top_posts = top_posts_result.scalars().all()
        
        # Get recent followers (same for both admin and regular users)
        recent_followers_result = await db.execute(
            select(BlogFollow, User)
            .join(User, BlogFollow.follower_id == User.id)
            .where(BlogFollow.author_id == current_user.id)
            .order_by(BlogFollow.created_at.desc())
            .limit(5)
        )
        recent_followers_data = recent_followers_result.fetchall()
        
        recent_followers = []
        for follow, user in recent_followers_data:
            recent_followers.append({
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "followed_at": follow.created_at.isoformat()
            })
        
        # Get author profile
        profile_result = await db.execute(
            select(BlogAuthorProfile).where(BlogAuthorProfile.user_id == current_user.id)
        )
        profile = profile_result.scalar_one_or_none()
        
        return {
            "recent_posts": [
                {
                    "id": post.id,
                    "title": post.title,
                    "status": post.status.value,
                    "view_count": post.view_count,
                    "like_count": post.like_count,
                    "updated_at": post.updated_at.isoformat(),
                    "author": {
                        "id": post.author.id,
                        "username": post.author.username,
                        "display_name": post.author.display_name
                    } if post.author else None,
                    "author_id": post.author_id
                }
                for post in recent_posts
            ],
            "recent_followers": recent_followers,
            "top_posts": [
                {
                    "id": post.id,
                    "title": post.title,
                    "view_count": post.view_count,
                    "like_count": post.like_count,
                    "published_at": post.published_at.isoformat() if post.published_at else None,
                    "author": {
                        "id": post.author.id,
                        "username": post.author.username,
                        "display_name": post.author.display_name
                    } if post.author else None,
                    "author_id": post.author_id
                }
                for post in top_posts
            ],
            "profile": {
                "bio": profile.bio if profile else "",
                "total_posts": profile.total_posts if profile else 0,
                "total_views": profile.total_views if profile else 0,
                "total_likes": profile.total_likes if profile else 0,
                "follower_count": profile.follower_count if profile else 0
            },
            "is_admin": current_user.is_admin
        }
        
    except Exception as e:
        logger.error(f"Error getting author dashboard for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get author dashboard"
        )


@router.get("/{user_id}", response_model=BlogAuthorProfileRead)
async def get_author_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """Get public author profile by user ID."""
    try:
        # Get user
        user_result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found"
            )
        
        # Get author profile
        profile_result = await db.execute(
            select(BlogAuthorProfile).where(BlogAuthorProfile.user_id == user_id)
        )
        profile = profile_result.scalar_one_or_none()
        
        if not profile:
            # Return basic profile info
            return {
                "id": 0,
                "user_id": user_id,
                "bio": "",
                "profile_image_url": None,
                "website_url": None,
                "twitter_handle": None,
                "instagram_handle": None,
                "linkedin_url": None,
                "total_posts": 0,
                "total_views": 0,
                "total_likes": 0,
                "follower_count": 0,
                "created_at": user.created_at,
                "updated_at": user.updated_at
            }
        
        # Update and return profile
        await update_profile_stats(db, profile)
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting author profile for user {user_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get author profile"
        )


async def update_profile_stats(db: AsyncSession, profile: BlogAuthorProfile):
    """Update cached statistics for an author profile."""
    try:
        # Get post stats
        post_stats = await db.execute(
            select(
                func.count(BlogPost.id).label('total_posts'),
                func.sum(BlogPost.view_count).label('total_views'),
                func.sum(BlogPost.like_count).label('total_likes')
            )
            .where(
                and_(
                    BlogPost.author_id == profile.user_id,
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.deleted_at.is_(None)
                )
            )
        )
        stats = post_stats.first()
        
        # Get follower count
        follower_count_result = await db.execute(
            select(func.count(BlogFollow.id))
            .where(BlogFollow.author_id == profile.user_id)
        )
        follower_count = follower_count_result.scalar() or 0
        
        # Update profile
        profile.total_posts = stats.total_posts or 0
        profile.total_views = stats.total_views or 0
        profile.total_likes = stats.total_likes or 0
        profile.follower_count = follower_count
        
        await db.commit()
        
    except Exception as e:
        logger.error(f"Error updating profile stats for user {profile.user_id}: {e}")
        await db.rollback()