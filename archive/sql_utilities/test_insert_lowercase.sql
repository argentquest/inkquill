-- Test insert with lowercase enum values
INSERT INTO prompts (title, prompt_content, reason_to_use, prompt_type, age_target, is_active) VALUES
-- Test with lowercase
('Test Genre', 'Test Genre', 'Test description', 'story_genre', 'ALL_AGES', true),
('Test Tone', 'Test Tone', 'Test description', 'story_tone', 'ALL_AGES', true),
('Test Conflict', 'Test Conflict', 'Test description', 'story_conflict', 'ALL_AGES', true);

-- Check if it worked
SELECT prompt_type, title FROM prompts WHERE title LIKE 'Test%';