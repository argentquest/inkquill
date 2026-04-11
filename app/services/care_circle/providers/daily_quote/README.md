# Daily Quote Provider

## Overview
Fetches a daily quote from an external public API, falling back safely to static content.

## Category
Core / Inspiration

## AI Usage
**No - External API only**

### How Content is Generated
- Fetches quotes from the ZenQuotes API (`https://zenquotes.io/api/today`)
- Parses quote text and author from API response
- No LLM or AI-generated text content

### Content Sources
- ZenQuotes API (free, public API)

## Configuration
- `api_url`: Quote API endpoint (default: "https://zenquotes.io/api/today")
- `fallback_quote`: Static fallback quote (default: "Every day is a new beginning.")
- `fallback_author`: Static fallback author (default: "Unknown")

## External Dependencies
- ZenQuotes API: `https://zenquotes.io/api/today`

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content to review
- Falls back gracefully to static content on API failure
- Note: External API quotes should be monitored for appropriateness
