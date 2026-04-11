# Color Match Provider

## Overview
A simple color matching game. Shows a color and the user guesses which familiar object has that color.

## Category
Games / Visual Recognition

## AI Usage
**No - Static content only**

### How Content is Generated
- Uses Python's `random.choice()` to select a color puzzle from a pre-configured list
- Each puzzle contains a color, the correct object, and multiple choice options
- All content is static and deterministic

### Content Sources
- Pre-configured color-to-object mappings (familiar items for elderly)
- Examples: Red-Apple, Yellow-Sunflower, Blue-Sky, Green-Grass, etc.

## Configuration
- `color_pairs`: Array of color puzzle objects with `color`, `object`, and `options` fields

## External Dependencies
- None

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content
- All content is pre-vetted and familiar to elderly users
- Simple, recognition-based gameplay suitable for dementia care
