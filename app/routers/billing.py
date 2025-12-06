from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from decimal import Decimal
import logging

from app.core.deps import get_db_session, get_current_active_user, get_current_user_with_anonymous_support
from app.models.user import User
from app.crud.billing import billing_crud
from app.services.billing_service import billing_service
from app.schemas.base import ApiResponse
from app.schemas.billing import (
    UserAccountResponse, 
    UserTransactionResponse, 
    CreditPackageResponse, 
    AddCreditsRequest,
    BillingDashboardResponse,
    BalanceCheckResponse
)
from app.schemas.ai_cost_log import RecentAICostResponse, AICallLogResponse, LastAICallResponse
from app.crud import ai_cost_log as crud_ai_cost

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/billing", tags=["billing"])

@router.get("/account", response_model=ApiResponse)
async def get_user_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get current user's billing account information"""
    account = await billing_crud.get_or_create_user_account(db, current_user.id)
    return account

@router.get("/balance")
async def get_user_balance(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(get_current_user_with_anonymous_support)
):
    """Get current user's Coin balance (supports anonymous users)"""
    try:
        if not current_user:
            logger.warning("No user found for balance check")
            return {"balance": 0.0, "currency": "Coins", "error": "No user session found"}
        
        balance = await billing_service.get_user_balance(db, current_user.id)
        logger.info(f"Retrieved balance for user {current_user.id} ({current_user.username}): {balance}")
        return {"balance": float(balance), "currency": "Coins"}
    except Exception as e:
        logger.error(f"Error getting balance for user {current_user.id if current_user else 'unknown'}: {e}")
        return {"balance": 0.0, "currency": "Coins", "error": str(e)}

@router.get("/transactions", response_model=ApiResponse)
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

@router.get("/packages", response_model=ApiResponse)
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

@router.get("/dashboard", response_model=ApiResponse)
async def get_billing_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get comprehensive billing dashboard data"""
    account = await billing_crud.get_or_create_user_account(db, current_user.id)
    recent_transactions = await billing_crud.get_user_transactions(db, account.id, limit=10)
    available_packages = await billing_crud.get_active_credit_packages(db)
    
    return BillingDashboardResponse(
        account=account,
        recent_transactions=recent_transactions,
        available_packages=available_packages
    )

@router.get("/balance-check/{required_amount}", response_model=ApiResponse)
async def check_balance(
    required_amount: Decimal,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Check if user has sufficient balance for an operation"""
    has_balance = await billing_service.check_sufficient_balance(db, current_user.id, required_amount)
    account = await billing_crud.get_or_create_user_account(db, current_user.id)
    
    return BalanceCheckResponse(
        sufficient_balance=has_balance,
        current_balance=account.current_balance,
        required_amount=required_amount
    )

@router.get("/ai-costs/recent", response_model=ApiResponse)
async def get_recent_ai_costs(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get recent AI cost logs and daily summary for the current user"""
    try:
        # Get recent AI calls (last 3 for mini display)
        recent_calls = await crud_ai_cost.get_recent_ai_calls(db, current_user.id, limit=3)
        
        # Get today's summary
        total_calls_today, total_cost_today, total_tokens_today = await crud_ai_cost.get_daily_ai_cost_summary(db, current_user.id)
        
        # Convert to response format
        recent_calls_response = [
            AICallLogResponse(
                id=call.id,
                model_name=call.model_name,
                call_type=call.call_type,
                prompt_tokens=call.prompt_tokens,
                completion_tokens=call.completion_tokens,
                total_tokens=call.total_tokens,
                calculated_cost_usd=call.calculated_cost_usd,
                created_at=call.created_at,
                duration_ms=call.duration_ms
            )
            for call in recent_calls
        ]
        
        last_call_time = recent_calls[0].created_at if recent_calls else None
        
        return RecentAICostResponse(
            recent_calls=recent_calls_response,
            total_calls_today=total_calls_today,
            total_cost_today=total_cost_today,
            total_tokens_today=total_tokens_today,
            last_call_time=last_call_time
        )
        
    except Exception as e:
        logger.error(f"Error getting recent AI costs for user {current_user.id}: {e}")
        # Return empty data on error
        return RecentAICostResponse(
            recent_calls=[],
            total_calls_today=0,
            total_cost_today=0.0,
            total_tokens_today=0,
            last_call_time=None
        )

@router.get("/ai-costs/last", response_model=ApiResponse)
async def get_last_ai_call(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    """Get the last AI call and today's summary in Coin currency"""
    try:
        # Get the most recent AI call
        recent_calls = await crud_ai_cost.get_recent_ai_calls(db, current_user.id, limit=1)
        
        # Get today's summary
        total_calls_today, total_cost_today, total_tokens_today = await crud_ai_cost.get_daily_ai_cost_summary(db, current_user.id)
        
        # Convert USD to Coins (1 Coin = $0.0001 USD)
        def usd_to_coins(usd_amount: float) -> int:
            return int(round(usd_amount * 10000))
        
        last_call = None
        last_call_cost_coins = 0
        
        if recent_calls:
            call = recent_calls[0]
            last_call = AICallLogResponse(
                id=call.id,
                model_name=call.model_name,
                call_type=call.call_type,
                prompt_tokens=call.prompt_tokens,
                completion_tokens=call.completion_tokens,
                total_tokens=call.total_tokens,
                calculated_cost_usd=call.calculated_cost_usd,
                created_at=call.created_at,
                duration_ms=call.duration_ms
            )
            last_call_cost_coins = usd_to_coins(call.calculated_cost_usd)
        
        return LastAICallResponse(
            last_call=last_call,
            last_call_cost_coins=last_call_cost_coins,
            total_calls_today=total_calls_today,
            total_cost_coins_today=usd_to_coins(total_cost_today)
        )
        
    except Exception as e:
        logger.error(f"Error getting last AI call for user {current_user.id}: {e}")
        # Return empty data on error
        return LastAICallResponse(
            last_call=None,
            last_call_cost_coins=0,
            total_calls_today=0,
            total_cost_coins_today=0
        )