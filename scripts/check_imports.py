import importlib
import sys
from pathlib import Path

# Add project root to sys.path so imports work
sys.path.insert(0, r"c:\code2025a\inbkandquill2")

providers_dir = Path(r"c:\code2025a\inbkandquill2\app\services\care_circle\providers")
report_file = Path(r"c:\code2025a\inbkandquill2\tests\unit\provider_import_report.txt")

failures = []

for item in providers_dir.iterdir():
    if not item.is_dir() or item.name in ["__pycache__", "themes", "whats_missing"]:
        continue
    
    module_path = f"app.services.care_circle.providers.{item.name}.provider"
    try:
        importlib.import_module(module_path)
    except Exception as e:
        failures.append(f"{item.name} failed: {type(e).__name__}: {str(e)}")

with open(report_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(failures))

print(f"Recorded {len(failures)} import failures.")
