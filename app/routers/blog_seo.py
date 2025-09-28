"""Blog SEO and social sharing API endpoints."""
import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.models.blog_post import BlogPost, BlogPostStatus

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/blog/seo", tags=["blog-seo"])


@router.get("/analyze/{post_id}")
async def analyze_seo(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Analyze SEO metrics for a blog post."""
    try:
        # Get post and verify ownership
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
                detail="Blog post not found or access denied"
            )
        
        # Analyze content
        content_analysis = analyze_content_seo(post)
        meta_analysis = analyze_meta_seo(post)
        technical_analysis = analyze_technical_seo(post)
        
        # Calculate overall score
        scores = [
            content_analysis["score"],
            meta_analysis["score"],
            technical_analysis["score"]
        ]
        overall_score = sum(scores) / len(scores)
        
        return {
            "post": {
                "id": post.id,
                "title": post.title,
                "status": post.status.value
            },
            "overall_score": round(overall_score, 1),
            "grade": get_seo_grade(overall_score),
            "analysis": {
                "content": content_analysis,
                "meta": meta_analysis,
                "technical": technical_analysis
            },
            "recommendations": generate_seo_recommendations(
                content_analysis, meta_analysis, technical_analysis
            )
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing SEO for post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze SEO"
        )


@router.post("/generate-meta/{post_id}")
async def generate_meta_tags(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Generate optimized meta tags for a blog post."""
    try:
        # Get post and verify ownership
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
                detail="Blog post not found or access denied"
            )
        
        # Generate meta suggestions
        meta_suggestions = {
            "title": generate_meta_title(post),
            "description": generate_meta_description(post),
            "keywords": generate_meta_keywords(post),
            "og_title": generate_og_title(post),
            "og_description": generate_og_description(post),
            "twitter_title": generate_twitter_title(post),
            "twitter_description": generate_twitter_description(post)
        }
        
        return {
            "post": {
                "id": post.id,
                "title": post.title
            },
            "current_meta": {
                "title": post.meta_title,
                "description": post.meta_description,
                "keywords": post.meta_keywords,
                "og_title": post.og_title,
                "og_description": post.og_description
            },
            "suggestions": meta_suggestions,
            "character_counts": {
                "title": len(meta_suggestions["title"]),
                "description": len(meta_suggestions["description"]),
                "og_title": len(meta_suggestions["og_title"]),
                "og_description": len(meta_suggestions["og_description"])
            },
            "optimal_lengths": {
                "title": "50-60 characters",
                "description": "150-160 characters",
                "og_title": "40-60 characters",
                "og_description": "150-200 characters"
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating meta tags for post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate meta tags"
        )


@router.get("/social-preview/{post_id}")
async def get_social_preview(
    post_id: int,
    platform: str = Query("facebook", regex="^(facebook|twitter|linkedin)$"),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get social media preview for a blog post."""
    try:
        # Get published post
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
        
        # Generate platform-specific preview
        if platform == "facebook":
            preview = {
                "title": post.og_title or post.meta_title or post.title,
                "description": post.og_description or post.excerpt or post.meta_description,
                "image": post.og_image_url or post.featured_image_url,
                "url": f"/blog/post/{post.slug}",
                "domain": "Your Blog",
                "constraints": {
                    "title_max": 60,
                    "description_max": 200
                }
            }
        elif platform == "twitter":
            preview = {
                "title": post.title,
                "description": post.excerpt or post.meta_description,
                "image": post.featured_image_url,
                "url": f"/blog/post/{post.slug}",
                "card_type": "summary_large_image",
                "constraints": {
                    "title_max": 70,
                    "description_max": 125
                }
            }
        elif platform == "linkedin":
            preview = {
                "title": post.og_title or post.title,
                "description": post.og_description or post.excerpt,
                "image": post.featured_image_url,
                "url": f"/blog/post/{post.slug}",
                "constraints": {
                    "title_max": 200,
                    "description_max": 300
                }
            }
        
        # Check if content fits constraints
        warnings = []
        if len(preview["title"]) > preview["constraints"]["title_max"]:
            warnings.append(f"Title too long for {platform} (max {preview['constraints']['title_max']} chars)")
        
        if preview["description"] and len(preview["description"]) > preview["constraints"]["description_max"]:
            warnings.append(f"Description too long for {platform} (max {preview['constraints']['description_max']} chars)")
        
        if not preview["image"]:
            warnings.append(f"No image set for {platform} preview")
        
        return {
            "platform": platform,
            "preview": preview,
            "warnings": warnings,
            "optimization_score": calculate_social_score(preview, platform)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting social preview for post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get social preview"
        )


@router.get("/sharing-stats/{post_id}")
async def get_sharing_stats(
    post_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
) -> Dict[str, Any]:
    """Get social sharing statistics for a blog post."""
    try:
        # Get post and verify ownership
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
                detail="Blog post not found or access denied"
            )
        
        # Generate sharing URLs
        post_url = f"/blog/post/{post.slug}"
        sharing_urls = {
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={post_url}",
            "twitter": f"https://twitter.com/intent/tweet?text={post.title}&url={post_url}",
            "linkedin": f"https://www.linkedin.com/sharing/share-offsite/?url={post_url}",
            "reddit": f"https://reddit.com/submit?url={post_url}&title={post.title}",
            "pinterest": f"https://pinterest.com/pin/create/button/?url={post_url}&description={post.title}",
            "whatsapp": f"https://wa.me/?text={post.title} {post_url}",
            "telegram": f"https://t.me/share/url?url={post_url}&text={post.title}",
            "email": f"mailto:?subject={post.title}&body=Check out this post: {post_url}"
        }
        
        # Mock sharing stats (in real implementation, you'd track actual shares)
        sharing_stats = {
            "facebook": {"shares": 0, "last_shared": None},
            "twitter": {"shares": 0, "last_shared": None},
            "linkedin": {"shares": 0, "last_shared": None},
            "reddit": {"shares": 0, "last_shared": None},
            "other": {"shares": 0, "last_shared": None}
        }
        
        total_shares = sum(stat["shares"] for stat in sharing_stats.values())
        
        return {
            "post": {
                "id": post.id,
                "title": post.title,
                "url": post_url
            },
            "sharing_urls": sharing_urls,
            "stats": sharing_stats,
            "total_shares": total_shares,
            "share_rate": round((total_shares / max(post.view_count, 1)) * 100, 2)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting sharing stats for post {post_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get sharing stats"
        )


# Helper functions for SEO analysis

def analyze_content_seo(post: BlogPost) -> Dict[str, Any]:
    """Analyze content-related SEO factors."""
    issues = []
    score = 100
    
    # Title analysis
    title_len = len(post.title)
    if title_len < 30:
        issues.append("Title is too short (aim for 30-60 characters)")
        score -= 15
    elif title_len > 60:
        issues.append("Title is too long (aim for 30-60 characters)")
        score -= 10
    
    # Content length analysis
    content_words = len(post.content.split()) if post.content else 0
    if content_words < 300:
        issues.append("Content is too short (aim for 300+ words)")
        score -= 20
    elif content_words < 500:
        issues.append("Consider adding more content (500+ words is better)")
        score -= 10
    
    # Excerpt analysis
    if not post.excerpt:
        issues.append("Missing excerpt")
        score -= 15
    elif len(post.excerpt) < 120:
        issues.append("Excerpt is too short (aim for 120-160 characters)")
        score -= 10
    
    return {
        "score": max(score, 0),
        "issues": issues,
        "metrics": {
            "title_length": title_len,
            "content_words": content_words,
            "excerpt_length": len(post.excerpt) if post.excerpt else 0
        }
    }


def analyze_meta_seo(post: BlogPost) -> Dict[str, Any]:
    """Analyze meta tag SEO factors."""
    issues = []
    score = 100
    
    # Meta title
    if not post.meta_title:
        issues.append("Missing meta title")
        score -= 25
    elif len(post.meta_title) > 60:
        issues.append("Meta title too long (max 60 characters)")
        score -= 10
    
    # Meta description
    if not post.meta_description:
        issues.append("Missing meta description")
        score -= 25
    elif len(post.meta_description) > 160:
        issues.append("Meta description too long (max 160 characters)")
        score -= 10
    elif len(post.meta_description) < 120:
        issues.append("Meta description too short (aim for 120-160 characters)")
        score -= 5
    
    # Open Graph tags
    if not post.og_title:
        issues.append("Missing Open Graph title")
        score -= 15
    
    if not post.og_description:
        issues.append("Missing Open Graph description")
        score -= 15
    
    return {
        "score": max(score, 0),
        "issues": issues,
        "metrics": {
            "meta_title_length": len(post.meta_title) if post.meta_title else 0,
            "meta_description_length": len(post.meta_description) if post.meta_description else 0,
            "has_og_tags": bool(post.og_title and post.og_description)
        }
    }


def analyze_technical_seo(post: BlogPost) -> Dict[str, Any]:
    """Analyze technical SEO factors."""
    issues = []
    score = 100
    
    # Slug analysis
    slug_len = len(post.slug)
    if slug_len > 60:
        issues.append("URL slug is too long")
        score -= 10
    
    if '-' not in post.slug and '_' not in post.slug:
        issues.append("URL slug should use hyphens for word separation")
        score -= 5
    
    # Featured image
    if not post.featured_image_url:
        issues.append("Missing featured image")
        score -= 15
    
    # Publication status
    if post.status != BlogPostStatus.PUBLISHED:
        issues.append("Post is not published")
        score -= 30
    
    return {
        "score": max(score, 0),
        "issues": issues,
        "metrics": {
            "slug_length": slug_len,
            "has_featured_image": bool(post.featured_image_url),
            "is_published": post.status == BlogPostStatus.PUBLISHED
        }
    }


def get_seo_grade(score: float) -> str:
    """Convert SEO score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def generate_seo_recommendations(content_analysis, meta_analysis, technical_analysis) -> List[str]:
    """Generate prioritized SEO recommendations."""
    recommendations = []
    
    # High priority issues
    if "Missing meta title" in meta_analysis["issues"]:
        recommendations.append("Add a meta title (highest priority)")
    if "Missing meta description" in meta_analysis["issues"]:
        recommendations.append("Add a meta description (highest priority)")
    
    # Medium priority issues
    if "Content is too short" in content_analysis["issues"]:
        recommendations.append("Expand your content to at least 300 words")
    if "Missing featured image" in technical_analysis["issues"]:
        recommendations.append("Add a featured image for better social sharing")
    
    # Low priority issues
    if "Missing excerpt" in content_analysis["issues"]:
        recommendations.append("Add an excerpt to improve search snippets")
    if "Missing Open Graph title" in meta_analysis["issues"]:
        recommendations.append("Add Open Graph tags for better social sharing")
    
    return recommendations[:5]  # Return top 5 recommendations


def generate_meta_title(post: BlogPost) -> str:
    """Generate an optimized meta title."""
    title = post.title
    if len(title) > 55:
        # Truncate and add ellipsis
        title = title[:52] + "..."
    return title


def generate_meta_description(post: BlogPost) -> str:
    """Generate an optimized meta description."""
    if post.excerpt and len(post.excerpt) <= 160:
        return post.excerpt
    
    # Generate from content
    if post.content:
        content_words = post.content.replace('\n', ' ').strip()
        if len(content_words) > 155:
            content_words = content_words[:152] + "..."
        return content_words
    
    return f"Read about {post.title} and discover insights about storytelling and creative writing."


def generate_meta_keywords(post: BlogPost) -> str:
    """Generate meta keywords from content."""
    keywords = ["storytelling", "writing", "creative writing"]
    
    if post.category:
        keywords.append(post.category.name.lower())
    
    if post.tags:
        keywords.extend([tag.name.lower() for tag in post.tags[:3]])
    
    return ", ".join(keywords[:10])


def generate_og_title(post: BlogPost) -> str:
    """Generate Open Graph title."""
    return post.title if len(post.title) <= 60 else post.title[:57] + "..."


def generate_og_description(post: BlogPost) -> str:
    """Generate Open Graph description."""
    if post.excerpt and len(post.excerpt) <= 200:
        return post.excerpt
    
    if post.content:
        content_words = post.content.replace('\n', ' ').strip()
        if len(content_words) > 195:
            content_words = content_words[:192] + "..."
        return content_words
    
    return f"Discover insights about {post.title} in this storytelling blog post."


def generate_twitter_title(post: BlogPost) -> str:
    """Generate Twitter-optimized title."""
    return post.title if len(post.title) <= 70 else post.title[:67] + "..."


def generate_twitter_description(post: BlogPost) -> str:
    """Generate Twitter-optimized description."""
    if post.excerpt and len(post.excerpt) <= 125:
        return post.excerpt
    
    if post.content:
        content_words = post.content.replace('\n', ' ').strip()
        if len(content_words) > 120:
            content_words = content_words[:117] + "..."
        return content_words
    
    return f"Read about {post.title}"


def calculate_social_score(preview: Dict[str, Any], platform: str) -> int:
    """Calculate social media optimization score."""
    score = 100
    
    if not preview["title"]:
        score -= 30
    elif len(preview["title"]) > preview["constraints"]["title_max"]:
        score -= 15
    
    if not preview["description"]:
        score -= 20
    elif len(preview["description"]) > preview["constraints"]["description_max"]:
        score -= 10
    
    if not preview["image"]:
        score -= 25
    
    return max(score, 0)