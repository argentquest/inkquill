# User Credit/Billing System Implementation Plan

## Overview

This document outlines the comprehensive implementation plan for adding a user credit/billing system to the AI Storytelling Assistant. The system will track AI costs, manage user account balances, and provide credit top-up functionality.

## Phase 1: Database Schema Design

### New Tables

#### 1. `user_accounts` - Core billing account information
```sql
CREATE TABLE user_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    current_balance DECIMAL(10,4) NOT NULL DEFAULT 0.0000,
    total_spent DECIMAL(10,4) NOT NULL DEFAULT 0.0000,
    total_credits_added DECIMAL(10,4) NOT NULL DEFAULT 0.0000,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    low_balance_threshold DECIMAL(10,4) DEFAULT 5.0000,
    notifications_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. `user_transactions` - All account activity history
```sql
CREATE TABLE user_transactions (
    id SERIAL PRIMARY KEY,
    user_account_id INTEGER NOT NULL REFERENCES user_accounts(id) ON DELETE CASCADE,
    transaction_type VARCHAR(20) NOT NULL CHECK (transaction_type IN ('credit_add', 'ai_cost_deduction', 'refund', 'adjustment')),
    amount DECIMAL(10,4) NOT NULL,
    balance_after DECIMAL(10,4) NOT NULL,
    description TEXT,
    ai_cost_log_id INTEGER REFERENCES ai_cost_logs(id) ON DELETE SET NULL,
    credit_package_id INTEGER REFERENCES credit_packages(id) ON DELETE SET NULL,
    payment_reference VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. `credit_packages` - Available credit purchase options
```sql
CREATE TABLE credit_packages (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    credit_amount DECIMAL(10,4) NOT NULL,
    price_usd DECIMAL(10,2) NOT NULL,
    bonus_percentage DECIMAL(5,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes and Constraints
```sql
-- Performance indexes
CREATE INDEX idx_user_transactions_user_account ON user_transactions(user_account_id, created_at DESC);
CREATE INDEX idx_user_transactions_type ON user_transactions(transaction_type);
CREATE INDEX idx_user_transactions_ai_cost_log ON user_transactions(ai_cost_log_id);
CREATE INDEX idx_credit_packages_active ON credit_packages(is_active, display_order);

-- Constraints
ALTER TABLE user_accounts ADD CONSTRAINT check_positive_balance CHECK (current_balance >= 0);
ALTER TABLE user_transactions ADD CONSTRAINT check_non_zero_amount CHECK (amount != 0);
```

## Phase 2: Pydantic Models and Schemas

### File: `app/models/user_account.py`
```python
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
    low_balance_threshold: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 4), default=Decimal('5.0000'))
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="account")
    transactions: Mapped[List["UserTransaction"]] = relationship("UserTransaction", back_populates="user_account", cascade="all, delete-orphan")
    
    __table_args__ = (
        CheckConstraint('current_balance >= 0', name='check_positive_balance'),
    )
```

### File: `app/models/user_transaction.py`
```python
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
    REFUND = "refund"
    ADJUSTMENT = "adjustment"

class UserTransaction(Base):
    __tablename__ = "user_transactions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_account_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_accounts.id", ondelete="CASCADE"), nullable=False)
    transaction_type: Mapped[TransactionType] = mapped_column(String(20), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    ai_cost_log_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ai_cost_logs.id", ondelete="SET NULL"))
    credit_package_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("credit_packages.id", ondelete="SET NULL"))
    payment_reference: Mapped[Optional[str]] = mapped_column(String(255))
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user_account: Mapped["UserAccount"] = relationship("UserAccount", back_populates="transactions")
    ai_cost_log: Mapped[Optional["AICostLog"]] = relationship("AICostLog")
    credit_package: Mapped[Optional["CreditPackage"]] = relationship("CreditPackage")
    
    __table_args__ = (
        CheckConstraint('amount != 0', name='check_non_zero_amount'),
    )
```

### File: `app/models/credit_package.py`
```python
from sqlalchemy import Column, Integer, String, DECIMAL, Text, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from decimal import Decimal
from typing import Optional
from app.db.database import Base

class CreditPackage(Base):
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
```

### File: `app/schemas/billing.py`
```python
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from app.models.user_transaction import TransactionType

class UserAccountBase(BaseModel):
    current_balance: Decimal = Field(..., ge=0, description="Current account balance")
    low_balance_threshold: Optional[Decimal] = Field(Decimal('5.0000'), ge=0)
    notifications_enabled: bool = True

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
    monthly_spending: Decimal
    usage_summary: dict
