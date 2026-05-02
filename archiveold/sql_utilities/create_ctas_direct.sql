-- SQL script to create 11 demo CTAs for all home page positions
-- This directly inserts into the database using existing enum values

-- Clear existing demo CTAs first (optional)
-- DELETE FROM cta_contents WHERE campaign_name LIKE 'Demo CTA%';

-- CTA 1: HOME_MAIN_TOP - Hero Welcome CTA
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class, 
    features, primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    '🎯 Welcome to AI Storytelling!',
    'Transform your creative ideas into captivating stories',
    '<p>Join thousands of writers using AI to bring their stories to life. Create rich worlds, compelling characters, and publish your masterpiece.</p>',
    'HOME_MAIN_TOP',
    'GRADIENT',
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    '#FFFFFF',
    'fas fa-rocket',
    '[{"icon": "fas fa-check-circle", "text": "AI-powered writing assistance", "color": "#10B981"}, {"icon": "fas fa-check-circle", "text": "Advanced world-building tools", "color": "#10B981"}, {"icon": "fas fa-check-circle", "text": "Publish and share your stories", "color": "#10B981"}]',
    'Start Writing Today',
    '/ui/register',
    'fas fa-pen-nib',
    true, true, true, true,
    'Demo CTA 1 - Hero Welcome',
    'homepage', 'cta', 'demo_hero_welcome',
    1, NOW(), NOW()
);

-- CTA 2: HOME_MAIN_TOP - Creative Potential CTA
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    secondary_button_text, secondary_button_url, secondary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    '✨ Unlock Your Creative Potential',
    'Professional writing tools at your fingertips',
    '<p>Whether you''re a seasoned author or just starting out, our AI-powered platform makes storytelling accessible and enjoyable for everyone.</p>',
    'HOME_MAIN_TOP',
    'HERO',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    '#FFFFFF',
    'fas fa-magic',
    'Try Free Demo',
    '/ui/brainstorm',
    'fas fa-play-circle',
    'Learn More',
    '/ui/user-guide',
    'fas fa-info-circle',
    true, true, true, true,
    'Demo CTA 2 - Creative Potential',
    'homepage', 'cta', 'demo_creative_potential',
    2, NOW(), NOW()
);

-- CTA 3: HOME_MAIN_TOP - Quick Start Guide
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    '🚀 Quick Start Guide',
    'Get up and running in just 3 simple steps',
    '<p>Complete our interactive tutorial and earn bonus coins to unlock premium AI features. Your storytelling journey starts here!</p>',
    'HOME_MAIN_TOP',
    'SOLID',
    '#4c6ef5',
    '#FFFFFF',
    'fas fa-graduation-cap',
    'Start Tutorial',
    '/ui/user-guide',
    'fas fa-play',
    true, true, true, true,
    'Demo CTA 3 - Quick Start',
    'homepage', 'cta', 'demo_quick_start',
    3, NOW(), NOW()
);

-- CTA 4: HOME_MAIN_BOTTOM - Writing Community
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    '📚 Join Our Writing Community',
    'Connect with fellow storytellers worldwide',
    '<p>Share your work, get feedback, and discover amazing stories from writers around the globe. Your next favorite read is waiting!</p>',
    'HOME_MAIN_BOTTOM',
    'GRADIENT',
    'linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)',
    '#FFFFFF',
    'fas fa-users',
    'Explore Stories',
    '/ui/stories',
    'fas fa-book-open',
    true, true, true, true,
    'Demo CTA 4 - Writing Community',
    'homepage', 'cta', 'demo_community',
    4, NOW(), NOW()
);

-- CTA 5: HOME_MAIN_BOTTOM - Premium Upgrade
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    features, primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    '💎 Upgrade to Premium',
    'Unlock unlimited AI assistance and advanced features',
    '<p>Get access to premium AI models, unlimited generations, priority support, and exclusive writing tools.</p>',
    'HOME_MAIN_BOTTOM',
    'HERO',
    'linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%)',
    '#FFFFFF',
    'fas fa-crown',
    '[{"icon": "fas fa-infinity", "text": "Unlimited AI generations", "color": "#FFFFFF"}, {"icon": "fas fa-bolt", "text": "Premium AI models", "color": "#FFFFFF"}, {"icon": "fas fa-headset", "text": "Priority support", "color": "#FFFFFF"}]',
    'Upgrade Now',
    '/ui/register',
    'fas fa-arrow-up',
    true, true, true, true,
    'Demo CTA 5 - Premium Upgrade',
    'homepage', 'cta', 'demo_premium',
    5, NOW(), NOW()
);

