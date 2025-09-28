-- Add RUNPOD to the ai_provider_enum type
ALTER TYPE ai_provider_enum ADD VALUE IF NOT EXISTS 'RUNPOD';

-- Verify the enum was added
SELECT enumlabel FROM pg_enum WHERE enumtypid = (
    SELECT oid FROM pg_type WHERE typname = 'ai_provider_enum'
);