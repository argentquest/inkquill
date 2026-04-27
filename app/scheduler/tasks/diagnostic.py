"""Diagnostic task — dev/test use only.

IMPORTANT: enabled_by_default is False.  Do not change it to True in
production.  This task runs a shell command and logs directory output;
it exists only to verify that APScheduler can execute jobs and that
subprocess calls work in the runtime environment.

To run it manually, use the admin UI "Run now" button or:
  POST /scheduler/jobs/scheduler.diagnostic_dir_list/run
"""

import logging
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from app.scheduler.registry import register_task
from app.scheduler.logging import task_execution_context

logger = logging.getLogger(__name__)


@register_task(
    key="scheduler.diagnostic_dir_list",
    name="Diagnostic Directory Listing",
    default_cron="*/5 * * * *",
    description="Dev only — runs 'dir' and logs the output. Disabled by default.",
    enabled_by_default=False,  # Never auto-schedule in any environment
    max_instances=1,
    misfire_grace_time=300,
)
async def diagnostic_dir_list() -> dict:
    """Run the OS dir command and return a summary.  Windows-only (cmd.exe)."""
    async with task_execution_context(
        task_key="scheduler.diagnostic_dir_list",
        task_name="Diagnostic Directory Listing",
    ) as ctx:
        try:
            result = subprocess.run(
                ["cmd.exe", "/c", "dir"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=Path(__file__).parent.parent.parent,  # repo root
            )

            ctx["output_length"] = len(result.stdout)
            ctx["success"] = True
            ctx["exit_code"] = result.returncode
            if result.stderr:
                ctx["stderr"] = result.stderr[:500]

            logger.info("Diagnostic: dir completed, %d chars captured", len(result.stdout))
            return {
                "task": "scheduler.diagnostic_dir_list",
                "status": "success",
                "executed_at": datetime.now(timezone.utc).isoformat(),
                "output_length": len(result.stdout),
                "exit_code": result.returncode,
                "first_200_chars": result.stdout[:200].replace("\n", " "),
            }

        except subprocess.TimeoutExpired:
            ctx["success"] = False
            ctx["error"] = "Timeout"
            logger.error("Diagnostic task timed out after 30s")
            raise
        except Exception as exc:
            ctx["success"] = False
            ctx["error"] = str(exc)
            logger.error("Diagnostic task failed: %s", exc, exc_info=True)
            raise
