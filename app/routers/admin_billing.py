from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from decimal import Decimal
import logging

from app.core.deps import get_db_session, get_current_active_user
from app.models.user import User
from app.crud.billing import billing_crud
from app.schemas.billing import (
    UserAccountResponse, 
    UserTransactionResponse,
    ManualCreditAdjustmentRequest,
    AdminBillingDashboardResponse
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin/billing", tags=["admin-billing"])

def verify_admin_user(current_user: User = Depends(get_current_active_user)):
    """Verify that the current user is an admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

@router.get("/dashboard", response_model=AdminBillingDashboardResponse)
async def get_admin_billing_dashboard(
    current_admin: User = Depends(verify_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get comprehensive admin billing dashboard data"""
    try:
        # Get system statistics
        stats = await billing_crud.get_system_statistics(db)
        
        # Get recent transactions across all users
        recent_transactions = await billing_crud.get_all_transactions_for_admin(db, limit=20)
        
        # Get all user accounts with stats
        user_accounts = await billing_crud.get_all_user_accounts_with_stats(db, limit=50)
        
        return AdminBillingDashboardResponse(
            system_stats=stats,
            recent_transactions=recent_transactions,
            user_accounts=user_accounts
        )
        
    except Exception as e:
        logger.error(f"Error loading admin billing dashboard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error loading admin dashboard"
        )

@router.get("/transactions", response_model=List[UserTransactionResponse])
async def get_all_transactions(
    limit: int = 100,
    offset: int = 0,
    current_admin: User = Depends(verify_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all transactions across all users for admin monitoring"""
    transactions = await billing_crud.get_all_transactions_for_admin(db, limit, offset)
    return transactions

@router.get("/users", response_model=List[UserAccountResponse])
async def get_all_user_accounts(
    limit: int = 100,
    offset: int = 0,
    current_admin: User = Depends(verify_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all user accounts with billing information"""
    accounts = await billing_crud.get_all_user_accounts_with_stats(db, limit, offset)
    return accounts

@router.post("/adjust-credits")
async def manual_credit_adjustment(
    request: ManualCreditAdjustmentRequest,
    current_admin: User = Depends(verify_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Manually adjust user credits (positive or negative)"""
    try:
        transaction = await billing_crud.manual_credit_adjustment(
            db=db,
            user_id=request.user_id,
            amount=request.amount,
            description=request.description,
            admin_user_id=current_admin.id
        )
        
        logger.info(f"Admin {current_admin.id} adjusted credits for user {request.user_id}: {request.amount} coins")
        
        return {
            "success": True,
            "message": f"Successfully adjusted {request.amount} coins for user {request.user_id}",
            "transaction_id": transaction.id
        }
        
    except Exception as e:
        logger.error(f"Error in manual credit adjustment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing credit adjustment"
        )

@router.get("/statistics")
async def get_system_statistics(
    current_admin: User = Depends(verify_admin_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get system-wide billing statistics"""
    stats = await billing_crud.get_system_statistics(db)
    return stats