import pytest
from sqlalchemy import select

from app.models.care_circle import CareCirclePatientProfile

pytestmark = pytest.mark.integration


def test_family_provider_registry_update(client, register_and_login):
    """`PUT /providers/{key}` updates global provider visibility flags."""
    payload, _ = register_and_login("carecircle_admin")

    # Test setting provider visibility through CRUD
    response = client.put(
        "/api/v1/care-circle/providers/weather",
        json={"enabled": False, "patient_visible": False},
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


def test_provider_registry_update_404_for_unknown_provider(client, register_and_login):
    """`PUT /providers/{unknown}` returns 404."""
    payload, _ = register_and_login("carecircle_admin")

    response = client.put(
        "/api/v1/care-circle/providers/nonexistent_provider_xyz",
        json={"enabled": False, "patient_visible": False},
    )
    assert response.status_code == 404


def test_provider_backed_session_assembly(client, register_and_login, run_db):
    """Patient session endpoint triggers provider assembly and returns highlights."""
    payload, _ = register_and_login("carecircle_patient_flow")

    # Force default seeding
    client.get("/api/v1/care-circle/family/patients")

    patient_id = _fetch_first_patient_for_current_user(client, run_db)

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


def _fetch_first_patient_for_current_user(client, run_db):
    """Get a patient ID from the family/patients list endpoint (ensures ownership)."""
    response = client.get("/api/v1/care-circle/family/patients")
    assert response.status_code == 200
    patients = response.json()["data"]
    assert len(patients) > 0
    return int(patients[0]["id"])


def test_patient_provider_configs_empty_for_new_patient(client, register_and_login, run_db):
    """`GET /family/patients/{id}/provider-configs` returns empty list initially."""
    payload, _ = register_and_login("carecircle_configs_test")

    # Force seeding
    client.get("/api/v1/care-circle/family/patients")

    patient_id = _fetch_first_patient_for_current_user(client, run_db)

    response = client.get(f"/api/v1/care-circle/family/patients/{patient_id}/provider-configs")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data == []


def test_patient_provider_config_upsert_creates_new(client, register_and_login, run_db):
    """`PUT /family/patients/{id}/provider-configs/{key}` creates a new config."""
    payload, _ = register_and_login("carecircle_upsert_test")

    # Force seeding
    client.get("/api/v1/care-circle/family/patients")

    patient_id = _fetch_first_patient_for_current_user(client, run_db)

    response = client.put(
        f"/api/v1/care-circle/family/patients/{patient_id}/provider-configs/weather",
        json={"is_enabled": False, "custom_parameters": {"city": "Chicago"}},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["provider_key"] == "weather"
    assert data["is_enabled"] is False
    assert data["custom_parameters"] == {"city": "Chicago"}


def test_patient_provider_config_upsert_updates_existing(client, register_and_login, run_db):
    """`PUT /family/patients/{id}/provider-configs/{key}` updates existing config."""
    payload, _ = register_and_login("carecircle_update_test")

    # Force seeding
    client.get("/api/v1/care-circle/family/patients")

    patient_id = _fetch_first_patient_for_current_user(client, run_db)

    # Create initial config
    client.put(
        f"/api/v1/care-circle/family/patients/{patient_id}/provider-configs/weather",
        json={"is_enabled": True, "custom_parameters": {}},
    )

    # Update the config
    response = client.put(
        f"/api/v1/care-circle/family/patients/{patient_id}/provider-configs/weather",
        json={"is_enabled": False, "custom_parameters": {"updated": True}},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["is_enabled"] is False
    assert data["custom_parameters"] == {"updated": True}


def test_patient_provider_config_list_shows_all_configs(client, register_and_login, run_db):
    """`GET /family/patients/{id}/provider-configs` returns all per-patient configs."""
    payload, _ = register_and_login("carecircle_list_test")

    # Force seeding
    client.get("/api/v1/care-circle/family/patients")

    patient_id = _fetch_first_patient_for_current_user(client, run_db)

    # Create two configs
    client.put(
        f"/api/v1/care-circle/family/patients/{patient_id}/provider-configs/weather",
        json={"is_enabled": False, "custom_parameters": {}},
    )
    client.put(
        f"/api/v1/care-circle/family/patients/{patient_id}/provider-configs/joke",
        json={"is_enabled": True, "custom_parameters": {"theme": "blue"}},
    )

    response = client.get(f"/api/v1/care-circle/family/patients/{patient_id}/provider-configs")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2


def test_patient_provider_config_404_for_unknown_patient(client, register_and_login):
    """Per-patient config endpoints return 404 for unknown patient."""
    payload, _ = register_and_login("carecircle_404_test")

    response = client.get("/api/v1/care-circle/family/patients/99999/provider-configs")
    assert response.status_code == 404

    response = client.put(
        "/api/v1/care-circle/family/patients/99999/provider-configs/weather",
        json={"is_enabled": False, "custom_parameters": {}},
    )
    assert response.status_code == 404


def test_family_patient_detail_update_persists_configuration(client, register_and_login, run_db):
    """`PUT /family/patients/{id}` updates patient and family-managed profile settings."""
    payload, _ = register_and_login("carecircle_family_update_test")

    client.get("/api/v1/care-circle/family/patients")
    patient_id = _fetch_first_patient_for_current_user(client, run_db)

    response = client.put(
        f"/api/v1/care-circle/family/patients/{patient_id}",
        json={
            "familyName": "Updated household",
            "joinCode": "UPD456",
            "displayName": "Rose Updated",
            "stage": "mild",
            "accessState": "inactive",
            "timezone": "America/Denver",
            "deliveryTime": "10:45",
            "days": ["Tue", "Thu"],
            "familyMembers": ["Lena", "Marco"],
            "preferences": ["jazz", "photo albums"],
            "authImageKeys": ["sun", "dog", "house"],
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["familyName"] == "Updated household"
    assert data["joinCode"] == "UPD456"
    assert data["displayName"] == "Rose Updated"
    assert data["stage"] == "mild"
    assert data["accessState"] == "inactive"
    assert data["timezone"] == "America/Denver"
    assert data["deliveryTime"] == "10:45"
    assert data["days"] == ["Tue", "Thu"]
    assert data["familyMembers"] == ["Lena", "Marco"]
    assert data["preferences"] == ["jazz", "photo albums"]

    refreshed = client.get(f"/api/v1/care-circle/family/patients/{patient_id}")
    assert refreshed.status_code == 200
    refreshed_data = refreshed.json()["data"]
    assert refreshed_data["familyName"] == "Updated household"
    assert refreshed_data["joinCode"] == "UPD456"
    assert refreshed_data["displayName"] == "Rose Updated"


def test_provider_registry_includes_all_seed_providers(client, register_and_login):
    """Provider catalog returns all seeded providers."""
    payload, _ = register_and_login("carecircle_seed_test")

    response = client.get("/api/v1/care-circle/providers")
    assert response.status_code == 200
    providers = response.json()["data"]

    # The CareCircle inventory now mirrors all implemented DailyNewsletter providers.
    assert len(providers) >= 40

    provider_keys = [p["providerKey"] for p in providers]
    assert "weather" in provider_keys
    assert "joke" in provider_keys
    assert "nostalgia" in provider_keys
    assert "brain_booster" in provider_keys
    assert "animal_friend" in provider_keys
    assert "bingo" in provider_keys
    assert "crossword" in provider_keys
    assert "daily_blessing" in provider_keys
    assert "memory_lane_photo" in provider_keys
    assert "simple_math" in provider_keys
    assert "word_connect" in provider_keys


def test_patient_session_includes_highlights_with_provider_keys(client, register_and_login, run_db):
    """Patient session highlights contain providerKey field for each card."""
    payload, _ = register_and_login("carecircle_highlights_test")

    client.get("/api/v1/care-circle/family/patients")

    patient_id = _fetch_first_patient_for_current_user(client, run_db)

    response = client.get(f"/api/v1/care-circle/patient/session/{patient_id}")
    assert response.status_code == 200
    session_data = response.json()["data"]

    highlights = session_data["highlights"]
    assert len(highlights) > 0

    for h in highlights:
        assert "providerKey" in h
        assert h["providerKey"] is not None
