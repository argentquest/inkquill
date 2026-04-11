# Animal Friend Provider

## Overview
Shows a friendly animal photo with a warm fact. Uses the Dog CEO API to fetch random dog photos and provides warm, friendly content about animals.

## Category
Memory / Animal Interaction

## AI Usage
**No - External API only**

### How Content is Generated
- Fetches random dog photos from the public Dog CEO API (`https://dog.ceo/api/breeds/image/random`)
- Uses static warm facts about animals from configuration
- No LLM or AI-generated text content

### Content Sources
- **Images**: Dog CEO API (free, public API)
- **Facts**: Pre-configured warm facts about animals (dogs, cats, birds, fish, bunnies, butterflies, horses, dolphins)

## Configuration
- `fallback`: Default fallback message
- `warm_facts`: Array of warm animal facts for elderly users

## External Dependencies
- Dog CEO API: `https://dog.ceo/api/breeds/image/random`

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content to review
- Falls back gracefully to static content on API failure
- Content is pre-vetted and appropriate for dementia care
