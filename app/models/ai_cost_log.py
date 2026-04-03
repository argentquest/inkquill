"""SQLAlchemy models for ai cost log."""

# /story_app/app/models/ai_cost_log.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING

from app.db.database import Base

if TYPE_CHECKING:
    from .user import User
    from .job_status import JobStatus
    from .ai_model_config import AIModelConfiguration

class AICallLog(Base):
    """
    SQLAlchemy ORM Model to log every call made to an AI service,
    tracking token usage, cost, and latency.
    """
    __tablename__ = "ai_call_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[Optional[str]] = mapped_column(String(255), ForeignKey("job_statuses.job_id"), index=True, nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    
    # --- FIX: Foreign key is now explicitly nullable ---
    model_config_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ai_model_configurations.id"), nullable=True, index=True)
    
    input_prompt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    call_type: Mapped[str] = mapped_column(String(50), index=True)
    
    # This field is redundant if joining on model_config, but useful for direct queries.
    model_name: Mapped[str] = mapped_column(String(255), index=True) 
    
    object_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    calculated_cost_usd: Mapped[float] = mapped_column(Numeric(10, 8), default=0.0)
    
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    owner: Mapped["User"] = relationship("User")
    job: Mapped[Optional["JobStatus"]] = relationship("JobStatus")
    model_config: Mapped[Optional["AIModelConfiguration"]] = relationship("AIModelConfiguration", back_populates="call_logs") # The ORM relationship can also be Optional

    def __repr__(self):
        return f"<AICallLog(id={self.id}, user_id={self.user_id}, config_id={self.model_config_id}, tokens={self.total_tokens})>"
