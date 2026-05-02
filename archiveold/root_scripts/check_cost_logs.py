#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append('/mnt/c/Code2025/rag')

from app.db.database import async_session_local
from sqlalchemy import select, desc, func
from app.models.ai_cost_log import AICallLog

async def check_recent_logs():
    try:
        async with async_session_local() as db:
            # Check total count
            count_result = await db.execute(select(func.count(AICallLog.id)))
            total_count = count_result.scalar()
            print(f"Total AI cost log entries: {total_count}")
            
            # Get recent logs
            result = await db.execute(
                select(AICallLog)
                .order_by(desc(AICallLog.created_at))
                .limit(5)
            )
            logs = result.scalars().all()
            
            if logs:
                print('\nRecent AI cost logs:')
                for log in logs:
                    print(f'- ID: {log.id}, Type: {log.call_type}, Model: {log.model_name}')
                    print(f'  Tokens: {log.total_tokens}, Cost: ${log.calculated_cost_usd:.6f}')
                    print(f'  Created: {log.created_at}, User: {log.user_id}')
                    print(f'  Object ID: {log.object_id}, Duration: {log.duration_ms}ms')
                    print()
            else:
                print('No AI cost logs found in database')
                
            # Check for act_review calls specifically
            review_result = await db.execute(
                select(AICallLog)
                .where(AICallLog.call_type == "act_review")
                .order_by(desc(AICallLog.created_at))
                .limit(3)
            )
            review_logs = review_result.scalars().all()
            
            if review_logs:
                print(f"Recent act_review calls ({len(review_logs)} found):")
                for log in review_logs:
                    print(f'- ID: {log.id}, Cost: ${log.calculated_cost_usd:.6f}, Tokens: {log.total_tokens}')
            else:
                print("No act_review calls found in cost logs")
                
    except Exception as e:
        print(f"Error checking database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_recent_logs())