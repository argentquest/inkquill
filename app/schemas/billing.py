"""Pydantic schemas for billing."""

from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models.user_transaction import TransactionType

# User schema for nested responses
class UserBillingInfo(BaseModel):
    """Pydantic schema for user billing info."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None

# User account schema for nested responses in transactions
class UserAccountBillingInfo(BaseModel):
    """Pydantic schema for user account billing info."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    current_balance: Decimal
    user: Optional[UserBillingInfo] = None

class UserAccountBase(BaseModel):
    """Pydantic schema for user account base."""
    current_balance: Decimal = Field(..., ge=0, description="Current account balance in Coins")

class UserAccountCreate(UserAccountBase):
    """Pydantic schema for user account create."""
    user_id: int

class UserAccountResponse(UserAccountBase):
    """Pydantic schema for user account response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    total_spent: Decimal
    total_credits_added: Decimal
    currency: str
    created_at: datetime
    updated_at: datetime
    user: Optional[UserBillingInfo] = None

class UserTransactionBase(BaseModel):
    """Pydantic schema for user transaction base."""
    transaction_type: TransactionType
    amount: Decimal = Field(..., description="Transaction amount (positive for credits, negative for deductions)")
    description: Optional[str] = None

class UserTransactionCreate(UserTransactionBase):
    """Pydantic schema for user transaction create."""
    user_account_id: int
    balance_after: Decimal
    ai_cost_log_id: Optional[int] = None
    credit_package_id: Optional[int] = None
    payment_reference: Optional[str] = None
    transaction_metadata: Optional[Dict[str, Any]] = None

class UserTransactionResponse(UserTransactionBase):
    """Pydantic schema for user transaction response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_account_id: int
    balance_after: Decimal
    created_at: datetime
    transaction_metadata: Optional[Dict[str, Any]] = None
    user_account: Optional[UserAccountBillingInfo] = None

class CreditPackageBase(BaseModel):
    """Pydantic schema for credit package base."""
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    credit_amount: Decimal = Field(..., gt=0)
    price_usd: Decimal = Field(..., gt=0)
    bonus_percentage: Decimal = Field(Decimal('0.00'), ge=0, le=100)
    display_order: int = 0

class CreditPackageCreate(CreditPackageBase):
    """Pydantic schema for credit package create."""
    is_active: bool = True

class CreditPackageResponse(CreditPackageBase):
    """Pydantic schema for credit package response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class AddCreditsRequest(BaseModel):
    """Pydantic schema for add credits request."""
    credit_package_id: int
    payment_reference: str = Field(..., description="Payment processor transaction ID")

class BillingDashboardResponse(BaseModel):
    """Pydantic schema for billing dashboard response."""
    account: UserAccountResponse
    recent_transactions: List[UserTransactionResponse]
    available_packages: List[CreditPackageResponse]

class BalanceCheckResponse(BaseModel):
    """Pydantic schema for balance check response."""
    sufficient_balance: bool
    current_balance: Decimal
    required_amount: Decimal

class ManualCreditAdjustmentRequest(BaseModel):
    """Pydantic schema for manual credit adjustment request."""
    user_id: int
    amount: Decimal = Field(..., description="Amount to adjust (positive for add, negative for deduct)")
    description: str = Field(..., max_length=500, description="Reason for adjustment")

class AdminBillingDashboardResponse(BaseModel):
    """Pydantic schema for admin billing dashboard response."""
    system_stats: dict
    recent_transactions: List[UserTransactionResponse]
    user_accounts: List[UserAccountResponse]
