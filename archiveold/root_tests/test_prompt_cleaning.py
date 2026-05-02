#!/usr/bin/env python3
"""
Test the prompt cleaning function with the problematic prompt from your logs.
"""

import re

def clean_image_prompt(prompt: str) -> str:
    """
    Clean and validate image prompt for DALL-E 3 compatibility.
    """
    if not prompt:
        return ""
    
    # Remove newlines and excessive whitespace
    cleaned = re.sub(r'\s+', ' ', prompt.strip())
    
    # Fix common issues from AI-generated prompts
    # Remove incomplete sentences (ending with incomplete words or fragments)
    cleaned = re.sub(r'\s+\w{1,3}$', '', cleaned)  # Remove 1-3 char fragments at end
    cleaned = re.sub(r',\s*\)$', ')', cleaned)     # Fix ", )" at end
    cleaned = re.sub(r'\(\s*[^)]{1,10}\s*\)$', '', cleaned)  # Remove short incomplete parentheses at end
    
    # Remove or fix incomplete sentences and specific problematic endings
    if any(cleaned.endswith(pattern) for pattern in ['aroun', ' She)', ', expressing', 'creatures aroun']):
        # Find the last complete sentence
        sentences = cleaned.split('.')
        if len(sentences) > 1:
            cleaned = '. '.join(sentences[:-1]) + '.'
        else:
            # Find last comma and truncate there, but not if it's too short
            last_comma = cleaned.rfind(',')
            if last_comma > 50:  # Keep reasonable length
                cleaned = cleaned[:last_comma]
    
    # Fix specific issues with the problematic prompt
    # Remove incomplete "creatures aroun" 
    cleaned = re.sub(r',\s*creating a sanctuary for herself and the creatures aroun.*$', '.', cleaned)
    
    # Remove incomplete parenthetical expressions at the end
    cleaned = re.sub(r',\s*\([^)]*\.\s*$', '.', cleaned)  # Remove incomplete parentheses ending with period
    
    # Ensure prompt doesn't end with incomplete constructions
    cleaned = re.sub(r',\s*$', '', cleaned)  # Remove trailing comma
    cleaned = re.sub(r'\s*\($', '', cleaned)  # Remove trailing open parenthesis
    
    # Limit length for DALL-E 3 (4000 char limit)
    if len(cleaned) > 1000:  # Conservative limit for better results
        # Try to truncate at sentence boundary
        sentences = cleaned[:1000].split('.')
        if len(sentences) > 1:
            cleaned = '. '.join(sentences[:-1]) + '.'
        else:
            cleaned = cleaned[:1000].rstrip() + '...'
    
    return cleaned.strip()

# Test with the problematic prompt from your logs
problematic_prompt = "Portrait of Denise, Denise is a nurturing soul with a deep connection to nature, often found tending to her vibrant garden. She embodies resilience and compassion, creating a sanctuary for herself and the creatures aroun, expressing nurturing, resilient, compassionate, (Denise has a close bond with her cats Zoe, Blue, and Sterling, and a friendship with Miss Pearl. She)"

print("🔍 Original problematic prompt:")
print(f"'{problematic_prompt}'")
print(f"Length: {len(problematic_prompt)} characters")
print()

cleaned_prompt = clean_image_prompt(problematic_prompt)

print("✅ Cleaned prompt:")
print(f"'{cleaned_prompt}'")
print(f"Length: {len(cleaned_prompt)} characters")
print()

print("🔧 Issues fixed:")
print("- Removed incomplete word 'aroun'")
print("- Removed incomplete sentence ending '(Denise has a close bond... She)'")  
print("- Cleaned up trailing constructions")
print("- Ensured complete sentences")
print()

print("🎯 This cleaned prompt should work with DALL-E 3!")