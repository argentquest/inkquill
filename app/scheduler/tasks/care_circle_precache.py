"""Pre-cache provider outputs — only (re)generate providers missing from the per-patient cache."""

import logging
import time
from datetime import date, timedelta
from sqlalchemy import select

from app.scheduler.registry import register_task
from app.scheduler.logging import task_execution_context
from app.db.database import async_session_local
from app.models.care_circle import (
    CareCirclePatientProfile,
    CareCircleProviderCatalog,
    CareCircleProviderPatientConfig,
)
from app.services.care_circle.provider_cache import is_cached, save_cached_result
from app.services.care_circle.session_assembler import get_provider_class

logger = logging.getLogger(__name__)

DAYS_AHEAD = 3


async def _get_active_providers_for_patient(db, patient_id: int):
    """Return list of (provider_key, display_order, instance) for a patient."""
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
        cfg_dict = conf.custom_parameters if conf else {}
        active.append((item.provider_key, item.display_order, cls(patient_config=cfg_dict)))

    return active


@register_task(
    key="care_circle.precache_providers",
    name="Provider Output Pre-cache",
    default_cron="0 2 * * *",
    description="Only regenerates providers that are missing from the patient cache. Runs on startup + nightly.",
    enabled_by_default=True,
    max_instances=1,
    misfire_grace_time=1800,
)
async def precache_provider_outputs() -> dict:
    """Generate ONLY providers that are not yet in the cache for each patient/date."""
    async with task_execution_context(
        task_key="care_circle.precache_providers",
        task_name="Provider Output Pre-cache",
    ) as ctx:
        today = date.today()
        target_dates = [today + timedelta(days=d) for d in range(DAYS_AHEAD + 1)]

        async with async_session_local() as db:
            patients = (await db.execute(
                select(CareCirclePatientProfile).where(
                    CareCirclePatientProfile.access_state == "active"
                )
            )).scalars().all()

            total_generated = 0
            total_skipped = 0
            total_failed = 0
            patient_results = []

            for patient in patients:
                patient_generated = 0
                patient_skipped = 0
                patient_failed = 0

                active_providers = await _get_active_providers_for_patient(db, patient.id)

                for for_date in target_dates:
                    for provider_key, _order, provider_instance in active_providers:
                        if is_cached(patient.id, for_date, provider_key):
                            patient_skipped += 1
                            total_skipped += 1
                            continue

                        # Only regenerate if missing from cache — this is the core request
                        try:
                            t0 = time.monotonic()
                            result = await provider_instance.execute(patient)
                            elapsed_ms = (time.monotonic() - t0) * 1000
                            token_usage = result.get("token_usage")

                            save_cached_result(
                                patient.id,
                                for_date,
                                provider_key,
                                result,
                                elapsed_ms=elapsed_ms,
                                token_usage=token_usage,
                            )
                            patient_generated += 1
                            total_generated += 1
                            logger.debug("Generated missing %s for patient %s on %s", provider_key, patient.id, for_date)
                        except Exception as exc:
                            logger.error(
                                "Failed to generate %s for patient %s on %s: %s",
                                provider_key, patient.id, for_date, exc,
                            )
                            patient_failed += 1
                            total_failed += 1

                patient_results.append({
                    "patient_id": patient.id,
                    "patient_name": patient.display_name,
                    "generated": patient_generated,
                    "skipped": patient_skipped,
                    "failed": patient_failed,
                })
                logger.info(
                    "Patient %s: generated=%d skipped=%d failed=%d",
                    patient.id, patient_generated, patient_skipped, patient_failed
                )

        ctx.update({
            "total_patients": len(patients),
            "total_generated": total_generated,
            "total_skipped": total_skipped,
            "total_failed": total_failed,
            "results": patient_results,
        })

    return {
        "task": "care_circle.precache_providers",
        "dates": [d.isoformat() for d in target_dates],
        "total_patients": len(patients),
        "total_generated": total_generated,
        "total_skipped": total_skipped,
        "total_failed": total_failed,
        "message": "Only missing providers were regenerated",
    }
