# Family Greeting Provider

## Overview
Generates a warm, imagined short note 'from' one of the recipient's family members. Enriches the message with life roles, pets, favourite foods, and hometown so each letter feels genuinely personal.

## Category
Core / Family Connection

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_text_with_usage()` to create a warm, personalized family note
- The LLM generates a 2-sentence note written as if from a family member
- The prompt is enriched with patient preferences (life roles, pets, favourite foods, hometown)

### Prompt Analysis
```
Write a short, loving note from {sender} to {recipient}.
2 sentences only.
Make it feel warm, caring, and full of love.
Write in first person as {sender}.
{context_str}
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear constraint (2 sentences only)
   - Personalized with family member name and recipient details
   - Context enrichment from patient preferences
2. **Improvements**:
   - Add explicit instruction to avoid mentioning illness or care situations
   - Consider adding a constraint to avoid complex or confusing references
   - Add validation for output length and tone
3. **Safety**: Has fallback content if LLM fails

## Configuration
- `fallback_text`: Static fallback greeting

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
