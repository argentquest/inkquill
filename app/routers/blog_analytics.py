"""Blog analytics API endpoints."""
import logging
import ipaddress
from datetime import UTC, datetime, date, timedelta
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload

from app.core.deps import get_db_session, get_current_active_user, get_current_user
from app.models.user import User
from app.models.blog_post import BlogPost, BlogPostStatus
from app.models.blog_view import BlogView
from app.models.blog_like import BlogLike
from app.models.blog_comment import BlogComment
from app.models.blog_analytics_summary import BlogAnalyticsSummary
from app.services.blog_analytics_summary import blog_analytics_summary_service
from app.schemas.base import ApiResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog/analytics", tags=["blog-analytics"])


def _normalize_client_ip(raw_host: Optional[str]) -> str:
    """Provide internal router support for normalize client ip."""
    if not raw_host:
        return "127.0.0.1"
    try:
        return str(ipaddress.ip_address(raw_host))
    except ValueError:
        return "127.0.0.1"


@router.post("/track-view/{post_id}", response_model=ApiResponse)
async def track_view(
    post_id: int,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> ApiResponse:
    """Track a blog post view."""
    try:
        # Check if post exists and is published
        post_result = await db.execute(
            select(BlogPost).where(
                and_(
                    BlogPost.id == post_id,
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.deleted_at.is_(None)
                )
            )
        )
        post = post_result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog post not found"
            )
        
        # Get client info
        client_ip = _normalize_client_ip(request.client.host if request.client else None)
        user_agent = request.headers.get("user-agent", "")
        referrer = request.headers.get("referer", "")
        
        # Check for duplicate view (same IP within 1 hour)
        one_hour_ago = datetime.now(UTC) - timedelta(hours=1)
        
        duplicate_check = await db.execute(
            select(BlogView).where(
                and_(
                    BlogView.post_id == post_id,
                    BlogView.ip_address == client_ip,
                    BlogView.created_at >= one_hour_ago
                )
            )
        )
        existing_view = duplicate_check.scalar_one_or_none()
        
        if existing_view:
            return ApiResponse.success_response(data={
                "tracked": False,
                "message": "View already tracked recently",
                "view_count": post.view_count
            })
        
        # Create new view record
        view = BlogView(
            post_id=post_id,
            user_id=current_user.id if current_user else None,
            ip_address=client_ip,
            user_agent=user_agent,
            referrer_url=referrer
        )
        db.add(view)
        
        # Increment post view count
        post.view_count += 1
        db.add(post)
        
        await db.commit()
        
        return ApiResponse.success_response(data={
            "tracked": True,
            "message": "View tracked successfully",
            "view_count": post.view_count
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error tracking view for post {post_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to track view"
        )


@router.put("/track-read-time/{post_id}", response_model=ApiResponse)
async def track_read_time(
    post_id: int,
    request: Request,
    read_time: int = Query(..., description="Reading time in seconds"),
    current_user: Optional[User] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
) -> ApiResponse:
    """Update reading time for a view."""
    try:
        client_ip = _normalize_client_ip(request.client.host if request.client else None)
        
        # Find recent view to update
        view_result = await db.execute(
            select(BlogView)
            .where(
                and_(
                    BlogView.post_id == post_id,
                    BlogView.ip_address == client_ip,
                    BlogView.created_at >= datetime.now(UTC) - timedelta(hours=2)
                )
            )
            .order_by(desc(BlogView.created_at))
            .limit(1)
        )
        view = view_result.scalar_one_or_none()
        
        if view:
            view.view_duration = read_time
            await db.commit()
            
            return ApiResponse.success_response(data={
                "updated": True,
                "message": "Reading time updated",
                "read_time": read_time
            })
        else:
            return ApiResponse.success_response(data={
                "updated": False,
                "message": "No recent view found to update"
            })
        
    except Exception as e:
        logger.error(f"Error updating read time for post {post_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update reading time"
        )


@router.get("/post/{post_id}", response_model=ApiResponse)
async def get_post_analytics(
    post_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> ApiResponse:
    """Get analytics for a specific post."""
    try:
        # Check if user owns the post
        post_result = await db.execute(
            select(BlogPost).where(
                and_(
                    BlogPost.id == post_id,
                    BlogPost.author_id == current_user.id
                )
            )
        )
        post = post_result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or access denied"
            )
        
        # Date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get daily view counts
        daily_views = await db.execute(
            select(
                func.date(BlogView.created_at).label('date'),
                func.count(BlogView.id).label('views'),
                func.count(func.distinct(BlogView.ip_address)).label('unique_views')
            )
            .where(
                and_(
                    BlogView.post_id == post_id,
                    func.date(BlogView.created_at) >= start_date,
                    func.date(BlogView.created_at) <= end_date
                )
            )
            .group_by(func.date(BlogView.created_at))
            .order_by(func.date(BlogView.created_at))
        )
        daily_stats = daily_views.fetchall()
        
        # Get engagement stats
        total_likes = await db.execute(
            select(func.count(BlogLike.id))
            .where(BlogLike.post_id == post_id)
        )
        like_count = total_likes.scalar() or 0
        
        total_comments = await db.execute(
            select(func.count(BlogComment.id))
            .where(BlogComment.post_id == post_id)
        )
        comment_count = total_comments.scalar() or 0
        
        # Get reading time stats
        reading_stats = await db.execute(
            select(
                func.avg(BlogView.view_duration).label('avg_read_time'),
                func.max(BlogView.view_duration).label('max_read_time'),
                func.count(BlogView.id).filter(BlogView.view_duration.isnot(None)).label('tracked_reads')
            )
            .where(BlogView.post_id == post_id)
        )
        read_stats = reading_stats.first()
        
        # Get referrer stats
        referrer_stats = await db.execute(
            select(
                BlogView.referrer_url,
                func.count(BlogView.id).label('count')
            )
            .where(
                and_(
                    BlogView.post_id == post_id,
                    BlogView.referrer_url.isnot(None),
                    BlogView.referrer_url != ''
                )
            )
            .group_by(BlogView.referrer_url)
            .order_by(desc(func.count(BlogView.id)))
            .limit(10)
        )
        referrers = referrer_stats.fetchall()
        
        # Format daily data
        daily_data = []
        for stat in daily_stats:
            daily_data.append({
                "date": stat.date.isoformat(),
                "views": stat.views,
                "unique_views": stat.unique_views
            })
        
        return ApiResponse.success_response(data={
            "post": {
                "id": post.id,
                "title": post.title,
                "published_at": post.published_at.isoformat() if post.published_at else None,
                "total_views": post.view_count,
                "total_likes": like_count,
                "total_comments": comment_count
            },
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "daily_stats": daily_data,
            "engagement": {
                "like_count": like_count,
                "comment_count": comment_count,
                "engagement_rate": round((like_count + comment_count) / max(post.view_count, 1) * 100, 2)
            },
            "reading": {
                "avg_read_time": round(read_stats.avg_read_time or 0),
                "max_read_time": read_stats.max_read_time or 0,
                "tracked_reads": read_stats.tracked_reads or 0
            },
            "referrers": [
                {
                    "url": ref.referrer_url,
                    "count": ref.count
                }
                for ref in referrers
            ]
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics for post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get post analytics"
        )


@router.get("/author-overview", response_model=ApiResponse)
async def get_author_analytics_overview(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> ApiResponse:
    """Get analytics overview for the current author."""
    try:
        # Date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get author's published posts
        posts_result = await db.execute(
            select(BlogPost.id)
            .where(
                and_(
                    BlogPost.author_id == current_user.id,
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.deleted_at.is_(None)
                )
            )
        )
        post_ids = [row[0] for row in posts_result.fetchall()]
        
        if not post_ids:
            return ApiResponse.success_response(data={
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "overview": {
                    "total_views": 0,
                    "total_likes": 0,
                    "total_comments": 0,
                    "total_posts": 0
                },
                "daily_stats": [],
                "top_posts": []
            })
        
        # Get overall stats
        total_views = await db.execute(
            select(func.sum(BlogPost.view_count))
            .where(BlogPost.id.in_(post_ids))
        )
        view_count = total_views.scalar() or 0
        
        total_likes = await db.execute(
            select(func.count(BlogLike.id))
            .where(BlogLike.post_id.in_(post_ids))
        )
        like_count = total_likes.scalar() or 0
        
        total_comments = await db.execute(
            select(func.count(BlogComment.id))
            .where(BlogComment.post_id.in_(post_ids))
        )
        comment_count = total_comments.scalar() or 0
        
        # Get daily stats for the period
        daily_stats = await db.execute(
            select(
                func.date(BlogView.created_at).label('date'),
                func.count(BlogView.id).label('views'),
                func.count(func.distinct(BlogView.ip_address)).label('unique_views')
            )
            .where(
                and_(
                    BlogView.post_id.in_(post_ids),
                    func.date(BlogView.created_at) >= start_date,
                    func.date(BlogView.created_at) <= end_date
                )
            )
            .group_by(func.date(BlogView.created_at))
            .order_by(func.date(BlogView.created_at))
        )
        daily_data = daily_stats.fetchall()
        
        # Get top performing posts
        top_posts = await db.execute(
            select(BlogPost)
            .where(BlogPost.id.in_(post_ids))
            .order_by(desc(BlogPost.view_count))
            .limit(5)
        )
        top_posts_data = top_posts.scalars().all()
        
        # Format daily data
        daily_analytics = []
        for stat in daily_data:
            daily_analytics.append({
                "date": stat.date.isoformat(),
                "views": stat.views,
                "unique_views": stat.unique_views
            })
        
        return ApiResponse.success_response(data={
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "overview": {
                "total_views": view_count,
                "total_likes": like_count,
                "total_comments": comment_count,
                "total_posts": len(post_ids),
                "avg_engagement_rate": round((like_count + comment_count) / max(view_count, 1) * 100, 2)
            },
            "daily_stats": daily_analytics,
            "top_posts": [
                {
                    "id": post.id,
                    "title": post.title,
                    "view_count": post.view_count,
                    "like_count": post.like_count,
                    "published_at": post.published_at.isoformat() if post.published_at else None
                }
                for post in top_posts_data
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting author analytics overview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get analytics overview"
        )


@router.get("/trending", response_model=ApiResponse)
async def get_trending_analytics(
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze"),
    limit: int = Query(10, ge=1, le=50, description="Number of posts to return"),
    db: AsyncSession = Depends(get_db_session)
) -> ApiResponse:
    """Get trending posts analytics."""
    try:
        # Date range for trending calculation
        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=days)
        
        # Get posts with recent activity
        trending_posts = await db.execute(
            select(
                BlogPost,
                func.count(BlogView.id).label('recent_views'),
                func.count(BlogLike.id).label('recent_likes')
            )
            .options(selectinload(BlogPost.author))
            .outerjoin(
                BlogView,
                and_(
                    BlogView.post_id == BlogPost.id,
                    BlogView.created_at >= start_date
                )
            )
            .outerjoin(
                BlogLike,
                and_(
                    BlogLike.post_id == BlogPost.id,
                    BlogLike.created_at >= start_date
                )
            )
            .where(
                and_(
                    BlogPost.status == BlogPostStatus.PUBLISHED,
                    BlogPost.deleted_at.is_(None)
                )
            )
            .group_by(BlogPost.id)
            .order_by(
                desc(func.count(BlogView.id) + func.count(BlogLike.id) * 2)
            )
            .limit(limit)
        )
        trending_data = trending_posts.fetchall()
        
        return ApiResponse.success_response(data={
            "period": {
                "start_date": start_date.date().isoformat(),
                "end_date": end_date.date().isoformat(),
                "days": days
            },
            "trending_posts": [
                {
                    "id": row.BlogPost.id,
                    "title": row.BlogPost.title,
                    "author": {
                        "id": row.BlogPost.author.id,
                        "username": row.BlogPost.author.username,
                        "display_name": row.BlogPost.author.display_name
                    },
                    "total_views": row.BlogPost.view_count,
                    "total_likes": row.BlogPost.like_count,
                    "recent_views": row.recent_views,
                    "recent_likes": row.recent_likes,
                    "trending_score": row.recent_views + (row.recent_likes * 2),
                    "published_at": row.BlogPost.published_at.isoformat() if row.BlogPost.published_at else None
                }
                for row in trending_data
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting trending analytics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get trending analytics"
        )


@router.post("/generate-summary/{post_id}", response_model=ApiResponse)
async def generate_daily_summary(
    post_id: int,
    target_date: date = Query(default_factory=lambda: date.today() - timedelta(days=1)),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> ApiResponse:
    """Generate daily analytics summary for a post."""
    try:
        # Check if user owns the post
        post_result = await db.execute(
            select(BlogPost).where(
                and_(
                    BlogPost.id == post_id,
                    BlogPost.author_id == current_user.id
                )
            )
        )
        post = post_result.scalar_one_or_none()
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found or access denied"
            )
        
        # Check if summary already exists
        existing_summary = await db.execute(
            select(BlogAnalyticsSummary).where(
                and_(
                    BlogAnalyticsSummary.post_id == post_id,
                    BlogAnalyticsSummary.date == target_date
                )
            )
        )
        summary = existing_summary.scalar_one_or_none()
        
        if not summary:
            summary = BlogAnalyticsSummary(
                post_id=post_id,
                date=target_date
            )
            db.add(summary)
        
        # Calculate metrics for the target date
        start_datetime = datetime.combine(target_date, datetime.min.time())
        end_datetime = start_datetime + timedelta(days=1)
        
        # View metrics
        view_stats = await db.execute(
            select(
                func.count(BlogView.id).label('total_views'),
                func.count(func.distinct(BlogView.ip_address)).label('unique_views'),
                func.avg(BlogView.view_duration).label('avg_read_time')
            )
            .where(
                and_(
                    BlogView.post_id == post_id,
                    BlogView.created_at >= start_datetime,
                    BlogView.created_at < end_datetime
                )
            )
        )
        view_data = view_stats.first()
        
        # Engagement metrics
        new_likes = await db.execute(
            select(func.count(BlogLike.id))
            .where(
                and_(
                    BlogLike.post_id == post_id,
                    BlogLike.created_at >= start_datetime,
                    BlogLike.created_at < end_datetime
                )
            )
        )
        likes_count = new_likes.scalar() or 0
        
        new_comments = await db.execute(
            select(func.count(BlogComment.id))
            .where(
                and_(
                    BlogComment.post_id == post_id,
                    BlogComment.created_at >= start_datetime,
                    BlogComment.created_at < end_datetime
                )
            )
        )
        comments_count = new_comments.scalar() or 0
        
        # Update summary
        summary.total_views = view_data.total_views or 0
        summary.unique_views = view_data.unique_views or 0
        summary.avg_read_time = int(view_data.avg_read_time or 0)
        summary.new_likes = likes_count
        summary.new_comments = comments_count
        
        # Calculate bounce rate (views with < 10 seconds read time)
        if summary.total_views > 0:
            short_reads = await db.execute(
                select(func.count(BlogView.id))
                .where(
                    and_(
                        BlogView.post_id == post_id,
                        BlogView.created_at >= start_datetime,
                        BlogView.created_at < end_datetime,
                        or_(
                            BlogView.view_duration.is_(None),
                            BlogView.view_duration < 10
                        )
                    )
                )
            )
            bounce_count = short_reads.scalar() or 0
            summary.bounce_rate = round((bounce_count / summary.total_views) * 100, 2)
        else:
            summary.bounce_rate = 0.0
        
        await db.commit()
        
        return ApiResponse.success_response(data={
            "summary_generated": True,
            "date": target_date.isoformat(),
            "metrics": {
                "total_views": summary.total_views,
                "unique_views": summary.unique_views,
                "new_likes": summary.new_likes,
                "new_comments": summary.new_comments,
                "avg_read_time": summary.avg_read_time,
                "bounce_rate": float(summary.bounce_rate)
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating summary for post {post_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate analytics summary"
        )


@router.get("/dashboard", response_model=ApiResponse)
async def get_dashboard_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> ApiResponse:
    """Get comprehensive analytics dashboard summary."""
    try:
        summary = await blog_analytics_summary_service.get_dashboard_summary(
            db=db,
            user_id=current_user.id,
            days=days
        )
        return ApiResponse.success_response(data=summary)
        
    except Exception as e:
        logger.error(f"Error getting dashboard summary for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get dashboard summary"
        )


@router.get("/engagement", response_model=ApiResponse)
async def get_engagement_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> ApiResponse:
    """Get detailed engagement metrics."""
    try:
        metrics = await blog_analytics_summary_service.get_engagement_metrics(
            db=db,
            user_id=current_user.id,
            days=days
        )
        return ApiResponse.success_response(data=metrics)
        
    except Exception as e:
        logger.error(f"Error getting engagement metrics for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get engagement metrics"
        )


@router.get("/admin/site-summary", response_model=ApiResponse)
async def get_site_analytics_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> ApiResponse:
    """Get site-wide analytics summary (admin only)."""
    try:
        if not current_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view site-wide analytics"
            )
        
        summary = await blog_analytics_summary_service.get_dashboard_summary(
            db=db,
            user_id=None,  # Site-wide
            days=days
        )
        return ApiResponse.success_response(data=summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting site analytics summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get site analytics summary"
        )