```

## Phase 3: Database CRUD Operations

### File: `app/crud/billing.py`
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from sqlalchemy.orm import selectinload
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, timedelta

from app.models.user_account import UserAccount
from app.models.user_transaction import UserTransaction, TransactionType
from app.models.credit_package import CreditPackage
from app.schemas.billing import UserAccountCreate, UserTransactionCreate, CreditPackageCreate

class BillingCRUD:
    
    # User Account Operations
    async def create_user_account(self, db: AsyncSession, account_data: UserAccountCreate) -> UserAccount:
        db_account = UserAccount(**account_data.model_dump())
        db.add(db_account)
        await db.commit()
        await db.refresh(db_account)
        return db_account
    
    async def get_user_account(self, db: AsyncSession, user_id: int) -> Optional[UserAccount]:
        result = await db.execute(
            select(UserAccount).where(UserAccount.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_user_account(self, db: AsyncSession, user_id: int) -> UserAccount:
        account = await self.get_user_account(db, user_id)
        if not account:
            account_data = UserAccountCreate(user_id=user_id, current_balance=Decimal('0.0000'))
            account = await self.create_user_account(db, account_data)
        return account
    
    async def update_account_balance(self, db: AsyncSession, user_account_id: int, new_balance: Decimal) -> UserAccount:
        result = await db.execute(
            select(UserAccount).where(UserAccount.id == user_account_id)
        )
        account = result.scalar_one()
        account.current_balance = new_balance
        account.updated_at = func.now()
        await db.commit()
        await db.refresh(account)
        return account
    
    # Transaction Operations
    async def create_transaction(self, db: AsyncSession, transaction_data: UserTransactionCreate) -> UserTransaction:
        db_transaction = UserTransaction(**transaction_data.model_dump())
        db.add(db_transaction)
        await db.commit()
        await db.refresh(db_transaction)
        return db_transaction
    
    async def get_user_transactions(self, db: AsyncSession, user_account_id: int, limit: int = 50, offset: int = 0) -> List[UserTransaction]:
        result = await db.execute(
            select(UserTransaction)
            .where(UserTransaction.user_account_id == user_account_id)
            .order_by(desc(UserTransaction.created_at))
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_monthly_spending(self, db: AsyncSession, user_account_id: int, month: Optional[datetime] = None) -> Decimal:
        if month is None:
            month = datetime.now()
        
        start_of_month = month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        start_of_next_month = (start_of_month + timedelta(days=32)).replace(day=1)
        
        result = await db.execute(
            select(func.sum(UserTransaction.amount))
            .where(
                and_(
                    UserTransaction.user_account_id == user_account_id,
                    UserTransaction.transaction_type == TransactionType.AI_COST_DEDUCTION,
                    UserTransaction.created_at >= start_of_month,
                    UserTransaction.created_at < start_of_next_month
                )
            )
        )
        total = result.scalar()
        return abs(total) if total else Decimal('0.0000')
    
    # Credit Package Operations
    async def get_active_credit_packages(self, db: AsyncSession) -> List[CreditPackage]:
        result = await db.execute(
            select(CreditPackage)
            .where(CreditPackage.is_active == True)
            .order_by(CreditPackage.display_order, CreditPackage.price_usd)
        )
        return result.scalars().all()
    
    async def get_credit_package(self, db: AsyncSession, package_id: int) -> Optional[CreditPackage]:
        result = await db.execute(
            select(CreditPackage).where(CreditPackage.id == package_id)
        )
        return result.scalar_one_or_none()

billing_crud = BillingCRUD()
```

## Phase 4: Core Billing Service

