"""Provider output pre-cache task.

Scheduled at 02:00 daily.  Also fires immediately on scheduler startup so the
cache is warm before the first daily pipeline begins at 06:00.

Strategy — only fill gaps
--------------------------
For each active patient × enabled provider × target date, check whether a
cached result already exists before running the (expensive) LLM/API call.
This makes the task safe to re-run at any time — duplicate work is skipped.

DAYS_AHEAD controls how many future days are pre-cached.  Value of 3 means
today + the next 3 days (4 dates total).  Increasing this trades storage and
API cost for resilience against multi-day scheduler outages.

Cache structure on disk:
  <CACHE_ROOT>/<patient_id>/<YYYY-MM-DD>/<provider_key>.json
"""

import logging
import time
from datetime import date, datetime, time as dt_time, timedelta, timezone
from sqlalchemy import select

from app.scheduler.registry import register_task
from app.scheduler.logging import task_execution_context
from app.scheduler.tasks._helpers import fetch_active_patients
from app.db.database import async_session_local
from app.models.care_circle import (
    CareCircleProviderCatalog,
    CareCircleProviderPatientConfig,
)
from app.services.care_circle.provider_cache import is_cached, save_cached_result
from app.services.care_circle.session_assembler import get_provider_class

logger = logging.getLogger(__name__)

# Number of future days to pre-cache beyond today.
# Today is always included, so DAYS_AHEAD=3 → 4 dates total.
DAYS_AHEAD = 3


async def _get_active_provider_configs_for_patient(
    db, patient_id: int
) -> list[tuple[str, int, type, dict]]:
    """Return (provider_key, display_order, provider_cls, config_dict) for each
    enabled provider for the given patient.

    A provider is skipped if:
    * The patient has explicitly disabled it (ProviderPatientConfig.is_enabled=False)
    * The provider class cannot be resolved
    * provider.is_enabled is False at the class level
    * provider.is_safe_for_patient is False
    """
    catalog_items = (await db.execute(
        select(CareCircleProviderCatalog).where(
            CareCircleProviderCatalog.enabled == True,
            CareCircleProviderCatalog.patient_visible == True,
        )
    )).scalars().all()

    user_configs = (await db.execute(
        select(CareCircleProviderPatientConfig).where(
            CareCircleProviderPatientConfig.patient_id == patient_id
        )
    )).scalars().all()
    config_map = {c.provider_key: c for c in user_configs}

    active = []
    for item in catalog_items:
        conf = config_map.get(item.provider_key)
        if conf and not conf.is_enabled:
            continue
        cls = get_provider_class(item.provider_key)
        if not cls:
            continue
        if not cls().is_enabled:
            continue
        if not cls.is_safe_for_patient:
            continue
        cfg_dict = dict(conf.custom_parameters or {}) if conf else {}
        active.append((item.provider_key, item.display_order, cls, cfg_dict))

    return active


@register_task(
    key="care_circle.precache_providers",
    name="Provider Output Pre-cache",
    default_cron="0 2 * * *",  # 02:00 daily
    description=(
        f"Fills missing provider cache entries for today + {DAYS_AHEAD} days. "
        "Already-cached entries are skipped. Also runs on scheduler startup."
    ),
    enabled_by_default=True,
    max_instances=1,  # Single instance prevents duplicate LLM calls
    misfire_grace_time=1800,  # 30-minute grace for the overnight window
)
async def precache_provider_outputs(reference_date: date | None = None) -> dict:
    """Generate only provider outputs that are absent from the on-disk cache.

    Args:
        reference_date: Start date for the cache window. Defaults to today.
    """
    async with task_execution_context(
        task_key="care_circle.precache_providers",
        task_name="Provider Output Pre-cache",
    ) as ctx:
        today = reference_date or date.today()
        target_dates = [today + timedelta(days=d) for d in range(DAYS_AHEAD + 1)]

        patients = await fetch_active_patients()
        total_generated = total_skipped = total_failed = 0
        patient_results = []

        async with async_session_local() as db:
            for patient in patients:
                p_generated = p_skipped = p_failed = 0
                active_providers = await _get_active_provider_configs_for_patient(db, patient.id)

                for for_date in target_dates:
                    # Simulate a generation timestamp of 09:00 on the target date
                    # so provider instances behave consistently regardless of when
                    # the task actually runs.
                    generated_at = datetime.combine(for_date, dt_time(hour=9, minute=0))

                    for provider_key, _order, provider_cls, base_cfg in active_providers:
                        if is_cached(patient.id, for_date, provider_key):
                            p_skipped += 1
                            total_skipped += 1
                            continue

                        provider_instance = provider_cls(patient_config={
                            **base_cfg,
                            "_for_date": for_date,
                            "_generated_at": generated_at,
                        })

                        try:
                            t0 = time.monotonic()
                            result = await provider_instance.execute(patient)
                            elapsed_ms = (time.monotonic() - t0) * 1000

                            save_cached_result(
                                patient.id, for_date, provider_key, result,
                                elapsed_ms=elapsed_ms,
                                token_usage=result.get("token_usage"),
                            )
                            p_generated += 1
                            total_generated += 1
                            logger.debug(
                                "Cached %s for patient %s on %s (%.0fms)",
                                provider_key, patient.id, for_date, elapsed_ms,
                            )
                        except Exception as exc:
                            logger.error(
                                "Failed to cache %s for patient %s on %s: %s",
                                provider_key, patient.id, for_date, exc,
                            )
                            p_failed += 1
                            total_failed += 1

                patient_results.append({
                    "patient_id": patient.id,
                    "patient_name": patient.display_name,
                    "generated": p_generated,
                    "skipped": p_skipped,
                    "failed": p_failed,
                })
                logger.info(
                    "Patient %s: generated=%d skipped=%d failed=%d",
                    patient.id, p_generated, p_skipped, p_failed,
                )

        ctx.update({
            "reference_date": today.isoformat(),
            "total_patients": len(patients),
            "total_generated": total_generated,
            "total_skipped": total_skipped,
            "total_failed": total_failed,
        })

    return {
        "task": "care_circle.precache_providers",
        "executed_at": datetime.now(timezone.utc).isoformat(),
        "reference_date": today.isoformat(),
        "dates": [d.isoformat() for d in target_dates],
        "total_patients": len(patients),
        "total_generated": total_generated,
        "total_skipped": total_skipped,
        "total_failed": total_failed,
        "message": "Only missing providers were (re)generated",
    }
