import sys
sys.path.insert(0, '.')

from datetime import date
import asyncio
from sqlalchemy import select
from app.services.care_circle.session_assembler import get_provider_class
from app.services.care_circle.provider_cache import save_cached_result, is_cached
from app.db.database import async_session_local
from app.models.care_circle import CareCirclePatientProfile

async def force_generate_comics():
    patient_id = 1
    for_date = date(2026, 4, 18)
    
    comic_keys = [
        "comic_mr_skygack",
        "comic_dino_cartoons",
        "comic_brownies",
        "comic_abe_martin"
    ]
    
    print(f"Force generating comics for patient {patient_id} on {for_date}")
    
    async with async_session_local() as db:
        result = await db.execute(
            select(CareCirclePatientProfile).where(CareCirclePatientProfile.id == patient_id)
        )
        patient = result.scalar_one_or_none()
        
        if not patient:
            print("Patient 1 not found")
            return
            
        for key in comic_keys:
            if is_cached(patient_id, for_date, key):
                print(f"  {key}: already cached")
                continue
                
            cls = get_provider_class(key)
            if not cls:
                print(f"  {key}: provider class not found")
                continue
                
            provider = cls()
            print(f"  Generating {key}...")
            
            try:
                result = await provider.execute(patient)
                save_cached_result(patient_id, for_date, key, result)
                print(f"  {key}: SUCCESS (image downloaded via _process_images)")
            except Exception as e:
                print(f"  {key}: FAILED - {type(e).__name__}: {e}")
    
    print("\nForce generation completed.")

if __name__ == "__main__":
    asyncio.run(force_generate_comics())
