# Nostalgia Provider

## Overview
Generates personalized nostalgic memories using a Large Language Model. Rotates across six topic areas (food, music/dance, neighbourhood, fashion, entertainment, school/work) to bring different warm memories each day. Personalises with nationality, hometown, life roles, favourite foods and TV shows when available.

## Category
Memory / Nostalgia

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Uses `generate_text_with_usage()` to generate a happy memory from a specific era
- Rotates across six nostalgia topics for variety
- Content is personalized based on patient preferences (nationality, hometown, life roles, favourite foods, TV shows)

### Prompt Analysis
```
Write a happy memory from the {era} for {name}.
{topic['hint']}
{context_str}
Keep it to 2 short sentences. Make it feel cozy and familiar.
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear constraint (2 short sentences)
   - Topic-specific hints guide appropriate content
   - Rich personalization from patient preferences
2. **Improvements**:
   - Add explicit instruction to avoid potentially distressing memories
   - Consider adding a constraint to ensure universally positive content
   - Add validation for output length and tone
3. **Safety**: Has fallback content from era-specific facts if LLM fails

## Configuration
- `default_era`: Fallback era when not specified (default: "1950s")
- `facts`: Era-specific fallback facts
- `fallback`: General fallback text

## External Dependencies
- None (uses LLM only)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
