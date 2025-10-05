# /ai_rag_story_app/app/crud/refresh_token.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from typing import Optional
from datetime import datetime, timedelta

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.core.config import settings

# --- CRUD Functions for RefreshToken ---

async def create_refresh_token(
    db: AsyncSession, 
    user_id: int, 
    ip_address: Optional[str] = None, 
    user_agent: Optional[str] = None
) -> RefreshToken:
    """
    Creates a new, unique refresh token for the specified user.
    """
    
    expires_at = datetime.now(settings.TIMEZONE) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    db_token = RefreshToken(
        user_id=user_id,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(db_token)
    await db.commit()
    await db.refresh(db_token)
    return db_token


async def get_valid_token_by_value(db: AsyncSession, token_value: str) -> Optional[RefreshToken]:
    """
    Retrieves a refresh token by its value, checking if it is valid (not expired, not revoked).
    """

    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.token == token_value,
            RefreshToken.expires_at > func.now(),
            RefreshToken.revoked_at.is_(None)
        )
    )
    return result.scalars().first()


async def revoke_token(db: AsyncSession, db_token: RefreshToken) -> RefreshToken:
    """
    Marks a refresh token as revoked and sets the revocation time.
    """
    if db_token.revoked_at is None:
        db_token.revoked_at = datetime.now(settings.TIMEZONE)
        db.add(db_token)
        await db.commit()
        await db.refresh(db_token)
        
    return db_token

async def revoke_all_user_tokens(db: AsyncSession, user_id: int) -> int:
    """
    Revokes all active refresh tokens for a specific user.
    Returns the number of tokens revoked.
    """
    now = datetime.now(settings.TIMEZONE)
    
    # Select all active tokens for the user
    result = await db.execute(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None)
        )
    )
    tokens_to_revoke = result.scalars().all()
    
    # Revoke each token
    for token in tokens_to_revoke:
        token.revoked_at = now
        db.add(token)
        
    await db.commit()
    return len(tokens_to_revoke)

# --- CRUD Class for Consistency ---

class RefreshTokenCRUD:
    def __init__(self, settings):
        self.settings = settings
    
    async def create(
        self, 
        db: AsyncSession, 
        user_id: int, 
        ip_address: Optional[str] = None, 
        user_agent: Optional[str] = None
    ) -> RefreshToken:
        return await create_refresh_token(db, user_id, ip_address, user_agent)
    
    async def get_valid(self, db: AsyncSession, token_value: str) -> Optional[RefreshToken]:
        return await get_valid_token_by_value(db, token_value)
    
    async def revoke(self, db: AsyncSession, db_token: RefreshToken) -> RefreshToken:
        return await revoke_token(db, db_token)
    
    async def revoke_all(self, db: AsyncSession, user_id: int) -> int:
        return await revoke_all_user_tokens(db, user_id)

# Initialize CRUD object with settings from config
refresh_token_crud = RefreshTokenCRUD(settings)
