"""Service helpers for oauth service."""

# /story_app/app/services/oauth_service.py

import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
import re
from passlib.context import CryptContext

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

async def generate_unique_username(db: AsyncSession, base_username: str) -> str:
    """Generate a unique username based on email or provider info"""
    # Extract username part from email
    if "@" in base_username:
        base_username = base_username.split("@")[0]
    
    # Clean username (alphanumeric and underscores only)
    base_username = re.sub(r'[^a-zA-Z0-9_]', '_', base_username)
    base_username = base_username[:50]  # Limit length
    
    # Check if username exists
    username = base_username
    counter = 1
    
    while True:
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        if not result.scalar_one_or_none():
            return username
        
        # Username exists, try with counter
        username = f"{base_username}_{counter}"
        counter += 1

async def get_or_create_oauth_user(
    db: AsyncSession,
    provider: str,
    user_info: Dict[str, Any]
) -> User:
    """Get existing OAuth user or create a new one"""
    provider_id = str(user_info.get("sub") or user_info.get("id"))
    email = user_info.get("email")
    
    # First, try to find user by provider_id
    stmt = select(User).where(
        User.auth_provider == provider,
        User.provider_id == provider_id
    )
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        logger.info(f"Found existing OAuth user: {existing_user.username}")
        return existing_user
    
    # Check if email already exists (different account)
    if email:
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        email_user = result.scalar_one_or_none()
        
        if email_user:
            # Email exists with different provider - create with modified email
            logger.info(f"Email {email} already exists, creating separate OAuth account")
            email = f"{provider}.{email}"
    
    # Create new user
    username = await generate_unique_username(db, email or f"{provider}_user")
    
    new_user = User(
        username=username,
        email=email,
        auth_provider=provider,
        provider_id=provider_id,
        provider_data=user_info,
        display_name=user_info.get("name") or user_info.get("given_name") or username,
        profile_picture_url=user_info.get("picture"),
        is_active=True,  # OAuth users are pre-verified
        hashed_password=None  # No password for OAuth users initially
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"Created new OAuth user: {new_user.username}")
    return new_user

async def create_password_for_oauth_user(
    db: AsyncSession,
    user: User,
    password: str
) -> bool:
    """Allow OAuth user to set a password for email/password login"""
    if user.hashed_password:
        logger.warning(f"User {user.username} already has a password")
        return False
    
    user.hashed_password = pwd_context.hash(password)
    await db.commit()
    
    logger.info(f"Password set for OAuth user: {user.username}")
    return True
