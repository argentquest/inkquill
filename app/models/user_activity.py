"""SQLAlchemy models for user activity."""

# /story_app/app/models/user_activity.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, JSON, Uuid
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING, Dict, Any
import uuid

from app.db.database import Base

if TYPE_CHECKING:
    from .user import User

class UserActivity(Base):
    """
    SQLAlchemy ORM Model to log user activities and actions throughout the application.
    This provides audit trail and analytics capabilities.
    """
    __tablename__ = "user_activities"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    
    # Action tracking
    action_type: Mapped[str] = mapped_column(String(100), index=True)  # e.g., "api_call", "login", "create_story", "websocket_connect"
    action_category: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True)  # e.g., "auth", "story", "world", "ai"
    action_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Human-readable description
    
    # HTTP request details
    endpoint: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    method: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # GET, POST, PUT, DELETE, etc.
    status_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Performance metrics
    duration_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Request context
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(36), index=True, nullable=True)  # For correlating with logs
    
    # Optional data payloads (be careful with sensitive data)
    request_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    response_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    extra_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Additional context
    
    # Error tracking
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Timestamps
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, action={self.action_type}, endpoint={self.endpoint})>"
