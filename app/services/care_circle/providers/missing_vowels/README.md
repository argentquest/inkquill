# Missing Vowels Provider

## Overview
Missing Vowels Puzzle - Recognition-based word puzzle. Strips vowels (A, E, I, O, U) from familiar words, letting the brain fill in the shapes. This taps into recognition memory rather than recall, making it accessible for dementia care.

## Category
Games / Word Puzzles

## AI Usage
**No - Static content only**

### How Content is Generated
- Builds a personalized word pool from family members, favorite activities, and default words
- Strips vowels from a randomly selected word
- Uses Python's `random.choice()` for word selection

### Content Sources
- Family member names from patient preferences
- Favorite activities from patient preferences
- Default word bank from configuration

## Configuration
- `words`: Array of default words for the puzzle

## External Dependencies
- None

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content
- Recognition-based gameplay suitable for dementia care
- Personalized word pool increases familiarity and success rate
