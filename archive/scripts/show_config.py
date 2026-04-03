#!/usr/bin/env python
"""
Show current configuration and database URL.
Usage: python scripts/show_config.py
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from app.core.config import settings, get_database_url
    
    print("=== Current Configuration ===")
    print(f"Environment: {settings.APP_ENV}")
    print()
    
    print("=== Database Configuration ===")
    print(f"POSTGRES_USER: {settings.POSTGRES_USER}")
    print(f"POSTGRES_PASSWORD: {'[HIDDEN]' if settings.POSTGRES_PASSWORD else '[NOT SET]'}")
    print(f"POSTGRES_SERVER: {settings.POSTGRES_SERVER}")
    print(f"POSTGRES_PORT: {settings.POSTGRES_PORT}")
    print(f"POSTGRES_DB: {settings.POSTGRES_DB}")
    print()
    
    database_url = get_database_url(settings)
    # Hide password in URL
    if '@' in database_url and ':' in database_url:
        parts = database_url.split('@')
        if len(parts) == 2:
            before_at = parts[0]
            after_at = parts[1]
            if ':' in before_at:
                protocol_user, password = before_at.rsplit(':', 1)
                safe_url = f"{protocol_user}:[HIDDEN]@{after_at}"
            else:
                safe_url = database_url
        else:
            safe_url = database_url
    else:
        safe_url = database_url
    
    print(f"Constructed Database URL: {safe_url}")
    print()
    
    print("=== Azure OpenAI Configuration ===")
    print(f"AZURE_OPENAI_ENDPOINT: {settings.AZURE_OPENAI_ENDPOINT}")
    print(f"AZURE_OPENAI_API_KEY: {'[HIDDEN]' if settings.AZURE_OPENAI_API_KEY else '[NOT SET]'}")
    print(f"AZURE_OPENAI_CHAT_DEPLOYMENT_NAME_DEFAULT: {settings.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME_DEFAULT}")
    print(f"AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME: {settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME}")
    print()
    
    # Check for placeholder values
    placeholder_vars = []
    if settings.POSTGRES_USER.endswith('_placeholder'):
        placeholder_vars.append('POSTGRES_USER')
    if settings.POSTGRES_PASSWORD.endswith('_placeholder'):
        placeholder_vars.append('POSTGRES_PASSWORD')
    if settings.POSTGRES_DB.endswith('_placeholder'):
        placeholder_vars.append('POSTGRES_DB')
    
    if placeholder_vars:
        print("⚠️  WARNING: The following variables have placeholder values:")
        for var in placeholder_vars:
            print(f"   - {var}")
        print()
        print("The application will use the default database connection:")
        print("postgresql+asyncpg://postgres:password@localhost:5432/ai_story_app_db_dev_default")
        print()
        
    print("=== Required Environment Variables ===")
    print("To set up a proper database connection, ensure these are set in your .env file:")
    print()
    print("# Database Configuration")
    print("POSTGRES_USER=your_postgres_username")
    print("POSTGRES_PASSWORD=your_postgres_password")
    print("POSTGRES_SERVER=localhost")
    print("POSTGRES_PORT=5432")
    print("POSTGRES_DB=your_database_name")
    print()
    print("# Azure OpenAI Configuration")
    print("AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
    print("AZURE_OPENAI_API_KEY=your_api_key")
    print("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME_DEFAULT=your_chat_model_deployment")
    print("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME=your_embedding_model_deployment")
    
except Exception as e:
    print(f"Error loading configuration: {e}")
    print("\nMake sure you're running from the project root and have a .env file configured.")