import os
import shutil
from pathlib import Path

source_dir = Path(r"C:\code2026\DailyNewsletter\backend\content_providers")
dest_dir = Path(r"c:\code2025a\inbkandquill2\app\services\care_circle\providers")

# Ensure destination exists
dest_dir.mkdir(parents=True, exist_ok=True)

for item in source_dir.iterdir():
    if item.is_dir() and item.name not in ["__pycache__"]:
        target_path = dest_dir / item.name
        if target_path.exists():
            # If the directory already exists (e.g. daily_quote, weather),
            # copy contents over without wiping it out to preserve our new provider.py
            for sub_item in item.iterdir():
                if sub_item.name == "__pycache__":
                    continue
                sub_target = target_path / sub_item.name
                if sub_item.is_dir():
                    if not sub_target.exists():
                        shutil.copytree(sub_item, sub_target)
                elif sub_item.is_file():
                    if sub_item.name == "provider.py" and item.name in ["daily_quote", "weather"]:
                        print(f"Skipping {sub_item.name} for {item.name} to preserve refactor.")
                        continue
                    shutil.copy2(sub_item, sub_target)
        else:
            # Copy whole directory for new providers
            print(f"Copying {item.name}...")
            shutil.copytree(item, target_path, ignore=shutil.ignore_patterns("__pycache__"))

print("Import complete.")
