# Song of the Day Provider

## Overview
Curates a daily song recommendation. Selects a song from the user's favourite singers, attempts to locate album art from TheAudioDB, and uses an LLM to write a nostalgic, warm fact about the track.

## Category
Memory / Music

## AI Usage
**Yes - LLM-generated content (partial)**

### How AI is Used
- Uses `generate_text_with_usage()` to generate a warm memory fact about the song
- Album art fetched from TheAudioDB API (no AI)
- Song selection is from pre-configured artist data

### Prompt Analysis
```
Write a 1-sentence, warm memory about the song '{song_title}' by {singer}.
Make it feel nostalgic and comforting.
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear constraint (1 sentence)
   - Specific song and artist context
   - Nostalgic tone requirement
2. **Improvements**:
   - Add explicit instruction to avoid potentially distressing memories
   - Consider adding a constraint to ensure factual accuracy about the song
   - Add validation for output length
3. **Safety**: Has fallback text if LLM fails

## Configuration
- `artists`: Array of artist objects with `name`, `songs`, and `era`

## External Dependencies
- TheAudioDB API: `https://www.theaudiodb.com/api/v1/json/2/search.php?s={singer}`

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
