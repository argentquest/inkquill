"""Blog subscription model for newsletter functionality."""
from datetime import datetime
from typing import TYPE_CHECKING, Optional
from enum import Enum

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Enum as SQLAlchemyEnum,
    ForeignKey, Index, Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class SubscriptionStatus(str, Enum):
    """Enum for subscription status."""
    ACTIVE = "active"
    PENDING = "pending"  # Email confirmation pending
    UNSUBSCRIBED = "unsubscribed"
    BOUNCED = "bounced"  # Email bounced
    COMPLAINED = "complained"  # Marked as spam


class SubscriptionFrequency(str, Enum):
    """Enum for subscription frequency."""
    IMMEDIATE = "immediate"  # Every new post
    DAILY = "daily"  # Daily digest
    WEEKLY = "weekly"  # Weekly digest
    MONTHLY = "monthly"  # Monthly digest


class BlogSubscription(Base):
    """Blog subscription model for newsletter functionality."""
    __tablename__ = "blog_subscriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Email (for non-registered users) or user reference
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=True, 
        index=True
    )
    
    # Subscription settings
    status: Mapped[SubscriptionStatus] = mapped_column(
        SQLAlchemyEnum(SubscriptionStatus), 
        nullable=False, 
        default=SubscriptionStatus.PENDING,
        index=True
    )
    frequency: Mapped[SubscriptionFrequency] = mapped_column(
        SQLAlchemyEnum(SubscriptionFrequency), 
        nullable=False, 
        default=SubscriptionFrequency.WEEKLY
    )
    
    # Subscription preferences
    include_categories: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list of category IDs
    include_tags: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list of tag IDs
    
    # Confirmation and unsubscribe tokens
    confirmation_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    unsubscribe_token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    # Email tracking
    last_sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    total_emails_sent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    open_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    click_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Bounces and complaints
    bounce_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    complaint_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    last_bounce_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_complaint_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # Where they subscribed from
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamps
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    unsubscribed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="blog_subscriptions")
    
    # Indexes
    __table_args__ = (
        Index('idx_blog_subscriptions_email_status', 'email', 'status'),
        Index('idx_blog_subscriptions_user_status', 'user_id', 'status'),
        Index('idx_blog_subscriptions_frequency_status', 'frequency', 'status'),
        Index('idx_blog_subscriptions_last_sent', 'last_sent_at'),
    )
    
    def __repr__(self):
        return f"<BlogSubscription(id={self.id}, email='{self.email}', status='{self.status}')>"
    
    @property
    def is_active(self) -> bool:
        """Check if subscription is active."""
        return self.status == SubscriptionStatus.ACTIVE
    
    @property
    def needs_confirmation(self) -> bool:
        """Check if subscription needs email confirmation."""
        return self.status == SubscriptionStatus.PENDING and self.confirmation_token is not None