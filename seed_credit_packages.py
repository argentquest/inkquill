import asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import async_session_local
from app.crud.billing import billing_crud
from app.schemas.billing import CreditPackageCreate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_credit_packages():
    """Seed initial credit packages for the MVP"""
    
    packages = [
        {
            "name": "Starter Pack",
            "description": "Perfect for trying out AI features",
            "credit_amount": Decimal("50000.00"),  # 50000 Coins
            "price_usd": Decimal("5.00"),
            "bonus_percentage": Decimal("0.00"),
            "display_order": 1,
            "is_active": True
        },
        {
            "name": "Value Pack",
            "description": "Great value for regular users",
            "credit_amount": Decimal("200000.00"),  # 200000 Coins
            "price_usd": Decimal("20.00"),
            "bonus_percentage": Decimal("0.00"),
            "display_order": 2,
            "is_active": True
        },
        {
            "name": "Pro Pack",
            "description": "For serious storytellers",
            "credit_amount": Decimal("500000.00"),  # 500000 Coins
            "price_usd": Decimal("50.00"),
            "bonus_percentage": Decimal("0.00"),
            "display_order": 3,
            "is_active": True
        },
        {
            "name": "Power User",
            "description": "Maximum value for heavy AI usage",
            "credit_amount": Decimal("1000000.00"),  # 1000000 Coins
            "price_usd": Decimal("100.00"),
            "bonus_percentage": Decimal("0.00"),
            "display_order": 4,
            "is_active": True
        }
    ]
    
    async with async_session_local() as db:
        try:
            # Check if packages already exist
            existing_packages = await billing_crud.get_active_credit_packages(db)
            if existing_packages:
                logger.info(f"Found {len(existing_packages)} existing credit packages. Skipping seed.")
                return
            
            # Create packages
            for package_data in packages:
                package = CreditPackageCreate(**package_data)
                created = await billing_crud.create_credit_package(db, package)
                logger.info(f"Created credit package: {created.name} - ${created.price_usd} for {created.credit_amount} Coins")
            
            logger.info("Successfully seeded credit packages!")
            
        except Exception as e:
            logger.error(f"Error seeding credit packages: {e}")
            raise

if __name__ == "__main__":
    asyncio.run(seed_credit_packages())