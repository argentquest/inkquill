# Activity Suggestion Provider

## Overview
Suggests one of the recipient's favourite activities in a warm, inviting way. Adapts to mobility level, and weaves in pets, favourite foods, and preferred pronoun where relevant.

## Category
Wellbeing / Activity Suggestions

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_text_with_usage()` to create a warm, personalized activity suggestion
- The LLM generates 2 short sentences encouraging the patient to enjoy a specific activity
- The prompt is enriched with patient preferences (mobility level, favourite foods, pets, pronouns)

### Prompt Analysis
```
Write 2 short sentences gently encouraging {name} to enjoy {activity} today.
Make it feel warm, inviting, and easy — like a lovely treat, not a task.
{context_str}
```

### Prompt Recommendations
1. **Strengths**: The prompt is well-structured with clear constraints (2 sentences, warm tone)
2. **Improvements**:
   - Add explicit instruction to avoid medical or health-related language
   - Consider adding a constraint to avoid questions that require memory recall
   - The `DEMENTIA_SYSTEM_PROMPT` is used, which should already handle dementia-care appropriateness
3. **Safety**: Has fallback content if LLM fails, ensuring reliable delivery

## Configuration
- `fallback_activities`: Default activities when none specified in preferences
- `fallback_text`: Static fallback text when LLM is unavailable

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
