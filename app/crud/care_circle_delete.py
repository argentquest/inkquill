"""CRUD function to permanently delete a patient and all related data."""

import logging
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.care_circle import (
    CareCirclePatientProfile,
    CareCirclePatientContentCard,
    CareCircleProviderPatientConfig,
    CareCircleProviderSessionOutput,
)

logger = logging.getLogger(__name__)


async def hard_delete_patient(db: AsyncSession, patient_id: int) -> bool:
    """
    Permanently deletes a patient and all associated data.
    This is irreversible.
    """
    try:
        # Delete in correct order to respect foreign key constraints
        tables_to_clean = [
            CareCircleProviderSessionOutput,
            CareCirclePatientContentCard,
            CareCircleProviderPatientConfig,
        ]

        for table in tables_to_clean:
            await db.execute(
                delete(table).where(table.patient_id == patient_id)
            )

        # Finally delete the patient
        await db.execute(
            delete(CareCirclePatientProfile).where(
                CareCirclePatientProfile.id == patient_id
            )
        )

        await db.commit()
        logger.info(f"Patient {patient_id} has been permanently deleted")
        return True

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to hard delete patient {patient_id}: {e}", exc_info=True)
        return False
