# /ai_rag_story_app/app/routers/world_chat.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

# Core imports
from app.core.deps import get_current_active_user, get_db_session
from app.core.azure_deps import get_blob_service_client
from azure.storage.blob.aio import BlobServiceClient
from app.models.user import User
from app.services.world_chat_service import WorldChatService
from app.crud import chat_session as chat_session_crud
from app.crud import chat_message as chat_message_crud
from app.crud import world as world_crud
from app.crud import chat_sample as chat_sample_crud
from app.schemas.chat import (
    ChatSessionRead,
    ChatSessionListResponse,
    ChatSessionWithMessages,
    SendMessageRequest,
    SendMessageResponse,
    WorldContextData
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/world-chat",
    tags=["World Chat"]
)


@router.get("/chat/samples")
async def get_chat_samples(
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user)
):
    """Get all active chat samples for suggestions"""
    try:
        logger.info("Chat samples endpoint called for registered user")
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


@router.post("/sessions/{world_id}", response_model=ChatSessionRead)
async def create_chat_session(
    world_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    """Create a new chat session for a world"""
    try:
        # Verify user owns the world
        world = await world_crud.get_world_for_user(db, world_id, current_user.id)
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found"
            )
        
        # Create chat session
        chat_service = WorldChatService(db, blob_service_client)
        session_id = await chat_service.create_chat_session(world_id, current_user.id)
        
        # Return the created session
        session = await chat_session_crud.get_chat_session(db, session_id, current_user.id)
        return ChatSessionRead.model_validate(session)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chat session"
        )


@router.get("/sessions/{world_id}", response_model=ChatSessionListResponse)
async def list_chat_sessions(
    world_id: int,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """List all chat sessions for a world"""
    try:
        # Verify user owns the world
        world = await world_crud.get_world_for_user(db, world_id, current_user.id)
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found"
            )
        
        # Get sessions
        sessions = await chat_session_crud.get_chat_sessions_by_world(
            db, world_id, current_user.id, skip, limit
        )
        total = await chat_session_crud.get_chat_sessions_count_by_world(
            db, world_id, current_user.id
        )
        
        return ChatSessionListResponse(
            sessions=[ChatSessionRead.model_validate(session) for session in sessions],
            total=total
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing chat sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list chat sessions"
        )


@router.get("/sessions/{world_id}/{session_id}", response_model=ChatSessionWithMessages)
async def get_chat_session(
    world_id: int,
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get a specific chat session with its messages"""
    try:
        # Get session
        session = await chat_session_crud.get_chat_session(db, session_id, current_user.id)
        if not session or session.world_id != world_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Get messages
        messages = await chat_message_crud.get_chat_messages_by_session(db, session_id)
        
        # Build response
        session_data = ChatSessionRead.model_validate(session)
        return ChatSessionWithMessages(
            **session_data.model_dump(),
            messages=[message for message in messages]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get chat session"
        )


@router.post("/sessions/{world_id}/{session_id}/messages", response_model=SendMessageResponse)
async def send_message(
    world_id: int,
    session_id: int,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    """Send a message in a chat session"""
    try:
        # Verify session exists and belongs to user
        session = await chat_session_crud.get_chat_session(db, session_id, current_user.id)
        if not session or session.world_id != world_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Process message
        chat_service = WorldChatService(db, blob_service_client)
        response = await chat_service.send_message(session_id, current_user.id, request)
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending message: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send message"
        )


@router.delete("/sessions/{world_id}/{session_id}")
async def delete_chat_session(
    world_id: int,
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Delete a chat session"""
    try:
        # Verify session exists and belongs to user
        session = await chat_session_crud.get_chat_session(db, session_id, current_user.id)
        if not session or session.world_id != world_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        # Delete session
        deleted = await chat_session_crud.delete_chat_session(db, session_id, current_user.id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chat session not found"
            )
        
        return {"message": "Chat session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chat session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat session"
        )


@router.get("/world-context/{world_id}", response_model=WorldContextData)
async def get_world_context(
    world_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
    blob_service_client: BlobServiceClient = Depends(get_blob_service_client)
):
    """Get complete world context data (for debugging/testing)"""
    try:
        # Verify user owns the world
        world = await world_crud.get_world_for_user(db, world_id, current_user.id)
        if not world:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="World not found"
            )
        
        # Load world context
        from app.services.world_context_loader import WorldContextLoader
        context_loader = WorldContextLoader(db, blob_service_client)
        context = await context_loader.load_full_world_context(world_id, current_user.id)
        
        if not context:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to load world context"
            )
        
        return context
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting world context: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get world context: {str(e)}"
        )