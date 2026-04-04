import os
from pathlib import Path

providers_dir = Path(r"c:\code2025a\inbkandquill2\app\services\care_circle\providers")

replacement_count = 0

for item in providers_dir.iterdir():
    if item.is_dir() and item.name not in ["__pycache__", "daily_quote", "weather"]:
        provider_file = item / "provider.py"
        if provider_file.exists():
            with open(provider_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if "BaseCareCircleProvider" in content:
                continue # Already migrated
            
            # Replace BaseContent import
            content = content.replace("from content_providers.base import BaseContent", "from app.services.care_circle.provider_base import BaseCareCircleProvider\nfrom typing import Any, Dict")
            
            # Replace Class Inheritance
            content = content.replace("(BaseContent):", "(BaseCareCircleProvider):\n    is_safe_for_patient = False\n")
            
            # Replace method signature
            content = content.replace("def get_content(self, **kwargs) -> dict:", "def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:")
            
            # Quick patch for self.config to self.patient_config
            content = content.replace("cfg = self.config", "cfg = self.patient_config")
            
            # Quick patch for self.profile to patient_profile
            content = content.replace("self.profile.get", "getattr(patient_profile, 'preferences', {}).get")
            
            with open(provider_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            replacement_count += 1

print(f"Mechanically patched {replacement_count} provider.py files to new BaseCareCircleProvider structure.")
