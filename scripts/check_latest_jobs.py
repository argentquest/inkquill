#!/usr/bin/env python
"""
Check the latest image generation jobs
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
    from app.models.job_status import JobStatus, JobTypeEnum
    import json
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)


async def check_latest_jobs(limit: int = 10):
    """Check the latest image generation jobs"""
    
    async with async_session_local() as db:
        result = await db.execute(
            select(JobStatus)
            .where(JobStatus.job_type == JobTypeEnum.IMAGE_GENERATION)
            .order_by(JobStatus.created_at.desc())
            .limit(limit)
        )
        jobs = result.scalars().all()
        
        logger.info(f"=== LATEST {len(jobs)} IMAGE GENERATION JOBS ===")
        
        for i, job in enumerate(jobs, 1):
            logger.info(f"\n[{i}] Job {job.job_id}")
            logger.info(f"    State: {job.state.value}")
            logger.info(f"    Status: {job.status_message}")
            logger.info(f"    Created: {job.created_at}")
            logger.info(f"    Updated: {job.updated_at}")
            
            if job.result_message:
                try:
                    result_data = json.loads(job.result_message)
                    if isinstance(result_data, dict):
                        element_type = result_data.get('element_type', 'unknown')
                        element_id = result_data.get('element_id', 'unknown')
                        logger.info(f"    Element: {element_type}:{element_id}")
                        
                        if job.state.value == "COMPLETED" and "image_id" in result_data:
                            logger.info(f"    Image ID: {result_data['image_id']}")
                        elif job.state.value in ["PENDING", "RUNNING"]:
                            prompt = result_data.get('prompt', '')
                            logger.info(f"    Prompt: {prompt[:100]}...")
                except json.JSONDecodeError:
                    logger.info(f"    Result: [JSON ERROR] {job.result_message[:50]}...")


async def main():
    """Main function"""
    logger.info("Checking latest image generation jobs...")
    await check_latest_jobs(10)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)