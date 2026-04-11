# Brain Booster Provider

## Overview
Generates gentle cognitive exercises using a Large Language Model. Rotates across four question types — phrase completion, either/or, name three, and true/false — to keep content fresh day to day.

## Category
Games / Cognitive Exercises

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_json_with_usage()` to generate thinking activities
- Returns JSON with `type`, `prompt`, and optionally `answer` fields
- Content is personalized based on the patient's era of youth

### Prompt Analysis
```
Create one fun, gentle thinking activity for someone who grew up in the {era}.
Use this type: {qt['label']} ({qt['example']}).
The activity must feel easy and fun, never like a test.
Return as JSON: {"type": "{qt["key"]}", "prompt": "...", {answer_field}}
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear instruction that activity must feel "easy and fun, never like a test"
   - Rotates across multiple question types for variety
   - Era-based personalization
2. **Improvements**:
   - Add explicit instruction to avoid topics that could trigger negative memories
   - Consider adding a constraint to ensure answers are common knowledge
   - Add validation for JSON response structure
3. **Safety**: Has fallback content from configuration if LLM fails

## Configuration
- `prompts`: Array of fallback prompts organized by type

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
- Designed to be recognition-based rather than recall-based
