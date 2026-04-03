#!/usr/bin/env python
"""
Script to check and analyze image generation job statuses.
Usage: python scripts/check_image_jobs.py [--clean-failed]
"""

import asyncio
import logging
import argparse
import sys
import json
from pathlib import Path
from typing import Optional, List, Dict

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
    from sqlalchemy import select, and_, or_, func
    from app.db.database import async_session_local
    from app.models.job_status import JobStatus, JobTypeEnum, JobStateEnum
    from app.models.generated_image import GeneratedImage
except ImportError as e:
    logger.error(f"Failed to import required modules: {e}")
    sys.exit(1)


async def analyze_image_generation_jobs(db: AsyncSession) -> Dict:
    """Analyze all image generation jobs"""
    
    # Get all image generation jobs
    result = await db.execute(
        select(JobStatus)
        .where(JobStatus.job_type == JobTypeEnum.IMAGE_GENERATION)
        .order_by(JobStatus.created_at.desc())
    )
    jobs = result.scalars().all()
    
    stats = {
        "total": len(jobs),
        "by_state": {},
        "failed_json_parse": [],
        "successful": [],
        "failed": [],
        "running": [],
        "pending": []
    }
    
    for job in jobs:
        state = job.state.value if job.state else "unknown"
        stats["by_state"][state] = stats["by_state"].get(state, 0) + 1
        
        # Check if result_message can be parsed as JSON
        if job.result_message:
            try:
                json.loads(job.result_message)
                if state == JobStateEnum.COMPLETED:
                    stats["successful"].append(job)
            except json.JSONDecodeError:
                stats["failed_json_parse"].append(job)
        
        # Categorize by state
        if state == JobStateEnum.FAILED:
            stats["failed"].append(job)
        elif state == JobStateEnum.RUNNING:
            stats["running"].append(job)
        elif state == JobStateEnum.PENDING:
            stats["pending"].append(job)
    
    return stats


async def check_generated_images(db: AsyncSession) -> Dict:
    """Check generated images status"""
    
    # Count total generated images
    result = await db.execute(select(func.count(GeneratedImage.id)))
    total_images = result.scalar()
    
    # Count by element type
    result = await db.execute(
        select(GeneratedImage.element_type, func.count(GeneratedImage.id))
        .group_by(GeneratedImage.element_type)
    )
    by_type = dict(result.fetchall())
    
    return {
        "total_images": total_images,
        "by_element_type": by_type
    }


async def clean_failed_jobs(db: AsyncSession, failed_jobs: List[JobStatus]) -> int:
    """Clean up failed jobs with JSON parse errors"""
    
    cleaned = 0
    for job in failed_jobs:
        try:
            # Update the job to failed state with a proper error message
            job.state = JobStateEnum.FAILED
            job.status_message = "Job failed with invalid result format"
            job.result_message = json.dumps({"error": "JSON parse error in original result"})
            
            cleaned += 1
            
        except Exception as e:
            logger.error(f"Error cleaning job {job.job_id}: {e}")
    
    await db.commit()
    return cleaned


async def show_recent_jobs(jobs: List[JobStatus], limit: int = 10):
    """Show recent job details"""
    
    logger.info(f"\n=== RECENT {limit} JOBS ===")
    for i, job in enumerate(jobs[:limit], 1):
        state = job.state.value if job.state else "unknown"
        created = job.created_at.strftime("%Y-%m-%d %H:%M:%S") if job.created_at else "unknown"
        
        logger.info(f"[{i}] Job {job.job_id}")
        logger.info(f"    State: {state}")
        logger.info(f"    Created: {created}")
        logger.info(f"    Message: {job.status_message}")
        
        # Try to parse result_message
        if job.result_message:
            try:
                result = json.loads(job.result_message)
                if isinstance(result, dict):
                    logger.info(f"    Result: {list(result.keys())}")
                else:
                    logger.info(f"    Result: {str(result)[:100]}...")
            except json.JSONDecodeError:
                logger.info(f"    Result: [JSON PARSE ERROR] {job.result_message[:50]}...")
        
        logger.info("")


async def main(args):
    """Main function"""
    async with async_session_local() as db:
        try:
            logger.info("=== IMAGE GENERATION JOBS ANALYSIS ===")
            
            # Analyze jobs
            job_stats = await analyze_image_generation_jobs(db)
            
            logger.info(f"\n=== JOB STATISTICS ===")
            logger.info(f"Total jobs: {job_stats['total']}")
            logger.info(f"By state:")
            for state, count in job_stats["by_state"].items():
                logger.info(f"  {state}: {count}")
            
            logger.info(f"\nProblematic jobs:")
            logger.info(f"  Failed JSON parse: {len(job_stats['failed_json_parse'])}")
            logger.info(f"  Explicitly failed: {len(job_stats['failed'])}")
            logger.info(f"  Still running: {len(job_stats['running'])}")
            logger.info(f"  Still pending: {len(job_stats['pending'])}")
            
            # Check generated images
            image_stats = await check_generated_images(db)
            
            logger.info(f"\n=== GENERATED IMAGES ===")
            logger.info(f"Total images: {image_stats['total_images']}")
            logger.info(f"By element type:")
            for element_type, count in image_stats["by_element_type"].items():
                logger.info(f"  {element_type}: {count}")
            
            # Show recent failed jobs with JSON parse errors
            if job_stats['failed_json_parse']:
                logger.info(f"\n=== JOBS WITH JSON PARSE ERRORS ===")
                await show_recent_jobs(job_stats['failed_json_parse'], 5)
            
            # Show recent successful jobs
            if job_stats['successful']:
                logger.info(f"\n=== RECENT SUCCESSFUL JOBS ===")
                await show_recent_jobs(job_stats['successful'], 3)
            
            # Clean failed jobs if requested
            if args.clean_failed and job_stats['failed_json_parse']:
                logger.info(f"\n=== CLEANING FAILED JOBS ===")
                cleaned = await clean_failed_jobs(db, job_stats['failed_json_parse'])
                logger.info(f"Cleaned {cleaned} jobs with JSON parse errors")
            
            # Summary and recommendations
            logger.info(f"\n=== RECOMMENDATIONS ===")
            
            if job_stats['failed_json_parse']:
                logger.info(f"• {len(job_stats['failed_json_parse'])} jobs have JSON parse errors")
                logger.info("  Run with --clean-failed to fix their status")
            
            if job_stats['running']:
                logger.info(f"• {len(job_stats['running'])} jobs are still running")
                logger.info("  Check if image generation service is working")
            
            if job_stats['pending']:
                logger.info(f"• {len(job_stats['pending'])} jobs are pending")
                logger.info("  These may need to be processed")
            
            success_rate = len(job_stats['successful']) / job_stats['total'] * 100 if job_stats['total'] > 0 else 0
            logger.info(f"• Success rate: {success_rate:.1f}%")
            
            if success_rate < 50:
                logger.warning("Low success rate - check RUNPOD configuration and connectivity")
            
        except Exception as e:
            logger.error(f"Error analyzing jobs: {e}")
            raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Analyze image generation job status")
    parser.add_argument("--clean-failed", action="store_true", help="Clean up jobs with JSON parse errors")
    
    args = parser.parse_args()
    
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        logger.info("Script interrupted by user")
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)