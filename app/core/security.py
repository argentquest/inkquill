# /ai_rag_story_app/app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional, Dict # Added Dict for type hint
from jose import jwt, JWTError as JoseJWTError 
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError 
import logging

# --- Core Application Imports ---
from app.core.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

ALGORITHM = settings.AUTH_ALGORITHM
SECRET_KEY = settings.AUTH_SECRET_KEY 

class JWTError(Exception):
    """Custom exception for JWT related errors."""
    pass

class TokenPayload(BaseModel):
    sub: Optional[str] = None 
    type: Optional[str] = None 
    exp: Optional[datetime] = None 

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its hashed version."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}", exc_info=True)
        return False

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except JoseJWTError as e:
        logger.error(f"Error encoding JWT: {e}", exc_info=True)
        raise JWTError(f"Could not create access token: {str(e)}") from e


async def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decodes a JWT access token and validates its claims.
    Args:
        token: The encoded JWT string.
    Returns:
        The decoded payload dictionary if the token is valid and not expired.
        Returns None if the token is invalid, expired, or decoding fails.
    """
    if not token:
        logger.debug("decode_access_token received an empty token string.")
        return None
    try:
        # Decode the JWT. `jwt.decode` will raise `ExpiredSignatureError` or `JWTError` on failure.
        payload_dict: Dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # The `jwt.decode` function from `python-jose` already checks for 'exp' claim
        # and raises ExpiredSignatureError if it's expired.
        
        logger.debug(f"Token decoded successfully. Payload subject: {payload_dict.get('sub')}")
        return payload_dict
    
    except JoseJWTError as e: # Catch specific errors from python-jose (e.g., ExpiredSignatureError, InvalidTokenError)
        logger.warning(f"Invalid token during decoding: {str(e)} (Type: {type(e).__name__})")
        return None # Return None for any JWT decoding issue
    except Exception as e_unhandled: # Catch any other unexpected errors during decoding
        logger.error(f"Unexpected error decoding token: {e_unhandled}", exc_info=True)
        return None