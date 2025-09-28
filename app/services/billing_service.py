from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from decimal import Decimal
from typing import Optional, Dict, Any
import logging

from app.crud.billing import billing_crud
from app.models.user_transaction import TransactionType
from app.models.ai_cost_log import AICallLog
from app.schemas.billing import UserTransactionCreate

logger = logging.getLogger(__name__)

class BillingService:
    
    async def check_sufficient_balance(self, db: AsyncSession, user_id: int, required_amount: Decimal) -> bool:
        """Check if user has sufficient balance for an operation"""
        account = await billing_crud.get_or_create_user_account(db, user_id)
        return account.current_balance >= required_amount
    
    async def deduct_ai_cost(self, db: AsyncSession, user_id: int, model_name: str, ai_cost_log_id: int) -> bool:
        """Deduct AI usage cost from user account based on actual token usage"""
        try:
            # Get the actual cost from the AI cost log
            result = await db.execute(
                select(AICallLog).where(AICallLog.id == ai_cost_log_id)
            )
            ai_cost_log = result.scalar_one_or_none()
            
            if not ai_cost_log:
                logger.error(f"AI cost log {ai_cost_log_id} not found")
                return False
            
            # Convert USD cost to Coins (1 Coin = 0.01 cent = $0.0001)
            # The calculated_cost_usd is already in USD, so multiply by 10000 to get coins
            amount = Decimal(str(ai_cost_log.calculated_cost_usd)) * Decimal('10000')
            
            # Round to 4 decimal places to match the database precision
            amount = amount.quantize(Decimal('0.0001'))
            
            # Skip billing for zero amounts (free models)
            if amount <= 0:
                logger.info(f"Skipping billing for user {user_id}: zero cost ({amount}) for free model {model_name}")
                return True
            
            account = await billing_crud.get_or_create_user_account(db, user_id)
            
            # Allow negative balance for MVP (complete operation then notify)
            new_balance = account.current_balance - amount
            
            # Create deduction transaction
            transaction_data = UserTransactionCreate(
                user_account_id=account.id,
                transaction_type=TransactionType.AI_COST_DEDUCTION,
                amount=-amount,  # Negative for deduction
                balance_after=new_balance,
                description=f"AI Usage: {model_name} ({ai_cost_log.total_tokens} tokens)",
                ai_cost_log_id=ai_cost_log_id
            )
            
            await billing_crud.create_transaction(db, transaction_data)
            
            # Update account balance and total spent
            account.current_balance = new_balance
            account.total_spent += amount
            await db.commit()
            
            logger.info(f"Deducted {amount} Coins from user {user_id} for {ai_cost_log.total_tokens} tokens. New balance: {new_balance}")
            
            # Return True even if balance goes negative (MVP requirement)
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
                description=f"Credits added: {package.name}" + (f" (includes {bonus_credits:.2f} bonus)" if bonus_credits > 0 else ""),
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
                "credits_added": float(total_credits),
                "bonus_credits": float(bonus_credits),
                "new_balance": float(new_balance)
            }
            
        except Exception as e:
            logger.error(f"Error adding credits for user {user_id}: {e}", exc_info=True)
            await db.rollback()
            return {"success": False, "error": "Internal error processing credit addition"}
    
    async def get_user_balance(self, db: AsyncSession, user_id: int) -> Decimal:
        """Get user's current Coin balance"""
        account = await billing_crud.get_or_create_user_account(db, user_id)
        return account.current_balance
    
    async def get_or_create_anonymous_user_balance(self, db: AsyncSession, user_id: int, is_anonymous: bool = False) -> Decimal:
        """Get user's current Coin balance, with special handling for anonymous users"""
        if not user_id:
            raise ValueError("user_id cannot be None")
            
        account = await billing_crud.get_user_account(db, user_id)
        
        if not account and is_anonymous:
            # Create account with 5 coins for anonymous user (reduced from 100, then from 25)
            from app.schemas.billing import UserAccountCreate
            
            # Start anonymous users with only 500 coins instead of 10000
            initial_coins = Decimal('500.0000')
            account_data = UserAccountCreate(user_id=user_id, current_balance=initial_coins)
            account = await billing_crud.create_user_account(db, account_data)
            
            # Override the default 50 coin welcome bonus for anonymous users
            # Remove the default welcome bonus transaction and replace with smaller amount
            from sqlalchemy import delete
            from app.models.user_transaction import UserTransaction, TransactionType
            
            await db.execute(
                delete(UserTransaction).where(
                    UserTransaction.user_account_id == account.id,
                    UserTransaction.transaction_type == TransactionType.WELCOME_BONUS
                )
            )
            
            # Add anonymous user bonus transaction (5 coins only)
            bonus_transaction = UserTransaction(
                user_account_id=account.id,
                transaction_type=TransactionType.WELCOME_BONUS,
                amount=initial_coins,
                balance_after=initial_coins,
                description="Anonymous user starter allowance - 5 Coins"
            )
            db.add(bonus_transaction)
            
            # Update account balance and totals
            account.current_balance = initial_coins
            account.total_credits_added = initial_coins
            
            await db.commit()
            await db.refresh(account)
            
            logger.info(f"Created account with {initial_coins} coins for anonymous user {user_id}")
            
        elif not account:
            # Regular user - create with default welcome bonus
            account = await billing_crud.get_or_create_user_account(db, user_id)
            
        return account.current_balance
    
    async def add_referral_reward(
        self, 
        db: AsyncSession, 
        user_id: int, 
        amount: int, 
        description: str
    ) -> bool:
        """Add referral reward coins to user account"""
        try:
            account = await billing_crud.get_or_create_user_account(db, user_id)
            
            # Convert integer coins to decimal
            amount_decimal = Decimal(str(amount))
            
            # Calculate new balance
            new_balance = account.current_balance + amount_decimal
            
            # Create transaction
            transaction_data = UserTransactionCreate(
                user_account_id=account.id,
                transaction_type=TransactionType.REFERRAL_BONUS,
                amount=amount_decimal,
                balance_after=new_balance,
                description=description
            )
            
            # Create the transaction record
            await billing_crud.create_transaction(db, transaction_data)
            
            # Update account balance and totals
            account.current_balance = new_balance
            account.total_credits_added += amount_decimal
            await db.commit()
            
            logger.info(f"Added {amount} referral reward coins to user {user_id}. New balance: {new_balance}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding referral reward: {e}", exc_info=True)
            await db.rollback()
            return False
    
    async def charge_fixed_amount(
        self, 
        db: AsyncSession, 
        user_id: int, 
        amount: Decimal, 
        description: str,
        service_type: str = "service"
    ) -> bool:
        """Charge a fixed amount from user account for services like image upload"""
        try:
            account = await billing_crud.get_or_create_user_account(db, user_id)
            
            # Calculate new balance (allow negative balance for MVP)
            new_balance = account.current_balance - amount
            
            # Create transaction record
            transaction_data = UserTransactionCreate(
                user_account_id=account.id,
                transaction_type=TransactionType.SERVICE_CHARGE,
                amount=amount,
                balance_after=new_balance,
                description=description
            )
            
            await billing_crud.create_transaction(db, transaction_data)
            
            # Update account balance and total spent
            account.current_balance = new_balance
            account.total_spent += amount
            await db.commit()
            
            logger.info(f"Charged {amount} coins from user {user_id} for {service_type}. New balance: {new_balance}")
            
            # Return True even if balance goes negative (MVP requirement)
            return True
            
        except Exception as e:
            logger.error(f"Error charging fixed amount for user {user_id}: {e}", exc_info=True)
            await db.rollback()
            return False

billing_service = BillingService()