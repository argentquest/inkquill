# Gentle Exercise Provider

## Overview
Provides a simple, low-impact exercise recommendation via static configuration.

## Category
Wellbeing / Physical Activity

## AI Usage
**No - Static content only**

### How Content is Generated
- Uses Python's `random.choice()` to select an exercise from a pre-configured list
- Each exercise has `name`, `steps`, and `benefit` fields
- All content is static and pre-configured

### Content Sources
- Pre-configured exercise list from configuration

## Configuration
- `exercises`: Array of exercise objects with `name`, `steps`, and `benefit` fields

## External Dependencies
- None

## Patient Safety
- `is_safe_for_patient = True`
- No AI-generated content
- All exercises are pre-vetted as gentle and appropriate for elderly users
- Seated, low-impact activities only
