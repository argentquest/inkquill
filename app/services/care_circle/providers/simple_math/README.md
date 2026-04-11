# Simple Math Provider

## Overview
Simple math problems with very basic arithmetic. Designed for elderly users - single digit numbers only.

## Category
Games / Math Puzzles

## AI Usage
**No - Static content only**

### How Content is Generated
- Uses Python's `random.randint()` to generate numbers based on difficulty level
- Randomly chooses addition or subtraction
- For subtraction, ensures positive result by swapping numbers if needed

### Content Sources
- Programmatically generated math problems
- Difficulty levels: easy (1-5), medium (1-9), hard (10-20)

## Configuration
- None required (difficulty level controls number ranges)

## External Dependencies
- None

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content
- Simple, recognition-based gameplay suitable for dementia care
- Difficulty levels ensure appropriate challenge
