# Personal Affirmation Provider

## Overview
Generates a deeply personal affirmation using the recipient's name, activities, life roles, preferred pronoun, and pets.

## Category
Wellbeing / Personal Affirmation

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_text_with_usage()` to generate a personal, loving affirmation
- The LLM generates 2 short sentences using the patient's name and personal details
- The prompt is enriched with patient preferences (activities, life roles, pronoun, pets)

### Prompt Analysis
```
Write a personal, loving affirmation for {name}.
2 short sentences only.
{context_str}
Make it feel warm, specific, and uplifting.
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear constraint (2 short sentences only)
   - Uses patient's name at least once
   - Personalized with specific patient details
2. **Improvements**:
   - Add explicit instruction to avoid mentioning illness or care situations
   - Consider adding a constraint to ensure universally positive content
   - Add validation for output length and tone
3. **Safety**: Has fallback content if LLM fails

## Configuration
- `fallback_text`: Static fallback affirmation

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
