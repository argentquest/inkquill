# Bingo Provider

## Overview
A 5x5 bingo card with familiar words. Designed for elderly users with familiar, easy-to-recognize items.

## Category
Games / Word Puzzles

## AI Usage
**No - Static content only**

### How Content is Generated
- Uses Python's `random.sample()` to select 24 words from a configurable word bank
- Inserts "FREE" in the center position (position 12)
- Splits words into 5 rows for a 5x5 bingo card

### Content Sources
- Pre-configured word bank containing familiar words (sun, moon, dog, cat, apple, bread, etc.)
- All content is static and deterministic

## Configuration
- `word_bank`: Array of familiar words for the bingo card (30+ words recommended)

## External Dependencies
- None

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content
- All words are pre-vetted and familiar to elderly users
- Simple, recognition-based gameplay suitable for dementia care
