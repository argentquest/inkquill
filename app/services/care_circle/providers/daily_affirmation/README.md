# Daily Affirmation Provider

## Overview
Fetches a daily positive affirmation from an external public API.

## Category
Core / Wellbeing

## AI Usage
**No - External API only**

### How Content is Generated
- Fetches affirmations from the affirmations.dev API (`https://www.affirmations.dev/`)
- No LLM or AI-generated text content

### Content Sources
- Affirmations.dev API (free, public API)

## Configuration
- `api_url`: Affirmation API endpoint (default: "https://www.affirmations.dev/")
- `fallback`: Static fallback affirmation (default: "You are loved. You are enough. You matter.")

## External Dependencies
- Affirmations.dev: `https://www.affirmations.dev/`

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content to review
- Falls back gracefully to static content on API failure
- Content is positive and appropriate for dementia care
