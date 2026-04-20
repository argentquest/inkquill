"""Simple diagnostic task that runs every 5 minutes."""

import logging
import subprocess
from datetime import datetime
from pathlib import Path

from app.scheduler.registry import register_task
from app.scheduler.logging import task_execution_context

logger = logging.getLogger(__name__)


@register_task(
    key="scheduler.diagnostic_dir_list",
    name="Diagnostic Directory Listing",
    default_cron="*/5 * * * *",   # Every 5 minutes
    description="Runs 'dir' command and logs the output. Useful for testing scheduler + command execution.",
    enabled_by_default=True,
    max_instances=1,
    misfire_grace_time=300,
)
async def diagnostic_dir_list() -> dict:
    """Run dir command and return directory listing."""
    async with task_execution_context(
        task_key="scheduler.diagnostic_dir_list",
        task_name="Diagnostic Directory Listing",
    ) as ctx:
        try:
            # Run 'dir' using command.com / shell
            result = subprocess.run(
                ["cmd.exe", "/c", "dir"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=Path(__file__).parent.parent.parent,  # Project root
            )
            
            output = result.stdout
            error = result.stderr
            
            logger.info("Diagnostic task completed. Directory listing captured.")
            ctx["output_length"] = len(output)
            ctx["success"] = True
            ctx["exit_code"] = result.returncode

            if error:
                ctx["stderr"] = error[:500]  # truncate

            return {
                "task": "scheduler.diagnostic_dir_list",
                "status": "success",
                "executed_at": datetime.utcnow().isoformat(),
                "output_length": len(output),
                "exit_code": result.returncode,
                "first_200_chars": output[:200].replace("\n", " "),
                "message": "Successfully executed 'dir' command",
            }

        except subprocess.TimeoutExpired:
            logger.error("Diagnostic task timed out")
            ctx["success"] = False
            ctx["error"] = "Timeout"
            raise
        except Exception as exc:
            logger.error("Diagnostic task failed: %s", exc, exc_info=True)
            ctx["success"] = False
            ctx["error"] = str(exc)
            raise