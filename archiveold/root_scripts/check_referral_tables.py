#!/usr/bin/env python3
"""
Check if referral tables exist in the database and create them if missing.
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

from app.db.database import async_session_local
from sqlalchemy import text

async def check_and_create_referral_tables():
    """Check if referral tables exist and create them if missing."""
    async with async_session_local() as db:
        print("Checking referral tables in database...")
        
        # Check if referral tables exist
        result = await db.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('referrals', 'referral_rewards', 'referral_limits');
        """))
        existing_tables = [row[0] for row in result.fetchall()]
        print(f"Existing referral tables: {existing_tables}")
        
        # Check current alembic version
        try:
            result = await db.execute(text('SELECT version_num FROM alembic_version'))
            version = result.scalar()
            print(f"Current Alembic version: {version}")
        except Exception as e:
            print(f"Error checking alembic version: {e}")
        
        # If referral tables don't exist, create them manually
        if not existing_tables:
            print("Creating referral tables manually...")
            
            # Create referrals table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS referrals (
                    id SERIAL PRIMARY KEY,
                    referrer_user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    referred_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                    anonymous_session_id VARCHAR(255),
                    referral_code VARCHAR(50) NOT NULL,
                    source_platform VARCHAR(50),
                    source_content_type VARCHAR(50),
                    source_content_id VARCHAR(255),
                    ip_address VARCHAR(45),
                    user_agent VARCHAR(500),
                    referral_url VARCHAR(1000),
                    is_converted BOOLEAN DEFAULT FALSE,
                    converted_at TIMESTAMP WITH TIME ZONE,
                    has_created_story BOOLEAN DEFAULT FALSE,
                    has_published_story BOOLEAN DEFAULT FALSE,
                    first_story_at TIMESTAMP WITH TIME ZONE,
                    first_publish_at TIMESTAMP WITH TIME ZONE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS ix_referrals_referrer_user_id ON referrals(referrer_user_id);
                CREATE INDEX IF NOT EXISTS ix_referrals_referred_user_id ON referrals(referred_user_id);
                CREATE INDEX IF NOT EXISTS ix_referrals_anonymous_session_id ON referrals(anonymous_session_id);
                CREATE INDEX IF NOT EXISTS ix_referrals_referral_code ON referrals(referral_code);
                CREATE INDEX IF NOT EXISTS ix_referrals_is_converted ON referrals(is_converted);
                CREATE INDEX IF NOT EXISTS ix_referrals_created_at ON referrals(created_at);
            """))
            
            # Create referral_rewards table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS referral_rewards (
                    id SERIAL PRIMARY KEY,
                    referral_id INTEGER NOT NULL REFERENCES referrals(id) ON DELETE CASCADE,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    reward_type VARCHAR(50) NOT NULL,
                    coin_amount INTEGER NOT NULL,
                    awarded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
                
                CREATE INDEX IF NOT EXISTS ix_referral_rewards_referral_id ON referral_rewards(referral_id);
                CREATE INDEX IF NOT EXISTS ix_referral_rewards_user_id ON referral_rewards(user_id);
                CREATE INDEX IF NOT EXISTS ix_referral_rewards_reward_type ON referral_rewards(reward_type);
                CREATE INDEX IF NOT EXISTS ix_referral_rewards_awarded_at ON referral_rewards(awarded_at);
            """))
            
            # Create referral_limits table
            await db.execute(text("""
                CREATE TABLE IF NOT EXISTS referral_limits (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    date TIMESTAMP WITH TIME ZONE NOT NULL,
                    total_coins_earned INTEGER DEFAULT 0,
                    visit_rewards_count INTEGER DEFAULT 0,
                    registration_rewards_count INTEGER DEFAULT 0,
                    story_rewards_count INTEGER DEFAULT 0,
                    publish_rewards_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    UNIQUE(user_id, date)
                );
                
                CREATE INDEX IF NOT EXISTS ix_referral_limits_user_id ON referral_limits(user_id);
                CREATE INDEX IF NOT EXISTS ix_referral_limits_date ON referral_limits(date);
            """))
            
            # Add referral columns to users table if they don't exist
            await db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS referred_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                ADD COLUMN IF NOT EXISTS referral_count INTEGER DEFAULT 0;
            """))
            
            await db.commit()
            print("✅ Referral tables created successfully!")
            
        else:
            print("✅ Referral tables already exist.")
        
        # Verify tables were created
        result = await db.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('referrals', 'referral_rewards', 'referral_limits');
        """))
        final_tables = [row[0] for row in result.fetchall()]
        print(f"Final referral tables: {final_tables}")

if __name__ == "__main__":
    asyncio.run(check_and_create_referral_tables())