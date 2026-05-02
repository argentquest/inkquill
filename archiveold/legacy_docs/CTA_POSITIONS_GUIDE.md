# Home Page CTA Positions Guide

This document shows all 11 CTA positions that have been implemented on the home page and provides sample CTAs for each position.

## Home Page Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                        HOME PAGE                                │
├─────────────────────────────────┬───────────────────────────────┤
│           MAIN CONTENT          │         SIDEBAR              │
│           (col-lg-7)            │        (col-lg-5)             │
├─────────────────────────────────┼───────────────────────────────┤
│                                 │                               │
│ 1. HOME_MAIN_TOP CTAs          │ 8. HOME_SIDEBAR_TOP CTAs      │
│    (Multiple sections)          │    (Top of sidebar)           │
│                                 │                               │
│ ┌─── Welcome Header Section ──┐ │ ┌─── AI Chat Worlds ────────┐ │
│ │ • Progress Steps            │ │ │ • Featured worlds          │ │
│ │ • Getting Started Guide     │ │ │ • Public chat worlds       │ │
│ └─────────────────────────────┘ │ └───────────────────────────┘ │
│                                 │                               │
│ ┌─── Quick Actions Section ───┐ │ ┌─── Published Stories ─────┐ │
│ │ • Referral Program          │ │ │ • Recent stories           │ │
│ │ • Story Brainstorm          │ │ │ • Community content        │ │
│ │ • Start Writing             │ │ │                            │ │
│ │ • World Builder             │ │ └───────────────────────────┘ │
│ └─────────────────────────────┘ │                               │
│                                 │ ┌─── Generated Images ──────┐ │
│ ┌─── Login/Register Section ──┐ │ │ • AI-generated artwork     │ │
│ │ (Anonymous users only)       │ │ │ • Recent creations         │ │
│ │ • Login Card                │ │ │                            │ │
│ │ • Register Card             │ │ └───────────────────────────┘ │
│ └─────────────────────────────┘ │                               │
│                                 │                               │
│ ┌─── Blog Posts Section ──────┐ │ 11. HOME_SIDEBAR_BOTTOM CTAs  │
│ │ • Latest blog posts         │ │     (Bottom of sidebar)       │
│ │ • Writing community         │ │                               │
│ └─────────────────────────────┘ │                               │
│                                 │                               │
│ 10. HOME_MAIN_BOTTOM CTAs      │                               │
│     (Final main position)       │                               │
│                                 │                               │
└─────────────────────────────────┴───────────────────────────────┘
```

## CTA Position Details

### Main Content CTAs (9 positions)

#### 1. HOME_MAIN_TOP 
**Location:** Top of main content, before welcome header
**Best for:** Primary announcements, hero CTAs, most important messages
**Visibility:** Maximum - first thing users see

#### 2-4. Section-specific positions (using HOME_MAIN_TOP)
- **Welcome Section Top/Bottom:** Around the progress steps
- **Quick Actions Top/Bottom:** Around the action buttons  
- **Login/Register Top/Bottom:** Around auth forms (anonymous only)

#### 5-7. Blog and content positions (using HOME_MAIN_BOTTOM)
- **Blog Section Top/Bottom:** Around blog posts
- **Community features**
- **Content promotion**

#### 8. HOME_MAIN_BOTTOM
**Location:** Very bottom of main content
**Best for:** Final conversion attempts, newsletter signups, secondary actions
**Visibility:** Good - users who scroll this far are engaged

### Sidebar CTAs (2 positions)

#### 9-10. HOME_SIDEBAR_TOP
**Location:** Top of right sidebar
**Best for:** Featured content, tools promotion, special offers
**Visibility:** High - always visible on desktop

#### 11. HOME_SIDEBAR_BOTTOM  
**Location:** Bottom of right sidebar
**Best for:** Support links, newsletter, secondary actions
**Visibility:** Medium - requires scrolling

## Sample CTA Records

Here are 11 sample CTAs that demonstrate all positions:

### Main Content CTAs

```sql
-- CTA 1: Hero Welcome (HOME_MAIN_TOP)
INSERT INTO cta_contents (title, subtitle, content, position, style, background_color, text_color, icon_class, primary_button_text, primary_button_url, primary_button_icon, is_active, campaign_name) 
VALUES (
    '🎯 Welcome to AI Storytelling!',
    'Transform your creative ideas into captivating stories', 
    '<p>Join thousands of writers using AI to bring their stories to life.</p>',
    'HOME_MAIN_TOP', 'GRADIENT', 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
    '#FFFFFF', 'fas fa-rocket', 'Start Writing Today', '/ui/register', 'fas fa-pen-nib', 
    true, 'Demo CTA 1 - Hero Welcome'
);

-- CTA 2: Creative Potential (HOME_MAIN_TOP) 
INSERT INTO cta_contents (title, subtitle, content, position, style, background_color, text_color, icon_class, primary_button_text, primary_button_url, primary_button_icon, secondary_button_text, secondary_button_url, secondary_button_icon, is_active, campaign_name)
VALUES (
    '✨ Unlock Your Creative Potential',
    'Professional writing tools at your fingertips',
    '<p>Our AI-powered platform makes storytelling accessible for everyone.</p>',
    'HOME_MAIN_TOP', 'HERO', 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    '#FFFFFF', 'fas fa-magic', 'Try Free Demo', '/ui/brainstorm', 'fas fa-play-circle',
    'Learn More', '/ui/user-guide', 'fas fa-info-circle',
    true, 'Demo CTA 2 - Creative Potential'
);

