"""Shared helpers used by more than one task module.

Keep this module dependency-light — it is imported at package init time and
must not trigger heavy imports (e.g. LLM clients, Playwright).
"""

import logging
from sqlalchemy import select

from app.db.database import async_session_local
from app.models.care_circle import CareCirclePatientProfile

logger = logging.getLogger(__name__)


async def fetch_active_patients() -> list[CareCirclePatientProfile]:
    """Return all patient profiles whose access_state is 'active'.

    Opens its own short-lived session so callers don't need to manage one.
    Each task that fans out over patients should call this once and reuse the
    returned list rather than querying inside the per-patient loop.
    """
    async with async_session_local() as db:
        rows = (
            await db.execute(
                select(CareCirclePatientProfile).where(
                    CareCirclePatientProfile.access_state == "active"
                )
            )
        ).scalars().all()
    logger.debug("fetch_active_patients: found %d active patients", len(rows))
    return list(rows)
