import sys
sys.path.insert(0, '.')

import asyncio
from app.db.database import async_session_local
from app.models.care_circle import CareCirclePatientProfile
from sqlalchemy import select
from app.services.care_circle.session_assembler import assemble_daily_patient_session
from app.services.care_circle.newsletter_email_service import send_newsletter_email
import app.core.config as config_module

async def send_test_newsletter_to_patient_5():
    async with async_session_local() as db:
        result = await db.execute(
            select(CareCirclePatientProfile).where(CareCirclePatientProfile.id == 5)
        )
        patient = result.scalar_one_or_none()
        
        if not patient:
            print("Patient 5 not found")
            return
            
        print(f"Sending test newsletter to Patient 5: {patient.display_name}")
        print(f"Patient email on record: {getattr(patient, 'email', 'None')}")
        
        # Enable test mode
        original_test_mode = getattr(config_module.settings, "EMAIL_TEST_MODE", False)
        original_test_address = getattr(config_module.settings, "EMAIL_TEST_ADDRESS", None)
        
        config_module.settings.EMAIL_TEST_MODE = True
        print(f"Test mode ENABLED. Emails will be sent to: {original_test_address or 'CONFIGURED_TEST_ADDRESS'}")
        
        session_data = await assemble_daily_patient_session(db, 5)
        html_content = session_data.get("html", "") if isinstance(session_data, dict) else ""
        
        if not html_content:
            print("Warning: No HTML content generated!")
        
        result = await send_newsletter_email(patient, html_content)
        print("\n=== Test Email Result ===")
        print(result)
        
        # Restore original setting
        config_module.settings.EMAIL_TEST_MODE = original_test_mode
        print("\nTest completed. Check your test email inbox.")

asyncio.run(send_test_newsletter_to_patient_5())
