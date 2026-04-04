import os
import re
from pathlib import Path

source_dir = Path(r"C:\code2026\DailyNewsletter\backend\content_providers")
dest_dir = Path(r"c:\code2025a\inbkandquill2\app\services\care_circle\providers")

def to_camel_case(snake_str):
    components = snake_str.split('_')
    return "".join(x.title() for x in components)

replacement_count = 0

for item in source_dir.iterdir():
    if not item.is_dir() or item.name in ["__pycache__", "daily_quote", "weather", "themes", "whats_missing"]:
        continue
        
    source_file = item / "provider.py"
    dest_file = dest_dir / item.name / "provider.py"
    
    if source_file.exists() and dest_file.exists():
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # REMOVE the entire multiline LLM import first!
        # It looks like: from content_providers.llm_service import (\n    generate_text_with_usage,\n    DEMENTIA_SYSTEM_PROMPT,\n)
        content = re.sub(r'from content_providers\.llm_service import\s*\([^)]*\)', '', content)
        # Also catch single-line variations
        content = re.sub(r'from content_providers\.llm_service import[^\n]*\n', '', content)
        # Also clean up `from toolkits`
        content = re.sub(r'from toolkits[^\n]*\n', '', content)
        
        # Now process line by line safely for the rest
        lines = content.split('\n')
        clean_lines = []
        for line in lines:
            if "from content_providers.base import BaseContent" in line:
                clean_lines.append("import logging")
                clean_lines.append("app_logger = logging.getLogger(__name__)")
                clean_lines.append("from app.services.care_circle.provider_base import BaseCareCircleProvider")
                clean_lines.append("from typing import Any, Dict")
            else:
                clean_lines.append(line)
        
        content = "\n".join(clean_lines)

        content = content.replace("def get_content(self, **kwargs) -> dict:", "def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:")
        content = content.replace("cfg = self.config", "cfg = self.patient_config")
        content = content.replace("self.profile.get", "getattr(patient_profile, 'preferences', {}).get")

        expected_class_name = to_camel_case(item.name) + "Provider"
        class_regex = r"class\s+([A-Za-z0-9_]+)\(BaseContent\):"
        
        def replace_class_def(match):
            return f"class {expected_class_name}(BaseCareCircleProvider):\n    is_safe_for_patient = False\n"
            
        content = re.sub(class_regex, replace_class_def, content)

        with open(dest_file, 'w', encoding='utf-8') as f:
            f.write(content)
            
        replacement_count += 1

print(f"Purged LLM imports perfectly and standardized {replacement_count} providers.")
