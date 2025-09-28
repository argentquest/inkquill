from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from decimal import Decimal
from typing import Optional, List
from app.db.database import Base

class UserAccount(Base):
    __tablename__ = "user_accounts"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    current_balance: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False, default=Decimal('0.0000'))
    total_spent: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False, default=Decimal('0.0000'))
    total_credits_added: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False, default=Decimal('0.0000'))
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default='USD')
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="account")
    transactions: Mapped[List["UserTransaction"]] = relationship("UserTransaction", back_populates="user_account", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint('current_balance >= 0', name='check_positive_balance'),
    )