-- Seed data for character roles and story generation prompts
-- Run this after applying migrations to populate the prompts table

-- Character Roles
INSERT INTO prompts (title, prompt_content, reason_to_use, prompt_type, age_target, is_active) VALUES
-- Primary Roles
('Protagonist', 'Protagonist', 'The main character driving the story forward, facing challenges and growing through the narrative', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Antagonist', 'Antagonist', 'The primary opposing force creating conflict for the protagonist, not necessarily evil but with opposing goals', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Deuteragonist', 'Deuteragonist', 'The second most important character, often a close ally, rival, or complementary force to the protagonist', 'CHARACTER_ROLE', 'ALL_AGES', true),

-- Supporting Roles
('Mentor', 'Mentor', 'Wise guide who provides advice, training, or magical gifts to help the protagonist on their journey', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Sidekick', 'Sidekick', 'Loyal companion providing support, comic relief, or assistance to the main character', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Love Interest', 'Love Interest', 'Romantic partner or potential partner creating emotional stakes and personal growth opportunities', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Comic Relief', 'Comic Relief', 'Character providing humor and levity to balance serious or tense moments in the story', 'CHARACTER_ROLE', 'ALL_AGES', true),

-- Archetypal Roles
('Herald', 'Herald', 'Brings the call to adventure or important news that sets the protagonist''s journey in motion', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Threshold Guardian', 'Threshold Guardian', 'Tests the hero''s resolve and worthiness before allowing progress to the next stage of the journey', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Shapeshifter', 'Shapeshifter', 'Character whose loyalty, nature, or allegiance is uncertain, creating doubt and tension', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Shadow', 'Shadow', 'Represents the dark side, repressed aspects, or negative potential of the protagonist', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Trickster', 'Trickster', 'Catalyst for change through mischief, rule-breaking, and questioning the status quo', 'CHARACTER_ROLE', 'ALL_AGES', true),

-- Supporting Cast
('Ally', 'Ally', 'Supporting character who helps the protagonist achieve their goals', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Rival', 'Rival', 'Competitive character who challenges the protagonist, not necessarily evil but pursuing similar goals', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Minion', 'Minion', 'Subordinate of the antagonist who carries out orders and creates obstacles', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Victim', 'Victim', 'Character in need of rescue or protection, raising the stakes and urgency', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Witness', 'Witness', 'Observer who provides crucial information, testimony, or perspective on events', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Background Character', 'Background Character', 'Populates the world to make it feel lived-in without significant story impact', 'CHARACTER_ROLE', 'ALL_AGES', true);

-- Story Genres
INSERT INTO prompts (title, prompt_content, reason_to_use, prompt_type, age_target, is_active) VALUES
('Fantasy Adventure', 'Fantasy Adventure', 'Epic quests with magic, mythical creatures, and heroic journeys in imaginary worlds', 'STORY_GENRE', 'ALL_AGES', true),
('Sci-Fi Thriller', 'Sci-Fi Thriller', 'Suspenseful stories featuring advanced technology, space exploration, or dystopian futures', 'STORY_GENRE', 'ALL_AGES', true),
('Mystery Drama', 'Mystery Drama', 'Character-driven narratives centered around solving puzzles, crimes, or uncovering secrets', 'STORY_GENRE', 'ALL_AGES', true),
('Romance Comedy', 'Romance Comedy', 'Light-hearted love stories with humor, misunderstandings, and happy endings', 'STORY_GENRE', 'ALL_AGES', true),
('Horror Suspense', 'Horror Suspense', 'Frightening tales that build tension, fear, and dread through atmosphere and threats', 'STORY_GENRE', 'ALL_AGES', true),
('Historical Fiction', 'Historical Fiction', 'Stories set in authentic historical periods with period-accurate details and real events', 'STORY_GENRE', 'ALL_AGES', true),
('Urban Fantasy', 'Urban Fantasy', 'Magic and supernatural elements hidden within modern city settings', 'STORY_GENRE', 'ALL_AGES', true),
('Space Opera', 'Space Opera', 'Grand-scale adventures across galaxies with alien civilizations and cosmic conflicts', 'STORY_GENRE', 'ALL_AGES', true),
('Cyberpunk', 'Cyberpunk', 'High-tech, low-life stories exploring the intersection of humanity and technology', 'STORY_GENRE', 'ALL_AGES', true),
('Epic Fantasy', 'Epic Fantasy', 'World-spanning adventures with complex magic systems, politics, and mythology', 'STORY_GENRE', 'ALL_AGES', true),
('Psychological Thriller', 'Psychological Thriller', 'Mind-bending stories that explore perception, memory, and the human psyche', 'STORY_GENRE', 'ALL_AGES', true),
('Coming of Age', 'Coming of Age', 'Personal growth stories focusing on the transition from youth to adulthood', 'STORY_GENRE', 'ALL_AGES', true);

-- Story Tones
INSERT INTO prompts (title, prompt_content, reason_to_use, prompt_type, age_target, is_active) VALUES
('Hopeful', 'Hopeful', 'Creates an optimistic atmosphere where characters overcome challenges with positive outcomes', 'STORY_TONE', 'ALL_AGES', true),
('Dark', 'Dark', 'Establishes a serious, grim mood exploring difficult themes and moral ambiguity', 'STORY_TONE', 'ALL_AGES', true),
('Whimsical', 'Whimsical', 'Brings playful, imaginative elements with unexpected twists and magical realism', 'STORY_TONE', 'ALL_AGES', true),
('Gritty', 'Gritty', 'Raw, realistic portrayal of harsh realities and tough character choices', 'STORY_TONE', 'ALL_AGES', true),
('Humorous', 'Humorous', 'Light-hearted approach using comedy to entertain and provide relief', 'STORY_TONE', 'ALL_AGES', true),
('Melancholic', 'Melancholic', 'Thoughtful, wistful atmosphere exploring loss, nostalgia, and bittersweet emotions', 'STORY_TONE', 'ALL_AGES', true),
('Adventurous', 'Adventurous', 'Exciting, fast-paced tone emphasizing action, exploration, and discovery', 'STORY_TONE', 'ALL_AGES', true),
('Mysterious', 'Mysterious', 'Enigmatic atmosphere with secrets to uncover and questions to answer', 'STORY_TONE', 'ALL_AGES', true),
('Romantic', 'Romantic', 'Emphasizes emotional connections, passion, and matters of the heart', 'STORY_TONE', 'ALL_AGES', true),
('Epic', 'Epic', 'Grand, sweeping tone with high stakes and legendary scope', 'STORY_TONE', 'ALL_AGES', true),
('Intimate', 'Intimate', 'Personal, character-focused tone with deep emotional exploration', 'STORY_TONE', 'ALL_AGES', true),
('Satirical', 'Satirical', 'Uses irony and humor to critique society, politics, or human nature', 'STORY_TONE', 'ALL_AGES', true);

-- Story Conflict Types
INSERT INTO prompts (title, prompt_content, reason_to_use, prompt_type, age_target, is_active) VALUES
('Character vs. Self', 'Character vs. Self', 'Internal struggles with personal demons, difficult decisions, or identity crises', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs. Character', 'Character vs. Character', 'Direct opposition between individuals with conflicting goals, beliefs, or desires', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs. Society', 'Character vs. Society', 'Protagonist challenges social norms, unjust systems, or cultural expectations', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs. Nature', 'Character vs. Nature', 'Survival against natural disasters, wilderness, or environmental forces', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs. Technology', 'Character vs. Technology', 'Struggle against artificial intelligence, machines, or technological systems', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs. Supernatural', 'Character vs. Supernatural', 'Confrontation with ghosts, demons, magic, or otherworldly forces', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs. Fate', 'Character vs. Fate', 'Struggle against destiny, prophecy, or seemingly inevitable outcomes', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs. Time', 'Character vs. Time', 'Racing against deadlines, aging, or temporal paradoxes', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs. Unknown', 'Character vs. Unknown', 'Facing mysterious forces, unexplained phenomena, or the fear of the unfamiliar', 'STORY_CONFLICT', 'ALL_AGES', true);

-- Query to verify the data was inserted correctly
-- SELECT prompt_type, COUNT(*) as count FROM prompts 
-- WHERE prompt_type IN ('CHARACTER_ROLE', 'STORY_GENRE', 'STORY_TONE', 'STORY_CONFLICT')
-- GROUP BY prompt_type;