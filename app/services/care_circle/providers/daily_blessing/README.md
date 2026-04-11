# Daily Blessing Provider

## Overview
Provides a simple, warm blessing or prayer each day. Gentle and uplifting content for elderly users.

## Category
Wellbeing / Spiritual

## AI Usage
**No - Static content only**

### How Content is Generated
- Uses day-of-year based selection for consistency
- Same blessing shown to all users on the same day
- Uses Python's `date.today().timetuple().tm_yday` for deterministic selection

### Content Sources
- Pre-configured blessings array (20 blessings)
- Examples: "May your day be filled with gentle joy and peaceful moments."

## Configuration
- `blessings`: Array of blessing strings

## External Dependencies
- None

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content
- All blessings are pre-vetted and appropriate for dementia care
- Gentle, non-denominational spiritual content
