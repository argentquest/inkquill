from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import logging

from app.core.deps import get_db_session, get_current_user
from app.core.azure_deps import get_blob_service_client
from azure.storage.blob.aio import BlobServiceClient
from app.models.world import World
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.schemas.world import WorldRead
from app.schemas.chat import ChatSessionCreate, ChatMessageCreate, ChatSessionRead, ChatMessageRead
from app.services.anonymous_user_service import anonymous_user_service
from app.services.billing_service import billing_service
from app.crud.user import get_user_by_username
from app.crud import chat_sample as chat_sample_crud
from decimal import Decimal

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/public", tags=["public-world-chat"])

# Anonymous user tracking
ANONYMOUS_SESSION_COOKIE = "anon_session"
ANONYMOUS_USER_COOKIE = "anon_user_id"

async def _check_and_get_image_url(blob_service_client: BlobServiceClient, blob_path: Optional[str]) -> Optional[str]:
    """Helper function to check if image blob exists and return URL"""
    from app.core.config import settings
    if not blob_path:
        return None
    try:
        container_name = settings.AZURE_STORAGE_CONTAINER_NAME_FOR_GENERATED_IMAGES
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
        if await blob_client.exists():
            return blob_client.url
    except Exception as e:
        logger.warning(f"Could not check for blob '{blob_path}' due to error: {e}")
    return None

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

@router.get("/chat/samples")
async def get_chat_samples(db: AsyncSession = Depends(get_db_session)):
    """Get all active chat samples for suggestions"""
    try:
        logger.info("Chat samples endpoint called")
        samples = await chat_sample_crud.get_active_chat_samples(db)
        logger.info(f"Retrieved {len(samples)} chat samples")
        return [
            {
                "id": sample.id,
                "title": sample.title,
                "prompt_text": sample.prompt_text,
                "category": sample.category,
                "sort_order": sample.sort_order
            }
            for sample in samples
        ]
    except Exception as e:
        logger.error(f"Error getting chat samples: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving chat samples"
        )

