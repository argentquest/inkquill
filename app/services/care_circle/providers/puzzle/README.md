# Puzzle Provider

## Overview
Multi-faceted puzzle provider. Randomly dispatches to one of three mini-puzzle sub-generators: word search, fill-in-the-blank, or word-pair intersect. Each result includes a pre-rendered `puzzle_content` HTML field so the template can render it without needing complex logic.

## Category
Games / Multi-Puzzle

## AI Usage
**No - Static content only**

### How Content is Generated
- Uses Python's `random.choice()` to select between three puzzle types:
  1. **Word Search**: Uses `word_search_generator` library to generate word search puzzles
  2. **Fill-in-the-Blank**: Selects from pre-configured phrase/answer pairs
  3. **Word Pair**: Selects from pre-configured intersecting word pairs with clues
- Each puzzle type includes pre-rendered HTML content

### Content Sources
- Word search: Generated programmatically using `word_search_generator` library
- Fill-in-the-blank: Pre-configured prompts
- Word pair: Pre-configured word pairs with clues

## Configuration
- `default_words`: Default words for word search
- `grid_size`: Word search grid size (default: 10)
- `fill_in_the_blank_prompts`: Array of phrase/answer objects
- `word_pairs`: Array of word pair objects with clues

## External Dependencies
- `word_search_generator` library

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content
- All puzzles are pre-vetted or programmatically generated
- Multiple puzzle types for variety
