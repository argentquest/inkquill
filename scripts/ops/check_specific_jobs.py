#!/usr/bin/env python
"""
Check specific job IDs to see their current status
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import List

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy import select
    from app.db.database import async_session_local
    from app.models.job_status import JobStatus
    import json
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)


async def check_specific_jobs(job_ids: List[str]):
    """Check specific job IDs"""
    
    async with async_session_local() as db:
        for job_id in job_ids:
            result = await db.execute(
                select(JobStatus).where(JobStatus.job_id == job_id)
            )
            job = result.scalar_one_or_none()
            
            if job:
                logger.info(f"\n=== JOB {job_id} ===")
                logger.info(f"State: {job.state.value}")
                logger.info(f"Status Message: {job.status_message}")
                logger.info(f"Created: {job.created_at}")
                logger.info(f"Updated: {job.updated_at}")
                
                if job.result_message:
                    try:
                        result_data = json.loads(job.result_message)
                        if isinstance(result_data, dict):
                            logger.info(f"Result keys: {list(result_data.keys())}")
                            if "element_type" in result_data:
                                logger.info(f"Element: {result_data.get('element_type')}:{result_data.get('element_id')}")
                            if "image_id" in result_data:
                                logger.info(f"Generated Image ID: {result_data['image_id']}")
                        else:
                            logger.info(f"Result: {str(result_data)[:100]}...")
                    except json.JSONDecodeError:
                        logger.info(f"Result (raw): {job.result_message[:100]}...")
            else:
                logger.info(f"\n=== JOB {job_id} === NOT FOUND")


async def main():
    """Main function"""
    
    # Our test job IDs
    test_job_ids = [
        "c82c0885-610c-46e3-9711-2754bdaa1191",  # Hello Eric story
        "de82cade-c3b1-493c-85a4-86e18fb93ca8"   # Frankenstein story
    ]
    
    logger.info("Checking status of our test jobs...")
    await check_specific_jobs(test_job_ids)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)