-- CTA 6: HOME_MAIN_BOTTOM - Blog Platform
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    '📝 Start Your Blog Today',
    'Share your writing journey and build your audience',
    '<p>Create engaging blog posts about your writing process, share tips with other writers, and build your author platform.</p>',
    'HOME_MAIN_BOTTOM',
    'BORDERED',
    '#ffffff',
    '#495057',
    'fas fa-blog',
    'Start Blogging',
    '/blog/editor',
    'fas fa-edit',
    true, true, true, true,
    'Demo CTA 6 - Blog Platform',
    'homepage', 'cta', 'demo_blog',
    6, NOW(), NOW()
);

-- CTA 7: HOME_MAIN_BOTTOM - AI Tools Showcase  
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    '🤖 Discover AI Writing Tools',
    'Explore our full suite of AI-powered writing assistants',
    '<p>From plot generators to character developers, dialogue writers to world builders - discover all the AI tools that can enhance your creativity.</p>',
    'HOME_MAIN_BOTTOM',
    'MINIMAL',
    '#f8f9fa',
    '#495057',
    'fas fa-robot',
    'Explore Tools',
    '/ui/brainstorm',
    'fas fa-tools',
    true, true, true, true,
    'Demo CTA 7 - AI Tools',
    'homepage', 'cta', 'demo_ai_tools',
    7, NOW(), NOW()
);

-- CTA 8: HOME_SIDEBAR_TOP - Featured World Builder
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    '📌 Featured: AI World Builder',
    'Create immersive fictional universes',
    '<p>Use our AI-powered world builder to create detailed fantasy and sci-fi worlds with rich lore, unique characters, and compelling locations.</p>',
    'HOME_SIDEBAR_TOP',
    'SOLID',
    '#17a2b8',
    '#FFFFFF',
    'fas fa-globe-americas',
    'Try World Builder',
    '/ui/worlds',
    'fas fa-hammer',
    true, true, true, true,
    'Demo CTA 8 - Featured World Builder',
    'homepage', 'sidebar_cta', 'demo_world_builder',
    8, NOW(), NOW()
);

-- CTA 9: HOME_SIDEBAR_TOP - AI Image Generator
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    '🎨 AI Image Generator',
    'Bring your characters and worlds to life',
    '<p>Generate stunning artwork for your stories using our advanced AI image generator. Perfect for character portraits and scene illustrations.</p>',
    'HOME_SIDEBAR_TOP',
    'GRADIENT',
    'linear-gradient(135deg, #28a745 0%, #20c997 100%)',
    '#FFFFFF',
    'fas fa-palette',
    'Generate Images',
    '/ui/worlds',
    'fas fa-images',
    true, true, true, true,
    'Demo CTA 9 - AI Images',
    'homepage', 'sidebar_cta', 'demo_ai_images',
    9, NOW(), NOW()
);

-- CTA 10: HOME_SIDEBAR_BOTTOM - Newsletter
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    '📧 Newsletter Signup',
    'Get weekly writing tips and platform updates',
    '<p>Join our newsletter for exclusive writing prompts, AI tips, feature updates, and success stories from our community.</p>',
    'HOME_SIDEBAR_BOTTOM',
    'BORDERED',
    '#ffffff',
    '#495057',
    'fas fa-envelope',
    'Subscribe Now',
    '/ui/register',
    'fas fa-bell',
    true, true, true, true,
    'Demo CTA 10 - Newsletter',
    'homepage', 'sidebar_cta', 'demo_newsletter',
    10, NOW(), NOW()
);

-- CTA 11: HOME_SIDEBAR_BOTTOM - Support 
INSERT INTO cta_contents (
    title, subtitle, content, position, style, background_color, text_color, icon_class,
    primary_button_text, primary_button_url, primary_button_icon,
    show_for_anonymous, show_for_authenticated, show_for_admin, is_active,
    campaign_name, utm_source, utm_medium, utm_campaign, sort_order, created_at, updated_at
) VALUES (
    '💬 Need Help?',
    'Get support from our friendly team',
    '<p>Have questions? Our support team is here to help you make the most of your storytelling journey.</p>',
    'HOME_SIDEBAR_BOTTOM',
    'SOLID',
    '#6c757d',
    '#FFFFFF',
    'fas fa-question-circle',
    'Contact Support',
    '/ui/user-guide',
    'fas fa-headset',
    true, true, true, true,
    'Demo CTA 11 - Support',
    'homepage', 'sidebar_cta', 'demo_support',
    11, NOW(), NOW()
);

-- Verify the created CTAs
SELECT 
    id, 
    title, 
    position, 
    style, 
    is_active,
    campaign_name,
    sort_order
FROM cta_contents 
WHERE campaign_name LIKE 'Demo CTA%'
ORDER BY sort_order;

-- Count CTAs by position  
SELECT 
    position,
    COUNT(*) as cta_count
FROM cta_contents 
WHERE campaign_name LIKE 'Demo CTA%'
GROUP BY position
ORDER BY position;