-- CTA 3: Quick Start (HOME_MAIN_TOP)
INSERT INTO cta_contents (title, subtitle, content, position, style, background_color, text_color, icon_class, primary_button_text, primary_button_url, primary_button_icon, is_active, campaign_name)
VALUES (
    '🚀 Quick Start Guide',
    'Get up and running in just 3 simple steps',
    '<p>Complete our interactive tutorial and earn bonus coins!</p>',
    'HOME_MAIN_TOP', 'SOLID', '#4c6ef5', '#FFFFFF', 'fas fa-graduation-cap',
    'Start Tutorial', '/ui/user-guide', 'fas fa-play',
    true, 'Demo CTA 3 - Quick Start'
);
```

### Main Bottom CTAs

```sql
-- CTA 4: Writing Community (HOME_MAIN_BOTTOM)
INSERT INTO cta_contents (title, subtitle, content, position, style, background_color, text_color, icon_class, primary_button_text, primary_button_url, primary_button_icon, is_active, campaign_name)
VALUES (
    '📚 Join Our Writing Community',
    'Connect with fellow storytellers worldwide',
    '<p>Share your work, get feedback, and discover amazing stories.</p>',
    'HOME_MAIN_BOTTOM', 'GRADIENT', 'linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)',
    '#FFFFFF', 'fas fa-users', 'Explore Stories', '/ui/stories', 'fas fa-book-open',
    true, 'Demo CTA 4 - Writing Community'
);

-- CTA 5: Premium Upgrade (HOME_MAIN_BOTTOM)
INSERT INTO cta_contents (title, subtitle, content, position, style, background_color, text_color, icon_class, features, primary_button_text, primary_button_url, primary_button_icon, is_active, campaign_name)
VALUES (
    '💎 Upgrade to Premium',
    'Unlock unlimited AI assistance and advanced features',
    '<p>Get access to premium AI models and exclusive tools.</p>',
    'HOME_MAIN_BOTTOM', 'HERO', 'linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%)',
    '#FFFFFF', 'fas fa-crown',
    '[{"icon": "fas fa-infinity", "text": "Unlimited AI generations", "color": "#FFFFFF"}]',
    'Upgrade Now', '/ui/register', 'fas fa-arrow-up',
    true, 'Demo CTA 5 - Premium Upgrade'
);
```

### Sidebar CTAs

```sql
-- CTA 6: Featured World Builder (HOME_SIDEBAR_TOP)
INSERT INTO cta_contents (title, subtitle, content, position, style, background_color, text_color, icon_class, primary_button_text, primary_button_url, primary_button_icon, is_active, campaign_name)
VALUES (
    '📌 Featured: AI World Builder',
    'Create immersive fictional universes',
    '<p>Build detailed fantasy and sci-fi worlds with AI assistance.</p>',
    'HOME_SIDEBAR_TOP', 'SOLID', '#17a2b8', '#FFFFFF', 'fas fa-globe-americas',
    'Try World Builder', '/ui/worlds', 'fas fa-hammer',
    true, 'Demo CTA 6 - Featured World Builder'
);

-- CTA 7: Newsletter (HOME_SIDEBAR_BOTTOM)
INSERT INTO cta_contents (title, subtitle, content, position, style, background_color, text_color, icon_class, primary_button_text, primary_button_url, primary_button_icon, is_active, campaign_name)
VALUES (
    '📧 Newsletter Signup',
    'Get weekly writing tips and updates',
    '<p>Join our newsletter for exclusive prompts and tips.</p>',
    'HOME_SIDEBAR_BOTTOM', 'BORDERED', '#ffffff', '#495057', 'fas fa-envelope',
    'Subscribe Now', '/ui/register', 'fas fa-bell',
    true, 'Demo CTA 7 - Newsletter'
);
```

## Visual Styles Available

1. **GRADIENT** - Colorful gradient backgrounds
2. **HERO** - Large format with features list
3. **SOLID** - Single color background  
4. **BORDERED** - White background with border
5. **MINIMAL** - Clean, subtle styling

## CTA Display Strategy

- **HOME_MAIN_TOP CTAs** appear in 3 different sections of main content
- **HOME_MAIN_BOTTOM CTAs** appear in 4 different sections of main content  
- **HOME_SIDEBAR_TOP CTAs** appear at top of sidebar
- **HOME_SIDEBAR_BOTTOM CTAs** appear at bottom of sidebar

This gives you **11 total CTA placement opportunities** across the home page for maximum conversion potential!

## Usage Instructions

1. Run the SQL inserts above to create demo CTAs
2. Visit the home page to see CTAs in all positions
3. Use the admin CTA manager to edit, disable, or create new CTAs
4. Each position can have multiple CTAs that rotate or display together

The template now supports all these positions and will automatically display CTAs based on user permissions (anonymous/authenticated/admin) and active status.