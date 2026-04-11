# Pen Pal Letter Provider

## Overview
Generates a warm, fictional short letter (80–100 words) written as if from an old dear friend. Addressed to the resident by name, mentions the current season, a nostalgic shared memory, and ends with one gentle question to spark a happy recollection.

## Category
Wellbeing / Personal Connection

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_text_with_usage()` to generate a warm pen pal letter
- Personalized with resident's name, era, activities, hometown, life roles, pets, favourite foods and TV shows
- Falls back to static letters from config if LLM is unavailable

### Prompt Analysis
```
Write a short, warm pen pal letter (80–100 words) to {name}.
Write it AS IF you are {friend_name}, an old dear friend from the {era}.
Mention something lovely about the current season ({season}) — a sight, smell, or simple pleasure.
Reference one warm shared memory from the {era}.
{context_str}
End with one gentle question inviting a happy recollection.
Tone: warm, familiar, simple, nostalgic.
Do NOT mention illness, care homes, or memory problems.
Start with 'Dear {name},' and sign off 'With love, {friend_name}'
```

### Prompt Recommendations
1. **Strengths**: 
   - Explicit instruction to avoid mentioning illness, care homes, or memory problems
   - Clear word count constraint (80-100 words)
   - Rich personalization from patient preferences
   - Specific format requirements (greeting and sign-off)
2. **Improvements**:
   - Consider adding a constraint to ensure the question is simple and answerable
   - Add validation for output length and format
3. **Safety**: Has fallback letters from configuration if LLM fails

## Configuration
- `friend_names`: Array of friend names to use
- `fallback_letters`: Array of fallback letter templates with placeholders

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
- Explicit safety constraints in prompt
