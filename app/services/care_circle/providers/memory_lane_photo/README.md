# Memory Lane Photo Provider

## Overview
Shows a vintage-style photo with a warm description. Uses free image APIs for nostalgic photography.

## Category
Memory / Visual Nostalgia

## AI Usage
**No - External API only**

### How Content is Generated
- Attempts to fetch vintage photos from Unsplash source API
- Falls back to pre-configured vintage photos from Unsplash
- No LLM or AI-generated text content

### Content Sources
- Unsplash source API (deprecated, may not work reliably)
- Pre-configured Unsplash photo URLs as fallback

## Configuration
- `fallback_photos`: Array of photo objects with `image_url` and `description`
- `fallback_description`: Default description

## External Dependencies
- Unsplash source API: `https://source.unsplash.com/600x400/?vintage,portrait`

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content to review
- Falls back gracefully to static content on API failure
- All photos are pre-vetted and appropriate
