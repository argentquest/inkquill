#!/usr/bin/env python3
"""
Maintenance Mode Control Script
Usage:
  python maintenance_control.py enable [message] [duration_minutes]
  python maintenance_control.py disable
  python maintenance_control.py status

Examples:
  python maintenance_control.py enable "System maintenance in progress" 10
  python maintenance_control.py enable
  python maintenance_control.py disable
  python maintenance_control.py status
"""

import sys
import argparse
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.maintenance import MaintenanceManager

def main():
    parser = argparse.ArgumentParser(description="Control maintenance mode for the application")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Enable command
    enable_parser = subparsers.add_parser('enable', help='Enable maintenance mode')
    enable_parser.add_argument('message', nargs='?', 
                              default="The application is getting an update and will be back in about 5 minutes.",
                              help='Maintenance message to display (optional)')
    enable_parser.add_argument('duration', nargs='?', type=int, default=5,
                              help='Duration in minutes (optional, default: 5)')
    
    # Disable command
    subparsers.add_parser('disable', help='Disable maintenance mode')
    
    # Status command
    subparsers.add_parser('status', help='Check maintenance status')
    
    args = parser.parse_args()
    
    if args.command == 'enable':
        MaintenanceManager.set_maintenance_mode(
            enabled=True,
            message=args.message,
            duration_minutes=args.duration
        )
        print(f"✅ Maintenance mode ENABLED")
        print(f"   Message: {args.message}")
        print(f"   Duration: {args.duration} minutes")
        
    elif args.command == 'disable':
        MaintenanceManager.set_maintenance_mode(enabled=False)
        print("✅ Maintenance mode DISABLED")
        
    elif args.command == 'status':
        status = MaintenanceManager.get_maintenance_status()
        if status.get('enabled'):
            print("🔧 Maintenance mode is ACTIVE")
            print(f"   Message: {status.get('message', 'No message')}")
            if status.get('estimated_end_time'):
                print(f"   Estimated end: {status.get('estimated_end_time')}")
        else:
            print("✅ Maintenance mode is INACTIVE")
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()