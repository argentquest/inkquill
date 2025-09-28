-- Seed forum data for testing
-- Insert forum categories if they don't exist
INSERT INTO forum_categories (name, description, slug, sort_order, is_active, icon, created_at, updated_at)
VALUES 
    ('General Discussion', 'General chat and discussion topics', 'general-discussion', 1, true, 'chat', NOW(), NOW()),
    ('World Building', 'Discuss world building techniques and share worlds', 'world-building', 2, true, 'world', NOW(), NOW()),
    ('Story Writing', 'Share stories, get feedback, and discuss writing', 'story-writing', 3, true, 'book', NOW(), NOW()),
    ('Feature Requests', 'Suggest new features and improvements', 'feature-requests', 4, true, 'lightbulb', NOW(), NOW()),
    ('Technical Support', 'Get help with technical issues', 'technical-support', 5, true, 'help', NOW(), NOW())
ON CONFLICT (name) DO NOTHING;

-- Get the admin user ID (assuming username 'admin' exists)
WITH admin_user AS (
    SELECT id FROM users WHERE username = 'admin' LIMIT 1
),
general_category AS (
    SELECT id FROM forum_categories WHERE slug = 'general-discussion' LIMIT 1
),
worldbuilding_category AS (
    SELECT id FROM forum_categories WHERE slug = 'world-building' LIMIT 1
),
writing_category AS (
    SELECT id FROM forum_categories WHERE slug = 'story-writing' LIMIT 1
)

-- Insert forum threads if they don't exist
INSERT INTO forum_threads (title, slug, status, category_id, user_id, view_count, post_count, is_pinned, is_locked, is_deleted, created_at, updated_at)
SELECT 
    'Welcome to the Community!', 'welcome-to-the-community', 'OPEN'::thread_status_enum, 
    general_category.id, admin_user.id, 0, 1, true, false, false, NOW(), NOW()
FROM admin_user, general_category
WHERE NOT EXISTS (SELECT 1 FROM forum_threads WHERE slug = 'welcome-to-the-community')

UNION ALL

SELECT 
    'Tips for Creating Compelling Characters', 'tips-for-creating-compelling-characters', 'OPEN'::thread_status_enum,
    worldbuilding_category.id, admin_user.id, 0, 1, false, false, false, NOW(), NOW()
FROM admin_user, worldbuilding_category
WHERE NOT EXISTS (SELECT 1 FROM forum_threads WHERE slug = 'tips-for-creating-compelling-characters')

UNION ALL

SELECT 
    'Share Your Latest Story', 'share-your-latest-story', 'OPEN'::thread_status_enum,
    writing_category.id, admin_user.id, 0, 1, false, false, false, NOW(), NOW()
FROM admin_user, writing_category
WHERE NOT EXISTS (SELECT 1 FROM forum_threads WHERE slug = 'share-your-latest-story');

-- Insert forum posts if they don't exist
WITH admin_user AS (
    SELECT id FROM users WHERE username = 'admin' LIMIT 1
),
welcome_thread AS (
    SELECT id FROM forum_threads WHERE slug = 'welcome-to-the-community' LIMIT 1
),
characters_thread AS (
    SELECT id FROM forum_threads WHERE slug = 'tips-for-creating-compelling-characters' LIMIT 1
),
stories_thread AS (
    SELECT id FROM forum_threads WHERE slug = 'share-your-latest-story' LIMIT 1
)

INSERT INTO forum_posts (content, thread_id, user_id, is_deleted, created_at, updated_at)
SELECT 
    'Welcome to our AI Storytelling Community! This is a place where writers, world-builders, and creative minds come together to share ideas, get feedback, and explore the possibilities of AI-assisted storytelling. Feel free to introduce yourself and let us know what brings you here!',
    welcome_thread.id, admin_user.id, false, NOW(), NOW()
FROM admin_user, welcome_thread
WHERE NOT EXISTS (
    SELECT 1 FROM forum_posts fp 
    JOIN forum_threads ft ON fp.thread_id = ft.id 
    WHERE ft.slug = 'welcome-to-the-community'
)

UNION ALL

SELECT 
    'Creating compelling characters is one of the most important aspects of storytelling. Here are some tips I''ve learned over the years:

1. Give your characters clear motivations and goals
2. Create internal conflicts that drive their actions
3. Develop unique voices and speech patterns
4. Build backstories that inform their present behavior

What techniques do you use to develop your characters?',
    characters_thread.id, admin_user.id, false, NOW(), NOW()
FROM admin_user, characters_thread
WHERE NOT EXISTS (
    SELECT 1 FROM forum_posts fp 
    JOIN forum_threads ft ON fp.thread_id = ft.id 
    WHERE ft.slug = 'tips-for-creating-compelling-characters'
)

UNION ALL

SELECT 
    'I''d love to see what stories everyone is working on! Whether it''s a short piece, a novel, or just an idea you''re developing, share it here. We''re all here to support each other and provide constructive feedback.

I''ll start: I''m currently working on a science fiction story about a colony ship that discovers something unexpected in deep space. Still figuring out the details, but I''m excited about the concept!',
    stories_thread.id, admin_user.id, false, NOW(), NOW()
FROM admin_user, stories_thread
WHERE NOT EXISTS (
    SELECT 1 FROM forum_posts fp 
    JOIN forum_threads ft ON fp.thread_id = ft.id 
    WHERE ft.slug = 'share-your-latest-story'
);

-- Update thread metadata
UPDATE forum_threads SET 
    post_count = (
        SELECT COUNT(*) 
        FROM forum_posts 
        WHERE thread_id = forum_threads.id AND is_deleted = false
    ),
    last_post_at = (
        SELECT MAX(created_at) 
        FROM forum_posts 
        WHERE thread_id = forum_threads.id AND is_deleted = false
    ),
    last_post_by_id = (
        SELECT fp.user_id 
        FROM forum_posts fp 
        WHERE fp.thread_id = forum_threads.id AND fp.is_deleted = false
        ORDER BY fp.created_at DESC 
        LIMIT 1
    )
WHERE EXISTS (
    SELECT 1 FROM forum_posts 
    WHERE thread_id = forum_threads.id AND is_deleted = false
);

-- Display results
SELECT 'Forum seeding completed successfully!' AS message;
SELECT 'Categories created:', COUNT(*) FROM forum_categories;
SELECT 'Threads created:', COUNT(*) FROM forum_threads;
SELECT 'Posts created:', COUNT(*) FROM forum_posts;