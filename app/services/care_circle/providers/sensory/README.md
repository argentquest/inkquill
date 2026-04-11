# Sensory Provider

## Overview
Suggests a simple grounding or sensory activity for the user. Rotates across all five senses (hearing, touch, smell, taste, sight). Personalises with favourite singers, foods, pets, hometown, and mobility level when available.

## Category
Wellbeing / Sensory Activities

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_text_with_usage()` to generate a simple sensory activity suggestion
- Rotates across five sensory modes for variety
- Content is personalized based on patient preferences (favourite singers, foods, pets, hometown, mobility level)

### Prompt Analysis
```
Suggest one simple sensory activity for {name} using the sense of {mode['key']}.
{mode['prompt_hint']}
{extra_str}
Keep it to 1 short sentence. Be specific and gentle.
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear constraint (1 short sentence)
   - Sense-specific prompt hints guide appropriate content
   - Personalized with patient preferences
2. **Improvements**:
   - Add explicit instruction to avoid potentially overwhelming sensory suggestions
   - Consider adding a constraint to ensure activities are accessible for seated patients
   - Add validation for output length and tone
3. **Safety**: Has fallback suggestions from configuration if LLM fails

## Configuration
- `default_singer`: Fallback singer (default: "Frank Sinatra")
- `suggestions`: Array of fallback suggestions

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