### File: `app/services/billing_service.py`
```python
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal
from typing import Optional, Dict, Any
import logging

from app.crud.billing import billing_crud
from app.models.user_transaction import TransactionType
from app.schemas.billing import UserTransactionCreate
from app.services.cost_tracker_service import CostTrackerService

logger = logging.getLogger(__name__)

class BillingService:
    
    async def check_sufficient_balance(self, db: AsyncSession, user_id: int, required_amount: Decimal) -> bool:
        """Check if user has sufficient balance for an operation"""
        account = await billing_crud.get_or_create_user_account(db, user_id)
        return account.current_balance >= required_amount
    
    async def deduct_ai_cost(self, db: AsyncSession, user_id: int, amount: Decimal, ai_cost_log_id: int, description: str) -> bool:
        """Deduct AI usage cost from user account"""
        try:
            account = await billing_crud.get_or_create_user_account(db, user_id)
            
            if account.current_balance < amount:
                logger.warning(f"Insufficient balance for user {user_id}. Required: {amount}, Available: {account.current_balance}")
                return False
            
            new_balance = account.current_balance - amount
            
            # Create deduction transaction
            transaction_data = UserTransactionCreate(
                user_account_id=account.id,
                transaction_type=TransactionType.AI_COST_DEDUCTION,
                amount=-amount,  # Negative for deduction
                balance_after=new_balance,
                description=description,
                ai_cost_log_id=ai_cost_log_id
            )
            
            await billing_crud.create_transaction(db, transaction_data)
            
            # Update account balance and total spent
            account.current_balance = new_balance
            account.total_spent += amount
            await db.commit()
            
            # Check for low balance notification
            if account.notifications_enabled and new_balance <= (account.low_balance_threshold or Decimal('5.0000')):
                await self._send_low_balance_notification(user_id, new_balance)
            
            logger.info(f"Deducted {amount} from user {user_id}. New balance: {new_balance}")
            return True
            
        except Exception as e:
            logger.error(f"Error deducting AI cost for user {user_id}: {e}", exc_info=True)
            await db.rollback()
            return False
    
    async def add_credits(self, db: AsyncSession, user_id: int, credit_package_id: int, payment_reference: str) -> Dict[str, Any]:
        """Add credits to user account from package purchase"""
        try:
            account = await billing_crud.get_or_create_user_account(db, user_id)
            package = await billing_crud.get_credit_package(db, credit_package_id)
            
            if not package or not package.is_active:
                return {"success": False, "error": "Credit package not found or inactive"}
            
            # Calculate final credit amount including bonus
            base_credits = package.credit_amount
            bonus_credits = base_credits * (package.bonus_percentage / Decimal('100'))
            total_credits = base_credits + bonus_credits
            
            new_balance = account.current_balance + total_credits
            
            # Create credit addition transaction
            transaction_data = UserTransactionCreate(
                user_account_id=account.id,
                transaction_type=TransactionType.CREDIT_ADD,
                amount=total_credits,
                balance_after=new_balance,
                description=f"Credits added: {package.name}" + (f" (includes {bonus_credits:.4f} bonus)" if bonus_credits > 0 else ""),
                credit_package_id=credit_package_id,
                payment_reference=payment_reference
            )
            
            await billing_crud.create_transaction(db, transaction_data)
            
            # Update account balance and total credits added
            account.current_balance = new_balance
            account.total_credits_added += total_credits
            await db.commit()
            
            logger.info(f"Added {total_credits} credits to user {user_id}. New balance: {new_balance}")
            
            return {
                "success": True,
                "credits_added": total_credits,
                "bonus_credits": bonus_credits,
                "new_balance": new_balance
            }
            
        except Exception as e:
            logger.error(f"Error adding credits for user {user_id}: {e}", exc_info=True)
            await db.rollback()
            return {"success": False, "error": "Internal error processing credit addition"}
    
    async def _send_low_balance_notification(self, user_id: int, current_balance: Decimal):
        """Send low balance notification to user (implement based on notification system)"""
        # TODO: Implement notification logic (email, in-app notification, etc.)
        logger.info(f"Low balance notification for user {user_id}: {current_balance}")

billing_service = BillingService()
```

## Phase 5: API Endpoints

### File: `app/routers/billing.py`
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from decimal import Decimal

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.crud.billing import billing_crud
from app.services.billing_service import billing_service
from app.schemas.billing import (
    UserAccountResponse, 
    UserTransactionResponse, 
    CreditPackageResponse, 
    AddCreditsRequest,
    BillingDashboardResponse
)

router = APIRouter(prefix="/billing", tags=["billing"])

@router.get("/account", response_model=UserAccountResponse)
async def get_user_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user's billing account information"""
    account = await billing_crud.get_or_create_user_account(db, current_user.id)
    return account

