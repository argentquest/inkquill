# Nature Scene Provider

## Overview
Generates a calming nature scene: AI text description followed by an AI image generated from that same description. The image prompt is derived directly from the generated text so the image and description always match.

## Category
Memory / Visual Relaxation

## AI Usage
**Yes - LLM-generated content and AI image generation**

### How AI is Used
- **Step 1**: Uses `generate_text_with_usage()` to generate a descriptive nature scene (2 short, warm sentences)
- **Step 2**: Uses `generate_text_with_usage()` to convert the description into an image generation prompt
- **Step 3**: Uses `generate_image_url_with_usage()` to generate an image from the prompt

### Prompt Analysis

**Text Description Prompt:**
```
Describe this peaceful scene in 2 short, warm sentences: {theme}.
Mention one colour and one gentle sound or smell.
Make it feel like a cozy, happy moment.
```

**Image Prompt Conversion:**
```
Turn this into a short image generation prompt (15 words max),
no people, peaceful outdoor scene: "{description}"
```

### Prompt Recommendations
1. **Strengths**: 
   - Clear constraints on length and tone
   - Image prompt derived from text ensures consistency
   - Multiple fallback layers for reliability
2. **Improvements**:
   - Add explicit instruction to avoid potentially distressing imagery
   - Consider adding a constraint to ensure seasonal appropriateness
   - Add validation for image URL response
3. **Safety**: Has comprehensive fallbacks for both text and image generation

## Configuration
- `descriptions`: Array of fallback descriptions
- `image_width`, `image_height`: Dimensions for fallback images

## External Dependencies
- Image generation service (via `generate_image_url_with_usage`)

## Patient Safety
- `is_safe_for_patient = True`
- Uses dementia-care appropriate system prompt
- Falls back gracefully to static content on LLM failure
- Fallback to picsum.photos for image generation failure
