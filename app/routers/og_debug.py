# /ai_rag_story_app/app/routers/og_debug.py

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db_session
from app.crud import story as crud_story
from app.crud import world as crud_world
from app.models.published_story import PublishedStory
from sqlalchemy import select
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug", tags=["Debug"])

@router.get("/og-tags/{content_type}/{content_id}", response_class=HTMLResponse)
async def debug_og_tags(
    content_type: str,
    content_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Debug endpoint to view Open Graph tags for content"""
    
    try:
        # Get content and generate meta tags
        meta_tags = []
        title = "Content Not Found"
        
        if content_type == "story":
            story = await crud_story.get_story(db, story_id=content_id)
            if story:
                title = story.title or "Untitled Story"
                description = story.summary or story.description or "An AI-generated story"
                image_url = story.image_url if hasattr(story, 'image_url') and story.image_url else str(request.url_for('generate_social_preview', content_type='story', content_id=story.id))
                
                meta_tags = [
                    f'<meta property="og:type" content="article" />',
                    f'<meta property="og:title" content="{title}" />',
                    f'<meta property="og:description" content="{description[:300]}" />',
                    f'<meta property="og:image" content="{image_url}" />',
                    f'<meta property="og:url" content="{request.url}" />',
                    f'<meta name="twitter:card" content="summary_large_image" />',
                    f'<meta name="twitter:title" content="{title}" />',
                    f'<meta name="twitter:description" content="{description[:200]}" />',
                    f'<meta name="twitter:image" content="{image_url}" />',
                ]
        
        elif content_type == "world":
            world = await crud_world.get_world(db, world_id=content_id)
            if world:
                title = world.name or "Untitled World"
                description = world.description or "An AI-created world"
                image_url = world.image_url if hasattr(world, 'image_url') and world.image_url else str(request.url_for('generate_social_preview', content_type='world', content_id=world.id))
                
                meta_tags = [
                    f'<meta property="og:type" content="article" />',
                    f'<meta property="og:title" content="{title}" />',
                    f'<meta property="og:description" content="{description[:300]}" />',
                    f'<meta property="og:image" content="{image_url}" />',
                    f'<meta property="og:url" content="{request.url}" />',
                    f'<meta name="twitter:card" content="summary_large_image" />',
                    f'<meta name="twitter:title" content="{title}" />',
                    f'<meta name="twitter:description" content="{description[:200]}" />',
                    f'<meta name="twitter:image" content="{image_url}" />',
                ]
        
        elif content_type == "published_story":
            result = await db.execute(
                select(PublishedStory).where(PublishedStory.id == content_id)
            )
            published_story = result.scalar_one_or_none()
            if published_story:
                title = published_story.title or "Published Story"
                description = published_story.description or "A published AI story"
                image_url = str(request.url_for('generate_social_preview', content_type='published_story', content_id=published_story.id))
                
                meta_tags = [
                    f'<meta property="og:type" content="article" />',
                    f'<meta property="og:title" content="{title}" />',
                    f'<meta property="og:description" content="{description[:300]}" />',
                    f'<meta property="og:image" content="{image_url}" />',
                    f'<meta property="og:url" content="{request.url}" />',
                    f'<meta name="twitter:card" content="summary_large_image" />',
                    f'<meta name="twitter:title" content="{title}" />',
                    f'<meta name="twitter:description" content="{description[:200]}" />',
                    f'<meta name="twitter:image" content="{image_url}" />',
                ]
        
        if not meta_tags:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Generate HTML preview
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Open Graph Debug - {title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                h1 {{ color: #333; border-bottom: 2px solid #007bff; padding-bottom: 10px; }}
                .meta-tag {{ background: #f8f9fa; padding: 10px; margin: 5px 0; border-left: 4px solid #007bff; font-family: monospace; word-break: break-all; }}
                .preview {{ margin-top: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background: #fafafa; }}
                .preview-image {{ max-width: 100%; height: auto; border-radius: 4px; }}
                .test-links {{ margin-top: 20px; }}
                .test-links a {{ display: inline-block; margin: 5px 10px 5px 0; padding: 8px 16px; background: #007bff; color: white; text-decoration: none; border-radius: 4px; }}
                .test-links a:hover {{ background: #0056b3; }}
            </style>
            {chr(10).join(meta_tags)}
        </head>
        <body>
            <div class="container">
                <h1>Open Graph Debug - {content_type.title()} #{content_id}</h1>
                
                <h2>Generated Meta Tags:</h2>
                {"".join(f'<div class="meta-tag">{tag}</div>' for tag in meta_tags)}
                
                <h2>Preview:</h2>
                <div class="preview">
                    <h3>{title}</h3>
                    <p>{description[:200] if 'description' in locals() else 'No description'}</p>
                    <img class="preview-image" src="{image_url if 'image_url' in locals() else ''}" alt="Preview Image" onerror="this.style.display='none'">
                </div>
                
                <div class="test-links">
                    <h3>Test Social Media Sharing:</h3>
                    <a href="https://developers.facebook.com/tools/debug/?q={request.url}" target="_blank">Facebook Debugger</a>
                    <a href="https://cards-dev.twitter.com/validator" target="_blank">Twitter Card Validator</a>
                    <a href="https://www.linkedin.com/post-inspector/" target="_blank">LinkedIn Post Inspector</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Error debugging OG tags: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/test-social-preview")
async def test_social_preview():
    """Test endpoint to verify social preview image generation works"""
    return {
        "message": "Social preview system operational",
        "endpoints": {
            "story_preview": "/api/v1/social/preview/story/{story_id}.jpg",
            "world_preview": "/api/v1/social/preview/world/{world_id}.jpg", 
            "published_story_preview": "/api/v1/social/preview/published_story/{published_story_id}.jpg"
        },
        "debug": {
            "og_tags": "/debug/og-tags/{content_type}/{content_id}"
        }
    }