-- Create multiple CTAs for each existing position to fill all placement spots
-- Using only the enum values that exist in the database

-- Check current CTAs
SELECT position, COUNT(*) as count 
FROM cta_contents 
WHERE is_active = true 
GROUP BY position 
ORDER BY position;

-- Create additional CTAs for HOME_MAIN_TOP (appears in multiple sections)
-- This will show in Welcome, Quick Actions, and other top sections

-- CTA for Welcome Section (using HOME_MAIN_TOP)
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Welcome Section Special',
    'Start your storytelling journey',
    '<p>Begin your creative writing adventure with AI-powered tools.</p>',
    'HOME_MAIN_TOP',
    'HERO',
    'linear-gradient(135deg, #ee7752, #e73c7e)',
    '#FFFFFF',
    'fas fa-flag-checkered',
    'Start Journey',
    '/ui/register',
    'fas fa-route',
    true, true, true, true,
    'Position Demo - Welcome Area',
    10, NOW(), NOW()
);

-- CTA for Quick Actions area (using HOME_MAIN_TOP)
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Quick Actions Special',
    'Explore our powerful tools',
    '<p>Discover AI tools for world-building, character creation, and more.</p>',
    'HOME_MAIN_TOP',
    'BORDERED',
    '#ffffff',
    '#495057',
    'fas fa-toolbox',
    'Explore Tools',
    '/ui/brainstorm',
    'fas fa-wand-magic-sparkles',
    true, true, true, true,
    'Position Demo - Quick Actions Area',
    20, NOW(), NOW()
);

-- Create additional CTAs for HOME_MAIN_BOTTOM (appears in multiple bottom sections)

-- CTA for Blog Section area (using HOME_MAIN_BOTTOM)
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Writing Blog Hub',
    'Read tips from expert writers',
    '<p>Explore articles, tutorials, and writing advice from our community.</p>',
    'HOME_MAIN_BOTTOM',
    'MINIMAL',
    '#f8f9fa',
    '#495057',
    'fas fa-newspaper',
    'Visit Blog',
    '/blog',
    'fas fa-arrow-right',
    true, true, true, true,
    'Position Demo - Blog Section',
    30, NOW(), NOW()
);

-- CTA for Login/Register area (using HOME_MAIN_BOTTOM, anonymous only)
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Join Our Community',
    'Free account with bonus credits',
    '<p>Sign up today and get 100 free AI credits to start your first story!</p>',
    'HOME_MAIN_BOTTOM',
    'GRADIENT',
    'linear-gradient(135deg, #23a6d5, #23d5ab)',
    '#FFFFFF',
    'fas fa-user-plus',
    'Create Account',
    '/ui/register',
    'fas fa-gift',
    true, false, false, true,
    'Position Demo - Registration CTA',
    40, NOW(), NOW()
);

-- Add more sidebar CTAs to demonstrate multiple CTAs per position

-- Additional HOME_SIDEBAR_TOP CTA
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Featured Tool',
    'AI Character Generator',
    '<p>Create unique characters with detailed backstories in seconds.</p>',
    'HOME_SIDEBAR_TOP',
    'SOLID',
    '#ff6b6b',
    '#FFFFFF',
    'fas fa-user-astronaut',
    'Create Character',
    '/ui/worlds',
    'fas fa-sparkles',
    true, true, true, true,
    'Position Demo - Sidebar Feature',
    15, NOW(), NOW()
);

-- Additional HOME_SIDEBAR_BOTTOM CTA
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Writing Resources',
    'Free guides and templates',
    '<p>Download our collection of writing templates and guides.</p>',
    'HOME_SIDEBAR_BOTTOM',
    'HERO',
    'linear-gradient(135deg, #4facfe, #00f2fe)',
    '#FFFFFF',
    'fas fa-download',
    'Get Resources',
    '/ui/user-guide',
    'fas fa-file-download',
    true, true, true, true,
    'Position Demo - Sidebar Resources',
    25, NOW(), NOW()
);

-- After running, verify the distribution
SELECT position, COUNT(*) as count, STRING_AGG(title, ', ' ORDER BY sort_order) as titles
FROM cta_contents 
WHERE is_active = true 
GROUP BY position 
ORDER BY position;