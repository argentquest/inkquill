#!/usr/bin/env python
"""
Direct database connection test with timeout and better error handling.
Usage: python scripts/test_db_direct.py
"""

import asyncio
import asyncpg
import logging
import sys
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

async def test_direct_connection():
    """Test direct connection to Azure PostgreSQL with timeout"""
    try:
        from app.core.config import settings
        
        # Build connection URL
        user = settings.POSTGRES_USER
        password = settings.POSTGRES_PASSWORD
        server = settings.POSTGRES_SERVER
        port = settings.POSTGRES_PORT
        db_name = settings.POSTGRES_DB
        
        logger.info("=== Database Connection Test ===")
        logger.info(f"Server: {server}")
        logger.info(f"Port: {port}")
        logger.info(f"Database: {db_name}")
        logger.info(f"User: {user}")
        logger.info("Password: [HIDDEN]")
        
        # Construct connection URL
        connection_url = f"postgresql://{user}:{password}@{server}:{port}/{db_name}"
        
        logger.info("Attempting connection with 30 second timeout...")
        
        # Try to connect with timeout
        try:
            conn = await asyncio.wait_for(
                asyncpg.connect(connection_url),
                timeout=30.0
            )
            
            logger.info("✓ Connection established!")
            
            # Test basic query
            result = await conn.fetchval("SELECT version()")
            logger.info(f"✓ PostgreSQL version: {result.split(' ')[0]}")
            
            # Test database query
            result = await conn.fetchval("SELECT current_database()")
            logger.info(f"✓ Connected to database: {result}")
            
            # Test user query
            result = await conn.fetchval("SELECT current_user")
            logger.info(f"✓ Connected as user: {result}")
            
            # Close connection
            await conn.close()
            logger.info("✓ Connection closed successfully")
            
            return True
            
        except asyncio.TimeoutError:
            logger.error("✗ Connection timed out after 30 seconds")
            logger.error("This usually indicates:")
            logger.error("  1. Server is unreachable")
            logger.error("  2. Firewall blocking the connection")
            logger.error("  3. Wrong server address or port")
            return False
            
    except Exception as e:
        logger.error(f"✗ Connection failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        
        if "authentication failed" in str(e).lower():
            logger.error("Authentication issue - check username/password")
        elif "does not exist" in str(e).lower():
            logger.error("Database does not exist")
        elif "connection refused" in str(e).lower():
            logger.error("Connection refused - server may not be running")
        elif "timeout" in str(e).lower():
            logger.error("Connection timeout - check network/firewall")
        
        return False

async def test_ssl_connection():
    """Test connection with SSL settings for Azure PostgreSQL"""
    try:
        from app.core.config import settings
        
        user = settings.POSTGRES_USER
        password = settings.POSTGRES_PASSWORD
        server = settings.POSTGRES_SERVER
        port = settings.POSTGRES_PORT
        db_name = settings.POSTGRES_DB
        
        logger.info("=== Testing SSL Connection (Azure PostgreSQL) ===")
        
        # Azure PostgreSQL requires SSL
        connection_params = {
            'user': user,
            'password': password,
            'host': server,
            'port': port,
            'database': db_name,
            'ssl': 'require'
        }
        
        logger.info("Attempting SSL connection...")
        
        try:
            conn = await asyncio.wait_for(
                asyncpg.connect(**connection_params),
                timeout=30.0
            )
            
            logger.info("✓ SSL connection established!")
            
            # Test SSL status
            result = await conn.fetchval("SHOW ssl")
            logger.info(f"✓ SSL status: {result}")
            
            await conn.close()
            logger.info("✓ SSL connection closed successfully")
            
            return True
            
        except asyncio.TimeoutError:
            logger.error("✗ SSL connection timed out")
            return False
            
    except Exception as e:
        logger.error(f"✗ SSL connection failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("Testing database connectivity...")
    
    # Test 1: Direct connection
    success1 = await test_direct_connection()
    
    # Test 2: SSL connection (Azure specific)
    success2 = await test_ssl_connection()
    
    if success1 or success2:
        logger.info("\n=== SUCCESS ===")
        logger.info("Database connection is working!")
        return True
    else:
        logger.error("\n=== FAILED ===")
        logger.error("Could not establish database connection")
        logger.error("\nTroubleshooting tips:")
        logger.error("1. Check if your IP is allowed in Azure PostgreSQL firewall rules")
        logger.error("2. Verify server name and credentials")
        logger.error("3. Ensure SSL is properly configured")
        logger.error("4. Test connection from Azure portal or pgAdmin")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)