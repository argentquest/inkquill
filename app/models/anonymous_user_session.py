"""SQLAlchemy models for anonymous user session."""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import TYPE_CHECKING
from datetime import datetime

from app.db.database import Base

if TYPE_CHECKING:
    from .user import User

class AnonymousUserSession(Base):
    """SQLAlchemy model for anonymous user session."""
    __tablename__ = "anonymous_user_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    ip_address: Mapped[str] = mapped_column(String(45), nullable=True, index=True)  # IPv6 support
    browser_fingerprint: Mapped[str] = mapped_column(String(32), nullable=True, index=True)
    user_agent: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="anonymous_sessions")

    def __repr__(self):
        return f"<AnonymousUserSession(id={self.id}, user_id={self.user_id}, ip={self.ip_address})>"