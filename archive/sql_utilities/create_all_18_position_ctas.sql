-- Complete SQL to create CTAs for ALL 18 home page positions
-- Run this after adding the enum values with add_cta_position_enums.sql

-- First, delete all existing CTAs if you want a clean slate
-- DELETE FROM cta_contents;

-- Check what positions we'll be creating
SELECT 'Creating CTAs for 18 positions:' as info;

-- MAIN CONTENT POSITIONS (10 positions)

-- 1. HOME_MAIN_TOP
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '1. Main Top Hero',
    'Premium storytelling starts here',
    '<p>This appears at the very top of the main content area - prime real estate!</p>',
    'HOME_MAIN_TOP',
    'GRADIENT',
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    '#FFFFFF',
    'fas fa-star',
    'Start Free',
    '/ui/register',
    'fas fa-rocket',
    true, true, true, true,
    'Position 1 - HOME_MAIN_TOP',
    1, NOW(), NOW()
);

-- 2. HOME_WELCOME_TOP
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '2. Welcome Top',
    'Before the progress steps',
    '<p>This CTA appears above the welcome header and progress tracker.</p>',
    'HOME_WELCOME_TOP',
    'SOLID',
    '#3b82f6',
    '#FFFFFF',
    'fas fa-flag-checkered',
    'Begin Journey',
    '/ui/user-guide',
    'fas fa-play',
    true, true, true, true,
    'Position 2 - HOME_WELCOME_TOP',
    2, NOW(), NOW()
);

-- 3. HOME_WELCOME_BOTTOM
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '3. Welcome Bottom',
    'After the progress steps',
    '<p>This appears below the 3-step progress indicator.</p>',
    'HOME_WELCOME_BOTTOM',
    'HERO',
    'linear-gradient(135deg, #10b981 0%, #059669 100%)',
    '#FFFFFF',
    'fas fa-check-circle',
    'Next Steps',
    '/ui/brainstorm',
    'fas fa-arrow-right',
    true, true, true, true,
    'Position 3 - HOME_WELCOME_BOTTOM',
    3, NOW(), NOW()
);

-- 4. HOME_QUICK_ACTIONS_TOP
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '4. Quick Actions Top',
    'Above the action buttons',
    '<p>This displays before the Quick Actions grid.</p>',
    'HOME_QUICK_ACTIONS_TOP',
    'BORDERED',
    '#ffffff',
    '#1e293b',
    'fas fa-bolt',
    'Power Tools',
    '/ui/worlds',
    'fas fa-toolbox',
    true, true, true, true,
    'Position 4 - HOME_QUICK_ACTIONS_TOP',
    4, NOW(), NOW()
);

-- 5. HOME_QUICK_ACTIONS_BOTTOM
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '5. Quick Actions Bottom',
    'After the action buttons',
    '<p>This appears below the Quick Actions grid.</p>',
    'HOME_QUICK_ACTIONS_BOTTOM',
    'MINIMAL',
    '#f8f9fa',
    '#495057',
    'fas fa-compass',
    'Explore More',
    '/ui/stories',
    'fas fa-search',
    true, true, true, true,
    'Position 5 - HOME_QUICK_ACTIONS_BOTTOM',
    5, NOW(), NOW()
);

-- 6. HOME_LOGIN_REGISTER_TOP (Anonymous only)
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '6. Login/Register Top',
    'Join our community',
    '<p>This shows above login/register cards for anonymous users only.</p>',
    'HOME_LOGIN_REGISTER_TOP',
    'GRADIENT',
    'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
    '#FFFFFF',
    'fas fa-users',
    'Join Now',
    '/ui/register',
    'fas fa-user-plus',
    true, false, false, true,
    'Position 6 - HOME_LOGIN_REGISTER_TOP',
    6, NOW(), NOW()
);

-- 7. HOME_LOGIN_REGISTER_BOTTOM (Anonymous only)
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '7. Login/Register Bottom',
    'Need help getting started?',
    '<p>This shows below login/register cards for anonymous users only.</p>',
    'HOME_LOGIN_REGISTER_BOTTOM',
    'SOLID',
    '#6c757d',
    '#FFFFFF',
    'fas fa-question-circle',
    'View Guide',
    '/ui/user-guide',
    'fas fa-book-open',
    true, false, false, true,
    'Position 7 - HOME_LOGIN_REGISTER_BOTTOM',
    7, NOW(), NOW()
);

-- 8. HOME_BLOG_SECTION_TOP
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '8. Blog Section Top',
    'Latest writing insights',
    '<p>This appears above the blog posts section.</p>',
    'HOME_BLOG_SECTION_TOP',
    'HERO',
    'linear-gradient(135deg, #ec4899 0%, #8b5cf6 100%)',
    '#FFFFFF',
    'fas fa-newspaper',
    'Read Blog',
    '/blog',
    'fas fa-arrow-right',
    true, true, true, true,
    'Position 8 - HOME_BLOG_SECTION_TOP',
    8, NOW(), NOW()
);

-- 9. HOME_BLOG_SECTION_BOTTOM
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '9. Blog Section Bottom',
    'Share your expertise',
    '<p>This appears below the blog posts section.</p>',
    'HOME_BLOG_SECTION_BOTTOM',
    'BORDERED',
    '#ffffff',
    '#1e293b',
    'fas fa-pen',
    'Write Article',
    '/blog/editor',
    'fas fa-edit',
    true, true, true, true,
    'Position 9 - HOME_BLOG_SECTION_BOTTOM',
    9, NOW(), NOW()
);

