"""Database CRUD helpers for billing."""

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
    
    # Admin Operations
    """Class for billing c r u d."""
    async def get_all_user_accounts_with_stats(self, db: AsyncSession, limit: int = 100, offset: int = 0) -> List[UserAccount]:
        """Get all user accounts with their transaction stats for admin dashboard"""
        result = await db.execute(
            select(UserAccount)
            .options(selectinload(UserAccount.user))
            .order_by(desc(UserAccount.updated_at))
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_all_transactions_for_admin(self, db: AsyncSession, limit: int = 100, offset: int = 0) -> List[UserTransaction]:
        """Get all transactions across all users for admin monitoring"""
        result = await db.execute(
            select(UserTransaction)
            .options(
                selectinload(UserTransaction.user_account).selectinload(UserAccount.user)
            )
            .order_by(desc(UserTransaction.created_at))
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()
    
    async def get_system_statistics(self, db: AsyncSession) -> dict:
        """Get overall system billing statistics"""
        # Total users with accounts
        total_users_result = await db.execute(
            select(func.count(UserAccount.id))
        )
        total_users = total_users_result.scalar()
        
        # Total coins in circulation
        total_balance_result = await db.execute(
            select(func.sum(UserAccount.current_balance))
        )
        total_balance = total_balance_result.scalar() or Decimal('0.0000')
        
        # Total coins ever added to system
        total_credits_result = await db.execute(
            select(func.sum(UserAccount.total_credits_added))
        )
        total_credits_added = total_credits_result.scalar() or Decimal('0.0000')
        
        # Total coins spent
        total_spent_result = await db.execute(
            select(func.sum(UserAccount.total_spent))
        )
        total_spent = total_spent_result.scalar() or Decimal('0.0000')
        
        # Total transactions
        total_transactions_result = await db.execute(
            select(func.count(UserTransaction.id))
        )
        total_transactions = total_transactions_result.scalar()
        
        # Recent activity (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        recent_transactions_result = await db.execute(
            select(func.count(UserTransaction.id))
            .where(UserTransaction.created_at >= yesterday)
        )
        recent_transactions = recent_transactions_result.scalar()
        
        return {
            "total_users": total_users,
            "total_balance": total_balance,
            "total_credits_added": total_credits_added,
            "total_spent": total_spent,
            "total_transactions": total_transactions,
            "recent_transactions_24h": recent_transactions
        }
    
    async def manual_credit_adjustment(self, db: AsyncSession, user_id: int, amount: Decimal, description: str, admin_user_id: int) -> UserTransaction:
        """Admin function to manually adjust user credits (positive or negative)"""
        account = await self.get_or_create_user_account(db, user_id)
        
        new_balance = account.current_balance + amount
        if new_balance < 0:
            new_balance = Decimal('0.0000')  # Don't allow negative balances from manual adjustments
        
        # Create manual adjustment transaction
        transaction_data = UserTransactionCreate(
            user_account_id=account.id,
            transaction_type=TransactionType.ADMIN_ADJUSTMENT if amount > 0 else TransactionType.ADMIN_DEDUCTION,
            amount=amount,
            balance_after=new_balance,
            description=f"Admin adjustment by user {admin_user_id}: {description}",
            payment_reference=f"ADMIN-{admin_user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        
        transaction = await self.create_transaction(db, transaction_data)
        
        # Update account balance
        account.current_balance = new_balance
        if amount > 0:
            account.total_credits_added += amount
        else:
            account.total_spent += abs(amount)
        
        await db.commit()
        await db.refresh(account)
        
        return transaction
    
    # User Account Operations
    async def create_user_account(self, db: AsyncSession, account_data: UserAccountCreate) -> UserAccount:
        db_account = UserAccount(**account_data.model_dump())
        db.add(db_account)
        await db.commit()
        await db.refresh(db_account)
        
        # Add welcome bonus transaction
        welcome_bonus = Decimal('2000.0000')  # 2000 Coins welcome bonus (20 Coins)
        welcome_transaction = UserTransaction(
            user_account_id=db_account.id,
            transaction_type=TransactionType.WELCOME_BONUS,
            amount=welcome_bonus,
            balance_after=welcome_bonus,
            description="Welcome bonus - 20 Coins"
        )
        db.add(welcome_transaction)
        
        # Update account balance
        db_account.current_balance = welcome_bonus
        db_account.total_credits_added = welcome_bonus
        
        await db.commit()
        await db.refresh(db_account)
        return db_account
    
    async def get_user_account(self, db: AsyncSession, user_id: int) -> Optional[UserAccount]:
        result = await db.execute(
            select(UserAccount).where(UserAccount.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create_user_account(self, db: AsyncSession, user_id: int) -> UserAccount:
        if not user_id:
            raise ValueError("user_id cannot be None")
        
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
    
    async def create_credit_package(self, db: AsyncSession, package_data: CreditPackageCreate) -> CreditPackage:
        db_package = CreditPackage(**package_data.model_dump())
        db.add(db_package)
        await db.commit()
        await db.refresh(db_package)
        return db_package

billing_crud = BillingCRUD()