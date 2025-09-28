-- Insert story generation dropdown data
-- Character Roles
INSERT INTO prompts (title, prompt_content, reason_to_use, prompt_type, age_target, is_active) VALUES
('Protagonist', 'Protagonist', 'The main character driving the story forward, facing challenges and growing through the narrative', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Antagonist', 'Antagonist', 'The primary opposing force creating conflict for the protagonist, not necessarily evil but with opposing goals', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Mentor', 'Mentor', 'Wise guide who provides advice, training, or magical gifts to help the protagonist on their journey', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Sidekick', 'Sidekick', 'Loyal companion providing support, comic relief, or assistance to the main character', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Love Interest', 'Love Interest', 'Romantic partner or potential partner creating emotional stakes and personal growth opportunities', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Ally', 'Ally', 'Supporting character who helps the protagonist achieve their goals', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Rival', 'Rival', 'Competitive character who challenges the protagonist, not necessarily evil but pursuing similar goals', 'CHARACTER_ROLE', 'ALL_AGES', true),
('Villain', 'Villain', 'Evil or malicious character who actively works against the protagonist with harmful intent', 'CHARACTER_ROLE', 'ALL_AGES', true);

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
('Humorous', 'Humorous', 'Light-hearted and comedic approach that entertains through wit and amusing situations', 'STORY_TONE', 'ALL_AGES', true),
('Mysterious', 'Mysterious', 'Creates intrigue and suspense through hidden information and gradual revelations', 'STORY_TONE', 'ALL_AGES', true),
('Romantic', 'Romantic', 'Emphasizes love, passion, and emotional connections between characters', 'STORY_TONE', 'ALL_AGES', true),
('Epic', 'Epic', 'Grand and heroic scale with larger-than-life characters and momentous events', 'STORY_TONE', 'ALL_AGES', true),
('Melancholic', 'Melancholic', 'Bittersweet and reflective mood exploring loss, nostalgia, and emotional depth', 'STORY_TONE', 'ALL_AGES', true),
('Suspenseful', 'Suspenseful', 'Builds tension and anticipation, keeping readers engaged through uncertainty', 'STORY_TONE', 'ALL_AGES', true),
('Whimsical', 'Whimsical', 'Playful and imaginative with quirky characters and unexpected magical elements', 'STORY_TONE', 'ALL_AGES', true),
('Gritty', 'Gritty', 'Raw and realistic portrayal of harsh circumstances and moral complexity', 'STORY_TONE', 'ALL_AGES', true),
('Inspirational', 'Inspirational', 'Uplifting stories that motivate and encourage personal growth and positive change', 'STORY_TONE', 'ALL_AGES', true),
('Nostalgic', 'Nostalgic', 'Evokes fond memories and longing for the past with warm, sentimental storytelling', 'STORY_TONE', 'ALL_AGES', true);

-- Story Conflicts
INSERT INTO prompts (title, prompt_content, reason_to_use, prompt_type, age_target, is_active) VALUES
('Character vs Self', 'Character vs Self', 'Internal struggle with personal demons, moral dilemmas, or psychological challenges', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs Character', 'Character vs Character', 'Direct opposition between protagonist and antagonist with personal stakes', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs Society', 'Character vs Society', 'Individual fighting against social norms, institutions, or cultural expectations', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs Nature', 'Character vs Nature', 'Struggle against natural forces, environment, or survival situations', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs Technology', 'Character vs Technology', 'Conflict with artificial intelligence, machines, or technological systems', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs Fate', 'Character vs Fate', 'Fighting against destiny, prophecy, or seemingly inevitable outcomes', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs Supernatural', 'Character vs Supernatural', 'Battle against gods, magic, curses, or otherworldly forces', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs Time', 'Character vs Time', 'Race against deadlines, aging, or temporal constraints and paradoxes', 'STORY_CONFLICT', 'ALL_AGES', true),
('Character vs Unknown', 'Character vs Unknown', 'Facing mysterious, unexplained, or incomprehensible threats and challenges', 'STORY_CONFLICT', 'ALL_AGES', true);