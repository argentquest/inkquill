"""SQLAlchemy model for standalone chatbot sessions."""
from sqlalchemy import Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING, List

from app.db.database import Base

if TYPE_CHECKING:
    from .user import User
    from .chatbot_message import ChatbotMessage


class ChatbotSession(Base):
    """Standalone chat session not tied to any world or story."""
    __tablename__ = "chatbot_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship("User", back_populates="chatbot_sessions")
    messages: Mapped[List["ChatbotMessage"]] = relationship(
        "ChatbotMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatbotMessage.created_at"
    )

    def __repr__(self) -> str:
        return f"<ChatbotSession(id={self.id}, user_id={self.user_id}, title={self.title!r})>"
