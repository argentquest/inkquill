"""SQLAlchemy models for chat sample."""

# /mnt/c/Code2025/rag/app/models/chat_sample.py

from sqlalchemy import Column, Integer, String, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.database import Base


class ChatSample(Base):
    """SQLAlchemy model for chat sample."""
    __tablename__ = "chat_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=True)  # e.g., "characters", "locations", "lore"
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<ChatSample(id={self.id}, title='{self.title}', category='{self.category}')>"