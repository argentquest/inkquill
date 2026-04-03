"""SQLAlchemy models for credit package."""

from sqlalchemy import Column, Integer, String, DECIMAL, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from decimal import Decimal
from typing import Optional
from app.db.database import Base

class CreditPackage(Base):
    """SQLAlchemy model for credit package."""
    __tablename__ = "credit_packages"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    credit_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False)
    price_usd: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    bonus_percentage: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), default=Decimal('0.00'))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())