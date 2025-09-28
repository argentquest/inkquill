#!/usr/bin/env python3
"""
Copy environment variables from .env file to Azure App Service
"""

import os
import sys
import subprocess
from typing import Dict


def read_env_file(filepath: str) -> Dict[str, str]:
    """Read environment variables from a .env file."""
    env_vars = {}
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if line and not line.startswith('#'):
                    # Handle KEY=VALUE format
                    if '=' in line:
                        key, value = line.split('=', 1)
                        # Remove quotes if present
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        env_vars[key] = value
    except FileNotFoundError:
        print(f"Error: File {filepath} not found.")
        sys.exit(1)
    
    return env_vars


def set_azure_app_settings(app_name: str, resource_group: str, env_vars: Dict[str, str]):
    """Set environment variables (app settings) in Azure App Service."""
    # Build the settings string
    settings = []
    for key, value in env_vars.items():
        # Escape special characters
        value = value.replace('"', '\\"')
        settings.append(f'{key}="{value}"')
    
    settings_str = ' '.join(settings)
    
    # Execute Azure CLI command
    cmd = [
        'az', 'webapp', 'config', 'appsettings', 'set',
        '--name', app_name,
        '--resource-group', resource_group,
        '--settings', settings_str
    ]
    
    try:
        print(f"Setting {len(env_vars)} environment variables in Azure App Service...")
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print(f"Successfully updated {len(env_vars)} app settings for {app_name}")
        else:
            print(f"Error: {result.stderr}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error executing Azure CLI: {e}")
        sys.exit(1)


def main():
    print("Azure App Service Environment Variables Copier")
    print("=" * 50)
    
    # Get input values from user
    env_file = input("\nEnter the path to your .env file (e.g., .env): ").strip()
    if not env_file:
        env_file = ".env"  # Default to .env
    
    # Read environment variables from file
    print(f"\nReading environment variables from {env_file}...")
    env_vars = read_env_file(env_file)
    print(f"Found {len(env_vars)} environment variables")
    
    # Show preview of variables
    print("\nPreview of environment variables found:")
    for i, (key, value) in enumerate(sorted(env_vars.items())):
        if i < 5:  # Show first 5
            masked_value = value[:3] + '***' if len(value) > 3 else '***'
            print(f"  {key}={masked_value}")
        elif i == 5:
            print(f"  ... and {len(env_vars) - 5} more variables")
            break
    
    # Get Azure details
    print("\nEnter Azure App Service details:")
    app_name = input("App Service name: ").strip()
    resource_group = input("Resource Group name: ").strip()
    
    # Confirm before proceeding
    print(f"\nReady to copy {len(env_vars)} environment variables to:")
    print(f"  App Service: {app_name}")
    print(f"  Resource Group: {resource_group}")
    
    confirm = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Operation cancelled.")
        return
    
    # Check if Azure CLI is installed
    try:
        subprocess.run(['az', '--version'], capture_output=True, check=True)
    except:
        print("\nError: Azure CLI is not installed or not in PATH")
        print("Please install Azure CLI: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli")
        sys.exit(1)
    
    # Set the app settings
    set_azure_app_settings(app_name, resource_group, env_vars)
    print("\nDone! Your app settings have been updated.")


if __name__ == '__main__':
    main()