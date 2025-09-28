-- SQL insert statements for new QUICK_AI prompts
-- These prompts complement the existing 9 QUICK_AI prompts with additional text transformation options

INSERT INTO prompts (prompt_type, title, prompt_content, reason_to_use, is_active, age_target, created_at, updated_at) VALUES

('QUICK_AI', 'Convert to Active Voice', 'Transform any passive voice constructions in this text to active voice. Make the writing more direct and engaging while preserving the original meaning and tone.', 'Transforms passive voice to active voice for more dynamic writing', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Add Sensory Details', 'Enhance this text by adding vivid sensory details (sight, sound, smell, taste, touch) to make the scene more immersive and engaging for readers.', 'Enriches text with sensory descriptions for better reader engagement', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Create Chapter Summary', 'Create a concise 2-3 sentence summary of this text that captures the main events, character developments, or key points.', 'Generates helpful summaries for chapters or sections', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Improve Flow and Transitions', 'Improve the flow between sentences and paragraphs in this text by adding better transitions and connecting phrases. Make the text read more smoothly.', 'Enhances readability by improving sentence and paragraph flow', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Convert to First Person', 'Rewrite this text from a first-person perspective, changing pronouns and adjusting the narrative voice while maintaining the story content.', 'Changes narrative perspective to first person for different storytelling effects', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Convert to Third Person', 'Rewrite this text from a third-person perspective, changing pronouns and adjusting the narrative voice while maintaining the story content.', 'Changes narrative perspective to third person for different storytelling effects', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Add Foreshadowing', 'Subtly add hints or foreshadowing elements to this text that suggest future events or developments in the story without being too obvious.', 'Adds literary depth by incorporating subtle hints about future events', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Improve Pacing', 'Adjust the pacing of this text - speed up slow sections and slow down rushed parts to create better narrative rhythm and reader engagement.', 'Optimizes narrative pacing for better reader experience', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Add Tension and Conflict', 'Increase the dramatic tension in this text by adding or emphasizing conflict, stakes, or uncertainty to make it more engaging.', 'Enhances dramatic tension to create more compelling narratives', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Create Hook or Cliffhanger', 'Transform the ending of this text into a compelling hook or cliffhanger that will make readers want to continue to the next section.', 'Creates compelling endings that encourage continued reading', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Strengthen Character Voice', 'Enhance the character voice in this text to make it more distinctive, consistent, and true to the character''s personality and background.', 'Improves character consistency and distinctiveness in dialogue and narration', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Add Subtext', 'Add subtle subtext to dialogue and interactions in this text - what characters really mean beneath what they''re saying on the surface.', 'Creates deeper, more sophisticated dialogue with hidden meanings', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Modernize Language', 'Update outdated or archaic language in this text to make it more accessible to modern readers while preserving the intended tone and meaning.', 'Makes older or formal text more accessible to contemporary readers', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Add Paragraph Breaks', 'Improve the readability of this text by adding appropriate paragraph breaks and reformatting for better visual flow and reading experience.', 'Improves text formatting and visual readability', true, 'ALL_AGES', NOW(), NOW()),

('QUICK_AI', 'Remove Redundancy', 'Eliminate repetitive phrases, redundant information, and unnecessary words from this text while preserving all essential meaning and impact.', 'Streamlines text by removing unnecessary repetition and wordiness', true, 'ALL_AGES', NOW(), NOW());