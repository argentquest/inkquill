from types import SimpleNamespace

import pytest

from app.models.job_status import JobStateEnum, JobTypeEnum
from app.scheduler.tasks import care_circle_session


@pytest.mark.asyncio
async def test_pregenerate_daily_sessions_creates_job_and_passes_job_id(monkeypatch):
    patient = SimpleNamespace(id=20, display_name="Marie", family_id=7, created_by_user_id=88)
    db_patient = SimpleNamespace(
        id=20,
        display_name="Marie",
        family_id=7,
        created_by_user_id=88,
    )
    family = SimpleNamespace(created_by_user_id=55)

    class _DB:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def get(self, model, key):
            if model.__name__ == "CareCirclePatientProfile":
                return db_patient
            return family

        async def scalar(self, *args, **kwargs):
            return None

    captured = {
        "created_jobs": [],
        "updated_jobs": [],
        "assembled": [],
    }

    async def fake_fetch_active_patients():
        return [patient]

    async def fake_create_job(db, job_id, user_id, job_type, status_message):
        captured["created_jobs"].append(
            {
                "job_id": job_id,
                "user_id": user_id,
                "job_type": job_type,
                "status_message": status_message,
            }
        )
        return SimpleNamespace(job_id=job_id)

    async def fake_update_job_status(
        db,
        job_id,
        state,
        status_message=None,
        result_message=None,
        world_id=None,
    ):
        captured["updated_jobs"].append(
            {
                "job_id": job_id,
                "state": state,
                "status_message": status_message,
                "result_message": result_message,
            }
        )
        return SimpleNamespace(job_id=job_id, state=state)

    async def fake_assemble_daily_patient_session(db, patient_id, force_regenerate=False, job_id=None, for_date=None):
        captured["assembled"].append(
            {
                "patient_id": patient_id,
                "job_id": job_id,
                "force_regenerate": force_regenerate,
                "for_date": for_date,
            }
        )
        return True

    monkeypatch.setattr(care_circle_session, "fetch_active_patients", fake_fetch_active_patients)
    monkeypatch.setattr(care_circle_session, "async_session_local", lambda: _DB())
    monkeypatch.setattr(care_circle_session.crud_job_status, "create_job", fake_create_job)
    monkeypatch.setattr(care_circle_session.crud_job_status, "update_job_status", fake_update_job_status)
    monkeypatch.setattr(
        "app.services.care_circle.session_assembler.assemble_daily_patient_session",
        fake_assemble_daily_patient_session,
    )

    result = await care_circle_session.pregenerate_daily_sessions()

    assert result["success_count"] == 1
    assert result["failure_count"] == 0
    assert captured["created_jobs"][0]["user_id"] == 55
    assert captured["created_jobs"][0]["job_type"] == JobTypeEnum.CARE_CIRCLE_DAILY_SESSION
    assert captured["updated_jobs"][0]["state"] == JobStateEnum.RUNNING
    assert captured["updated_jobs"][1]["state"] == JobStateEnum.COMPLETED
    assert captured["assembled"][0]["patient_id"] == 20
    assert captured["assembled"][0]["job_id"] == captured["created_jobs"][0]["job_id"]
    assert result["results"][0]["job_id"] == captured["created_jobs"][0]["job_id"]
