"""
Social Share tracking models for analytics and coin rewards.
"""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base


class SocialShare(Base):
    """Track social media shares for analytics and coin rewards."""
    
    __tablename__ = "social_shares"
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
    
    # Content information
    content_type: Mapped[str] = mapped_column(String(50), index=True)  # 'image_preview', 'published_story', 'ai_public_chat'
    content_id: Mapped[str] = mapped_column(String(255), index=True)  # ID of the shared content
    content_title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    content_url: Mapped[str] = mapped_column(Text)  # Full URL that was shared
    
    # Share details
    platform: Mapped[str] = mapped_column(String(50), index=True)  # 'facebook', 'twitter', 'linkedin', etc.
    shared_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # The text content that was shared
    shared_hashtags: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Hashtags used
    
    # Tracking information
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)  # For anonymous tracking
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    referrer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Coin reward tracking
    coin_awarded: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    coin_amount: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User", back_populates="social_shares")


class SocialShareDailySummary(Base):
    """Daily summary for tracking user coin limits and analytics."""
    
    __tablename__ = "social_share_daily_summaries"
    
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # Date tracking
    date: Mapped[datetime] = mapped_column(DateTime, index=True)  # Date (without time)
    
    # Daily counters
    total_shares: Mapped[int] = mapped_column(Integer, default=0)
    coins_earned: Mapped[int] = mapped_column(Integer, default=0)
    max_coins_reached: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Platform breakdown
    facebook_shares: Mapped[int] = mapped_column(Integer, default=0)
    twitter_shares: Mapped[int] = mapped_column(Integer, default=0)
    linkedin_shares: Mapped[int] = mapped_column(Integer, default=0)
    reddit_shares: Mapped[int] = mapped_column(Integer, default=0)
    whatsapp_shares: Mapped[int] = mapped_column(Integer, default=0)
    email_shares: Mapped[int] = mapped_column(Integer, default=0)
    copy_link_shares: Mapped[int] = mapped_column(Integer, default=0)
    pinterest_shares: Mapped[int] = mapped_column(Integer, default=0)
    telegram_shares: Mapped[int] = mapped_column(Integer, default=0)
    
    # Content type breakdown
    image_preview_shares: Mapped[int] = mapped_column(Integer, default=0)
    published_story_shares: Mapped[int] = mapped_column(Integer, default=0)
    ai_public_chat_shares: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="social_share_summaries")