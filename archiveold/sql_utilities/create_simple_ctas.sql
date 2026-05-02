-- Create simple demo CTAs without Unicode characters

-- CTA 1: HOME_MAIN_TOP
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    'Welcome to AI Storytelling!',
    'Transform your creative ideas into captivating stories',
    '<p>Join thousands of writers using AI to bring their stories to life.</p>',
    'HOME_MAIN_TOP',
    'GRADIENT',
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    '#FFFFFF',
    'fas fa-rocket',
    'Start Writing Today',
    '/ui/register',
    'fas fa-pen-nib',
    true, true, true, true,
    'Demo CTA 1 - Hero Welcome',
    'homepage', 'cta', 'demo_hero_welcome',
    1, NOW(), NOW()
);

-- CTA 2: HOME_MAIN_BOTTOM
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    'Join Our Writing Community',
    'Connect with fellow storytellers worldwide',
    '<p>Share your work, get feedback, and discover amazing stories.</p>',
    'HOME_MAIN_BOTTOM',
    'GRADIENT',
    'linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)',
    '#FFFFFF',
    'fas fa-users',
    'Explore Stories',
    '/ui/stories',
    'fas fa-book-open',
    true, true, true, true,
    'Demo CTA 2 - Community',
    'homepage', 'cta', 'demo_community',
    2, NOW(), NOW()
);

-- CTA 3: HOME_SIDEBAR_TOP
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    'AI World Builder',
    'Create immersive fictional universes',
    '<p>Build detailed fantasy and sci-fi worlds with AI assistance.</p>',
    'HOME_SIDEBAR_TOP',
    'SOLID',
    '#17a2b8',
    '#FFFFFF',
    'fas fa-globe-americas',
    'Try World Builder',
    '/ui/worlds',
    'fas fa-hammer',
    true, true, true, true,
    'Demo CTA 3 - World Builder',
    'homepage', 'sidebar_cta', 'demo_world_builder',
    3, NOW(), NOW()
);

-- CTA 4: HOME_SIDEBAR_BOTTOM
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    'Newsletter Signup',
    'Get weekly writing tips and platform updates',
    '<p>Join our newsletter for exclusive writing prompts and AI tips.</p>',
    'HOME_SIDEBAR_BOTTOM',
    'BORDERED',
    '#ffffff',
    '#495057',
    'fas fa-envelope',
    'Subscribe Now',
    '/ui/register',
    'fas fa-bell',
    true, true, true, true,
    'Demo CTA 4 - Newsletter',
    'homepage', 'sidebar_cta', 'demo_newsletter',
    4, NOW(), NOW()
);