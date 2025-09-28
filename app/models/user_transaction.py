from sqlalchemy import Column, Integer, String, DECIMAL, Text, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from decimal import Decimal
from typing import Optional, Dict, Any
from enum import Enum
from app.db.database import Base

class TransactionType(str, Enum):
    CREDIT_ADD = "credit_add"
    AI_COST_DEDUCTION = "ai_cost_deduction"
    SERVICE_CHARGE = "service_charge"
    WELCOME_BONUS = "welcome_bonus"
    MONTHLY_BONUS = "monthly_bonus"
    STEP_BONUS = "step_bonus"
    REFERRAL_BONUS = "referral_bonus"
    ADMIN_ADJUSTMENT = "admin_adjustment"
    ADMIN_DEDUCTION = "admin_deduction"

class UserTransaction(Base):
    __tablename__ = "user_transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_account_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    ai_cost_log_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ai_call_logs.id", ondelete="SET NULL"))
    credit_package_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("credit_packages.id", ondelete="SET NULL"))
    payment_reference: Mapped[Optional[str]] = mapped_column(String(255))
    transaction_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_account: Mapped["UserAccount"] = relationship("UserAccount", back_populates="transactions")
    ai_cost_log: Mapped[Optional["AICallLog"]] = relationship("AICallLog")
    credit_package: Mapped[Optional["CreditPackage"]] = relationship("CreditPackage")
    
    __table_args__ = (
        CheckConstraint('amount != 0', name='check_non_zero_amount'),
    )