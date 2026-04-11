# Dog Photo Provider

## Overview
Fetches a random picture of a dog from the public Dog API. Attempts to parse the specific dog breed from the URL structure to provide context alongside the image.

## Category
Memory / Animal Photos

## AI Usage
**No - External API only**

### How Content is Generated
- Fetches random dog photos from the Dog CEO API (`https://dog.ceo/api/breeds/image/random`)
- Extracts breed name from URL path structure
- No LLM or AI-generated text content

### Content Sources
- Dog CEO API (free, public API)

## Configuration
- `api_url`: Dog photo API endpoint (default: "https://dog.ceo/api/breeds/image/random")
- `default_caption`: Default caption for photos

## External Dependencies
- Dog CEO API: `https://dog.ceo/api/breeds/image/random`

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content to review
- Falls back gracefully to static content on API failure
- Content is generally safe and uplifting
