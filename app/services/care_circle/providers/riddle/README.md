# Riddle Provider

## Overview
Generates simple, easy-to-guess riddles using a Large Language Model. Rotates across five riddle styles — what am I, rhyme finish, knock-knock, animal, and household object — for daily variety.

## Category
Games / Riddles

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_json_with_usage()` to generate riddles
- Rotates across five riddle styles for variety
- Returns JSON with `question` and `answer` fields

### Prompt Analysis
```
{style['instruction']}
The riddle must feel fun and easy — never frustrating.
Example style: {style['example']}.
Return as JSON: {"question": "...", "answer": "..."}
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear instruction that riddle must be "fun and easy — never frustrating"
   - Style-specific instructions guide appropriate content
   - JSON output format requirement
2. **Improvements**:
   - Add explicit instruction to avoid obscure or complex riddles
   - Consider adding a constraint to ensure answers are common knowledge
   - Add validation for JSON response structure
3. **Safety**: Has fallback riddles from configuration if LLM fails

## Configuration
- `riddles`: Array of fallback riddle objects with `question` and `answer`

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
