# /ai_rag_story_app/app/core/maintenance.py

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Maintenance file path
MAINTENANCE_FILE_PATH = Path("maintenance_status.json")

class MaintenanceManager:
    """Simple maintenance mode manager using a JSON file"""
    
    @staticmethod
    def set_maintenance_mode(
        enabled: bool = True,
        message: str = "The application is getting an update and will be back in about 5 minutes.",
        duration_minutes: int = 5
    ) -> None:
        """Enable or disable maintenance mode"""
        maintenance_data = {
            "enabled": enabled,
            "message": message,
            "start_time": datetime.now().isoformat() if enabled else None,
            "estimated_end_time": (datetime.now() + timedelta(minutes=duration_minutes)).isoformat() if enabled else None,
            "duration_minutes": duration_minutes if enabled else None
        }
        
        try:
            with open(MAINTENANCE_FILE_PATH, 'w') as f:
                json.dump(maintenance_data, f, indent=2)
            logger.info(f"Maintenance mode {'enabled' if enabled else 'disabled'}")
        except Exception as e:
            logger.error(f"Failed to update maintenance status: {e}")
    
    @staticmethod
    def get_maintenance_status() -> Dict[str, Any]:
        """Get current maintenance status"""
        try:
            if not MAINTENANCE_FILE_PATH.exists():
                return {"enabled": False, "message": None}
            
            with open(MAINTENANCE_FILE_PATH, 'r') as f:
                data = json.load(f)
            
            # Auto-disable if estimated end time has passed
            if data.get("enabled") and data.get("estimated_end_time"):
                estimated_end = datetime.fromisoformat(data["estimated_end_time"])
                if datetime.now() > estimated_end:
                    logger.info("Maintenance window has expired, auto-disabling maintenance mode")
                    MaintenanceManager.set_maintenance_mode(enabled=False)
                    return {"enabled": False, "message": None}
            
            return data
        except Exception as e:
            logger.error(f"Failed to read maintenance status: {e}")
            return {"enabled": False, "message": None}
    
    @staticmethod
    def is_maintenance_active() -> bool:
        """Check if maintenance mode is currently active"""
        status = MaintenanceManager.get_maintenance_status()
        return status.get("enabled", False)
    
    @staticmethod
    def get_maintenance_message() -> Optional[str]:
        """Get the current maintenance message"""
        status = MaintenanceManager.get_maintenance_status()
        return status.get("message") if status.get("enabled") else None