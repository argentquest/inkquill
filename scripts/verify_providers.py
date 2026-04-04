import os
import sys
import importlib
import traceback
from pathlib import Path

# Add project root to sys.path so imports work
sys.path.insert(0, r"c:\code2025a\inbkandquill2")

from app.services.care_circle.provider_base import BaseCareCircleProvider

providers_dir = Path(r"c:\code2025a\inbkandquill2\app\services\care_circle\providers")
report_path = Path(r"C:\Users\Hack\.gemini\antigravity\brain\bfde2ba2-cee6-4bce-9603-6020c421d7d2\care_circle_provider_verification.md")

results = []

for item in providers_dir.iterdir():
    if not item.is_dir() or item.name == "__pycache__":
        continue
    
    provider_name = item.name
    provider_file = item / "provider.py"
    
    if not provider_file.exists():
        results.append(f"| {provider_name} | ❌ Missing provider.py | - | - |")
        continue

    # Try to dynamically import the module
    module_path = f"app.services.care_circle.providers.{provider_name}.provider"
    
    try:
        module = importlib.import_module(module_path)
        
        # Find the class that inherits from BaseCareCircleProvider
        provider_class = None
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and issubclass(attr, BaseCareCircleProvider) and attr is not BaseCareCircleProvider:
                provider_class = attr
                break
                
        if not provider_class:
            results.append(f"| {provider_name} | ❌ No Valid Class | - | - |")
            continue
            
        # Instantiate and check
        instance = provider_class()
        
        has_generate = hasattr(instance, '_generate_payload')
        safety = getattr(instance, 'is_safe_for_patient', 'Unknown')
        
        if has_generate and safety in [True, False]:
            results.append(f"| {provider_name} | ✅ Passed | `{provider_class.__name__}` | {safety} |")
        else:
            results.append(f"| {provider_name} | ❌ Invalid Structure | `{provider_class.__name__}` | {safety} |")
            
    except Exception as e:
        error_msg = str(e).replace('\n', ' ')[:60]
        results.append(f"| {provider_name} | ❌ Error: {error_msg} | - | - |")

# Write Report
report = """# Care Circle Provider Verification Report

| Provider Folder | Status | Discovered Class | Safe For Patient |
|-----------------|--------|------------------|------------------|
"""
report += "\n".join(results)

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"Verification complete. Check artifacts for detailed report.")
