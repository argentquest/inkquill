#!/usr/bin/env python3
"""
Security scan script to detect and clean malicious content from the database.
Run this script to check for and remove malicious iframe content.
"""

import asyncio
import asyncpg
import os
import logging
from dotenv import load_dotenv
from app.core.content_sanitizer import ContentSanitizer

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scan_and_clean_database():
    """Scan database for malicious content and clean it."""
    
    try:
        # Connect to database
        conn = await asyncpg.connect(
            host=os.getenv('DATABASE_HOST', 'localhost'),
            port=int(os.getenv('DATABASE_PORT', 5432)),
            user=os.getenv('DATABASE_USER', 'postgres'),
            password=os.getenv('DATABASE_PASSWORD', ''),
            database=os.getenv('DATABASE_NAME', 'story_app')
        )
        
        logger.info("Connected to database successfully")
        
        # Tables and columns to check
        content_checks = [
            ('stories', 'ai_summary', 'id'),
            ('stories', 'short_description', 'id'),
            ('acts', 'description', 'id'),
            ('scenes', 'description', 'id'),
            ('published_stories', 'description', 'id'),
            ('characters', 'description', 'id'),
            ('locations', 'description', 'id'),
            ('lore_items', 'description', 'id'),
        ]
        
        total_issues = 0
        total_cleaned = 0
        
        for table, column, id_column in content_checks:
            logger.info(f"Scanning {table}.{column}...")
            
            try:
                # Find potentially malicious content
                query = f"""
                    SELECT {id_column}, {column} 
                    FROM {table} 
                    WHERE {column} IS NOT NULL 
                    AND (
                        LOWER({column}) LIKE '%bedpage%' 
                        OR LOWER({column}) LIKE '%iframe%'
                        OR LOWER({column}) LIKE '%<script%'
                        OR LOWER({column}) LIKE '%<object%'
                        OR LOWER({column}) LIKE '%<embed%'
                    )
                """
                
                rows = await conn.fetch(query)
                
                if rows:
                    logger.warning(f"Found {len(rows)} potentially malicious entries in {table}.{column}")
                    total_issues += len(rows)
                    
                    for row in rows:
                        record_id = row[0]
                        content = row[1]
                        
                        logger.info(f"Checking {table} ID {record_id}")
                        
                        # Check if content is actually malicious
                        if not ContentSanitizer.is_content_safe(content):
                            logger.critical(f"MALICIOUS CONTENT DETECTED in {table} ID {record_id}")
                            
                            # Sanitize the content
                            cleaned_content = ContentSanitizer.sanitize_html_content(content)
                            
                            if cleaned_content != content:
                                # Update the database with cleaned content
                                update_query = f"UPDATE {table} SET {column} = $1 WHERE {id_column} = $2"
                                await conn.execute(update_query, cleaned_content, record_id)
                                logger.info(f"Cleaned content for {table} ID {record_id}")
                                total_cleaned += 1
                            else:
                                logger.info(f"Content for {table} ID {record_id} was already clean")
                        else:
                            logger.info(f"Content for {table} ID {record_id} is safe (false positive)")
                else:
                    logger.info(f"No suspicious content found in {table}.{column}")
                    
            except Exception as e:
                logger.error(f"Error scanning {table}.{column}: {e}")
        
        await conn.close()
        
        logger.info(f"Security scan complete!")
        logger.info(f"Total suspicious entries found: {total_issues}")
        logger.info(f"Total entries cleaned: {total_cleaned}")
        
        if total_issues > 0:
            logger.warning("SECURITY ALERT: Malicious content was detected and cleaned from your database.")
            logger.warning("Please review your content input validation and consider how this content got into your system.")
        
    except Exception as e:
        logger.error(f"Database security scan failed: {e}")
        logger.error("Please check your database connection settings and try again")

if __name__ == "__main__":
    print("🔒 Starting security scan of database content...")
    asyncio.run(scan_and_clean_database())
    print("✅ Security scan completed!")
