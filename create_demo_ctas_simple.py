#!/usr/bin/env python3
"""
Script to create demo CTA records using existing enum values.
This creates multiple CTAs for the 4 existing home positions with different styles.
Run with: python create_demo_ctas_simple.py
"""

import requests
import json

# CTA creation data using existing positions
cta_demos = [
    # HOME_MAIN_TOP CTAs (will appear in multiple main sections)
    {
        "title": "🎯 Welcome to AI Storytelling!",
        "subtitle": "Transform your creative ideas into captivating stories",
        "content": "<p>Join thousands of writers using AI to bring their stories to life. Create rich worlds, compelling characters, and publish your masterpiece.</p>",
        "position": "HOME_MAIN_TOP",
        "style": "gradient",
        "background_color": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "text_color": "#FFFFFF",
        "icon_class": "fas fa-rocket",
        "features": [
            {"icon": "fas fa-check-circle", "text": "AI-powered writing assistance", "color": "#10B981"},
            {"icon": "fas fa-check-circle", "text": "Advanced world-building tools", "color": "#10B981"},
            {"icon": "fas fa-check-circle", "text": "Publish and share your stories", "color": "#10B981"}
        ],
        "primary_button_text": "Start Writing Today",
        "primary_button_url": "/ui/register",
        "primary_button_icon": "fas fa-pen-nib",
        "campaign_name": "Main Top Hero CTA"
    },
    {
        "title": "✨ Unlock Your Creative Potential",
        "subtitle": "Professional writing tools at your fingertips",
        "content": "<p>Whether you're a seasoned author or just starting out, our AI-powered platform makes storytelling accessible and enjoyable for everyone.</p>",
        "position": "HOME_MAIN_TOP", 
        "style": "hero",
        "background_color": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "text_color": "#FFFFFF",
        "icon_class": "fas fa-magic",
        "primary_button_text": "Try Free Demo",
        "primary_button_url": "/ui/brainstorm",
        "primary_button_icon": "fas fa-play-circle",
        "secondary_button_text": "Learn More",
        "secondary_button_url": "/ui/user-guide",
        "secondary_button_icon": "fas fa-info-circle",
        "campaign_name": "Main Top Demo CTA"
    },
    {
        "title": "🚀 Quick Start Guide",
        "subtitle": "Get up and running in just 3 simple steps",
        "content": "<p>Complete our interactive tutorial and earn bonus coins to unlock premium AI features. Your storytelling journey starts here!</p>",
        "position": "HOME_MAIN_TOP",
        "style": "solid",
        "background_color": "#4c6ef5",
        "text_color": "#FFFFFF",
        "icon_class": "fas fa-graduation-cap",
        "primary_button_text": "Start Tutorial",
        "primary_button_url": "/ui/user-guide",
        "primary_button_icon": "fas fa-play",
        "campaign_name": "Main Top Tutorial CTA"
    },
    
    # HOME_MAIN_BOTTOM CTAs (will appear at bottom sections)
    {
        "title": "📚 Join Our Writing Community",
        "subtitle": "Connect with fellow storytellers worldwide",
        "content": "<p>Share your work, get feedback, and discover amazing stories from writers around the globe. Your next favorite read is waiting!</p>",
        "position": "HOME_MAIN_BOTTOM",
        "style": "gradient",
        "background_color": "linear-gradient(135deg, #74b9ff 0%, #0984e3 100%)",
        "text_color": "#FFFFFF", 
        "icon_class": "fas fa-users",
        "primary_button_text": "Explore Stories",
        "primary_button_url": "/ui/stories",
        "primary_button_icon": "fas fa-book-open",
        "campaign_name": "Main Bottom Community CTA"
    },
    {
        "title": "💎 Upgrade to Premium",
        "subtitle": "Unlock unlimited AI assistance and advanced features",
        "content": "<p>Get access to premium AI models, unlimited generations, priority support, and exclusive writing tools.</p>",
        "position": "HOME_MAIN_BOTTOM",
        "style": "hero",
        "background_color": "linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%)",
        "text_color": "#FFFFFF",
        "icon_class": "fas fa-crown",
        "features": [
            {"icon": "fas fa-infinity", "text": "Unlimited AI generations", "color": "#FFFFFF"},
            {"icon": "fas fa-bolt", "text": "Premium AI models", "color": "#FFFFFF"},
            {"icon": "fas fa-headset", "text": "Priority support", "color": "#FFFFFF"}
        ],
        "primary_button_text": "Upgrade Now",
        "primary_button_url": "/ui/register",
        "primary_button_icon": "fas fa-arrow-up",
        "campaign_name": "Main Bottom Premium CTA"
    },
    {
        "title": "📝 Start Your Blog Today",
        "subtitle": "Share your writing journey and build your audience",
        "content": "<p>Create engaging blog posts about your writing process, share tips with other writers, and build your author platform.</p>",
        "position": "HOME_MAIN_BOTTOM",
        "style": "bordered",
        "background_color": "#ffffff",
        "text_color": "#495057",
        "icon_class": "fas fa-blog",
        "primary_button_text": "Start Blogging",
        "primary_button_url": "/blog/editor", 
        "primary_button_icon": "fas fa-edit",
        "campaign_name": "Main Bottom Blog CTA"
    },
    
    # HOME_SIDEBAR_TOP CTAs
    {
        "title": "📌 Featured: AI World Builder",
        "subtitle": "Create immersive fictional universes",
        "content": "<p>Use our AI-powered world builder to create detailed fantasy and sci-fi worlds with rich lore, unique characters, and compelling locations.</p>",
        "position": "HOME_SIDEBAR_TOP",
        "style": "minimal",
        "background_color": "#f8f9fa",
        "text_color": "#495057", 
        "icon_class": "fas fa-globe-americas",
        "primary_button_text": "Try World Builder",
        "primary_button_url": "/ui/worlds",
        "primary_button_icon": "fas fa-hammer",
        "campaign_name": "Sidebar Top Featured CTA"
    },
    {
        "title": "🎨 AI Image Generator",
        "subtitle": "Bring your characters and worlds to life",
        "content": "<p>Generate stunning artwork for your stories using our advanced AI image generator. Perfect for character portraits and scene illustrations.</p>",
        "position": "HOME_SIDEBAR_TOP",
        "style": "solid",
        "background_color": "#28a745",
        "text_color": "#FFFFFF",
        "icon_class": "fas fa-palette",
        "primary_button_text": "Generate Images",
        "primary_button_url": "/ui/worlds",
        "primary_button_icon": "fas fa-images",
        "campaign_name": "Sidebar Top Images CTA"
    },
    
    # HOME_SIDEBAR_BOTTOM CTAs
    {
        "title": "📧 Newsletter Signup",
        "subtitle": "Get weekly writing tips and platform updates",
        "content": "<p>Join our newsletter for exclusive writing prompts, AI tips, feature updates, and success stories from our community.</p>",
        "position": "HOME_SIDEBAR_BOTTOM",
        "style": "bordered",
        "background_color": "#ffffff",
        "text_color": "#495057",
        "icon_class": "fas fa-envelope",
        "primary_button_text": "Subscribe Now",
        "primary_button_url": "/ui/register",
        "primary_button_icon": "fas fa-bell",
        "campaign_name": "Sidebar Bottom Newsletter CTA"
    },
    {
        "title": "💬 Need Help?",
        "subtitle": "Get support from our friendly team",
        "content": "<p>Have questions? Our support team is here to help you make the most of your storytelling journey.</p>",
        "position": "HOME_SIDEBAR_BOTTOM", 
        "style": "solid",
        "background_color": "#6c757d",
        "text_color": "#FFFFFF",
        "icon_class": "fas fa-question-circle",
        "primary_button_text": "Contact Support",
        "primary_button_url": "/ui/user-guide",
        "primary_button_icon": "fas fa-headset",
        "campaign_name": "Sidebar Bottom Support CTA"
    }
]

