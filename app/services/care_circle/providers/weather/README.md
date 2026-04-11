# Weather Provider

## Overview
Fetches real weather from wttr.in and generates a warm message. Provides current temperature and weather conditions for the patient's configured city.

## Category
Core / Daily Information

## AI Usage
**No - External API only**

### How Content is Generated
- Fetches weather data from wttr.in API (`https://wttr.in/{city}?format=j1`)
- Formats a warm greeting message with temperature and conditions
- No LLM or AI-generated text content (LLM bypassed for Sprint 02)

### Content Sources
- wttr.in API (free, public weather API)

## Configuration
- `default_city`: Fallback city when not specified in preferences (default: "Unknown")
- `fallback`: Fallback message when weather is unavailable

## External Dependencies
- wttr.in: `https://wttr.in/{city}?format=j1`

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content to review
- Falls back gracefully to static content on API failure
- Note: LLM warm message generation is currently bypassed
