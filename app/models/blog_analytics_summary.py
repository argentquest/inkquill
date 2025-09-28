"""Blog analytics summary model for aggregated metrics."""
from datetime import datetime, date
from typing import TYPE_CHECKING
from decimal import Decimal

from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date, DECIMAL, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.database import Base

if TYPE_CHECKING:
    from app.models.blog_post import BlogPost


class BlogAnalyticsSummary(Base):
    """Blog analytics summary model for daily aggregated metrics."""
    __tablename__ = "blog_analytics_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    # Post relationship
    post_id: Mapped[int] = mapped_column(
        Integer, 
        ForeignKey("blog_posts.id", ondelete="CASCADE"), 
        nullable=False, 
        index=True
    )
    
    # Date for the summary
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    # View metrics
    unique_views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Engagement metrics
    new_likes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    new_comments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Reading metrics
    avg_read_time: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # seconds
    bounce_rate: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), default=0.00, nullable=False)
    
    # Social metrics
    social_shares: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    post: Mapped["BlogPost"] = relationship("BlogPost", back_populates="analytics_summaries")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('post_id', 'date', name='unique_post_date'),
    )
    
    def __repr__(self):
        return f"<BlogAnalyticsSummary(id={self.id}, post_id={self.post_id}, date={self.date}, unique_views={self.unique_views})>"