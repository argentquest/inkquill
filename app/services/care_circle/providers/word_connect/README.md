# Word Connect Provider

## Overview
A word connection puzzle - connect related words. Shows pairs of related words, user identifies the connection.

## Category
Games / Word Puzzles

## AI Usage
**No - Static content only**

### How Content is Generated
- Uses Python's `random.sample()` to select 4 word pairs from a pre-configured list
- Each pair has two related words and their connection description
- All content is static and pre-configured

### Content Sources
- Pre-configured word pairs with connections (e.g., Sun-Sky "Both are in the sky", Cat-Meow "Cats say meow")

## Configuration
- `word_pairs`: Array of word pair objects with `word1`, `word2`, and `connection` fields

## External Dependencies
- None

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content
- All word pairs are pre-vetted and familiar
- Simple, recognition-based gameplay suitable for dementia care
