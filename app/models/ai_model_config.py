"""SQLAlchemy models for ai model config."""

# /story_app/app/models/ai_model_config.py
import enum
from sqlalchemy import Column, Integer, String, Boolean, Float, Enum as SQLAlchemyEnum, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .ai_call_log import AICallLog

# --- FIX: The self-import was removed. These enums are defined right here. ---

class AIProviderEnum(str, enum.Enum):
    """SQLAlchemy model for a i provider enum."""
    OPENROUTER = "OPENROUTER"
    OPENAI = "OPENAI"
    RUNPOD = "RUNPOD"

class AIModelTypeEnum(str, enum.Enum):
    """SQLAlchemy model for a i model type enum."""
    GENERATION = "GENERATION"
    EMBEDDING = "EMBEDDING"

class AIModelConfiguration(Base):
    """SQLAlchemy model for a i model configuration."""
    __tablename__ = "ai_model_configurations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    
    display_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    
    provider: Mapped[AIProviderEnum] = mapped_column(SQLAlchemyEnum(AIProviderEnum, name="ai_provider_enum"), nullable=False)
    model_type: Mapped[AIModelTypeEnum] = mapped_column(SQLAlchemyEnum(AIModelTypeEnum, name="ai_model_type_enum"), nullable=False, index=True)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_public_chat_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True, index=True)
    
    max_tokens: Mapped[int] = mapped_column(Integer, default=2000)
    temperature: Mapped[float] = mapped_column(Float, default=0.7)
    top_p: Mapped[float] = mapped_column(Float, default=1.0)
    presence_penalty: Mapped[float] = mapped_column(Float, default=0.0)
    frequency_penalty: Mapped[float] = mapped_column(Float, default=0.0)
    is_json_mode: Mapped[bool] = mapped_column(Boolean, default=False)

    provider_cost_input_usd_pm: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    provider_cost_output_usd_pm: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    user_price_input_usd_pm: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    user_price_output_usd_pm: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    call_logs: Mapped[List["AICallLog"]] = relationship("AICallLog", back_populates="model_config")

    def __repr__(self):
        return f"<AIModelConfiguration(id={self.id}, name='{self.display_name}', model='{self.model_name}')>"

