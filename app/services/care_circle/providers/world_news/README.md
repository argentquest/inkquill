# World News Provider

## Overview
Fetches the top 3 headlines from a public RSS feed and uses the LLM to produce a short, plain-language summary (≤ 20 words) for each story.

## Category
Core / Current Events

## AI Usage
**Yes - LLM-generated content**

### How AI is Used
- Fetches RSS feed from BBC News World
- Uses `generate_text_with_usage()` to simplify each headline/description into a ≤ 20-word summary
- Returns 3 stories with title and simplified summary

### Prompt Analysis
```
News headline: {title}
Details: {description}

Write ONE sentence of 20 words or fewer. Rules:
- One idea only — do not combine multiple facts.
- Short, common words — no jargon or complex vocabulary.
- Present tense (e.g. 'Leaders meet' not 'Leaders met').
- Plain English only — as if explaining to a 10-year-old.
Output the sentence only, no preamble.
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear constraint (20 words or fewer, one sentence)
   - Specific rules for simplicity (short words, present tense, plain English)
   - Explicit instruction to avoid jargon and complex vocabulary
2. **Improvements**:
   - Add explicit instruction to avoid potentially distressing or violent news
   - Consider adding a filter for positive/neutral news only
   - Add validation for output length
3. **Safety**: Falls back to truncated description if LLM fails

## Configuration
- `rss_url`: RSS feed URL (default: BBC News World)
- `item_count`: Number of headlines to fetch (default: 3)
- `fallback_stories`: Array of fallback stories

## External Dependencies
- BBC News RSS: `https://feeds.bbci.co.uk/news/world/rss.xml`

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to truncated descriptions on LLM failure
- Note: News content may contain distressing topics - consider content filtering
