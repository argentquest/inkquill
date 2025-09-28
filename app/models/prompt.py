# /ai_rag_story_app/app/models/prompt.py

from sqlalchemy import (
    Column, Integer, String, Text, Boolean, ForeignKey, DateTime,
    Enum as SQLAlchemyEnum
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, TYPE_CHECKING
import enum

from app.db.database import Base

if TYPE_CHECKING:
    from .user import User

class PromptTypeEnum(str, enum.Enum):
    GENERAL = "GENERAL"
    CHARACTER_DEVELOPMENT = "CHARACTER_DEVELOPMENT"
    PLOT_POINT = "PLOT_POINT"
    WORLD_BUILDING = "WORLD_BUILDING"
    DIALOGUE = "DIALOGUE"
    SCENE_GENERATION = "SCENE_GENERATION"
    SYSTEM = "SYSTEM"
    ACT = "ACT"
    STORY = "STORY"
    IMAGE_STYLE = "IMAGE_STYLE"
    CHARACTER_ROLE = "CHARACTER_ROLE"
    STORY_GENRE = "STORY_GENRE"
    STORY_TONE = "STORY_TONE"
    STORY_CONFLICT = "STORY_CONFLICT"
    QUICK_AI = "QUICK_AI"
    OTHER = "OTHER"

class AgeTargetEnum(str, enum.Enum):
    AGES_2_5 = "AGES_2_5"
    AGES_6_8 = "AGES_6_8"
    AGES_9_12 = "AGES_9_12"
    AGES_13_15 = "AGES_13_15"
    AGES_16_18 = "AGES_16_18"
    ALL_AGES = "ALL_AGES"

class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    prompt_content: Mapped[str] = mapped_column(Text, nullable=False)
    reason_to_use: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    prompt_type: Mapped[PromptTypeEnum] = mapped_column(
        SQLAlchemyEnum(PromptTypeEnum, name="prompt_type_enum", create_type=True),
        nullable=False,
        index=True
    )

    age_target: Mapped[AgeTargetEnum] = mapped_column(
        SQLAlchemyEnum(AgeTargetEnum, name="age_target_enum", create_type=True),
        nullable=False,
        index=True,
        default=AgeTargetEnum.ALL_AGES
    )
    
    user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    last_updated_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner: Mapped[Optional["User"]] = relationship("User", foreign_keys=[user_id], back_populates="prompts")
    last_updated_by: Mapped[Optional["User"]] = relationship("User", foreign_keys=[last_updated_by_user_id])

    def __repr__(self):
        prompt_type_value = self.prompt_type.value if self.prompt_type else "UNKNOWN_TYPE"
        return f"<Prompt(id={self.id}, title='{self.title}', type='{prompt_type_value}', owner_id={self.user_id})>"