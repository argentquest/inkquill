"""Blog engagement API endpoints for likes and follows."""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.models.blog_post import BlogPost
from app.models.blog_like import BlogLike
from app.models.blog_follow import BlogFollow
from app.schemas.blog import BlogPostRead
from app.schemas.base import ApiResponse
from app.services.blog_service import blog_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog/engagement", tags=["blog-engagement"])


def _build_blog_post_read(post: BlogPost) -> BlogPostRead:
    """Provide internal router support for build blog post read."""
    return BlogPostRead.model_validate(post, from_attributes=True)


@router.post("/posts/{post_id}/like", response_model=ApiResponse)
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Like or unlike a blog post."""
    try:
        # Check if post exists
        post_result = await db.execute(
            select(BlogPost).where(BlogPost.id == post_id)
        )
        post = post_result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        # Check if user already liked this post
        like_result = await db.execute(
            select(BlogLike).where(
                and_(
                    BlogLike.post_id == post_id,
                    BlogLike.user_id == current_user.id
                )
            )
        )
        existing_like = like_result.scalar_one_or_none()
        
        if existing_like:
            # Unlike the post
            await db.delete(existing_like)
            
            # Update like count
            post.like_count = max(0, post.like_count - 1)
            db.add(post)
            
            await db.commit()
            
            return ApiResponse.success_response(
                data={
                    "liked": False,
                    "like_count": post.like_count,
                    "message": "Post unliked successfully",
                }
            )
        else:
            # Like the post
            new_like = BlogLike(
                post_id=post_id,
                user_id=current_user.id
            )
            db.add(new_like)
            
            # Update like count
            post.like_count += 1
            db.add(post)
            
            await db.commit()
            
            return ApiResponse.success_response(
                data={
                    "liked": True,
                    "like_count": post.like_count,
                    "message": "Post liked successfully",
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling like for post {post_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle like"
        )


@router.get("/posts/{post_id}/like-status", response_model=ApiResponse)
async def get_like_status(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Check if current user has liked a post."""
    try:
        # Check if user liked this post
        like_result = await db.execute(
            select(BlogLike).where(
                and_(
                    BlogLike.post_id == post_id,
                    BlogLike.user_id == current_user.id
                )
            )
        )
        existing_like = like_result.scalar_one_or_none()
        
        # Get total like count
        post_result = await db.execute(
            select(BlogPost.like_count).where(BlogPost.id == post_id)
        )
        like_count = post_result.scalar() or 0
        
        return ApiResponse.success_response(
            data={
                "liked": existing_like is not None,
                "like_count": like_count,
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting like status for post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get like status"
        )


@router.post("/authors/{author_id}/follow", response_model=ApiResponse)
async def follow_author(
    author_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Follow or unfollow a blog author."""
    try:
        # Can't follow yourself
        if author_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot follow yourself"
            )
        
        # Check if author exists
        author_result = await db.execute(
            select(User).where(User.id == author_id)
        )
        author = author_result.scalar_one_or_none()
        
        if not author:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Author not found"
            )
        
        # Check if already following
        follow_result = await db.execute(
            select(BlogFollow).where(
                and_(
                    BlogFollow.author_id == author_id,
                    BlogFollow.follower_id == current_user.id
                )
            )
        )
        existing_follow = follow_result.scalar_one_or_none()
        
        if existing_follow:
            # Unfollow
            await db.delete(existing_follow)
            await db.commit()
            
            return ApiResponse.success_response(
                data={
                    "following": False,
                    "message": f"Unfollowed {author.display_name or author.username}",
                }
            )
        else:
            # Follow
            new_follow = BlogFollow(
                author_id=author_id,
                follower_id=current_user.id
            )
            db.add(new_follow)
            await db.commit()
            
            return ApiResponse.success_response(
                data={
                    "following": True,
                    "message": f"Now following {author.display_name or author.username}",
                }
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling follow for author {author_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to toggle follow"
        )


@router.get("/authors/{author_id}/follow-status", response_model=ApiResponse)
async def get_follow_status(
    author_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Check if current user is following an author."""
    try:
        # Check if following this author
        follow_result = await db.execute(
            select(BlogFollow).where(
                and_(
                    BlogFollow.author_id == author_id,
                    BlogFollow.follower_id == current_user.id
                )
            )
        )
        existing_follow = follow_result.scalar_one_or_none()
        
        # Get follower count
        follower_count_result = await db.execute(
            select(func.count(BlogFollow.id)).where(BlogFollow.author_id == author_id)
        )
        follower_count = follower_count_result.scalar() or 0
        
        return ApiResponse.success_response(
            data={
                "following": existing_follow is not None,
                "follower_count": follower_count,
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting follow status for author {author_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get follow status"
        )


@router.get("/my-liked-posts", response_model=ApiResponse)
async def get_my_liked_posts(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get posts liked by the current user."""
    try:
        # Get liked post IDs
        liked_posts_result = await db.execute(
            select(BlogLike.post_id)
            .where(BlogLike.user_id == current_user.id)
            .order_by(BlogLike.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        liked_post_ids = [row[0] for row in liked_posts_result.fetchall()]
        
        if not liked_post_ids:
            return ApiResponse.success_response(data=[])
        
        # Get the actual posts
        posts_result = await db.execute(
            select(BlogPost)
            .where(BlogPost.id.in_(liked_post_ids))
            .options(
                selectinload(BlogPost.author),
                selectinload(BlogPost.category),
                selectinload(BlogPost.tags),
            )
            .order_by(BlogPost.published_at.desc())
        )
        posts = posts_result.scalars().all()
        
        return ApiResponse.success_response(
            data=[_build_blog_post_read(post) for post in posts]
        )
        
    except Exception as e:
        logger.error(f"Error getting liked posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get liked posts"
        )


@router.get("/following-posts", response_model=ApiResponse)
async def get_following_posts(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get recent posts from followed authors."""
    try:
        # Get followed author IDs
        following_result = await db.execute(
            select(BlogFollow.author_id)
            .where(BlogFollow.follower_id == current_user.id)
        )
        followed_author_ids = [row[0] for row in following_result.fetchall()]
        
        if not followed_author_ids:
            return ApiResponse.success_response(data=[])
        
        # Get posts from followed authors
        posts = await blog_service.get_published_posts(
            db=db,
            skip=skip,
            limit=limit,
            author_ids=followed_author_ids
        )
        
        return ApiResponse.success_response(
            data=[_build_blog_post_read(post) for post in posts]
        )
        
    except Exception as e:
        logger.error(f"Error getting following posts: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get following posts"
        )


@router.get("/my-followers", response_model=ApiResponse)
async def get_my_followers(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user's followers."""
    try:
        # Get follower count and recent followers
        followers_result = await db.execute(
            select(BlogFollow, User)
            .join(User, BlogFollow.follower_id == User.id)
            .where(BlogFollow.author_id == current_user.id)
            .order_by(BlogFollow.created_at.desc())
            .limit(50)
        )
        followers_data = followers_result.fetchall()
        
        followers = []
        for follow, user in followers_data:
            followers.append({
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "followed_at": follow.created_at.isoformat()
            })
        
        # Get total count
        count_result = await db.execute(
            select(func.count(BlogFollow.id))
            .where(BlogFollow.author_id == current_user.id)
        )
        total_count = count_result.scalar() or 0
        
        return ApiResponse.success_response(
            data={
                "followers": followers,
                "total_count": total_count,
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting followers: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get followers"
        )


@router.get("/my-following", response_model=ApiResponse)
async def get_my_following(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get authors that current user is following."""
    try:
        # Get following data
        following_result = await db.execute(
            select(BlogFollow, User)
            .join(User, BlogFollow.author_id == User.id)
            .where(BlogFollow.follower_id == current_user.id)
            .order_by(BlogFollow.created_at.desc())
        )
        following_data = following_result.fetchall()
        
        following = []
        for follow, user in following_data:
            following.append({
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name,
                "followed_at": follow.created_at.isoformat()
            })
        
        return ApiResponse.success_response(
            data={
                "following": following,
                "total_count": len(following),
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting following: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get following"
        )
