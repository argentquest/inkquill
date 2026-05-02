-- Create CTAs for all 10 home page positions to demonstrate every placement

-- HOME_WELCOME_TOP
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
    'Welcome Section Top CTA',
    1, NOW(), NOW()
);

-- HOME_WELCOME_BOTTOM
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
    'Welcome Section Bottom CTA',
    2, NOW(), NOW()
);

-- HOME_QUICK_ACTIONS_TOP
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
    'Quick Actions Top CTA',
    3, NOW(), NOW()
);

-- HOME_QUICK_ACTIONS_BOTTOM
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
    'Quick Actions Bottom CTA',
    4, NOW(), NOW()
);

-- HOME_LOGIN_REGISTER_TOP
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
    'Login Register Top CTA',
    5, NOW(), NOW()
);

-- HOME_LOGIN_REGISTER_BOTTOM
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
    'Login Register Bottom CTA',
    6, NOW(), NOW()
);

-- HOME_BLOG_SECTION_TOP
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
    'Blog Section Top CTA',
    7, NOW(), NOW()
);

-- HOME_BLOG_SECTION_BOTTOM
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
    'Blog Section Bottom CTA',
    8, NOW(), NOW()
);

-- Add two more CTAs for HOME_SIDEBAR_TOP (multiple CTAs per position)
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Sidebar Special Offer',
    'Limited time premium access',
    '<p>Get 30 days of premium AI features completely free!</p>',
    'HOME_SIDEBAR_TOP',
    'SOLID',
    '#dc3545',
    '#FFFFFF',
    'fas fa-gift',
    'Claim Offer',
    '/ui/register',
    'fas fa-crown',
    true, true, true, true,
    'Sidebar Special Offer CTA',
    9, NOW(), NOW()
);

-- Add another CTA for HOME_SIDEBAR_BOTTOM
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, sort_order, created_at, updated_at
) VALUES (
    'Community Support',
    'Connect with fellow writers',
    '<p>Join our Discord community for real-time writing support and feedback.</p>',
    'HOME_SIDEBAR_BOTTOM',
    'GRADIENT',
    'linear-gradient(135deg, #5865f2 0%, #7289da 100%)',
    '#FFFFFF',
    'fab fa-discord',
    'Join Discord',
    '#',
    'fas fa-comments',
    true, true, true, true,
    'Community Support CTA',
    10, NOW(), NOW()
);