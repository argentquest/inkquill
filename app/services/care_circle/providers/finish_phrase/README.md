# Finish Phrase Provider

## Overview
Finish the Phrase Puzzle - Idioms & Lyrics completion. Phrases are era-tagged so the selection is weighted toward the user's generation, with universal idioms always available as fallback.

## Category
Games / Word Puzzles

## AI Usage
**No - Static content only**

### How Content is Generated
- Uses Python's `random.choice()` to select a phrase from a filtered pool
- Filters phrases by era of youth when available
- All content is static and pre-configured

### Content Sources
- Pre-configured phrase bank with era tags
- Each phrase has `phrase`, `answer`, `category`, and optional `era` and `artist` fields

## Configuration
- `phrases`: Array of phrase objects with `phrase`, `answer`, `category`, `era`, and optional `artist`

## External Dependencies
- None

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content
- All phrases are pre-vetted and familiar
- Era-based selection increases relevance and success rate
