"""SQLAlchemy models for refresh token."""

# /story_app/app/models/refresh_token.py

import sqlalchemy
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime, timedelta, timezone
from typing import Optional, TYPE_CHECKING
import uuid

# --- Core Application Imports ---
# Assumes User model is available via Type-Checking
from app.db.database import Base 

if TYPE_CHECKING:
    from .user import User

class RefreshToken(Base):
    """
    Database model to store and manage long-lived refresh tokens.
    Refresh tokens are revocable, single-use tokens used to issue new access tokens.
    """
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # The actual token value - UUID is good for preventing enumeration attacks
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Metadata for the token
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Optional fields for security/tracking
    revoked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True) # IPv4 or IPv6
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Relationship
    user: Mapped["User"] = relationship(
        "User",
        back_populates="refresh_tokens"
    )

    @property
    def is_expired(self) -> bool:
        """Check if the token has expired."""
        now = datetime.now(timezone.utc)
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return expires_at < now

    @property
    def is_revoked(self) -> bool:
        """Check if the token has been explicitly revoked."""
        return self.revoked_at is not None

    @property
    def is_valid(self) -> bool:
        """Check if the token is both not expired and not revoked."""
        return not self.is_expired and not self.is_revoked

    @property
    def is_active(self) -> bool:
        """Compatibility property for auth routes."""
        return self.is_valid

    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, expires_at='{self.expires_at}')>"

