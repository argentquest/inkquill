import sys
sys.path.insert(0, '.')

from datetime import date, timedelta
import asyncio
from sqlalchemy import select
from app.services.care_circle.session_assembler import get_provider_class
from app.services.care_circle.provider_cache import is_cached, save_cached_result
from app.db.database import async_session_local
from app.models.care_circle import CareCirclePatientProfile, CareCircleProviderCatalog, CareCircleProviderPatientConfig
from app.scheduler.logging import task_execution_context

async def backfill_all_missing_providers(days_ahead=3):
    today = date.today()
    target_dates = [today + timedelta(days=d) for d in range(days_ahead + 1)]
    
    print(f"Backfilling all missing providers for dates: {[d.isoformat() for d in target_dates]}")
    
    async with task_execution_context(
        task_key="care_circle.backfill_missing",
        task_name="Backfill All Missing Providers",
    ) as ctx:
        async with async_session_local() as db:
            patients = (await db.execute(
                select(CareCirclePatientProfile).where(
                    CareCirclePatientProfile.access_state == "active"
                )
            )).scalars().all()
            
            total_generated = 0
            total_skipped = 0
            total_failed = 0
            
            for patient in patients:
                patient_generated = 0
                patient_skipped = 0
                patient_failed = 0
                
                # Get active providers for this patient
                catalog_items = (await db.execute(
                    select(CareCircleProviderCatalog).where(
                        CareCircleProviderCatalog.enabled == True,
                        CareCircleProviderCatalog.patient_visible == True,
                    )
                )).scalars().all()

                user_configs = (await db.execute(
                    select(CareCircleProviderPatientConfig).where(
                        CareCircleProviderPatientConfig.patient_id == patient.id
                    )
                )).scalars().all()
                config_map = {c.provider_key: c for c in user_configs}

                active_providers = []
                for item in catalog_items:
                    conf = config_map.get(item.provider_key)
                    if conf and not conf.is_enabled:
                        continue
                    cls = get_provider_class(item.provider_key)
                    if not cls or not cls().is_enabled:
                        continue
                    if not getattr(cls, 'is_safe_for_patient', True):
                        continue
                    cfg_dict = conf.custom_parameters if conf else {}
                    active_providers.append((item.provider_key, cls(patient_config=cfg_dict)))

                print(f"\nPatient {patient.id} ({patient.display_name}): {len(active_providers)} active providers")
                
                for for_date in target_dates:
                    for provider_key, provider_instance in active_providers:
                        if is_cached(patient.id, for_date, provider_key):
                            patient_skipped += 1
                            total_skipped += 1
                            continue
                        
                        print(f"  Generating missing {provider_key} for patient {patient.id} on {for_date}...")
                        try:
                            result = await provider_instance.execute(patient)
                            save_cached_result(patient.id, for_date, provider_key, result)
                            patient_generated += 1
                            total_generated += 1
                            print(f"    → Success")
                        except Exception as e:
                            print(f"    → Failed: {type(e).__name__}: {e}")
                            patient_failed += 1
                            total_failed += 1
                
                print(f"  Patient {patient.id}: generated={patient_generated}, skipped={patient_skipped}, failed={patient_failed}")
            
            ctx.update({
                "total_patients": len(patients),
                "total_generated": total_generated,
                "total_skipped": total_skipped,
                "total_failed": total_failed,
            })
    
    print(f"\nBackfill complete!")
    print(f"Total generated: {total_generated}")
    print(f"Total skipped:   {total_skipped}")
    print(f"Total failed:    {total_failed}")
    return {"status": "completed", "generated": total_generated, "skipped": total_skipped, "failed": total_failed}

if __name__ == "__main__":
    asyncio.run(backfill_all_missing_providers())
