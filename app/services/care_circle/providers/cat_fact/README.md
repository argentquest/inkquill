# Cat Fact Provider

## Overview
Fetches a random cat fact from an external public API. Also provides a placeholder image URL for rendering in templates.

## Category
Memory / Animal Facts

## AI Usage
**No - External API only**

### How Content is Generated
- Fetches cat facts from the Ninja Cat Fact API (`https://catfact.ninja/fact`)
- Provides cat images from the Cataas API (`https://cataas.com/cat`)
- No LLM or AI-generated text content

### Content Sources
- **Facts**: Cat Fact Ninja API (free, public API)
- **Images**: Cataas API (free, public cat image API)

## Configuration
- `api_url`: Cat fact API endpoint (default: "https://catfact.ninja/fact")
- `image_api`: Cat image API endpoint (default: "https://cataas.com/cat")
- `fallback`: Static fallback fact

## External Dependencies
- Cat Fact Ninja: `https://catfact.ninja/fact`
- Cataas: `https://cataas.com/cat`

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content to review
- Falls back gracefully to static content on API failure
- Content is generally safe and lighthearted
