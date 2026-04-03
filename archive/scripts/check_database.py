#!/usr/bin/env python
"""
Simple database connectivity checker.
Usage: python scripts/check_database.py
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_environment():
    """Check if required environment variables are set"""
    logger.info("Checking environment variables...")
    
    # Check database variables (Postgres individual vars)
    postgres_vars = [
        'POSTGRES_USER',
        'POSTGRES_PASSWORD', 
        'POSTGRES_SERVER',
        'POSTGRES_PORT',
        'POSTGRES_DB'
    ]
    
    other_vars = [
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENAI_API_KEY'
    ]
    
    missing_vars = []
    placeholder_vars = []
    
    # Check Postgres variables
    for var in postgres_vars:
        value = os.getenv(var)
        if value:
            if '_PASSWORD' in var or '_KEY' in var:
                logger.info(f"✓ {var}: [HIDDEN]")
            else:
                logger.info(f"✓ {var}: {value}")
            
            # Check for placeholder values
            if value.endswith('_placeholder'):
                placeholder_vars.append(var)
        else:
            logger.error(f"✗ {var}: Not set")
            missing_vars.append(var)
    
    # Check other required variables
    for var in other_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var or 'KEY' in var or 'SECRET' in var:
                logger.info(f"✓ {var}: [HIDDEN]")
            else:
                logger.info(f"✓ {var}: {value}")
        else:
            logger.error(f"✗ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    if placeholder_vars:
        logger.warning(f"Variables with placeholder values: {placeholder_vars}")
        logger.warning("Application will use default database connection")
    
    return True

async def test_basic_connection():
    """Test basic database connection using app config"""
    try:
        from app.core.config import settings, get_database_url
        
        # Get database URL from app configuration
        database_url = get_database_url(settings)
        
        logger.info("Testing direct database connection...")
        
        # Parse the URL to hide password in logs
        if '@' in database_url:
            before_at, after_at = database_url.split('@', 1)
            if ':' in before_at:
                protocol_user, password = before_at.rsplit(':', 1)
                safe_url = f"{protocol_user}:[HIDDEN]@{after_at}"
            else:
                safe_url = database_url
        else:
            safe_url = database_url
        
        logger.info(f"Database URL: {safe_url}")
        
        # Test connection
        import asyncpg
        conn = await asyncpg.connect(database_url)
        
        # Test simple query
        result = await conn.fetchval('SELECT 1')
        await conn.close()
        
        if result == 1:
            logger.info("✓ Direct database connection successful")
            return True
        else:
            logger.error("✗ Database query returned unexpected result")
            return False
            
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Direct database connection failed: {e}")
        logger.error("Common causes:")
        logger.error("  1. PostgreSQL server is not running")
        logger.error("  2. Database credentials are incorrect") 
        logger.error("  3. Database does not exist")
        logger.error("  4. Connection timeout or network issue")
        return False

async def test_app_connection():
    """Test database connection through app modules"""
    try:
        logger.info("Testing app database connection...")
        
        from app.core.config import settings
        from app.db.database import async_session_local
        from sqlalchemy import text
        
        async with async_session_local() as db:
            result = await db.execute(text("SELECT current_database(), current_user, version()"))
            row = result.fetchone()
            
            if row:
                logger.info(f"✓ Connected to database: {row[0]}")
                logger.info(f"✓ Connected as user: {row[1]}")
                logger.info(f"✓ PostgreSQL version: {row[2].split(' ')[0]}")
                return True
            else:
                logger.error("✗ No result from database query")
                return False
                
    except Exception as e:
        logger.error(f"✗ App database connection failed: {e}")
        return False

async def test_tables():
    """Test if main tables exist"""
    try:
        logger.info("Checking database tables...")
        
        from app.db.database import async_session_local
        from sqlalchemy import text
        
        async with async_session_local() as db:
            # Check if main tables exist
            tables_to_check = ['users', 'worlds', 'stories', 'acts', 'scenes']
            
            for table in tables_to_check:
                result = await db.execute(
                    text("SELECT count(*) FROM information_schema.tables WHERE table_name = :table_name"),
                    {"table_name": table}
                )
                count = result.scalar()
                
                if count > 0:
                    # Get row count
                    row_result = await db.execute(text(f"SELECT count(*) FROM {table}"))
                    row_count = row_result.scalar()
                    logger.info(f"✓ Table '{table}' exists with {row_count} rows")
                else:
                    logger.error(f"✗ Table '{table}' does not exist")
            
            return True
            
    except Exception as e:
        logger.error(f"✗ Table check failed: {e}")
        return False

async def main():
    """Main diagnostic function"""
    logger.info("=== Database Connectivity Checker ===")
    
    # Step 1: Check environment variables
    if not check_environment():
        logger.error("Environment check failed")
        return False
    
    # Step 2: Test direct connection
    if not await test_basic_connection():
        logger.error("Basic connection test failed")
        return False
    
    # Step 3: Test app connection
    if not await test_app_connection():
        logger.error("App connection test failed")
        return False
    
    # Step 4: Test tables
    if not await test_tables():
        logger.error("Table check failed")
        return False
    
    logger.info("=== All checks passed! ===")
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if not result:
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Checker failed: {e}")
        sys.exit(1)