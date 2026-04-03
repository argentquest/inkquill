-- Add missing CTA position enum values to PostgreSQL
-- Run each ALTER TYPE command separately if needed

-- First, check what enum values currently exist
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'ctaposition')
ORDER BY enumsortorder;

-- Add new enum values
-- NOTE: These must be run outside of a transaction block
-- If running in a tool like pgAdmin, run each ALTER TYPE separately

ALTER TYPE ctaposition ADD VALUE 'HOME_WELCOME_TOP';
ALTER TYPE ctaposition ADD VALUE 'HOME_WELCOME_BOTTOM';
ALTER TYPE ctaposition ADD VALUE 'HOME_QUICK_ACTIONS_TOP';
ALTER TYPE ctaposition ADD VALUE 'HOME_QUICK_ACTIONS_BOTTOM';
ALTER TYPE ctaposition ADD VALUE 'HOME_LOGIN_REGISTER_TOP';
ALTER TYPE ctaposition ADD VALUE 'HOME_LOGIN_REGISTER_BOTTOM';
ALTER TYPE ctaposition ADD VALUE 'HOME_BLOG_SECTION_TOP';
ALTER TYPE ctaposition ADD VALUE 'HOME_BLOG_SECTION_BOTTOM';

-- Verify the new values were added
SELECT enumlabel 
FROM pg_enum 
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'ctaposition')
ORDER BY enumsortorder;