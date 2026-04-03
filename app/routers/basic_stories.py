"""API routes for basic stories."""

# /story_app/app/routers/basic_stories.py

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.core.deps import get_db_session, get_current_active_user, get_current_user
from app.models.user import User
from app.models.story import Story
from app.services.story_service import story_service, BasicStoryCreate
from app.services.basic_story_ai_service import basic_story_ai_service
from app.services.anonymous_user_service import anonymous_user_service
from app.schemas.story import StoryResponse, BasicStoryCreateResponse
from app.schemas.base import ApiResponse
from sqlalchemy import select

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stories/basic", tags=["basic-stories"])

# Anonymous user tracking
ANONYMOUS_SESSION_COOKIE = "anon_session"
ANONYMOUS_USER_COOKIE = "anon_user_id"

def generate_browser_fingerprint(request: Request) -> str:
    """Generate a simple browser fingerprint for additional tracking"""
    user_agent = request.headers.get("User-Agent", "")
    accept_language = request.headers.get("Accept-Language", "")
    accept_encoding = request.headers.get("Accept-Encoding", "")
    
    # Create a hash of browser characteristics
    import hashlib
    fingerprint_data = f"{user_agent}:{accept_language}:{accept_encoding}"
    return hashlib.md5(fingerprint_data.encode()).hexdigest()[:12]