@router.get("/transactions", response_model=List[UserTransactionResponse])
async def get_user_transactions(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get user's transaction history"""
    account = await billing_crud.get_or_create_user_account(db, current_user.id)
    transactions = await billing_crud.get_user_transactions(db, account.id, limit, offset)
    return transactions

@router.get("/packages", response_model=List[CreditPackageResponse])
async def get_credit_packages(db: AsyncSession = Depends(get_db_session)):
    """Get available credit packages"""
    packages = await billing_crud.get_active_credit_packages(db)
    return packages

@router.post("/add-credits")
async def add_credits(
    request: AddCreditsRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Add credits to user account"""
    result = await billing_service.add_credits(
        db, current_user.id, request.credit_package_id, request.payment_reference
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("error", "Failed to add credits")
        )
    
    return result

@router.get("/dashboard", response_model=BillingDashboardResponse)
async def get_billing_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get comprehensive billing dashboard data"""
    account = await billing_crud.get_or_create_user_account(db, current_user.id)
    recent_transactions = await billing_crud.get_user_transactions(db, account.id, limit=10)
    available_packages = await billing_crud.get_active_credit_packages(db)
    monthly_spending = await billing_crud.get_monthly_spending(db, account.id)
    
    # TODO: Add usage summary calculation
    usage_summary = {
        "total_ai_calls_this_month": 0,
        "most_used_model": "N/A",
        "average_daily_cost": 0.0
    }
    
    return BillingDashboardResponse(
        account=account,
        recent_transactions=recent_transactions,
        available_packages=available_packages,
        monthly_spending=monthly_spending,
        usage_summary=usage_summary
    )

@router.get("/balance-check/{required_amount}")
async def check_balance(
    required_amount: Decimal,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Check if user has sufficient balance for an operation"""
    has_balance = await billing_service.check_sufficient_balance(db, current_user.id, required_amount)
    account = await billing_crud.get_or_create_user_account(db, current_user.id)
    
    return {
        "sufficient_balance": has_balance,
        "current_balance": account.current_balance,
        "required_amount": required_amount
    }
```

## Phase 6: Integration with Existing AI Cost Tracking

### Modify: `app/services/cost_tracker_service.py`
```python
# Add to existing cost_tracker_service.py

from app.services.billing_service import billing_service

async def log_ai_call_with_billing(
    user_id: int,
    model_config: AIModelConfiguration,
    usage: Optional[Dict[str, int]],
    call_type: str,
    input_prompt: Optional[str] = None,
    duration_ms: Optional[int] = None,
    job_id: Optional[str] = None,
    object_id: Optional[int] = None,
    db: Optional[AsyncSession] = None
) -> Optional[int]:
    """Enhanced version that includes billing deduction"""
    
    # First log the AI call as before
    cost_log_id = await log_ai_call(
        user_id, model_config, usage, call_type, 
        input_prompt, duration_ms, job_id, object_id, db
    )
    
    if cost_log_id and usage:
        # Calculate cost and deduct from user balance
        total_tokens = usage.get('total_tokens', 0)
        estimated_cost = (total_tokens * model_config.cost_per_token) if total_tokens > 0 else Decimal('0.0001')
        
        # Deduct from user balance
        success = await billing_service.deduct_ai_cost(
            db, user_id, estimated_cost, cost_log_id, 
            f"{call_type} - {model_config.display_name}"
        )
        
        if not success:
            logger.warning(f"Failed to deduct cost for AI call {cost_log_id}. User {user_id} may have insufficient balance.")
    
    return cost_log_id
```

## Phase 7: Frontend UI Components

### Billing Dashboard Page: `app/templates/pages/billing_dashboard.html`
```html
{% extends "layouts/base.html" %}

{% block title %}Billing Dashboard{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-12">
            <h2>Billing Dashboard</h2>
        </div>
    </div>
    
    <!-- Account Summary Cards -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card bg-primary text-white">
                <div class="card-body">
                    <h5 class="card-title">Current Balance</h5>
                    <h3 id="current-balance">$0.00</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-info text-white">
                <div class="card-body">
                    <h5 class="card-title">This Month</h5>
                    <h3 id="monthly-spending">$0.00</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-success text-white">
                <div class="card-body">
                    <h5 class="card-title">Total Added</h5>
                    <h3 id="total-credits">$0.00</h3>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card bg-warning text-white">
                <div class="card-body">
                    <h5 class="card-title">Total Spent</h5>
                    <h3 id="total-spent">$0.00</h3>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Add Credits Section -->
    <div class="row mb-4">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5>Add Credits</h5>
                </div>
                <div class="card-body">
                    <div class="row" id="credit-packages">
                        <!-- Credit packages will be loaded here -->
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Recent Transactions -->
    <div class="row">
        <div class="col-12">
            <div class="card">
                <div class="card-header">
                    <h5>Recent Transactions</h5>
                </div>
                <div class="card-body">
                    <div class="table-responsive">
                        <table class="table table-hover" id="transactions-table">
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Type</th>
                                    <th>Amount</th>
                                    <th>Balance After</th>
                                    <th>Description</th>
                                </tr>
                            </thead>
                            <tbody>
                                <!-- Transactions will be loaded here -->
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Add Credits Modal -->
<div class="modal fade" id="addCreditsModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Add Credits</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                <form id="add-credits-form">
                    <input type="hidden" id="selected-package-id">
                    <div class="mb-3">
                        <label class="form-label">Selected Package</label>
                        <div id="selected-package-info" class="alert alert-info"></div>
                    </div>
                    <div class="mb-3">
                        <label for="payment-reference" class="form-label">Payment Reference</label>
                        <input type="text" class="form-control" id="payment-reference" required>
                        <div class="form-text">Enter your payment processor transaction ID</div>
                    </div>
                </form>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                <button type="button" class="btn btn-primary" id="confirm-add-credits">Add Credits</button>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script src="{{ url_for('static', path='/js/billing_dashboard.js') }}"></script>
{% endblock %}
```

### Frontend JavaScript: `app/static/js/billing_dashboard.js`
```javascript
class BillingDashboard {
    constructor() {
        this.init();
    }
    
    async init() {
        await this.loadDashboardData();
        this.setupEventListeners();
    }
    
    async loadDashboardData() {
        try {
            const response = await fetch('/billing/dashboard');
            const data = await response.json();
            
            this.updateAccountSummary(data.account);
            this.updateMonthlySummary(data.monthly_spending);
            this.renderCreditPackages(data.available_packages);
            this.renderTransactions(data.recent_transactions);
            
        } catch (error) {
            console.error('Error loading billing dashboard:', error);
            this.showNotification('Error loading billing data', 'error');
        }
    }
    
    updateAccountSummary(account) {
        document.getElementById('current-balance').textContent = `$${account.current_balance}`;
        document.getElementById('total-credits').textContent = `$${account.total_credits_added}`;
        document.getElementById('total-spent').textContent = `$${account.total_spent}`;
    }
    
    updateMonthlySummary(monthlySpending) {
        document.getElementById('monthly-spending').textContent = `$${monthlySpending}`;
    }
    
    renderCreditPackages(packages) {
        const container = document.getElementById('credit-packages');
        container.innerHTML = '';
        
        packages.forEach(pkg => {
            const packageCard = document.createElement('div');
            packageCard.className = 'col-md-4 mb-3';
            
            const bonusText = pkg.bonus_percentage > 0 ? 
                `<span class="badge bg-success">+${pkg.bonus_percentage}% Bonus</span>` : '';
            
            packageCard.innerHTML = `
                <div class="card">
                    <div class="card-body text-center">
                        <h5 class="card-title">${pkg.name}</h5>
                        <p class="card-text">${pkg.description || ''}</p>
                        <h4 class="text-primary">$${pkg.credit_amount}</h4>
                        <p class="text-muted">for $${pkg.price_usd}</p>
                        ${bonusText}
                        <button class="btn btn-primary w-100 mt-2" 
                                onclick="billingDashboard.selectCreditPackage(${pkg.id}, '${pkg.name}', ${pkg.credit_amount}, ${pkg.price_usd}, ${pkg.bonus_percentage})">
                            Purchase
                        </button>
                    </div>
                </div>
            `;
            
            container.appendChild(packageCard);
        });
    }
    
    renderTransactions(transactions) {
        const tbody = document.querySelector('#transactions-table tbody');
        tbody.innerHTML = '';
        
        transactions.forEach(tx => {
            const row = document.createElement('tr');
            const amountClass = tx.amount >= 0 ? 'text-success' : 'text-danger';
            const amountSign = tx.amount >= 0 ? '+' : '';
            
            row.innerHTML = `
                <td>${new Date(tx.created_at).toLocaleDateString()}</td>
                <td><span class="badge bg-secondary">${tx.transaction_type}</span></td>
                <td class="${amountClass}">${amountSign}$${Math.abs(tx.amount)}</td>
                <td>$${tx.balance_after}</td>
                <td>${tx.description || ''}</td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    selectCreditPackage(id, name, credits, price, bonus) {
        document.getElementById('selected-package-id').value = id;
        
        const bonusText = bonus > 0 ? ` (includes ${bonus}% bonus)` : '';
        document.getElementById('selected-package-info').innerHTML = `
            <strong>${name}</strong><br>
            $${credits} credits for $${price}${bonusText}
        `;
        
        const modal = new bootstrap.Modal(document.getElementById('addCreditsModal'));
        modal.show();
    }
    
    setupEventListeners() {
        document.getElementById('confirm-add-credits').addEventListener('click', () => {
            this.addCredits();
        });
    }
    
    async addCredits() {
        const packageId = document.getElementById('selected-package-id').value;
        const paymentReference = document.getElementById('payment-reference').value;
        
        if (!paymentReference.trim()) {
            this.showNotification('Please enter a payment reference', 'error');
            return;
        }
        
        try {
            const response = await fetch('/billing/add-credits', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    credit_package_id: parseInt(packageId),
                    payment_reference: paymentReference
                })
            });
            
            const result = await response.json();
            
            if (response.ok && result.success) {
                this.showNotification(`Successfully added $${result.credits_added} credits!`, 'success');
                const modal = bootstrap.Modal.getInstance(document.getElementById('addCreditsModal'));
                modal.hide();
                document.getElementById('add-credits-form').reset();
                
                // Reload dashboard data
                await this.loadDashboardData();
            } else {
                this.showNotification(result.error || 'Failed to add credits', 'error');
            }
            
        } catch (error) {
            console.error('Error adding credits:', error);
            this.showNotification('Error processing credit addition', 'error');
        }
    }
    
    showNotification(message, type) {
        // Implement notification system (toast, alert, etc.)
        if (type === 'error') {
            alert('Error: ' + message);
        } else {
            alert('Success: ' + message);
        }
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    window.billingDashboard = new BillingDashboard();
});
```

## Phase 8: Database Migration

### Create Alembic Migration
```bash
alembic revision --autogenerate -m "add_billing_system_tables"
```

### Sample Data for Credit Packages
```python
# Add to seed script or create separate seeding function
async def seed_credit_packages():
    packages = [
        {
            "name": "Starter Pack",
            "description": "Perfect for trying out AI features",
            "credit_amount": Decimal("5.00"),
            "price_usd": Decimal("5.00"),
            "bonus_percentage": Decimal("0.00"),
            "display_order": 1
        },
        {
            "name": "Value Pack",
            "description": "Great value for regular users",
            "credit_amount": Decimal("25.00"),
            "price_usd": Decimal("20.00"),
            "bonus_percentage": Decimal("25.00"),
            "display_order": 2
        },
        {
            "name": "Power User",
            "description": "For heavy AI usage",
            "credit_amount": Decimal("100.00"),
            "price_usd": Decimal("75.00"),
            "bonus_percentage": Decimal("33.33"),
            "display_order": 3
        }
    ]
```

## Phase 9: Integration Points

### 1. Add Balance Checks to AI Operations
- Modify WebSocket handlers to check balance before processing
- Add balance validation to API endpoints that trigger AI calls
- Implement graceful degradation when balance is insufficient

### 2. Update Navigation
- Add billing dashboard link to main navigation
- Show current balance in user menu
- Add low balance warnings

### 3. Admin Interface
- Create admin endpoints for managing credit packages
- Add transaction monitoring and reporting
- Implement refund and adjustment capabilities

## Implementation Timeline

### Week 1: Database & Core Models
- [ ] Create database schema and run migrations
- [ ] Implement Pydantic models and schemas
- [ ] Create CRUD operations
- [ ] Write unit tests for core functionality

### Week 2: Business Logic & API
- [ ] Implement billing service logic
- [ ] Create API endpoints
- [ ] Integrate with existing cost tracking
- [ ] Add balance checks to AI operations

### Week 3: Frontend & UX
- [ ] Build billing dashboard UI
- [ ] Implement credit package selection
- [ ] Add balance indicators to existing pages
- [ ] Create transaction history views

### Week 4: Testing & Polish
- [ ] End-to-end testing
- [ ] Performance optimization
- [ ] Security review
- [ ] Documentation and deployment

## Security Considerations

1. **Input Validation**: All financial amounts must be validated and sanitized
2. **Transaction Integrity**: Use database transactions to ensure consistency
3. **Audit Trail**: Maintain comprehensive logs of all billing operations
4. **Rate Limiting**: Implement rate limits on credit addition endpoints
5. **Payment Verification**: Validate payment references before crediting accounts

## Monitoring & Alerts

1. **Low Balance Notifications**: Alert users when balance drops below threshold
2. **Failed Transactions**: Monitor and alert on failed billing operations
3. **Usage Patterns**: Track unusual spending patterns
4. **System Health**: Monitor billing service performance and availability

This comprehensive implementation plan provides a solid foundation for adding user credit and billing functionality to the AI Storytelling Assistant. The modular design allows for incremental implementation and easy future enhancements.