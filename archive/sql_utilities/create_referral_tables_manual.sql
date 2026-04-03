-- Manual creation of referral system tables
-- Based on migration 7cb2cea8948c_add_referral_tracking_system_tables.py

BEGIN;

-- Add referral columns to users table if they don't exist
DO $$ 
BEGIN
    -- Add referred_by_user_id column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'referred_by_user_id') THEN
        ALTER TABLE users ADD COLUMN referred_by_user_id INTEGER;
    END IF;
    
    -- Add referral_count column
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'users' AND column_name = 'referral_count') THEN
        ALTER TABLE users ADD COLUMN referral_count INTEGER DEFAULT 0;
    END IF;
END $$;

-- Update existing users to have referral_count = 0 where NULL
UPDATE users SET referral_count = 0 WHERE referral_count IS NULL;

-- Make referral_count NOT NULL
ALTER TABLE users ALTER COLUMN referral_count SET NOT NULL;

-- Add foreign key constraint for referred_by_user_id if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.table_constraints 
                   WHERE constraint_name = 'users_referred_by_user_id_fkey' 
                   AND table_name = 'users') THEN
        ALTER TABLE users ADD CONSTRAINT users_referred_by_user_id_fkey 
        FOREIGN KEY (referred_by_user_id) REFERENCES users (id) ON DELETE SET NULL;
    END IF;
END $$;

-- Create referrals table if it doesn't exist
CREATE TABLE IF NOT EXISTS referrals (
    id SERIAL PRIMARY KEY,
    referrer_user_id INTEGER NOT NULL,
    referred_user_id INTEGER,
    anonymous_session_id VARCHAR(255),
    source_platform VARCHAR(50),
    source_content_type VARCHAR(50),
    source_content_id VARCHAR(100),
    referral_url TEXT,
    ip_address VARCHAR(45),
    user_agent TEXT,
    is_converted BOOLEAN NOT NULL DEFAULT false,
    converted_at TIMESTAMP WITH TIME ZONE,
    has_created_story BOOLEAN NOT NULL DEFAULT false,
    has_published_story BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    
    CONSTRAINT referrals_referrer_user_id_fkey 
        FOREIGN KEY (referrer_user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT referrals_referred_user_id_fkey 
        FOREIGN KEY (referred_user_id) REFERENCES users (id) ON DELETE CASCADE
);

-- Create indexes for referrals table if they don't exist
CREATE INDEX IF NOT EXISTS ix_referrals_referrer_user_id ON referrals (referrer_user_id);
CREATE INDEX IF NOT EXISTS ix_referrals_referred_user_id ON referrals (referred_user_id);
CREATE INDEX IF NOT EXISTS ix_referrals_anonymous_session_id ON referrals (anonymous_session_id);

-- Create referral_rewards table if it doesn't exist
CREATE TABLE IF NOT EXISTS referral_rewards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    referral_id INTEGER NOT NULL,
    reward_type VARCHAR(50) NOT NULL,
    coin_amount INTEGER NOT NULL,
    awarded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    
    CONSTRAINT referral_rewards_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT referral_rewards_referral_id_fkey 
        FOREIGN KEY (referral_id) REFERENCES referrals (id) ON DELETE CASCADE
);

-- Create indexes for referral_rewards table if they don't exist
CREATE INDEX IF NOT EXISTS ix_referral_rewards_user_id ON referral_rewards (user_id);
CREATE INDEX IF NOT EXISTS ix_referral_rewards_referral_id ON referral_rewards (referral_id);

-- Create referral_limits table if it doesn't exist
CREATE TABLE IF NOT EXISTS referral_limits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    total_coins_earned INTEGER NOT NULL DEFAULT 0,
    visit_rewards_count INTEGER NOT NULL DEFAULT 0,
    registration_rewards_count INTEGER NOT NULL DEFAULT 0,
    story_rewards_count INTEGER NOT NULL DEFAULT 0,
    publish_rewards_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    
    CONSTRAINT referral_limits_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
    CONSTRAINT uq_referral_limits_user_date UNIQUE (user_id, date)
);

-- Create indexes for referral_limits table if they don't exist
CREATE INDEX IF NOT EXISTS ix_referral_limits_user_id ON referral_limits (user_id);
CREATE INDEX IF NOT EXISTS ix_referral_limits_date ON referral_limits (date);

COMMIT;

-- Verify the tables were created
SELECT 'referrals' as table_name, count(*) as row_count FROM referrals
UNION ALL
SELECT 'referral_rewards' as table_name, count(*) as row_count FROM referral_rewards
UNION ALL
SELECT 'referral_limits' as table_name, count(*) as row_count FROM referral_limits;