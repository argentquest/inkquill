# Hobby Spotlight Provider

## Overview
Generates a warm, personal story about one of the recipient's hobbies. Enriches the prompt with life roles, hometown, era of youth, and nationality/background when available.

## Category
Lifestyle / Personal Interest

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_text_with_usage()` to create a warm, personalized story about a hobby
- The LLM generates 2 short, warm sentences about the patient and their hobby
- The prompt is enriched with patient preferences (life roles, hometown, era, nationality)

### Prompt Analysis
```
Write 2 short, warm sentences about {name} and their love of {hobby}.
{context_str}
Make it feel personal, cozy, and joyful.
Do not ask questions. Just describe how lovely {hobby} is.
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear constraint (2 short sentences)
   - Explicit instruction to avoid questions
   - Personalized with patient preferences
2. **Improvements**:
   - Add explicit instruction to avoid mentioning illness or care situations
   - Consider adding a constraint to ensure content is universally understandable
   - Add validation for output length and tone
3. **Safety**: Has fallback content if LLM fails

## Configuration
- `fallback_hobbies`: Default hobbies when none specified in preferences
- `fallback_text`: Static fallback text

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
