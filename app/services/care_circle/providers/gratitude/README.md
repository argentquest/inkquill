# Gratitude Provider

## Overview
Generates a gentle thought of gratitude using a Large Language Model. Rotates across five gratitude themes (nature, person, simple comfort, memory, body) to keep daily reflections fresh and varied.

## Category
Wellbeing / Mindfulness

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_text_with_usage()` to generate a gratitude thought
- Rotates across five gratitude modes: nature, person, simple comfort, memory, body
- Content is personalized based on patient name

### Prompt Analysis
```
Write one gentle gratitude thought for {name}.
{mode['instruction']}
Keep it to 1-2 short sentences.
Do NOT ask a question that tests memory.
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear constraint on length (1-2 short sentences)
   - Explicit instruction to avoid memory-testing questions
   - Rotates across multiple themes for variety
2. **Improvements**:
   - Add explicit instruction to avoid mentioning illness or care situations
   - Consider adding a constraint to ensure positive, uplifting content
   - Add validation for output length and tone
3. **Safety**: Has fallback content from configuration if LLM fails

## Configuration
- `prompts`: Array of fallback prompts

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
