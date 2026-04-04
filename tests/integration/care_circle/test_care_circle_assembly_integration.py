import pytest
from sqlalchemy import select

from app.models.care_circle import CareCirclePatientProfile

pytestmark = pytest.mark.integration

def test_family_provider_registry_update(client, register_and_login):
    payload, _ = register_and_login("carecircle_admin")
    
    # Test setting provider visibility through CRUD
    response = client.put(
        "/api/v1/care-circle/providers/weather",
        json={"enabled": False, "patient_visible": False}
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["message"] == "Updated successfully"

    response = client.get("/api/v1/care-circle/providers")
    assert response.status_code == 200
    providers = response.json()["data"]
    weather = next(p for p in providers if p["providerKey"] == "weather")
    assert weather["enabled"] is False
    assert weather["patientVisible"] is False


def test_provider_backed_session_assembly(client, register_and_login, run_db):
    payload, _ = register_and_login("carecircle_patient_flow")
    
    # Force default seeding
    client.get("/api/v1/care-circle/family/patients")

    def fetch_patient_id(session):
        async def _inner():
            patient = await session.scalar(select(CareCirclePatientProfile).limit(1))
            return patient.id
        return _inner()
        
    patient_id = run_db(fetch_patient_id)
    assert patient_id is not None

    # Fetching the session dynamically triggers the assembler
    response = client.get(f"/api/v1/care-circle/patient/session/{patient_id}")
    assert response.status_code == 200
    session_data = response.json()["data"]
    
    highlights = session_data["highlights"]
    assert len(highlights) > 0
    
    for h in highlights:
        assert h["title"] is not None
        assert h["body"] is not None
        assert h["kind"] is not None
