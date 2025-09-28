from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from app.models.user_transaction import TransactionType

# User schema for nested responses
class UserBillingInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: Optional[str] = None
    display_name: Optional[str] = None

# User account schema for nested responses in transactions
class UserAccountBillingInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_id: int
    current_balance: Decimal
    user: Optional[UserBillingInfo] = None

class UserAccountBase(BaseModel):
    current_balance: Decimal = Field(..., ge=0, description="Current account balance in Coins")

class UserAccountCreate(UserAccountBase):
    user_id: int

class UserAccountResponse(UserAccountBase):
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
    transaction_type: TransactionType
    amount: Decimal = Field(..., description="Transaction amount (positive for credits, negative for deductions)")
    description: Optional[str] = None

class UserTransactionCreate(UserTransactionBase):
    user_account_id: int
    balance_after: Decimal
    ai_cost_log_id: Optional[int] = None
    credit_package_id: Optional[int] = None
    payment_reference: Optional[str] = None

class UserTransactionResponse(UserTransactionBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    user_account_id: int
    balance_after: Decimal
    created_at: datetime
    user_account: Optional[UserAccountBillingInfo] = None

class CreditPackageBase(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    credit_amount: Decimal = Field(..., gt=0)
    price_usd: Decimal = Field(..., gt=0)
    bonus_percentage: Decimal = Field(Decimal('0.00'), ge=0, le=100)
    display_order: int = 0

class CreditPackageCreate(CreditPackageBase):
    is_active: bool = True

class CreditPackageResponse(CreditPackageBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

class AddCreditsRequest(BaseModel):
    credit_package_id: int
    payment_reference: str = Field(..., description="Payment processor transaction ID")

class BillingDashboardResponse(BaseModel):
    account: UserAccountResponse
    recent_transactions: List[UserTransactionResponse]
    available_packages: List[CreditPackageResponse]

class BalanceCheckResponse(BaseModel):
    sufficient_balance: bool
    current_balance: Decimal
    required_amount: Decimal

class ManualCreditAdjustmentRequest(BaseModel):
    user_id: int
    amount: Decimal = Field(..., description="Amount to adjust (positive for add, negative for deduct)")
    description: str = Field(..., max_length=500, description="Reason for adjustment")

class AdminBillingDashboardResponse(BaseModel):
    system_stats: dict
    recent_transactions: List[UserTransactionResponse]
    user_accounts: List[UserAccountResponse]