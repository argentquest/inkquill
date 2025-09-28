import time
import secrets
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, Tuple
import logging
from datetime import datetime, timedelta

from app.crud.user import user_crud
from app.crud.billing import billing_crud
from app.models.user import User
from app.schemas.user import UserCreate
from app.schemas.billing import UserAccountCreate
from decimal import Decimal

logger = logging.getLogger(__name__)

class AnonymousUserService:
    
    def generate_anonymous_username(self, ip_address: str = None) -> str:
        """Generate unique anonymous username: anon_<timestamp>_<ip_hash>_<random>"""
        timestamp = int(time.time())
        random_suffix = secrets.token_hex(3)  # 6 character hex string
        
        # Create a short hash of the IP address if provided
        if ip_address:
            import hashlib
            ip_hash = hashlib.md5(ip_address.encode()).hexdigest()[:8]
            return f"anon_{timestamp}_{ip_hash}_{random_suffix}"
        else:
            return f"anon_{timestamp}_{random_suffix}"
    
    async def check_ip_abuse_limits(self, db: AsyncSession, ip_address: str) -> bool:
        """
        Check if IP address has exceeded anonymous user creation limits
        Returns True if IP is within limits, False if abusing
        """
        if not ip_address:
            return True  # Allow if no IP available
            
        # Check how many anonymous users created from this IP in last 24 hours
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        
        result = await db.execute(
            select(func.count(User.id))
            .where(
                User.username.like(f"anon_%_{ip_address[:8]}_%"),  # Match IP hash pattern
                User.created_at >= twenty_four_hours_ago
            )
        )
        recent_count = result.scalar() or 0
        
        # Allow max 3 anonymous users per IP per 24 hours in production
        # Allow more in development for testing
        from app.core.config import settings
        env_name = settings.APP_ENV.lower().strip().split('#')[0].strip()  # Handle comments in env
        if env_name == "development":
            MAX_ANON_USERS_PER_IP_24H = 30  # Much more lenient for dev
        else:
            MAX_ANON_USERS_PER_IP_24H = 3   # Strict for production
        
        if recent_count >= MAX_ANON_USERS_PER_IP_24H:
            logger.warning(f"IP {ip_address} exceeded anonymous user limit: {recent_count} in 24h (env: {settings.APP_ENV})")
            return False
            
        return True

    async def check_fingerprint_abuse_limits(self, db: AsyncSession, browser_fingerprint: str) -> bool:
        """
        Check if browser fingerprint has exceeded anonymous user creation limits
        Returns True if fingerprint is within limits, False if abusing
        """
        if not browser_fingerprint:
            return True  # Allow if no fingerprint available
            
        # Check how many anonymous users created with this fingerprint in last 24 hours
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        
        from app.models.anonymous_user_session import AnonymousUserSession
        result = await db.execute(
            select(func.count(AnonymousUserSession.id))
            .where(
                AnonymousUserSession.browser_fingerprint == browser_fingerprint,
                AnonymousUserSession.created_at >= twenty_four_hours_ago
            )
        )
        recent_count = result.scalar() or 0
        
        # Allow max 2 anonymous users per fingerprint per 24 hours in production
        # Allow more in development for testing
        from app.core.config import settings
        env_name = settings.APP_ENV.lower().strip().split('#')[0].strip()  # Handle comments in env
        if env_name == "development":
            MAX_ANON_USERS_PER_FINGERPRINT_24H = 20  # Much more lenient for dev
        else:
            MAX_ANON_USERS_PER_FINGERPRINT_24H = 2   # Strict for production
        
        if recent_count >= MAX_ANON_USERS_PER_FINGERPRINT_24H:
            logger.warning(f"Browser fingerprint {browser_fingerprint} exceeded anonymous user limit: {recent_count} in 24h (env: {settings.APP_ENV})")
            return False
            
        return True

    async def create_session_record(self, db: AsyncSession, user_id: int, session_token: str, ip_address: str = None, browser_fingerprint: str = None, user_agent: str = None):
        """Create session record for tracking anonymous user"""
        from app.models.anonymous_user_session import AnonymousUserSession
        
        session_record = AnonymousUserSession(
            user_id=user_id,
            session_token=session_token,
            ip_address=ip_address,
            browser_fingerprint=browser_fingerprint,
            user_agent=user_agent
        )
        
        db.add(session_record)
        await db.flush()
        logger.info(f"Created session record for user {user_id} with fingerprint {browser_fingerprint}")

    async def create_anonymous_user(self, db: AsyncSession, ip_address: str = None, browser_fingerprint: str = None, user_agent: str = None) -> Tuple[User, str]:
        """
        Create an anonymous user with session tracking
        Returns: (User object, session_token for tracking)
        """
        try:
            # Check IP-based abuse limits
            if not await self.check_ip_abuse_limits(db, ip_address):
                raise ValueError("IP address has exceeded anonymous user creation limits")
            
            # Check fingerprint-based abuse limits
            if not await self.check_fingerprint_abuse_limits(db, browser_fingerprint):
                raise ValueError("Browser fingerprint has exceeded anonymous user creation limits")
            
            # Generate unique anonymous username with IP if provided
            anonymous_username = self.generate_anonymous_username(ip_address)
            
            # Create anonymous user with a secure random password
            # Anonymous users can't login with password anyway
            random_password = secrets.token_urlsafe(32)
            user_data = UserCreate(
                username=anonymous_username,
                email=None,
                password=random_password,  # Random password for anonymous users
                display_name="Anonymous User"
            )
            
            # Create the user record
            anonymous_user = await user_crud.create_user(db, user_data)
            await db.flush()  # Flush to get the user ID
            await db.refresh(anonymous_user)  # Refresh to get the generated ID
            
            if not anonymous_user.id:
                raise ValueError("Failed to get user ID after creation")
                
            logger.info(f"Created anonymous user: {anonymous_username}, ID: {anonymous_user.id}")
            
            # Create billing account (this will add welcome bonus of 2000)
            billing_account_data = UserAccountCreate(
                user_id=anonymous_user.id,
                current_balance=Decimal('0.00')  # Start with 0, welcome bonus will be added
            )
            billing_account = await billing_crud.create_user_account(db, billing_account_data)
            
            # Override the welcome bonus to give anonymous users only 500 coins
            await billing_crud.update_account_balance(db, billing_account.id, Decimal('500.00'))
            logger.info(f"Created billing account for anonymous user {anonymous_user.id} with 500 starter coins (overrode welcome bonus)")
            
            # Generate session token for tracking
            session_token = secrets.token_urlsafe(32)
            
            # Create session record with fingerprint data
            await self.create_session_record(
                db, 
                anonymous_user.id, 
                session_token, 
                ip_address, 
                browser_fingerprint, 
                user_agent
            )
            
            return anonymous_user, session_token
            
        except Exception as e:
            logger.error(f"Error creating anonymous user: {e}", exc_info=True)
            await db.rollback()  # Rollback the transaction on error
            raise
    
    async def get_anonymous_user_by_session(self, db: AsyncSession, session_token: str) -> Optional[User]:
        """
        Get anonymous user by session token
        In this implementation, we'll need to store session_token somewhere
        For now, we'll use a simple approach and get by username pattern
        """
        # TODO: Consider adding session tracking table if needed
        # For MVP, we can use cookie-based tracking with user lookup
        return None
    
    async def is_anonymous_user(self, user: User) -> bool:
        """Check if a user is anonymous based on username pattern"""
        return user.username.startswith("anon_") if user.username else False
    
    async def convert_anonymous_to_registered(
        self, 
        db: AsyncSession, 
        anonymous_user: User, 
        username: str, 
        email: str, 
        password_hash: str,
        display_name: Optional[str] = None
    ) -> User:
        """
        Convert anonymous user to registered user
        Updates the existing user record to preserve transaction history
        """
        try:
            if not await self.is_anonymous_user(anonymous_user):
                raise ValueError("User is not anonymous")
            
            # Check if new username already exists
            existing_user = await user_crud.get_user_by_username(db, username)
            if existing_user and existing_user.id != anonymous_user.id:
                raise ValueError(f"Username '{username}' already exists")
            
            # Check if email already exists
            if email:
                existing_email_user = await user_crud.get_user_by_email(db, email)
                if existing_email_user and existing_email_user.id != anonymous_user.id:
                    raise ValueError(f"Email '{email}' already exists")
            
            # Update the anonymous user record
            old_username = anonymous_user.username
            anonymous_user.username = username
            anonymous_user.email = email
            anonymous_user.password_hash = password_hash
            anonymous_user.display_name = display_name or username
            
            await db.commit()
            await db.refresh(anonymous_user)
            
            logger.info(f"Converted anonymous user {old_username} to registered user {username}")
            return anonymous_user
            
        except Exception as e:
            logger.error(f"Error converting anonymous user to registered: {e}")
            await db.rollback()
            raise
    
    async def reset_weekly_coins(self, db: AsyncSession, user: User) -> None:
        """
        Reset anonymous user's coins to 5 for weekly allowance (reduced from 100, then from 25)
        Only works for anonymous users
        """
        try:
            if not await self.is_anonymous_user(user):
                logger.warning(f"Attempted to reset coins for non-anonymous user: {user.username}")
                return
            
            # Get user account
            account = await billing_crud.get_user_account(db, user.id)
            if not account:
                logger.error(f"No account found for anonymous user: {user.username}")
                return
            
            # Reset to 5 coins (reduced from 100, then from 25)
            account.current_balance = Decimal('5.0000')
            await db.commit()
            
            logger.info(f"Reset weekly coins for anonymous user: {user.username}")
            
        except Exception as e:
            logger.error(f"Error resetting weekly coins: {e}")
            await db.rollback()
            raise
    
    async def award_engagement_coins(self, db: AsyncSession, user: User, activity_type: str) -> bool:
        """
        Award small amounts of coins for user engagement
        Returns True if coins were awarded, False if already maxed out
        """
        try:
            if not await self.is_anonymous_user(user):
                return False
                
            account = await billing_crud.get_user_account(db, user.id)
            if not account:
                return False
            
            # Award different amounts based on activity (reduced for 5 coin starting balance)
            coin_awards = {
                "first_world_visit": Decimal('1.0000'),
                "first_message": Decimal('2.0000'),
                "daily_active": Decimal('0.5000'),
                "profile_completion": Decimal('3.0000')
            }
            
            award_amount = coin_awards.get(activity_type, Decimal('0.0000'))
            if award_amount == Decimal('0.0000'):
                return False
            
            # Cap total earned coins for anonymous users at 10 (reduced for 5 coin starting balance)
            MAX_ANONYMOUS_EARNINGS = Decimal('10.0000')
            if account.total_credits_added >= MAX_ANONYMOUS_EARNINGS:
                logger.info(f"Anonymous user {user.username} has reached max earnings cap")
                return False
            
            # Award the coins
            from app.models.user_transaction import UserTransaction, TransactionType
            
            new_balance = account.current_balance + award_amount
            account.current_balance = new_balance
            account.total_credits_added += award_amount
            
            # Create transaction record
            earning_transaction = UserTransaction(
                user_account_id=account.id,
                transaction_type=TransactionType.WELCOME_BONUS,
                amount=award_amount,
                balance_after=new_balance,
                description=f"Engagement reward: {activity_type}"
            )
            db.add(earning_transaction)
            
            await db.commit()
            logger.info(f"Awarded {award_amount} coins to {user.username} for {activity_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error awarding engagement coins: {e}")
            await db.rollback()
            return False

anonymous_user_service = AnonymousUserService()