async def get_or_create_anonymous_user(request: Request, response: Response, db: AsyncSession) -> User:
    """Get existing anonymous user or create a new one"""
    
    # Check for existing anonymous user in cookies
    anon_user_id = request.cookies.get(ANONYMOUS_USER_COOKIE)
    anon_session = request.cookies.get(ANONYMOUS_SESSION_COOKIE)
    
    if anon_user_id:
        try:
            # Try to get existing user
            existing_user = await db.execute(
                select(User).where(User.id == int(anon_user_id))
            )
            user = existing_user.scalar_one_or_none()
            
            if user and await anonymous_user_service.is_anonymous_user(user):
                logger.info(f"Found existing anonymous user: {user.username}")
                return user
        except (ValueError, Exception) as e:
            logger.warning(f"Invalid anonymous user cookie: {e}")
    
    # Create new anonymous user with IP address and browser fingerprint
    # Get client IP address
    client_ip = request.client.host
    if request.headers.get("X-Forwarded-For"):
        # If behind a proxy, get the real IP
        client_ip = request.headers.get("X-Forwarded-For").split(",")[0].strip()
    
    # Generate browser fingerprint for additional abuse detection
    browser_fingerprint = generate_browser_fingerprint(request)
    logger.info(f"Creating new anonymous user from IP: {client_ip}, fingerprint: {browser_fingerprint}")
    
    try:
        user_agent = request.headers.get("User-Agent", "")
        user, session_token = await anonymous_user_service.create_anonymous_user(
            db, client_ip, browser_fingerprint, user_agent
        )
        await db.commit()  # Ensure the user is committed to the database
        logger.info(f"Created anonymous user: {user.username} (ID: {user.id})")
    except ValueError as ve:
        # Handle abuse limit errors specifically
        logger.warning(f"Anonymous user creation blocked: {ve}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many anonymous users created from this location. Please try again later or register for unlimited access."
        )
    except Exception as e:
        logger.error(f"Failed to create anonymous user: {e}", exc_info=True)
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create anonymous user session"
        )
    
    # Set cookies for tracking (7 days instead of 30 - shorter to encourage registration)
    response.set_cookie(
        key=ANONYMOUS_USER_COOKIE,
        value=str(user.id),
        max_age=7 * 24 * 60 * 60,  # 7 days (reduced from 30)
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    response.set_cookie(
        key=ANONYMOUS_SESSION_COOKIE,
        value=session_token,
        max_age=7 * 24 * 60 * 60,  # 7 days (reduced from 30)
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    logger.info(f"Created new anonymous user: {user.username}")
    return user


class BasicStoryCreateRequest:
    """Request model for Basic Story creation"""
    def __init__(self, title: str, short_description: Optional[str] = None):
        self.title = title
        self.short_description = short_description


class StoryUpgradeRequest:
    """Request model for story upgrade"""
    def __init__(self, new_world_name: Optional[str] = None):
        self.new_world_name = new_world_name


@router.post("/create", response_model=ApiResponse)
async def create_basic_story(
    request_data: dict,  # Using dict for now, can create Pydantic model later
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Create a new Basic Story with shadow world and first act.
    
    Body:
    - title: Story title (required)
    - short_description: Optional description
    """
    try:
        # Handle anonymous users - create or get anonymous user if not authenticated
        if current_user is None:
            logger.info("Anonymous user creating basic story, creating anonymous account")
            current_user = await get_or_create_anonymous_user(request, response, db)
        
        # Validate required fields
        if 'title' not in request_data or not request_data['title'].strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Story title is required"
            )
        
        # Create Basic Story
        story_data = BasicStoryCreate(
            title=request_data['title'].strip(),
            short_description=request_data.get('short_description')
        )
        
        story, first_act = await story_service.create_basic_story(
            db=db,
            story_data=story_data,
            user=current_user
        )
        
        # Commit the transaction
        await db.commit()
        
        # Convert to response format
        response_data = BasicStoryCreateResponse(
            id=story.id,
            title=story.title,
            short_description=story.short_description,
            ai_summary=story.ai_summary,
            world_id=story.world_id,
            story_type=story.story_type,
            story_genre=story.story_genre,
            story_tone=story.story_tone,
            primary_conflict_type=story.primary_conflict_type,
            created_at=story.created_at,
            updated_at=story.updated_at,
            user_id=story.user_id,
            first_act_id=first_act.id
        )
        
        # Add editor_url for frontend redirect
        response_dict = response_data.model_dump()
        response_dict["editor_url"] = f"/ui/basic-story-editor?story_id={story.id}&act_id={first_act.id}"
        
        return ApiResponse.success_response(data=response_dict)
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create Basic Story: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create story: {str(e)}"
        )



@router.get("/{story_id:int}", response_model=ApiResponse)
async def get_basic_story(
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get a Basic Story by ID (with authorization check)"""
    try:
        from app.crud import story as story_crud
        
        story = await story_crud.get_story_for_user(db, story_id, current_user.id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        # Verify it's a Basic Story
        if story.story_type != 'basic':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Story is not a Basic Story"
            )
        
        return ApiResponse.success_response(data=StoryResponse(
            id=story.id,
            title=story.title,
            short_description=story.short_description,
            ai_summary=story.ai_summary,
            world_id=story.world_id,
            story_type=story.story_type,
            story_genre=story.story_genre,
            story_tone=story.story_tone,
            primary_conflict_type=story.primary_conflict_type,
            created_at=story.created_at,
            updated_at=story.updated_at,
            user_id=story.user_id
        ))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get Basic Story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch story"
        )


@router.put("/{story_id:int}", response_model=ApiResponse)
async def update_basic_story(
    story_id: int,
    request_data: dict,  # Using dict for now
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a Basic Story.
    
    Body:
    - title: Story title (optional)
    - short_description: Story description (optional)
    - content: Story content (optional)
    """
    try:
        from app.crud import story as story_crud
        from app.crud import act as act_crud
        from app.schemas.story import StoryUpdate
        from app.schemas.base import ApiResponse

        # Get and validate story
        story = await story_crud.get_story_for_user(db, story_id, current_user.id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        # Verify it's a Basic Story
        if story.story_type != 'basic':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Story is not a Basic Story"
            )
        
        # Update story fields if provided
        update_data = {}
        if 'title' in request_data and request_data['title'].strip():
            update_data['title'] = request_data['title'].strip()
        if 'short_description' in request_data:
            update_data['short_description'] = request_data.get('short_description')
        
        # Update story if there are changes
        if update_data:
            story_update = StoryUpdate(**update_data)
            story = await story_crud.update_story(
                db=db,
                story_id=story_id,
                story_update=story_update,
                user_id=current_user.id
            )
        
        # Update act content if provided
        if 'content' in request_data:
            # Get the first act for this basic story
            acts = await act_crud.get_acts_by_story(db, story_id, limit=1)
            if acts:
                first_act = acts[0]
                # Update the act's description with the content
                from app.schemas.act import ActUpdate
                act_update = ActUpdate(description=request_data['content'])
                await act_crud.update_act(
                    db=db,
                    db_act=first_act,
                    act_update=act_update,
                    updater_user_id=current_user.id
                )
        
        await db.commit()
        await db.refresh(story)
        
        return ApiResponse.success_response(data=StoryResponse(
            id=story.id,
            title=story.title,
            short_description=story.short_description,
            ai_summary=story.ai_summary,
            world_id=story.world_id,
            story_type=story.story_type,
            story_genre=story.story_genre,
            story_tone=story.story_tone,
            primary_conflict_type=story.primary_conflict_type,
            created_at=story.created_at,
            updated_at=story.updated_at,
            user_id=story.user_id
        ))
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update Basic Story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update story: {str(e)}"
        )


@router.post("/{story_id:int}/publish")
async def publish_basic_story(
    story_id: int,
    request_data: dict,  # Will contain title, description, content, visibility
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Publish a Basic Story.
    
    Body:
    - title: Published story title
    - description: Story description (optional)
    - content: Story content (HTML from editor)
    - visibility: 'public' or 'private'
    """
    try:
        from app.crud import story as story_crud
        from app.models.published_story import PublishedStory
        from app.schemas.published_story import PublishedStoryCreate
        import uuid
        import os
        import tempfile
        from app.core.config import settings
        
        # Get and validate story
        story = await story_crud.get_story_for_user(db, story_id, current_user.id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        # Verify it's a Basic Story
        if story.story_type != 'basic':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only Basic Stories can be published through this endpoint"
            )
        
        # Extract data from request
        title = request_data.get('title', story.title).strip()
        description = request_data.get('description', story.short_description)
        content = request_data.get('content', '')
        visibility = request_data.get('visibility', 'public')
        
        if not title:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title is required for publishing"
            )
        
        if not content or content.strip() == '' or content.strip() == '<p><br></p>':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content is required for publishing. Please add some content to your story."
            )
        
        # Calculate word count (strip HTML tags)
        import re
        word_count = len(re.sub(r'<[^>]*>', '', content).split())
        
        # Generate unique filename
        filename = f"story_{story_id}_{uuid.uuid4().hex[:8]}.html"
        
        # Get story image URL
        story_image_url = story.image_url if hasattr(story, 'image_url') and story.image_url else story.image_blob_path
        has_image = story_image_url and story_image_url.strip()
        
        # Calculate read time
        read_time = max(1, round(word_count / 200))
        
        # Create HTML content for the published story (matching preview structure)
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* Base Styles */
        body {{
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.6;
            max-width: 1000px;
            margin: 0 auto;
            padding: 2rem;
            color: #333;
            background-color: #fefefe;
        }}
        
        /* Story Header Styles (matching preview) */
        .story-header {{
            margin-bottom: 3rem;
        }}
        .story-header .row {{
            display: flex;
            align-items: center;
            gap: 2rem;
        }}
        .story-header .col-content {{
            flex: 2;
        }}
        .story-header .col-image {{
            flex: 1;
            text-align: center;
        }}
        .story-title-large {{
            font-size: 2.5rem;
            font-weight: 700;
            color: #2c3e50;
            line-height: 1.2;
            margin-bottom: 0.5rem;
        }}
        .story-meta {{
            font-size: 1rem;
            color: #7f8c8d;
            margin-bottom: 1rem;
        }}
        .story-image-preview img {{
            max-height: 200px;
            max-width: 100%;
            object-fit: cover;
            border-radius: 8px;
            border: 1px solid #dee2e6;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .story-header hr {{
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, #dee2e6, transparent);
            margin: 2rem 0;
        }}
        
        /* Story Content */
        .story-content {{
            font-size: 1.1rem;
            line-height: 1.8;
        }}
        .story-content p {{
            margin-bottom: 1.5rem;
        }}
        
        /* Image Size Classes */
        .img-blog-small {{
            width: 25% !important;
            height: auto !important;
        }}
        .img-blog-medium {{
            width: 50% !important;
            height: auto !important;
        }}
        .img-blog-large {{
            width: 75% !important;
            height: auto !important;
        }}
        .img-blog-full {{
            width: 100% !important;
            height: auto !important;
        }}
        
        /* Image Alignment Classes */
        .img-blog-left {{
            float: left;
            margin-right: 1.5rem;
            margin-bottom: 1rem;
        }}
        .img-blog-right {{
            float: right;
            margin-left: 1.5rem;
            margin-bottom: 1rem;
        }}
        .img-blog-center {{
            display: block;
            margin: 1.5rem auto;
        }}
        
        /* Image Effects */
        .img-blog-border {{
            border: 2px solid #dee2e6 !important;
        }}
        .img-blog-shadow {{
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        }}
        .img-blog-rounded {{
            border-radius: 8px !important;
        }}
        
        /* Image Caption */
        .img-blog-caption {{
            display: block;
            margin-top: 0.5rem;
            font-size: 0.875rem;
            color: #6c757d;
            font-style: italic;
            text-align: center;
        }}
        
        /* General Image Styles */
        .story-content img {{
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }}
        
        /* Footer Styles */
        .story-footer {{
            margin-top: 3rem;
            padding-top: 2rem;
            text-align: center;
            color: #6c757d;
            font-size: 0.9rem;
        }}
        .story-footer hr {{
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, #dee2e6, transparent);
            margin-bottom: 1.5rem;
        }}
        .story-footer a {{
            color: #007bff;
            text-decoration: none;
            font-weight: 500;
        }}
        .story-footer a:hover {{
            color: #0056b3;
            text-decoration: underline;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            h1 {{
                font-size: 2rem;
            }}
            .img-blog-small,
            .img-blog-medium,
            .img-blog-large {{
                width: 100% !important;
            }}
            .img-blog-left,
            .img-blog-right {{
                float: none;
                margin: 1.5rem auto;
                text-align: center;
                display: block;
            }}
        }}
        
        @media print {{
            body {{ 
                margin: 0; 
                padding: 15px; 
            }}
            .img-blog-left,
            .img-blog-right {{
                float: none;
                display: block;
                margin: 1rem auto;
            }}
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            body {{
                padding: 1rem;
            }}
            .story-title-large {{
                font-size: 2rem;
            }}
            .story-header .row {{
                flex-direction: column-reverse;
                gap: 1rem;
            }}
            .story-header .col-content,
            .story-header .col-image {{
                flex: none;
            }}
            .story-header .col-image {{
                margin-bottom: 1rem;
            }}
            .img-blog-small,
            .img-blog-medium,
            .img-blog-large {{
                width: 100% !important;
            }}
            .img-blog-left,
            .img-blog-right {{
                float: none;
                margin: 1.5rem auto;
                text-align: center;
                display: block;
            }}
        }}
        
        @media print {{
            body {{ 
                margin: 0; 
                padding: 15px; 
            }}
            .img-blog-left,
            .img-blog-right {{
                float: none;
                display: block;
                margin: 1rem auto;
            }}
        }}
    </style>
</head>
<body>
    <!-- Story Header with Image (matching preview structure) -->
    <div class="story-header">
        <div class="row">
            <div class="col-content">
                <h1 class="story-title-large">{title}</h1>
                <div class="story-meta">
                    {f'<p>{description}</p>' if description else ''}
                    <span>{word_count} words</span> • <span>{read_time} min read</span>
                </div>
            </div>
            {f'''<div class="col-image">
                <div class="story-image-preview">
                    <img src="{story_image_url}" alt="Story Cover Image">
                </div>
            </div>''' if has_image else ''}
        </div>
        <hr>
    </div>
    
    <!-- Story Content -->
    <div class="story-content">
        {content}
    </div>
    
    <footer class="story-footer">
        <hr>
        <p>This story was created using <a href="https://inkandquill.ai" target="_blank" rel="noopener">Ink And Quill</a> - AI-powered storytelling tools for writers.</p>
    </footer>
</body>
</html>"""
        
        # Check if story is already published
        existing_published = await db.execute(
            select(PublishedStory).where(PublishedStory.story_id == story_id)
        )
        existing_published = existing_published.scalars().first()
        
        if existing_published:
            # Update existing published story
            existing_published.title = title
            existing_published.description = description
            existing_published.word_count = word_count
            existing_published.is_public = (visibility == 'public')
            
            # Upload updated content to blob storage
            published_url = existing_published.published_url
            
            # TODO: Move published assets into managed storage if needed
            # For now, use a placeholder URL
            if not published_url:
                published_url = f"https://yourdomain.com/published/{filename}"
            
            await db.commit()
            published_story = existing_published
            
        else:
            # Create new published story
            published_url = f"https://yourdomain.com/published/{filename}"
            
            # TODO: Move published assets into managed storage if needed
            # For now, we'll create the database record
            
            published_story = PublishedStory(
                story_id=story_id,
                user_id=current_user.id,
                title=title,
                description=description,
                word_count=word_count,
                published_url=published_url,
                filename=filename,
                is_public=(visibility == 'public')
            )
            
            db.add(published_story)
            await db.commit()
            await db.refresh(published_story)
        
        logger.info(f"Successfully published basic story {story_id} as '{title}' by user {current_user.id}")
        
        return {
            "success": True,
            "message": "Story published successfully!",
            "published_story": {
                "id": published_story.id,
                "title": published_story.title,
                "description": published_story.description,
                "published_url": published_story.published_url,
                "word_count": published_story.word_count,
                "is_public": published_story.is_public,
                "published_at": published_story.published_at.isoformat()
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to publish Basic Story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish story: {str(e)}"
        )


@router.post("/{story_id:int}/upgrade", response_model=ApiResponse)
async def upgrade_story_to_advanced(
    story_id: int,
    request: dict,  # Using dict for now
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upgrade a Basic Story to Advanced Story.
    
    Body:
    - new_world_name: Optional new name for the revealed world
    """
    try:
        story = await story_service.upgrade_story_to_advanced(
            db=db,
            story_id=story_id,
            user_id=current_user.id,
            new_world_name=request.get('new_world_name')
        )
        
        await db.commit()
        
        return ApiResponse.success_response(data=StoryResponse(
            id=story.id,
            title=story.title,
            short_description=story.short_description,
            ai_summary=story.ai_summary,
            world_id=story.world_id,
            story_type=story.story_type,
            story_genre=story.story_genre,
            story_tone=story.story_tone,
            primary_conflict_type=story.primary_conflict_type,
            created_at=story.created_at,
            updated_at=story.updated_at,
            user_id=story.user_id
        ))
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to upgrade story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upgrade story: {str(e)}"
        )


