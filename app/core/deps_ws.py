# /ai_rag_story_app/app/core/deps_ws.py

from fastapi import WebSocket, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any 
import logging
import sys 
from datetime import datetime, timezone

from app.core import security 
from app.models.user import User
from app.crud import user as crud_user
from app.core.deps import get_db_session 
from app.core.config import settings 

logger = logging.getLogger("app.core.deps_ws")
logger.setLevel(logging.DEBUG) 
logger.propagate = True

class WebSocketException(HTTPException): 
    def __init__(self, code: int, reason: Optional[str] = None):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=reason) 
        self.code = code 
        self.reason = reason

async def get_current_user_from_ws_ticket(
    websocket: WebSocket, 
    ticket: Optional[str] = Query(None, description="WebSocket authentication ticket"),
    db: AsyncSession = Depends(get_db_session) 
) -> User:
    
    logger.info(f"Attempting WebSocket authentication for path: {websocket.url.path}")

    if not ticket:
        logger.warning("WS Ticket Auth: No ticket provided in query.")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Authentication ticket required.")

    payload: Optional[Dict[str, Any]] = None
    try:
        payload = await security.decode_access_token(token=ticket) 

        if payload is None:
            logger.warning("WS Ticket Auth: Invalid ticket - payload is None after decoding (token might be malformed, expired, or signature invalid).")
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication ticket (decode failed).")
        
        exp_time_unix = payload.get("exp")
        exp_datetime_str = datetime.fromtimestamp(exp_time_unix, timezone.utc).isoformat() if exp_time_unix and isinstance(exp_time_unix, (int, float)) else "N/A (exp not found or invalid)"
        sub_user = payload.get("sub")
        token_type_from_payload = payload.get("type")
        logger.debug(f"WS Ticket Auth: Decoded payload: sub='{sub_user}', type='{token_type_from_payload}', exp_unix='{exp_time_unix}'")

        if token_type_from_payload != "ws-ticket":
            logger.warning(f"WS Ticket Auth: Invalid ticket type. Expected 'ws-ticket', got '{token_type_from_payload}'.")
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid ticket type.")
        
        username: Optional[str] = payload.get("sub")
        if username is None:
            logger.warning("WS Ticket Auth: Username (sub) not found in ticket payload.")
            raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid authentication ticket (no subject).")
        logger.debug(f"WS Ticket Auth: Username from ticket: {username}")

    except security.JWTError as e: 
        logger.warning(f"WS Ticket Auth: JWTError during ticket decoding: {str(e)} (Type: {type(e).__name__})")
        if "expired" in str(e).lower():
             logger.warning("WS Ticket Auth: The ticket has likely EXPIRED.")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason=f"Invalid authentication ticket: {str(e)}")
    except WebSocketException as wse:
        logger.debug(f"WS Ticket Auth: Re-raising WebSocketException from ticket validation: {wse.detail}")
        raise
    except Exception as e_decode: 
        logger.error(f"WS Ticket Auth: Unexpected error during ticket decoding: {e_decode}", exc_info=True)
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Ticket processing error.")
    
    user_crud_instance = crud_user 
    user = await user_crud_instance.get_user_by_username(db, username=username)
    if user is None:
        logger.warning(f"WS Ticket Auth: User '{username}' from ticket not found in DB.")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="User from ticket not found.")
    logger.debug(f"WS Ticket Auth: User '{username}' (ID: {user.id}) found in DB. Active: {user.is_active}")
    
    if not user.is_active:
        logger.warning(f"WS Ticket Auth: User '{username}' from ticket is inactive.")
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason="Inactive user account.")
        
    logger.info(f"WS Ticket Auth: WebSocket authenticated successfully for user: {user.username} (ID: {user.id}) for path: {websocket.url.path}")
    return user