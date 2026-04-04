import os
from pathlib import Path
import re

providers_dir = Path(r"c:\code2025a\inbkandquill2\app\services\care_circle\providers")
test_file_path = Path(r"c:\code2025a\inbkandquill2\tests\unit\test_all_imported_providers.py")

test_code = 'import pytest\nfrom app.services.care_circle.provider_base import BaseCareCircleProvider\n\n'

valid_providers = []

for item in providers_dir.iterdir():
    if item.is_dir() and item.name not in ["__pycache__", "daily_quote", "weather", "themes", "whats_missing"]:
        provider_file = item / "provider.py"
        if provider_file.exists():
            with open(provider_file, 'r', encoding='utf-8') as f:
                content = f.read()

            match = re.search(r'class\s+([A-Za-z0-9_]+)\(BaseCareCircleProvider\):', content)
            if match:
                class_name = match.group(1)
                valid_providers.append((item.name, class_name))

for folder_name, class_name in valid_providers:
    test_code += f"def test_{folder_name}_structure():\n"
    test_code += f"    from app.services.care_circle.providers.{folder_name}.provider import {class_name}\n"
    test_code += f"    provider = {class_name}()\n"
    test_code += f"    assert isinstance(provider, BaseCareCircleProvider)\n"
    test_code += f"    assert hasattr(provider, '_generate_payload')\n"
    test_code += f"    assert provider.is_safe_for_patient is False  # Safe by default\n\n"

with open(test_file_path, 'w', encoding='utf-8') as f:
    f.write(test_code)

print(f"Generated {len(valid_providers)} tests.")
