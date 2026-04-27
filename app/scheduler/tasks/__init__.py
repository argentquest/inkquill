"""Scheduled task implementations.

Task execution order (daily pipeline)
--------------------------------------
02:00  care_circle.precache_providers   — regenerate missing provider cache entries
06:00  care_circle.daily_session        — assemble full daily session per patient
07:00  care_circle.newsletter_pdf       — render newsletter PDFs
08:00  care_circle.daily_newsletter     — email/SMS dispatch
09:00  care_circle.mini_newsletter      — lightweight random-sample newsletter

03:00 Sunday  scheduler.cleanup_old_run_logs  — prune old DB rows

dev only (disabled by default):
       scheduler.diagnostic_dir_list   — sanity-check scheduler + subprocess
"""

# Shared helpers used across multiple task modules
from app.scheduler.tasks._helpers import fetch_active_patients  # noqa: F401
