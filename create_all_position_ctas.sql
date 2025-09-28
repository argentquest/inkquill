-- SQL to create CTAs for all home page positions
-- This will demonstrate every CTA placement opportunity

-- First, let's check what positions we already have
SELECT position, COUNT(*) as count 
FROM cta_contents 
WHERE is_active = true 
GROUP BY position 
ORDER BY position;

-- Now create CTAs for the missing positions

-- 1. HOME_WELCOME_TOP - Top of welcome section
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Welcome Section Top',
    'Start your storytelling journey here',
    '<p>This CTA appears at the top of the welcome section with progress steps.</p>',
    'HOME_WELCOME_TOP',
    'GRADIENT',
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    '#FFFFFF',
    'fas fa-flag',
    'Get Started',
    '/ui/register',
    'fas fa-rocket',
    true, true, true, true,
    'Position Demo - Welcome Top',
    1, NOW(), NOW()
);

-- 2. HOME_WELCOME_BOTTOM - Bottom of welcome section
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Welcome Section Bottom',
    'Ready to dive deeper?',
    '<p>This CTA appears at the bottom of the welcome section after progress steps.</p>',
    'HOME_WELCOME_BOTTOM',
    'SOLID',
    '#28a745',
    '#FFFFFF',
    'fas fa-arrow-down',
    'Continue Reading',
    '/ui/user-guide',
    'fas fa-book',
    true, true, true, true,
    'Position Demo - Welcome Bottom',
    2, NOW(), NOW()
);

-- 3. HOME_QUICK_ACTIONS_TOP - Before quick action buttons
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Quick Actions Top',
    'Before you explore the tools',
    '<p>This CTA appears above the quick action buttons section.</p>',
    'HOME_QUICK_ACTIONS_TOP',
    'HERO',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    '#FFFFFF',
    'fas fa-bolt',
    'Power Up',
    '/ui/brainstorm',
    'fas fa-magic',
    true, true, true, true,
    'Position Demo - Quick Actions Top',
    3, NOW(), NOW()
);

-- 4. HOME_QUICK_ACTIONS_BOTTOM - After quick action buttons
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Quick Actions Bottom',
    'Found the perfect tool?',
    '<p>This CTA appears below the quick action buttons section.</p>',
    'HOME_QUICK_ACTIONS_BOTTOM',
    'BORDERED',
    '#ffffff',
    '#495057',
    'fas fa-check-circle',
    'Start Creating',
    '/ui/worlds',
    'fas fa-plus',
    true, true, true, true,
    'Position Demo - Quick Actions Bottom',
    4, NOW(), NOW()
);

-- 5. HOME_LOGIN_REGISTER_TOP - For anonymous users only
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Login Register Top',
    'Join thousands of writers',
    '<p>This CTA appears above the login/register section for anonymous users.</p>',
    'HOME_LOGIN_REGISTER_TOP',
    'MINIMAL',
    '#f8f9fa',
    '#495057',
    'fas fa-users',
    'Join Community',
    '/ui/register',
    'fas fa-user-plus',
    true, false, false, true,
    'Position Demo - Login Top',
    5, NOW(), NOW()
);

-- 6. HOME_LOGIN_REGISTER_BOTTOM - For anonymous users only
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Login Register Bottom',
    'Still have questions?',
    '<p>This CTA appears below the login/register section for anonymous users.</p>',
    'HOME_LOGIN_REGISTER_BOTTOM',
    'SOLID',
    '#6c757d',
    '#FFFFFF',
    'fas fa-question-circle',
    'Get Help',
    '/ui/user-guide',
    'fas fa-headset',
    true, false, false, true,
    'Position Demo - Login Bottom',
    6, NOW(), NOW()
);

-- 7. HOME_BLOG_SECTION_TOP - Above blog posts
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Blog Section Top',
    'Explore our latest insights',
    '<p>This CTA appears above the blog posts section.</p>',
    'HOME_BLOG_SECTION_TOP',
    'GRADIENT',
    'linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)',
    '#FFFFFF',
    'fas fa-newspaper',
    'Read Blog',
    '/blog',
    'fas fa-external-link-alt',
    true, true, true, true,
    'Position Demo - Blog Top',
    7, NOW(), NOW()
);

-- 8. HOME_BLOG_SECTION_BOTTOM - Below blog posts
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Blog Section Bottom',
    'Want to contribute?',
    '<p>This CTA appears below the blog posts section.</p>',
    'HOME_BLOG_SECTION_BOTTOM',
    'HERO',
    'linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%)',
    '#FFFFFF',
    'fas fa-pen',
    'Write Article',
    '/blog/editor',
    'fas fa-edit',
    true, true, true, true,
    'Position Demo - Blog Bottom',
    8, NOW(), NOW()
);

-- After running the inserts, verify all positions are filled:
SELECT position, COUNT(*) as count 
FROM cta_contents 
WHERE is_active = true 
GROUP BY position 
ORDER BY position;

-- Check all CTAs with their positions:
SELECT id, title, position, style, is_active 
FROM cta_contents 
WHERE is_active = true
ORDER BY position, sort_order;