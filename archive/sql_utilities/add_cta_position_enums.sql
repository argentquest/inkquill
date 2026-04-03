-- Add missing CTA position enum values to PostgreSQL

-- First, check current enum values
SELECT unnest(enum_range(NULL::ctaposition)) AS existing_positions;

-- Add the missing enum values one by one
-- PostgreSQL requires ALTER TYPE commands to add new enum values
-- NOTE: Run each ALTER TYPE separately if in a transaction block

-- Main content area positions
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_WELCOME_TOP';
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_WELCOME_BOTTOM';
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_QUICK_ACTIONS_TOP';
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_QUICK_ACTIONS_BOTTOM';
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_LOGIN_REGISTER_TOP';
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_LOGIN_REGISTER_BOTTOM';
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_BLOG_SECTION_TOP'; 
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_BLOG_SECTION_BOTTOM';

-- Sidebar section positions for AI Chat Worlds
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_AI_CHAT_WORLDS_TOP';
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_AI_CHAT_WORLDS_BOTTOM';

-- Sidebar section positions for Recent Published Stories
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_PUBLISHED_STORIES_TOP';
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_PUBLISHED_STORIES_BOTTOM';

-- Sidebar section positions for Recent Generated Images
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_GENERATED_IMAGES_TOP';
ALTER TYPE ctaposition ADD VALUE IF NOT EXISTS 'HOME_GENERATED_IMAGES_BOTTOM';

-- Verify all enum values after adding
SELECT unnest(enum_range(NULL::ctaposition)) AS all_positions
ORDER BY all_positions;

-- Now you can run the create_all_position_ctas.sql file to create CTAs for all positions