def create_cta_via_api(cta_data):
    """Create a CTA using the admin API endpoint."""
    url = "http://localhost:8000/admin/cta-content"
    
    try:
        response = requests.post(url, json=cta_data)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created CTA: {cta_data['title']} (ID: {result.get('id')})")
            return result
        else:
            print(f"❌ Failed to create CTA: {cta_data['title']}")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating CTA {cta_data['title']}: {e}")
        return None

def main():
    """Create all demo CTAs."""
    print("🚀 Creating 11 demo CTAs for home page...")
    print(f"📍 Using {len(cta_demos)} CTA configurations")
    
    created_count = 0
    failed_count = 0
    
    for i, cta_data in enumerate(cta_demos, 1):
        print(f"\n📝 Creating CTA {i}/{len(cta_demos)}: {cta_data['title']}")
        result = create_cta_via_api(cta_data)
        
        if result:
            created_count += 1
        else:
            failed_count += 1
    
    print(f"\n🎉 Demo CTA creation complete!")
    print(f"✅ Successfully created: {created_count}")
    if failed_count > 0:
        print(f"❌ Failed to create: {failed_count}")
    
    print(f"\n📋 CTA Positions Used:")
    positions = {}
    for cta in cta_demos:
        pos = cta['position']
        if pos not in positions:
            positions[pos] = 0
        positions[pos] += 1
    
    for pos, count in positions.items():
        print(f"   {pos}: {count} CTAs")
    
    print(f"\n🎨 Visual Styles Used:")
    styles = {}
    for cta in cta_demos:
        style = cta['style']
        if style not in styles:
            styles[style] = 0
        styles[style] += 1
    
    for style, count in styles.items():
        print(f"   {style}: {count} CTAs")
    
    print(f"\n💡 These CTAs will demonstrate:")
    print("   • HOME_MAIN_TOP: Shows in welcome, quick actions, and blog sections")
    print("   • HOME_MAIN_BOTTOM: Shows in multiple bottom positions")
    print("   • HOME_SIDEBAR_TOP: Shows at top of right sidebar")
    print("   • HOME_SIDEBAR_BOTTOM: Shows at bottom of right sidebar")

if __name__ == "__main__":
    main()