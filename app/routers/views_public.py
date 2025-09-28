# /mnt/c/Code2025/rag/app/routers/views_public.py

from fastapi import APIRouter, Request, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import logging
from typing import Optional

from app.core.deps import get_db_session
from app.models.world import World

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/public",
    tags=["public-views"],
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/gallery", response_class=HTMLResponse, name="public_world_gallery")
async def public_world_gallery(
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Public world gallery page - no authentication required"""
    logger.info("Serving public world gallery page")
    
    try:
        # Fetch worlds that are available for public chat
        result = await db.execute(
            select(World)
            .options(selectinload(World.current_image))
            .where(World.is_free_chat_enabled == True)
            .order_by(World.created_at.desc())
        )
        worlds = result.scalars().all()
        
        logger.info(f"Found {len(worlds)} worlds available for public chat")
        
    except Exception as e:
        logger.error(f"Error fetching worlds for public gallery: {e}")
        worlds = []
    
    return templates.TemplateResponse(
        "pages/public_world_gallery.html",
        {
            "request": request,
            "current_user": None,  # No authentication required
            "worlds": worlds
        }
    )

@router.get("/chat/{world_id}", response_class=HTMLResponse, name="public_world_chat")
async def public_world_chat(
    world_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Public world chat page for a specific world"""
    try:
        # Verify world exists and is available for public chat
        result = await db.execute(
            select(World)
            .where(World.id == world_id)
            .where(World.is_free_chat_enabled == True)
        )
        world = result.scalar_one_or_none()
        
        if not world:
            logger.warning(f"World {world_id} not found or not available for public chat")
            return RedirectResponse(url="/public/gallery", status_code=status.HTTP_303_SEE_OTHER)
        
        logger.info(f"Serving public world chat page for world: {world.name} (ID: {world_id})")
        
        return templates.TemplateResponse(
            "pages/public_world_chat.html",
            {
                "request": request,
                "current_user": None,  # No authentication required
                "world_id": world_id,
                "world_name": world.name
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading public world chat page: {e}")
        return RedirectResponse(url="/public/gallery", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/image", response_class=HTMLResponse, name="public_image_preview")
async def public_image_preview(
    request: Request,
    url: str = Query(..., description="Image URL to preview"),
    title: Optional[str] = Query(None, description="Image title"),
    description: Optional[str] = Query(None, description="Image description"),
    context_url: Optional[str] = Query(None, description="URL to return to"),
    context_text: Optional[str] = Query(None, description="Text for return button"),
    db: AsyncSession = Depends(get_db_session)
):
    """Public image preview page for sharing AI-generated images"""
    try:
        logger.info(f"Serving public image preview for: {url}")
        
        # Validate that the URL appears to be an image (more flexible validation)
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        is_valid_image = (
            any(url.lower().endswith(ext) for ext in valid_extensions) or
            'blob' in url.lower() or
            '/image/' in url.lower() or  # Allow URLs like httpbin.org/image/jpeg
            'composite-image' in url.lower() or  # Allow our composite image URLs
            url.lower().endswith('.jpg') or url.lower().endswith('.jpeg') or url.lower().endswith('.png')
        )
        
        if not is_valid_image:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image URL"
            )
        
        # Extract image ID from URL if possible (for tracking)
        image_id = None
        if 'blob' in url:
            # Extract some identifier from blob URL for tracking
            import re
            match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', url)
            if match:
                image_id = match.group(1)
        
        # Prepare metadata
        image_meta = [
            {'icon': 'fas fa-robot', 'text': 'AI Generated'},
            {'icon': 'fas fa-eye', 'text': 'Public Preview'}
        ]
        
        if not title:
            title = "AI Generated Image"
        
        if not description:
            description = "Beautiful AI-generated artwork created with advanced AI models"
        
        return templates.TemplateResponse(
            "pages/image_preview.html",
            {
                "request": request,
                "current_user": None,  # No authentication required
                "image_url": url,
                "image_title": title,
                "image_description": description,
                "image_id": image_id,
                "image_meta": image_meta,
                "original_context_url": context_url,
                "original_context_text": context_text,
                "back_url": context_url,
                "back_text": context_text or "Back"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading public image preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error loading image preview"
        )

@router.get("/image-share", response_class=HTMLResponse, name="public_image_share")
async def public_image_share(
    request: Request,
    image_url: str = Query(..., description="Composite image URL"),
    title: str = Query("AI Generated Image", description="Image title"),
    description: str = Query("Beautiful AI-generated artwork", description="Image description"),
    type: str = Query("AI Art", description="Image type"),
    owner: str = Query("Creator", description="Image owner"),
    date: str = Query("Recently created", description="Creation date"),
    db: AsyncSession = Depends(get_db_session)
):
    """Shareable page for AI-generated images with Open Graph meta tags for social media"""
    try:
        logger.info(f"Serving image share page for: {title}")
        
        # Prepare enhanced metadata for the composite image
        image_meta = [
            {'icon': 'fas fa-tag', 'text': f'Type: {type}'},
            {'icon': 'fas fa-user', 'text': f'Created by: {owner}'},
            {'icon': 'fas fa-calendar', 'text': f'Date: {date}'},
            {'icon': 'fas fa-robot', 'text': 'AI Generated'}
        ]
        
        return templates.TemplateResponse(
            "pages/image_share.html",
            {
                "request": request,
                "current_user": None,  # No authentication required for sharing
                "image_url": image_url,
                "image_title": title,
                "image_description": description,
                "image_type": type,
                "image_owner": owner,
                "image_date": date,
                "image_meta": image_meta,
                "share_url": str(request.url),
                "share_title": title,
                "share_description": f"{description} - Created by {owner}"
            }
        )
        
    except Exception as e:
        logger.error(f"Error loading image share page: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error loading image share page"
        )