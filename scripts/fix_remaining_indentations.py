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
        
    original = content
    
    # Remove `    generate_json_with_usage,` and similar imports left over
    content = re.sub(r'^\s*generate_json_with_usage,?\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*generate_text_with_usage,?\s*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*DEMENTIA_SYSTEM_PROMPT,?\s*$', '', content, flags=re.MULTILINE)
    
    # Remove syntax error in `puzzle` caused by bad regex
    content = re.sub(r'^\s*\)\s*$\n(?=.*TRIVIA_CATEGORIES)', '', content, flags=re.MULTILINE | re.DOTALL)
    
    # Remove any standalone parenthesis right before a class or a CONSTANT
    lines = content.split('\n')
    clean_lines = []
    for line in lines:
        if line.strip() == ')' or line.strip() == '),':
            continue
        clean_lines.append(line)
        
    content = "\n".join(clean_lines)
    
    if content != original:
        with open(provider_file, 'w', encoding='utf-8') as f:
            f.write(content)
        count += 1

print(f"Fixed remaining orphaned json imports in {count} files.")
