#!/usr/bin/env python3
"""
Script to run alembic migrations directly
"""
import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from alembic.config import Config
    from alembic import command

    def run_migration():
        """Run alembic upgrade head"""
        print("Running alembic upgrade head...")
        try:
            # Load alembic config
            alembic_cfg = Config("alembic.ini")
            print("Alembic config loaded")

            # Run upgrade to latest
            command.upgrade(alembic_cfg, "head")
            print("✅ Migration completed successfully!")

        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False

        return True

    if __name__ == "__main__":
        success = run_migration()
        sys.exit(0 if success else 1)

except ImportError as e:
    print(f"❌ Failed to import alembic: {e}")
    print("Try installing with: pip install alembic==1.16.1")
    sys.exit(1)