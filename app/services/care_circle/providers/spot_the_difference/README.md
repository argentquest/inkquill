# Spot the Difference Provider

## Overview
Spot the Difference (Text Version) provider. Two lists of 5 familiar words — identical except one item is swapped. The reader identifies which word changed between List A and List B. LLM generates the lists; falls back to static pairs from config.

## Category
Games / Visual Recognition

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_json_with_usage()` to generate two word lists with one difference
- Returns JSON with `list_a`, `list_b`, `changed_in_a`, and `changed_in_b` fields
- Falls back to static word sets from configuration if LLM fails

### Prompt Analysis
```
Create a simple 'Spot the Difference' word puzzle for an elderly person.
Write two lists (List A and List B), each with exactly 5 short, familiar words.
The lists must be identical EXCEPT one word is different between them.
Use only simple, familiar words: animals, food, colours, flowers, household items.
Return ONLY valid JSON in this exact format:
{"list_a": ["Word1","Word2","Word3","Word4","Word5"], "list_b": [...], "changed_in_a": "original word", "changed_in_b": "replacement word"}
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear constraint on word types (simple, familiar words)
   - Explicit JSON format requirement
   - Specific list size requirement (5 words each)
2. **Improvements**:
   - Add explicit instruction to avoid obscure or complex words
   - Consider adding a constraint to ensure the changed word is clearly different
   - Add validation for JSON response structure
3. **Safety**: Has fallback word sets from configuration if LLM fails

## Configuration
- `fallback_sets`: Array of fallback word set objects with `list_a`, `list_b`, `changed_in_a`, `changed_in_b`

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
