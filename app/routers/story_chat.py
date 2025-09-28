# /ai_rag_story_app/app/routers/story_chat.py

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.websockets import WebSocketState
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json
import logging
from typing import Dict, Any, Optional

from app.core.deps import get_db_session, get_current_user
from app.core.deps_ws import get_current_user_from_ws_ticket
from app.models.user import User
from app.models.story import Story
from app.services.story_chat_service import StoryChatService
from app.schemas.story_chat import (
    StoryChatSessionCreate, SendStoryChatMessageRequest,
    StoryChatSessionRead, StoryChatSessionWithMessages
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/story-chat",
    tags=["story-chat"]
)

class StoryChatConnectionManager:
    """WebSocket connection manager for story chat sessions"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, connection_id: str):
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        logger.info(f"Story Chat WS connected: {connection_id} (Total: {len(self.active_connections)})")
    
    def disconnect(self, connection_id: str):
        if connection_id in self.active_connections:
            self.active_connections.pop(connection_id)
            logger.info(f"Story Chat WS disconnected: {connection_id} (Total: {len(self.active_connections)})")
    
    async def send_json_message(self, data: Dict, connection_id: str):
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json(data)
            except Exception as e:
                logger.error(f"Error sending Story Chat WS JSON message to {connection_id}: {e}")
                self.disconnect(connection_id)
    
    async def send_text_chunk(self, text: str, connection_id: str):
        """Send a text chunk for streaming responses"""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_json({
                    "type": "text_chunk",
                    "content": text
                })
            except Exception as e:
                logger.error(f"Error sending Story Chat WS text chunk to {connection_id}: {e}")
                self.disconnect(connection_id)

story_chat_manager = StoryChatConnectionManager()

# --- REST API Endpoints ---

@router.post("/stories/{story_id}/sessions", response_model=StoryChatSessionRead)
async def create_chat_session(
    story_id: int,
    session_data: StoryChatSessionCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Create a new story chat session"""
    service = StoryChatService(db)
    return await service.create_session(story_id, current_user.id, session_data)

@router.get("/stories/{story_id}/sessions")
async def list_chat_sessions(
    story_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """List all chat sessions for a story"""
    service = StoryChatService(db)
    return await service.get_sessions(story_id, current_user.id)

@router.get("/stories/{story_id}/sessions/{session_id}", response_model=StoryChatSessionWithMessages)
async def get_chat_session(
    story_id: int,
    session_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Get a chat session with its messages"""
    service = StoryChatService(db)
    session = await service.get_session_with_messages(story_id, session_id, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/stories/{story_id}/sessions/{session_id}")
async def delete_chat_session(
    story_id: int,
    session_id: int,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    """Delete a chat session"""
    service = StoryChatService(db)
    success = await service.delete_session(story_id, session_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}

# --- WebSocket Endpoint ---

@router.websocket("/ws/stories/{story_id}/sessions/{session_id}/chat")
async def story_chat_websocket(
    websocket: WebSocket,
    story_id: int,
    session_id: int,
    ticket: str,
    db: AsyncSession = Depends(get_db_session)
):
    """
    WebSocket endpoint for real-time story chat conversations.
    
    Handles:
    - Real-time message exchange
    - Streaming AI responses
    - Story context integration
    - Cost tracking
    """
    
    # Authenticate user  
    try:
        from app.core import security
        from app.crud import user as crud_user
        
        if not ticket:
            await websocket.close(code=1008, reason="Authentication ticket required")
            return
            
        payload = await security.decode_access_token(token=ticket)
        if not payload or payload.get("type") != "ws-ticket":
            await websocket.close(code=1008, reason="Invalid authentication ticket")
            return
            
        username = payload.get("sub")
        if not username:
            await websocket.close(code=1008, reason="Invalid authentication ticket")
            return
            
        current_user = await crud_user.get_by_username(db, username=username)
        if not current_user:
            await websocket.close(code=1008, reason="User not found")
            return
            
    except Exception as e:
        logger.error(f"Story chat WS authentication failed: {e}")
        await websocket.close(code=1008, reason="Authentication failed")
        return
    
    # Create connection ID
    connection_id = f"story_chat_{story_id}_{session_id}_{current_user.username}"
    
    # Connect to WebSocket
    await story_chat_manager.connect(websocket, connection_id)
    
    try:
        # Initialize service
        service = StoryChatService(db)
        
        # Verify session access
        try:
            session = await service.get_session_with_messages(story_id, session_id, current_user.id)
            if not session:
                await story_chat_manager.send_json_message({
                    "type": "error",
                    "message": "Session not found or access denied"
                }, connection_id)
                return
        except Exception as e:
            await story_chat_manager.send_json_message({
                "type": "error", 
                "message": f"Failed to access session: {str(e)}"
            }, connection_id)
            return
        
        # Send session info
        await story_chat_manager.send_json_message({
            "type": "session_info",
            "session": {
                "id": session.id,
                "title": session.title,
                "focus_area": session.focus_area,
                "story_title": session.story.title if hasattr(session, 'story') else "Unknown"
            }
        }, connection_id)
        
        # Message handling loop
        while True:
            try:
                # Receive message from client
                message_data = await websocket.receive_json()
                message_type = message_data.get("type")
                
                if message_type == "send_message":
                    # Extract message content
                    content = message_data.get("content", "").strip()
                    target_element = message_data.get("target_element")
                    target_element_id = message_data.get("target_element_id")
                    
                    if not content:
                        await story_chat_manager.send_json_message({
                            "type": "error",
                            "message": "Message content cannot be empty"
                        }, connection_id)
                        continue
                    
                    # Create request object
                    request = SendStoryChatMessageRequest(
                        message=content,
                        target_element=target_element,
                        target_element_id=target_element_id,
                        streaming=True
                    )
                    
                    # Send start signal
                    await story_chat_manager.send_json_message({
                        "type": "response_start"
                    }, connection_id)
                    
                    # Stream AI response
                    try:
                        async for chunk in service.send_message(
                            story_id, session_id, current_user.id, request
                        ):
                            await story_chat_manager.send_text_chunk(chunk, connection_id)
                        
                        # Send completion signal
                        await story_chat_manager.send_json_message({
                            "type": "response_complete"
                        }, connection_id)
                        
                    except Exception as e:
                        logger.error(f"Error in story chat AI response: {e}")
                        await story_chat_manager.send_json_message({
                            "type": "error",
                            "message": f"AI response error: {str(e)}"
                        }, connection_id)
                
                elif message_type == "ping":
                    # Respond to ping
                    await story_chat_manager.send_json_message({
                        "type": "pong"
                    }, connection_id)
                    
                else:
                    logger.warning(f"Unknown story chat message type: {message_type}")
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"Error in story chat WebSocket loop: {e}")
                await story_chat_manager.send_json_message({
                    "type": "error",
                    "message": "Internal error occurred"
                }, connection_id)
                break
    
    finally:
        story_chat_manager.disconnect(connection_id)