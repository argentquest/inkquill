-- Test SQL to check dropdown content for story generation
-- Run this to see what data is available for the dropdowns

-- Check if prompts table exists and has data
SELECT 'Total Prompts' as category, COUNT(*) as count 
FROM prompts;

-- Check Story Genres
SELECT 'Story Genres' as category, COUNT(*) as count 
FROM prompts 
WHERE prompt_type = 'STORY_GENRE' AND is_active = true;

-- Check Story Tones  
SELECT 'Story Tones' as category, COUNT(*) as count 
FROM prompts 
WHERE prompt_type = 'STORY_TONE' AND is_active = true;

-- Check Story Conflicts
SELECT 'Story Conflicts' as category, COUNT(*) as count 
FROM prompts 
WHERE prompt_type = 'STORY_CONFLICT' AND is_active = true;

-- Check Character Roles
SELECT 'Character Roles' as category, COUNT(*) as count 
FROM prompts 
WHERE prompt_type = 'CHARACTER_ROLE' AND is_active = true;

-- Show actual Story Genres available
SELECT 'STORY_GENRE' as type, title, reason_to_use 
FROM prompts 
WHERE prompt_type = 'STORY_GENRE' AND is_active = true 
ORDER BY title;

-- Show actual Story Tones available  
SELECT 'STORY_TONE' as type, title, reason_to_use 
FROM prompts 
WHERE prompt_type = 'STORY_TONE' AND is_active = true 
ORDER BY title;

-- Show actual Story Conflicts available
SELECT 'STORY_CONFLICT' as type, title, reason_to_use 
FROM prompts 
WHERE prompt_type = 'STORY_CONFLICT' AND is_active = true 
ORDER BY title;

-- Check if the enum values exist (this might fail if enum doesn't have these values)
SELECT DISTINCT prompt_type 
FROM prompts 
WHERE prompt_type IN ('STORY_GENRE', 'STORY_TONE', 'STORY_CONFLICT', 'CHARACTER_ROLE');