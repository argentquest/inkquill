"""SQLAlchemy model for standalone chatbot messages."""
from sqlalchemy import Integer, String, ForeignKey, DateTime, Text, Float
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING

from app.db.database import Base

if TYPE_CHECKING:
    from .chatbot_session import ChatbotSession


class ChatbotMessage(Base):
    """A single turn in a standalone chatbot session."""
    __tablename__ = "chatbot_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("chatbot_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # 'user' or 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session: Mapped["ChatbotSession"] = relationship("ChatbotSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<ChatbotMessage(id={self.id}, session_id={self.session_id}, role={self.role!r})>"
