# Local History Provider

## Overview
Generates a warm, positive historical fact about the recipient's area. Prefers hometown (where they grew up) over city_for_weather. Enriches the prompt with era of youth, nationality/background, and life roles so the fact feels personally relevant.

## Category
Memory / Local History

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_text_with_usage()` to generate a warm historical fact
- The LLM generates 2 short sentences about the location's history
- The prompt is enriched with patient preferences (era, nationality, life roles)

### Prompt Analysis
```
Write one warm, positive historical fact about {location}.
2 short sentences only.
{context_str}
Focus on something cheerful — a famous landmark, a lovely tradition, or something the town is proud of.
Make it feel like a proud, happy memory.
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear constraint (2 short sentences only)
   - Explicit instruction for positive, cheerful content
   - Personalized with patient preferences
2. **Improvements**:
   - Add explicit instruction to avoid controversial or distressing historical events
   - Consider adding a constraint to ensure factual accuracy
   - Add validation for output length and tone
3. **Safety**: Has fallback content if LLM fails

## Configuration
- `fallback_text`: Static fallback text

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
