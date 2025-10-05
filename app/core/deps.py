# /ai_rag_story_app/app/core/deps.py

from typing import Optional, AsyncGenerator, Dict, Any 
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import logging

# --- Core Application Imports ---
from app.db.database import async_session_local
from app.core import security
from app.models.user import User
from app.crud import user as crud_user
from app.core.config import settings

logger = logging.getLogger(__name__)

# OAuth2 scheme for Bearer token authentication (API access)
oauth2_bearer_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/token")

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_local() as session:
        logger.debug(f"Database session {id(session)} created for request.")
        try:
            yield session
        except Exception as e:
            if not isinstance(e, HTTPException):
                logger.error(f"Error in database session {id(session)} during request: {e}", exc_info=True)
            else:
                logger.info(f"Handled HTTPException during DB session {id(session)}: Status {e.status_code}, Detail: {e.detail}")
            
            await session.rollback() 
            raise
        finally:
            logger.debug(f"Database session {id(session)} closed after request.")
            await session.close()

async def get_current_user(
    request: Request, 
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    token = request.cookies.get("access_token")
    if not token:
        logger.debug("No access_token cookie found in request for get_current_user.")
        return None 

    try:
        payload: Optional[Dict[str, Any]] = await security.decode_access_token(token=token) 
        
        if payload is None: 
            logger.warning("Token decoding returned None (invalid, expired, or error during decoding).")
            return None 
        
        username_from_payload: Optional[str] = payload.get("sub") 
        if username_from_payload is None:
            logger.warning("Username (sub) not found in token payload.")
            return None
        
    except Exception as e_unhandled: 
        logger.error(f"Unexpected error processing token in get_current_user: {e_unhandled}", exc_info=True)
        return None
    
    user = await crud_user.get_user_by_username(db, username=username_from_payload)
    if user is None:
        logger.warning(f"User '{username_from_payload}' from token not found in database for get_current_user.")
        return None 
    
    return user

async def get_current_active_user(
    current_user_optional: Optional[User] = Depends(get_current_user) 
) -> User:
    if current_user_optional is None:
        logger.warning("Attempt to access protected route without authentication (get_current_user returned None).")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not current_user_optional.is_active:
        logger.warning(f"Attempt to access protected route by inactive user: {current_user_optional.username}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    
    logger.debug(f"Active user '{current_user_optional.username}' authenticated by get_current_active_user.")
    return current_user_optional

async def get_current_user_with_anonymous_support(
    request: Request, 
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """
    Get current user supporting both authenticated users and anonymous users.
    First tries JWT authentication, then falls back to anonymous user cookies.
    """
    # First try normal JWT authentication
    current_user = await get_current_user(request, db)
    if current_user:
        return current_user
    
    # Check for anonymous user cookies
    anon_user_id = request.cookies.get("anon_user_id")
    anon_session = request.cookies.get("anon_session")
    
    if anon_user_id:
        try:
            from sqlalchemy import select
            # Try to get existing anonymous user
            existing_user = await db.execute(
                select(User).where(User.id == int(anon_user_id))
            )
            user = existing_user.scalar_one_or_none()
            
            if user and user.username and user.username.startswith('anon_'):
                logger.info(f"Found anonymous user from cookies: {user.username}")
                return user
        except (ValueError, Exception) as e:
            logger.warning(f"Invalid anonymous user cookie: {e}")

    return None

# --- Bearer Token Authentication Functions ---
async def get_current_user_from_bearer_token(
    token: str = Depends(oauth2_bearer_scheme),
    db: AsyncSession = Depends(get_db_session)
) -> Optional[User]:
    """
    Get current user from Bearer token (for API authentication).
    Validates JWT access token and checks refresh token validity.
    """
    try:
        # Decode the access token
        payload: Optional[Dict[str, Any]] = await security.decode_access_token(token=token)

        if payload is None:
            logger.warning("Bearer token decoding returned None (invalid, expired, or error during decoding).")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired access token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract user info from token
        username_from_payload: Optional[str] = payload.get("sub")
        user_id_from_payload: Optional[int] = payload.get("user_id")

        if username_from_payload is None or user_id_from_payload is None:
            logger.warning("Username or user_id not found in Bearer token payload.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user from database
        user = await crud_user.get_user_by_username(db, username=username_from_payload)
        if user is None:
            logger.warning(f"User '{username_from_payload}' from Bearer token not found in database.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing Bearer token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user_from_bearer_token(
    current_user: User = Depends(get_current_user_from_bearer_token)
) -> User:
    """
    Get current active user from Bearer token, ensuring user is active.
    """
    if not current_user.is_active:
        logger.warning(f"Attempt to access protected route by inactive user: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    logger.debug(f"Active user '{current_user.username}' authenticated via Bearer token.")
    return current_user