# Odd One Out Provider

## Overview
Odd One Out Logic Game - Categorization puzzle. Engages categorization skills without requiring writing - the user can just point to or circle the answer. Three items from one category plus one from a different category, shuffled randomly.

## Category
Games / Logic Puzzles

## AI Usage
**No - Static content only**

### How Content is Generated
- Uses Python's `random.choice()` and `random.sample()` to select categories and items
- Picks two different categories, selects 3 items from main category and 1 from odd category
- Shuffles items randomly

### Content Sources
- Pre-configured categories with item lists
- Family member names can be added as a category if available

## Configuration
- `categories`: Dictionary of category names to item arrays

## External Dependencies
- None

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content
- Recognition-based gameplay suitable for dementia care
- Simple pointing/circling interaction
