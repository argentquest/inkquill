# AI Trivia Provider

## Overview
Provides a daily trivia fact and a music suggestion using a Large Language Model. Rotates across six trivia categories (daily life, inventions, entertainment, nature/seasons, food/drink, sport/leisure) for day-to-day variety.

## Category
Games / Trivia

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_json_with_usage()` to generate trivia facts and music suggestions
- Returns JSON with `trivia` and `music` fields
- Content is personalized based on the patient's era of youth and favorite singers

### Prompt Analysis
```
{category['hint']} Focus on the {era}.
Also suggest one song by {singer} or a similar artist to listen to today.
Keep each to 1 short sentence.
Return as JSON: {"trivia": "...", "music": "..."}
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear JSON output format requirement
   - Category hints guide the LLM toward appropriate content
   - Era-based personalization adds relevance
2. **Improvements**:
   - Add explicit instruction to avoid obscure or potentially distressing historical facts
   - Consider adding a constraint to ensure trivia is positive/uplifting
   - Add validation for the JSON response structure
3. **Safety**: Has fallback content for both trivia and music if LLM fails

## Configuration
- `default_era`: Fallback era when not specified in preferences (default: "1950s")
- `default_singer`: Fallback singer when none specified (default: "Frank Sinatra")
- `fallback_trivia`: Static trivia fallback
- `fallback_music`: Static music fallback

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