-- 10. HOME_MAIN_BOTTOM
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '10. Main Content Bottom',
    'Final call to action',
    '<p>This is the last CTA in the main content column.</p>',
    'HOME_MAIN_BOTTOM',
    'GRADIENT',
    'linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%)',
    '#FFFFFF',
    'fas fa-rocket',
    'Get Started',
    '/ui/register',
    'fas fa-arrow-up',
    true, true, true, true,
    'Position 10 - HOME_MAIN_BOTTOM',
    10, NOW(), NOW()
);

-- SIDEBAR POSITIONS (8 positions)

-- 11. HOME_SIDEBAR_TOP
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '11. Sidebar Top',
    'Featured tool of the week',
    '<p>This appears at the very top of the sidebar.</p>',
    'HOME_SIDEBAR_TOP',
    'SOLID',
    '#dc2626',
    '#FFFFFF',
    'fas fa-fire',
    'Try Now',
    '/ui/brainstorm',
    'fas fa-star',
    true, true, true, true,
    'Position 11 - HOME_SIDEBAR_TOP',
    11, NOW(), NOW()
);

-- 12. HOME_AI_CHAT_WORLDS_TOP
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '12. AI Chat Worlds Top',
    'Explore interactive worlds',
    '<p>This appears above the AI Chat Worlds section.</p>',
    'HOME_AI_CHAT_WORLDS_TOP',
    'MINIMAL',
    '#fef3c7',
    '#78350f',
    'fas fa-globe',
    'Browse Worlds',
    '/ui/public-worlds',
    'fas fa-compass',
    true, true, true, true,
    'Position 12 - HOME_AI_CHAT_WORLDS_TOP',
    12, NOW(), NOW()
);

-- 13. HOME_AI_CHAT_WORLDS_BOTTOM
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '13. AI Chat Worlds Bottom',
    'Create your own world',
    '<p>This appears below the AI Chat Worlds section.</p>',
    'HOME_AI_CHAT_WORLDS_BOTTOM',
    'BORDERED',
    '#ffffff',
    '#059669',
    'fas fa-plus-circle',
    'Build World',
    '/ui/world-builder-wizard',
    'fas fa-hammer',
    true, true, true, true,
    'Position 13 - HOME_AI_CHAT_WORLDS_BOTTOM',
    13, NOW(), NOW()
);

-- 14. HOME_PUBLISHED_STORIES_TOP
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '14. Published Stories Top',
    'Discover amazing stories',
    '<p>This appears above the Published Stories section.</p>',
    'HOME_PUBLISHED_STORIES_TOP',
    'GRADIENT',
    'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
    '#FFFFFF',
    'fas fa-book',
    'Browse Stories',
    '/ui/stories',
    'fas fa-book-open',
    true, true, true, true,
    'Position 14 - HOME_PUBLISHED_STORIES_TOP',
    14, NOW(), NOW()
);

-- 15. HOME_PUBLISHED_STORIES_BOTTOM
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '15. Published Stories Bottom',
    'Share your story',
    '<p>This appears below the Published Stories section.</p>',
    'HOME_PUBLISHED_STORIES_BOTTOM',
    'SOLID',
    '#4c1d95',
    '#FFFFFF',
    'fas fa-upload',
    'Publish Story',
    '/ui/my-stories',
    'fas fa-share',
    true, true, true, true,
    'Position 15 - HOME_PUBLISHED_STORIES_BOTTOM',
    15, NOW(), NOW()
);

-- 16. HOME_GENERATED_IMAGES_TOP
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '16. Generated Images Top',
    'AI-powered artwork',
    '<p>This appears above the Generated Images section.</p>',
    'HOME_GENERATED_IMAGES_TOP',
    'HERO',
    'linear-gradient(135deg, #f97316 0%, #ea580c 100%)',
    '#FFFFFF',
    'fas fa-palette',
    'Create Art',
    '/ui/worlds',
    'fas fa-paint-brush',
    true, true, true, true,
    'Position 16 - HOME_GENERATED_IMAGES_TOP',
    16, NOW(), NOW()
);

-- 17. HOME_GENERATED_IMAGES_BOTTOM
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '17. Generated Images Bottom',
    'Generate your own images',
    '<p>This appears below the Generated Images section.</p>',
    'HOME_GENERATED_IMAGES_BOTTOM',
    'MINIMAL',
    '#fef3c7',
    '#92400e',
    'fas fa-images',
    'Start Creating',
    '/ui/worlds',
    'fas fa-magic',
    true, true, true, true,
    'Position 17 - HOME_GENERATED_IMAGES_BOTTOM',
    17, NOW(), NOW()
);

-- 18. HOME_SIDEBAR_BOTTOM
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    '18. Sidebar Bottom',
    'Stay connected',
    '<p>This is the final CTA at the bottom of the sidebar.</p>',
    'HOME_SIDEBAR_BOTTOM',
    'GRADIENT',
    'linear-gradient(135deg, #0891b2 0%, #0e7490 100%)',
    '#FFFFFF',
    'fas fa-envelope',
    'Subscribe',
    '/ui/register',
    'fas fa-bell',
    true, true, true, true,
    'Position 18 - HOME_SIDEBAR_BOTTOM',
    18, NOW(), NOW()
);

-- Verify all 18 positions were created
SELECT 
    position,
    COUNT(*) as count,
    STRING_AGG(title, ', ' ORDER BY sort_order) as cta_titles
FROM cta_contents 
WHERE campaign_name LIKE 'Position %'
GROUP BY position
ORDER BY MIN(sort_order);

-- Summary of all positions
SELECT 
    'Total Positions' as metric,
    COUNT(DISTINCT position) as value
FROM cta_contents
WHERE campaign_name LIKE 'Position %';

SELECT 
    'Total CTAs Created' as metric,
    COUNT(*) as value
FROM cta_contents
WHERE campaign_name LIKE 'Position %';