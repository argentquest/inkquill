-- Create referral tables manually
-- Run this script in your PostgreSQL database to create the missing referral tables

-- First, check if the tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name IN ('referrals', 'referral_rewards', 'referral_limits');

-- Create referrals table
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

-- Create indexes for referrals table
CREATE INDEX IF NOT EXISTS ix_referrals_referrer_user_id ON referrals(referrer_user_id);
CREATE INDEX IF NOT EXISTS ix_referrals_referred_user_id ON referrals(referred_user_id);
CREATE INDEX IF NOT EXISTS ix_referrals_anonymous_session_id ON referrals(anonymous_session_id);
CREATE INDEX IF NOT EXISTS ix_referrals_referral_code ON referrals(referral_code);
CREATE INDEX IF NOT EXISTS ix_referrals_is_converted ON referrals(is_converted);
CREATE INDEX IF NOT EXISTS ix_referrals_created_at ON referrals(created_at);

-- Create referral_rewards table
CREATE TABLE IF NOT EXISTS referral_rewards (
    id SERIAL PRIMARY KEY,
    referral_id INTEGER NOT NULL REFERENCES referrals(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    reward_type VARCHAR(50) NOT NULL,
    coin_amount INTEGER NOT NULL,
    awarded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for referral_rewards table
CREATE INDEX IF NOT EXISTS ix_referral_rewards_referral_id ON referral_rewards(referral_id);
CREATE INDEX IF NOT EXISTS ix_referral_rewards_user_id ON referral_rewards(user_id);
CREATE INDEX IF NOT EXISTS ix_referral_rewards_reward_type ON referral_rewards(reward_type);
CREATE INDEX IF NOT EXISTS ix_referral_rewards_awarded_at ON referral_rewards(awarded_at);

-- Create referral_limits table
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

-- Create indexes for referral_limits table
CREATE INDEX IF NOT EXISTS ix_referral_limits_user_id ON referral_limits(user_id);
CREATE INDEX IF NOT EXISTS ix_referral_limits_date ON referral_limits(date);

-- Add referral columns to users table if they don't exist
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS referred_by_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS referral_count INTEGER DEFAULT 0;

-- Update existing users to have referral_count = 0 if NULL
UPDATE users SET referral_count = 0 WHERE referral_count IS NULL;

-- Verify tables were created
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name IN ('referrals', 'referral_rewards', 'referral_limits')
ORDER BY table_name;