# Simple Recipe Provider

## Overview
Generates a very simple, nostalgic recipe with 3-4 steps using an LLM. Rotates across five recipe categories (baked treat, warm drink, simple dessert, soup/stew, light snack) to keep content fresh day to day.

## Category
Lifestyle / Cooking

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_json_with_usage()` to generate a simple recipe
- Rotates across five recipe categories for variety
- Returns JSON with `name`, `ingredients`, and `steps` fields

### Prompt Analysis
```
Think of {category['label']} from the {era}.
It should use common ingredients everyone has at home.
The steps should be very short and easy to follow (3-4 steps max).
Each step should be one short sentence.
Return as JSON: {"name": "...", "ingredients": "...", "steps": "..."}
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear constraint on steps (3-4 steps max, one short sentence each)
   - Era-based personalization
   - JSON output format requirement
2. **Improvements**:
   - Add explicit instruction to avoid complex or hard-to-find ingredients
   - Consider adding a constraint to ensure steps are safe and simple
   - Add validation for JSON response structure
3. **Safety**: Has fallback recipes from configuration if LLM fails

## Configuration
- `recipes`: Array of fallback recipe objects with `name`, `ingredients`, and `steps`

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
