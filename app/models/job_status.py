"""SQLAlchemy models for job status."""

# /story_app/app/models/job_status.py

import enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLAlchemyEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING

from app.db.database import Base

if TYPE_CHECKING:
    from .user import User
    from .world import World

class JobTypeEnum(str, enum.Enum):
    """SQLAlchemy model for job type enum."""
    WORLD_EXTRACTION_FROM_DOC = "WORLD_EXTRACTION_FROM_DOC"
    DOCUMENT_CONTEXT_PROCESSING = "DOCUMENT_CONTEXT_PROCESSING"
    WORLD_IMPORT_FROM_TITLE = "WORLD_IMPORT_FROM_TITLE"
    IMAGE_GENERATION = "IMAGE_GENERATION"

class JobStateEnum(str, enum.Enum):
    """SQLAlchemy model for job state enum."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class JobStatus(Base):
    """
    SQLAlchemy ORM Model to track the status of long-running background jobs.
    """
    __tablename__ = "job_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    job_type: Mapped[JobTypeEnum] = mapped_column(SQLAlchemyEnum(JobTypeEnum, name="job_type_enum", create_type=True), nullable=False)
    
    state: Mapped[JobStateEnum] = mapped_column(SQLAlchemyEnum(JobStateEnum, name="job_state_enum", create_type=True), nullable=False, default=JobStateEnum.PENDING)
    
    status_message: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    result_message: Mapped[Optional[Text]] = mapped_column(Text, nullable=True)
    
    # Foreign key to the User who initiated the job
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Optional foreign key to the world created by or associated with this job
    world_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("worlds.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner: Mapped["User"] = relationship("User")
    world: Mapped[Optional["World"]] = relationship("World")

    def __repr__(self):
        return f"<JobStatus(id={self.id}, job_id='{self.job_id}', type='{self.job_type.value}', state='{self.state.value}')>"

