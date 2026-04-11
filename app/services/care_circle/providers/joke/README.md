# Joke Provider

## Overview
Fetches a safe, single-line joke from an external public API.

## Category
Games / Humor

## AI Usage
**No - External API only**

### How Content is Generated
- Fetches jokes from the JokeAPI (`https://v2.jokeapi.dev/joke/Any?safe-mode&type=single`)
- Uses safe-mode to ensure appropriate content
- No LLM or AI-generated text content

### Content Sources
- JokeAPI (free, public API with safe-mode filtering)

## Configuration
- `api_url`: Joke API endpoint (default: "https://v2.jokeapi.dev/joke/Any?safe-mode&type=single")
- `fallback`: Static fallback joke

## External Dependencies
- JokeAPI: `https://v2.jokeapi.dev/joke/Any?safe-mode&type=single`

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content to review
- Falls back gracefully to static content on API failure
- Uses safe-mode filtering for appropriate content
