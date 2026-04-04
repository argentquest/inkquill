import os
import re
from pathlib import Path

providers_dir = Path(r"c:\code2025a\inbkandquill2\app\services\care_circle\providers")
count = 0

for item in providers_dir.iterdir():
    if not item.is_dir() or item.name in ["__pycache__", "themes", "whats_missing"]:
        continue
    
    provider_file = item / "provider.py"
    if not provider_file.exists():
        continue
        
    with open(provider_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Remove orphaned lines from the multi-line import
    # Usually they look like:
    #     generate_text_with_usage,
    #     DEMENTIA_SYSTEM_PROMPT,
    # )
    # We can just remove these specific strings anywhere they appear outside a function.
    # Actually, a regex that removes them from the top of the file:
    content = re.sub(r'^\s*generate_text_with_usage,?\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*DEMENTIA_SYSTEM_PROMPT,?\s*$', '', content, flags=re.MULTILINE)
    
    # We also need to remove the standalone closing parenthesis if it's left orphaned
    # A standalone `)` on a line by itself before the class definition:
    content = re.sub(r'^\s*\)\s*$\n(?=.*class )', '', content, flags=re.MULTILINE | re.DOTALL)
    
    with open(provider_file, 'w', encoding='utf-8') as f:
        f.write(content)
    count += 1

print(f"Fixed orphaned imports in {count} files.")
