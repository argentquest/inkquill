# Complete the Duo Provider

## Overview
Shows one half of a well-known pair and asks the reader to complete it. Pure recognition — almost impossible to get wrong. No LLM required. Pairs are selected daily via a stable date-hash so all profiles see the same set each day.

## Category
Games / Word Puzzles

## AI Usage
**No - Static content only**

### How Content is Generated
- Uses a stable date-hash to select pairs consistently throughout the day
- All users see the same pairs on the same day
- Uses Python's `random.Random(seed).sample()` for deterministic selection

### Content Sources
- Pre-configured pairs from configuration (e.g., "Salt" / "Pepper", "Peanut Butter" / "Jelly")

## Configuration
- `pairs`: Array of famous pairs with `prompt` and `answer` fields
- `pairs_per_day`: Number of pairs to show per day (default: 4)

## External Dependencies
- None

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content
- All pairs are pre-vetted famous pairs
- Simple, recognition-based gameplay suitable for dementia care
