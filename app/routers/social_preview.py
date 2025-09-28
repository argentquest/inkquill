# /ai_rag_story_app/app/routers/social_preview.py

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.deps import get_db_session
from app.crud import story as crud_story
from app.crud import world as crud_world
from app.models.published_story import PublishedStory
from sqlalchemy import select
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap
import logging
import httpx

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/social", tags=["Social Media"])

@router.get("/preview/{content_type}/{content_id}.jpg")
async def generate_social_preview(
    content_type: str,
    content_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    """Generate a dynamic social media preview image for stories, worlds, etc."""
    
    try:
        # Get content based on type
        content_data = None
        title = "AI Storytelling Assistant"
        description = "Create amazing stories with AI"
        
        if content_type == "story":
            story = await crud_story.get_story(db, story_id=content_id)
            if story:
                content_data = story
                title = story.title or "Untitled Story"
                description = story.summary or story.description or "An AI-generated story"
        
        elif content_type == "world":
            world = await crud_world.get_world(db, world_id=content_id)
            if world:
                content_data = world
                title = world.name or "Untitled World"
                description = world.description or "An AI-created world"
        
        elif content_type == "published_story":
            result = await db.execute(
                select(PublishedStory).where(PublishedStory.id == content_id)
            )
            published_story = result.scalar_one_or_none()
            if published_story:
                content_data = published_story
                title = published_story.title or "Published Story"
                description = published_story.description or "A published AI story"
        
        if not content_data:
            raise HTTPException(status_code=404, detail="Content not found")
        
        # Generate the image
        image_bytes = generate_preview_image(title, description, content_type)
        
        return Response(
            content=image_bytes,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "Content-Disposition": f"inline; filename={content_type}_{content_id}_preview.jpg"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating social preview: {e}")
        raise HTTPException(status_code=500, detail="Error generating preview image")

def generate_preview_image(title: str, description: str, content_type: str) -> bytes:
    """Generate a social media preview image with text overlay"""
    
    # Create image with standard social media dimensions (1200x630)
    width, height = 1200, 630
    
    # Create gradient background based on content type
    img = Image.new('RGB', (width, height), color='#1a1a1a')
    draw = ImageDraw.Draw(img)
    
    # Create gradient background
    if content_type == "story":
        # Blue to purple gradient for stories
        for y in range(height):
            r = int(32 + (135 - 32) * y / height)
            g = int(107 + (168 - 107) * y / height) 
            b = int(196 + (247 - 196) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    elif content_type == "world":
        # Green to blue gradient for worlds
        for y in range(height):
            r = int(34 + (32 - 34) * y / height)
            g = int(139 + (107 - 139) * y / height)
            b = int(34 + (196 - 34) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    else:
        # Default purple gradient
        for y in range(height):
            r = int(168 + (135 - 168) * y / height)
            g = int(85 + (107 - 85) * y / height)
            b = int(247 + (196 - 247) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    
    # Add overlay for better text readability
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 80))
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts, fall back to default if not available
    try:
        title_font = ImageFont.truetype("arial.ttf", 72)
        desc_font = ImageFont.truetype("arial.ttf", 36)
        brand_font = ImageFont.truetype("arial.ttf", 28)
    except:
        try:
            title_font = ImageFont.load_default()
            desc_font = ImageFont.load_default() 
            brand_font = ImageFont.load_default()
        except:
            # Fallback for minimal PIL installations
            title_font = None
            desc_font = None
            brand_font = None
    
    # Text positioning
    text_x = 60
    text_y_start = 120
    text_width = width - 120
    
    # Wrap title text
    if title_font:
        title_lines = textwrap.wrap(title, width=20)  # Adjust based on font size
    else:
        title_lines = [title[:30]]  # Simple truncation fallback
    
    # Draw title
    current_y = text_y_start
    for line in title_lines[:3]:  # Max 3 lines for title
        if title_font:
            draw.text((text_x, current_y), line, font=title_font, fill='white')
            current_y += 80
        else:
            draw.text((text_x, current_y), line, fill='white')
            current_y += 40
    
    # Draw description
    current_y += 40
    if desc_font:
        desc_lines = textwrap.wrap(description, width=50)
    else:
        desc_lines = [description[:50]]
    
    for line in desc_lines[:2]:  # Max 2 lines for description
        if desc_font:
            draw.text((text_x, current_y), line, font=desc_font, fill=(230, 230, 230))
            current_y += 50
        else:
            draw.text((text_x, current_y), line, fill='white')
            current_y += 30
    
    # Add branding
    brand_text = "AI Storytelling Assistant"
    brand_y = height - 80
    if brand_font:
        draw.text((text_x, brand_y), brand_text, font=brand_font, fill=(204, 204, 204))
    else:
        draw.text((text_x, brand_y), brand_text, fill='white')
    
    # Add content type badge
    badge_text = content_type.replace("_", " ").title()
    badge_x = width - 200
    badge_y = 60
    
    # Draw badge background
    badge_width = 150
    badge_height = 40
    draw.rounded_rectangle(
        [badge_x, badge_y, badge_x + badge_width, badge_y + badge_height],
        radius=20,
        fill=(51, 51, 51)
    )
    
    # Draw badge text
    badge_text_x = badge_x + 20
    badge_text_y = badge_y + 10
    if brand_font:
        draw.text((badge_text_x, badge_text_y), badge_text, font=brand_font, fill='white')
    else:
        draw.text((badge_text_x, badge_text_y), badge_text, fill='white')
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='JPEG', quality=85, optimize=True)
    img_buffer.seek(0)
    
    return img_buffer.getvalue()

@router.get("/composite-image/{image_id}.jpg")
async def generate_composite_image_preview(
    image_id: str,
    title: str = "",
    description: str = "",
    image_type: str = "",
    owner: str = "",
    date: str = "",
    original_url: str = "",
    request: Request = None
):
    """Generate a composite social media image that includes the original image plus metadata overlay"""
    
    try:
        from urllib.parse import unquote
        
        # Download the original image
        if not original_url:
            raise HTTPException(status_code=400, detail="Original image URL required")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(original_url, timeout=10)
                response.raise_for_status()
                original_image = Image.open(io.BytesIO(response.content))
        except Exception as e:
            logger.error(f"Error downloading original image: {e}")
            # Fallback to a placeholder if image download fails
            original_image = Image.new('RGB', (512, 512), color='#f0f0f0')
        
        # Generate composite image
        composite_bytes = generate_composite_image_with_metadata(
            original_image, title, description, image_type, owner, date
        )
        
        return Response(
            content=composite_bytes,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "public, max-age=3600",
                "Content-Disposition": f"inline; filename=composite_{image_id}_preview.jpg"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating composite image: {e}")
        raise HTTPException(status_code=500, detail="Error generating composite image")

def generate_composite_image_with_metadata(
    original_image: Image.Image, 
    title: str, 
    description: str, 
    image_type: str, 
    owner: str, 
    date: str
) -> bytes:
    """Generate a composite image with original image and metadata overlay for social sharing"""
    
    # Standard social media dimensions (1200x630)
    canvas_width, canvas_height = 1200, 630
    
    # Create main canvas
    canvas = Image.new('RGB', (canvas_width, canvas_height), color='#1a1a1a')
    
    # Create gradient background
    draw = ImageDraw.Draw(canvas)
    for y in range(canvas_height):
        r = int(32 + (64 - 32) * y / canvas_height)
        g = int(107 + (139 - 107) * y / canvas_height) 
        b = int(196 + (224 - 196) * y / canvas_height)
        draw.line([(0, y), (canvas_width, y)], fill=(r, g, b))
    
    # Add overlay for better contrast
    overlay = Image.new('RGBA', (canvas_width, canvas_height), (0, 0, 0, 60))
    canvas = Image.alpha_composite(canvas.convert('RGBA'), overlay).convert('RGB')
    draw = ImageDraw.Draw(canvas)
    
    # Resize and position the original image
    image_size = 400  # Square size for the original image
    image_x = 50  # Left margin
    image_y = (canvas_height - image_size) // 2  # Center vertically
    
    # Resize original image to fit
    original_image.thumbnail((image_size, image_size), Image.Resampling.LANCZOS)
    
    # Create a rounded rectangle for the image
    image_bg = Image.new('RGBA', (image_size, image_size), (255, 255, 255, 0))
    image_bg.paste(original_image, ((image_size - original_image.width) // 2, 
                                   (image_size - original_image.height) // 2))
    
    # Paste the image onto canvas
    canvas.paste(image_bg, (image_x, image_y), image_bg)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("arial.ttf", 48)
        desc_font = ImageFont.truetype("arial.ttf", 32)
        meta_font = ImageFont.truetype("arial.ttf", 24)
        brand_font = ImageFont.truetype("arial.ttf", 20)
    except:
        try:
            title_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
            meta_font = ImageFont.load_default()
            brand_font = ImageFont.load_default()
        except:
            title_font = desc_font = meta_font = brand_font = None
    
    # Text area positioning (to the right of the image)
    text_x = image_x + image_size + 40
    text_width = canvas_width - text_x - 40
    text_y_start = 80
    
    # Draw title
    current_y = text_y_start
    if title and title_font:
        title_lines = textwrap.wrap(title, width=25)
        for line in title_lines[:2]:  # Max 2 lines
            draw.text((text_x, current_y), line, font=title_font, fill='white')
            current_y += 55
    
    # Draw description
    current_y += 20
    if description and desc_font:
        desc_lines = textwrap.wrap(description, width=35)
        for line in desc_lines[:3]:  # Max 3 lines
            draw.text((text_x, current_y), line, font=desc_font, fill=(230, 230, 230))  # Light gray instead of rgba
            current_y += 40
    
    # Draw metadata
    current_y += 30
    metadata_items = []
    if image_type:
        metadata_items.append(f"{image_type}")
    if owner:
        metadata_items.append(f"{owner}")
    if date:
        metadata_items.append(f"{date}")
    
    for item in metadata_items:
        if meta_font:
            draw.text((text_x, current_y), item, font=meta_font, fill=(204, 204, 204))
            current_y += 35
    
    # Add branding
    brand_text = "Image generated by https://inkandquill.io - Your gateway to AI Assisted Story Telling"
    brand_y = canvas_height - 50
    if brand_font:
        draw.text((text_x, brand_y), brand_text, font=brand_font, fill=(179, 179, 179))
    
    # Add a subtle border around the image
    border_color = (255, 255, 255, 100)
    draw.rectangle([image_x-2, image_y-2, image_x+image_size+2, image_y+image_size+2], 
                  outline=border_color, width=2)
    
    # Convert to bytes
    img_buffer = io.BytesIO()
    canvas.save(img_buffer, format='JPEG', quality=90, optimize=True)
    img_buffer.seek(0)
    
    return img_buffer.getvalue()

@router.get("/test-composite")
async def test_composite_endpoint():
    """Test endpoint to verify composite image generation system"""
    return {
        "message": "Composite image generation system operational",
        "endpoints": {
            "composite_image": "/api/v1/social/composite-image/{image_id}.jpg?title=...&description=...&image_type=...&owner=...&date=...&original_url=...",
            "example": "/api/v1/social/composite-image/test123.jpg?title=Test%20Image&description=A%20beautiful%20AI%20generated%20image&image_type=Character&owner=John%20Doe&date=Jan%2015,%202025&original_url=https://example.com/image.jpg"
        },
        "features": [
            "Downloads original image and embeds it in composite",
            "Adds title, description, and metadata overlay",
            "Creates social media optimized 1200x630 image",
            "Includes branding and visual styling",
            "Fallback handling for image download failures"
        ]
    }

@router.get("/debug-facebook-share")
async def debug_facebook_share(
    request: Request,
    image_url: str = "https://httpbin.org/image/jpeg",
    title: str = "Test Image",
    description: str = "Test Description"
):
    """Debug endpoint to test Facebook sharing URLs and Open Graph tags"""
    
    # Generate composite image URL
    composite_url = f"/api/v1/social/composite-image/debug123.jpg?title={title}&description={description}&image_type=Debug&owner=Test&date=Today&original_url={image_url}"
    full_composite_url = str(request.url_for("generate_composite_image_preview", image_id="debug123.jpg")).replace("/debug123.jpg", "/debug123.jpg") + f"?title={title}&description={description}&image_type=Debug&owner=Test&date=Today&original_url={image_url}"
    
    # Generate share page URL
    from urllib.parse import quote_plus
    share_page_url = f"/public/image?url={quote_plus(full_composite_url)}&title={quote_plus(title)}&description={quote_plus(description)}"
    full_share_page_url = str(request.base_url) + share_page_url.lstrip('/')
    
    # Generate Facebook share URL
    facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={quote_plus(full_share_page_url)}&quote={quote_plus(title)}"
    
    return {
        "debug_info": {
            "original_image": image_url,
            "composite_image_url": full_composite_url,
            "share_page_url": full_share_page_url,
            "facebook_share_url": facebook_url
        },
        "test_links": {
            "view_composite": full_composite_url,
            "view_share_page": full_share_page_url,
            "facebook_debugger": f"https://developers.facebook.com/tools/debug/?q={quote_plus(full_share_page_url)}"
        },
        "instructions": [
            "1. Test the composite image URL to verify it generates correctly",
            "2. Test the share page URL to verify Open Graph tags are present",
            "3. Use Facebook's Debug Tool to see what Facebook sees when crawling the page",
            "4. Check browser console for any JavaScript errors during sharing"
        ]
    }