@router.get("/list", response_model=ApiResponse)
async def list_basic_stories(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """List user's Basic Stories"""
    try:
        stories = await story_service.get_stories_by_type(
            db=db,
            user_id=current_user.id,
            story_type='basic',
            skip=skip,
            limit=limit
        )
        
        return ApiResponse.success_response(data=[
            StoryResponse(
                id=story.id,
                title=story.title,
                short_description=story.short_description,
                ai_summary=story.ai_summary,
                world_id=story.world_id,
                story_type=story.story_type,
                story_genre=story.story_genre,
                story_tone=story.story_tone,
                primary_conflict_type=story.primary_conflict_type,
                created_at=story.created_at,
                updated_at=story.updated_at,
                user_id=story.user_id
            )
            for story in stories
        ])
        
    except Exception as e:
        logger.error(f"Failed to list Basic Stories: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch stories"
        )


@router.get("/{story_id:int}/features")
async def get_story_features(
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get available features for a Basic Story"""
    try:
        from app.crud import story as story_crud
        
        story = await story_crud.get_story_for_user(db, story_id, current_user.id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        features = story_service.get_available_features(story)
        
        return ApiResponse.success_response(
            data={
                "story_id": story_id,
                "story_type": story.story_type,
                "features": features
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get features for story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch story features"
        )


@router.post("/{story_id:int}/ai-assist")
async def get_ai_assistance(
    story_id: int,
    request: dict,  # Using dict for now
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI writing assistance for a Basic Story with proper cost tracking.
    
    Body:
    - assistance_type: Type of assistance ("general", "continue", "what_happens_next", etc.)
    - story_content: Current story content
    - specific_request: Optional specific request
    """
    try:
        from app.crud import story as story_crud
        
        # Get and validate story
        story = await story_crud.get_story_for_user(db, story_id, current_user.id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        if story.story_type != 'basic':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="AI assistance endpoint is for Basic Stories only"
            )
        
        # Validate request
        assistance_type = request.get('assistance_type', 'general')
        story_content = request.get('story_content', '')
        specific_request = request.get('specific_request')
        model_id = request.get('model_id')  # Optional model ID from admin users
        
        # Stream AI response with logging
        async def stream_response():
            async for chunk in basic_story_ai_service.get_writing_assistance(
                db=db,
                story=story,
                user=current_user,
                story_content=story_content,
                assistance_type=assistance_type,
                specific_request=specific_request,
                model_id=model_id
            ):
                yield chunk
        
        from fastapi.responses import StreamingResponse
        return StreamingResponse(
            stream_response(),
            media_type="text/plain",
            headers={
                "X-Story-Type": "basic",
                "X-Assistance-Type": assistance_type,
                "X-Cost-Tracked": "true"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get AI assistance for story {story_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get AI assistance"
        )


@router.post("/{story_id:int}/export-pdf")
async def export_story_to_pdf(
    story_id: int,
    request_data: dict,  # Will contain title and content
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    Export a Basic Story to PDF with professional formatting.
    
    Body:
    - title: Story title (optional, uses story title if not provided)
    - content: Story content (HTML from editor)
    """
    try:
        from app.crud import story as story_crud
        from app.services.pdf_export_service import pdf_export_service
        from fastapi.responses import Response
        import re
        
        # Get and validate story
        story = await story_crud.get_story_for_user(db, story_id, current_user.id)
        if not story:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Story not found"
            )
        
        # Verify it's a Basic Story
        if story.story_type != 'basic':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only Basic Stories can be exported to PDF through this endpoint"
            )
        
        # Extract data from request
        title_override = request_data.get('title')
        content_override = request_data.get('content')
        
        # Validate content
        content = content_override or story.content
        if not content or content.strip() == '':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Story must have content to export to PDF"
            )
        
        logger.info(f"Exporting story {story_id} to PDF for user {current_user.id}")
        
        # Generate PDF
        pdf_bytes = await pdf_export_service.export_story_to_pdf(
            story=story,
            user=current_user,
            title=title_override,
            content=content
        )
        
        # Create filename
        title = title_override or story.title or "Untitled_Story"
        # Sanitize filename
        filename = re.sub(r'[^a-zA-Z0-9\s\-_]', '', title).replace(' ', '_')
        if len(filename) > 50:
            filename = filename[:50]
        filename = f"{filename}.pdf"
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\"",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to export story {story_id} to PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export PDF: {str(e)}"
        )

