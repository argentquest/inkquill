-- Migration to add new values to prompt_type_enum
-- This must be run BEFORE trying to insert data with the new enum values

-- PostgreSQL doesn't allow direct modification of enum types, so we need to:
-- 1. Add new values to the existing enum type

-- Add CHARACTER_ROLE to prompt_type_enum if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'CHARACTER_ROLE' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'prompt_type_enum')) THEN
        ALTER TYPE prompt_type_enum ADD VALUE 'CHARACTER_ROLE';
    END IF;
END $$;

-- Add STORY_GENRE to prompt_type_enum if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'STORY_GENRE' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'prompt_type_enum')) THEN
        ALTER TYPE prompt_type_enum ADD VALUE 'STORY_GENRE';
    END IF;
END $$;

-- Add STORY_TONE to prompt_type_enum if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'STORY_TONE' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'prompt_type_enum')) THEN
        ALTER TYPE prompt_type_enum ADD VALUE 'STORY_TONE';
    END IF;
END $$;

-- Add STORY_CONFLICT to prompt_type_enum if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_enum WHERE enumlabel = 'STORY_CONFLICT' AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'prompt_type_enum')) THEN
        ALTER TYPE prompt_type_enum ADD VALUE 'STORY_CONFLICT';
    END IF;
END $$;

-- Verify the enum values were added
SELECT enumlabel FROM pg_enum 
WHERE enumtypid = (SELECT oid FROM pg_type WHERE typname = 'prompt_type_enum')
ORDER BY enumsortorder;