@router.get("/worlds", response_model=List[WorldRead])
async def get_public_worlds(
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    """Get all worlds available for public chat"""
    try:
        result = await db.execute(
            select(World)
            .where(World.is_free_chat_enabled == True)
            .order_by(World.name)
        )
        worlds = result.scalars().all()
        
        # Convert to response format with image URLs
        world_responses = []
        for world in worlds:
            # Get image URL if available
            image_url = await _check_and_get_image_url(blob_service_client, world.image_blob_path)
            
            world_dict = {
                "id": world.id,
                "name": world.name,
                "description": world.description,
                "user_id": world.user_id,
                "image_prompt_definition": world.image_prompt_definition,
                "is_free_chat_enabled": getattr(world, 'is_free_chat_enabled', False),  # Default to False if field doesn't exist
                "created_at": world.created_at,
                "updated_at": world.updated_at,
                "image_url": image_url
            }
            world_responses.append(WorldRead(**world_dict))
        
        return world_responses
        
    except Exception as e:
        logger.error(f"Error getting public worlds: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving public worlds"
        )

@router.get("/worlds/{world_id}")
async def get_public_world_details(
    world_id: int,
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    """Get detailed information about a public world including characters, locations, lore"""
    try:
        # Get world
        result = await db.execute(
            select(World)
            .where(World.id == world_id)
            .where(World.is_free_chat_enabled == True)
        )
        world = result.scalar_one_or_none()
        
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found or not available for public chat"
            )
        
        # Get world details (read-only)
        from app.crud.character import get_characters_by_world
        from app.crud.location import get_locations_by_world
        from app.crud.lore_item import get_lore_items_by_world
        
        characters = await get_characters_by_world(db, world_id)
        locations = await get_locations_by_world(db, world_id)
        lore_items = await get_lore_items_by_world(db, world_id)
        
        # Get image URL if available
        image_url = await _check_and_get_image_url(blob_service_client, world.image_blob_path)
        
        return {
            "world": {
                "id": world.id,
                "name": world.name,
                "description": world.description,
                "image_url": image_url
            },
            "characters": [
                {
                    "id": char.id,
                    "name": char.name,
                    "description": char.description
                } for char in characters
            ],
            "locations": [
                {
                    "id": loc.id,
                    "name": loc.name,
                    "description": loc.description
                } for loc in locations
            ],
            "lore_items": [
                {
                    "id": lore.id,
                    "title": lore.title,
                    "description": lore.description
                } for lore in lore_items
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting world details for world {world_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving world details: {str(e)}"
        )

@router.post("/worlds/{world_id}/chat")
async def start_chat_session(
    world_id: int,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Start a new chat session for a world (supports both authenticated and anonymous users)"""
    try:
        # Verify world is available for public chat
        result = await db.execute(
            select(World)
            .where(World.id == world_id)
            .where(World.is_free_chat_enabled == True)
        )
        world = result.scalar_one_or_none()
        
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found or not available for public chat"
            )
        
        # Determine user and balance requirements based on authentication status
        if current_user:
            # Authenticated user
            user = current_user
            required_balance = Decimal('1.00')  # Very low threshold for authenticated users
            logger.info(f"Authenticated user {user.username} starting chat in world {world_id}")
        else:
            # Anonymous user
            user = await get_or_create_anonymous_user(request, response, db)
            required_balance = Decimal('300.0000')  # Higher threshold for anonymous users
            logger.info(f"Anonymous user {user.username} starting chat in world {world_id}")
        
        # Check if user has sufficient balance
        account = await billing_service.get_user_balance(db, user.id)
        if account < required_balance:
            return JSONResponse(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                content={
                    "error": "insufficient_credits",
                    "message": "You have run out of free credits. Please register for unlimited access!" if not current_user else "Insufficient account balance.",
                    "remaining_balance": float(account),
                    "required_balance": float(required_balance)
                }
            )
        
        # Create chat session
        from app.crud.chat_session import chat_session_crud
        
        session_data = ChatSessionCreate(
            world_id=world_id,
            title=f"Public Chat - {world.name}"
        )
        
        chat_session = await chat_session_crud.create_chat_session(db, session_data, user.id)
        await db.commit()
        
        return {
            "session_id": chat_session.id,
            "world_name": world.name,
            "remaining_balance": float(account),
            "user_id": user.id,
            "username": user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting anonymous chat session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error starting chat session"
        )

@router.post("/chat/{session_id}/message")
async def send_chat_message(
    session_id: int,
    message_data: dict,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Send a message in a chat session (supports both authenticated and anonymous users)"""
    try:
        # Determine user based on authentication status
        if current_user:
            user = current_user
            required_balance = Decimal('1.00')
        else:
            user = await get_or_create_anonymous_user(request, response, db)
            required_balance = Decimal('300.0000')
        
        # Get chat session
        from app.crud.chat_session import chat_session_crud
        from app.crud.chat_message import chat_message_crud
        
        chat_session = await chat_session_crud.get_chat_session(db, session_id, user.id)
        if not chat_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Verify world is still available for public chat
        result = await db.execute(
            select(World)
            .where(World.id == chat_session.world_id)
            .where(World.is_free_chat_enabled == True)
        )
        world = result.scalar_one_or_none()
        
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World no longer available for public chat"
            )
        
        # Check balance before processing
        account_balance = await billing_service.get_user_balance(db, user.id)
        if account_balance < required_balance:
            return JSONResponse(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                content={
                    "error": "insufficient_credits",
                    "message": "You have run out of free credits. Please register for unlimited access!" if not current_user else "Insufficient account balance.",
                    "remaining_balance": float(account_balance),
                    "required_balance": float(required_balance)
                }
            )
        
        # Generate AI response using world chat service  
        # Create a simplified SendMessageRequest for anonymous users
        from app.schemas.chat import SendMessageRequest
        from app.services.world_chat_service import WorldChatService
        
        # Initialize world chat service
        chat_service = WorldChatService(db)
        
        # HARDCODED: Always use GPT-4.1 Mini (Next Generation) for public chat (model ID 9)
        hardcoded_model_id = 9  # GPT-4.1 Mini (Next Generation)
        logger.info(f"Public chat will use HARDCODED GPT-4.1 Mini (model ID {hardcoded_model_id})")
        
        # Create request with hardcoded model ID
        send_request = SendMessageRequest(
            message=message_data.get("content", ""),
            ai_model_config_id=hardcoded_model_id,
            element_type=None,
            element_id=None
        )
        
        # Send message and get response (this creates both user and AI messages)
        response = await chat_service.send_message(
            session_id=session_id,
            user_id=user.id,
            request=send_request,
            public_chat=True
        )
        await db.commit()
        
        # Get updated balance
        new_balance = await billing_service.get_user_balance(db, user.id)
        
        return {
            "user_message": {
                "id": response.user_message.id,
                "content": response.user_message.content,
                "sender": "user",
                "created_at": response.user_message.created_at
            },
            "ai_message": {
                "id": response.ai_response.id,
                "content": response.ai_response.content,
                "sender": "assistant",
                "created_at": response.ai_response.created_at,
                "sources": response.ai_response.sources if hasattr(response.ai_response, 'sources') else []
            },
            "remaining_balance": float(new_balance),
            "cost_deducted": float(account_balance - new_balance),
            "call_stats": {
                "input_tokens": response.call_stats.input_tokens,
                "output_tokens": response.call_stats.output_tokens,
                "total_tokens": response.call_stats.total_tokens,
                "cost": response.call_stats.cost,
                "model_name": response.call_stats.model_name,
                "duration_ms": response.call_stats.duration_ms
            } if response.call_stats else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending anonymous chat message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing chat message"
        )

@router.get("/chat/{session_id}/messages")
async def get_chat_messages(
    session_id: int,
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get messages from a chat session (supports both authenticated and anonymous users)"""
    try:
        # Determine user based on authentication status
        if current_user:
            user = current_user
        else:
            user = await get_or_create_anonymous_user(request, response, db)
        
        # Get chat session
        from app.crud.chat_session import chat_session_crud
        from app.crud.chat_message import chat_message_crud
        
        chat_session = await chat_session_crud.get_chat_session(db, session_id, user.id)
        if not chat_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Get messages
        messages = await chat_message_crud.get_messages_by_session(db, session_id)
        
        return {
            "session_id": session_id,
            "messages": [
                {
                    "id": msg.id,
                    "content": msg.content,
                    "sender": msg.role,  # Note: ChatMessage uses 'role' not 'sender'
                    "created_at": msg.created_at,
                    "full_context": msg.full_context  # Include full context with sources
                } for msg in messages
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving chat messages"
        )

@router.get("/user/balance")
async def get_anonymous_user_balance(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db_session)
):
    """Get current anonymous user's coin balance"""
    try:
        logger.info("Getting anonymous user balance...")
        user = await get_or_create_anonymous_user(request, response, db)
        
        if not user or not user.id:
            logger.error("Failed to get or create anonymous user - user or user.id is None")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create anonymous user session"
            )
        
        logger.info(f"Got user: {user.username} (ID: {user.id})")
        
        # Check if user is anonymous and use special balance function
        is_anon = await anonymous_user_service.is_anonymous_user(user)
        balance = await billing_service.get_or_create_anonymous_user_balance(db, user.id, is_anon)
        logger.info(f"User balance: {balance}")
        
        return {
            "balance": float(balance),
            "currency": "Coins",
            "username": user.username,
            "display_name": user.display_name,
            "weekly_limit": 5
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Error getting anonymous user balance: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving balance"
        )