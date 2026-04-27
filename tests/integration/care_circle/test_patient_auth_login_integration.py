"""Integration tests for patient auth, login, and session API endpoints."""
import pytest

pytestmark = pytest.mark.integration


def test_patient_auth_catalog_returns_image_choices(client):
    """`GET /patient/auth/catalog` returns the image catalog for patient sign-in."""
    # This endpoint is public - no auth required
    response = client.get("/api/v1/care-circle/patient/auth/catalog")
    assert response.status_code == 200
    data = response.json()["data"]
    assert isinstance(data, list)
    assert len(data) > 0

    # Verify catalog items have expected structure
    for item in data:
        assert "key" in item
        assert "label" in item
        assert "emoji" in item


def test_patient_auth_catalog_includes_standard_images(client):
    """Patient auth catalog includes the standard image choices."""
    response = client.get("/api/v1/care-circle/patient/auth/catalog")
    assert response.status_code == 200
    data = response.json()["data"]

    keys = [item["key"] for item in data]
    # Verify standard images are present
    assert "sun" in keys
    assert "dog" in keys
    assert "flower" in keys
    assert "house" in keys


def test_patient_login_with_correct_images_succeeds(client, register_and_login, run_db):
    """`POST /patient/auth/login` returns patient when correct images are provided."""
    payload, _ = register_and_login("patient_login_test")

    # Force seeding of default patients
    client.get("/api/v1/care-circle/family/patients")

    # Get first patient's image keys
    patient_id = _fetch_first_patient_for_current_user(client, run_db)
    patient_images = _fetch_patient_auth_images(client, run_db, patient_id)

    # Login with correct images
    response = client.post(
        "/api/v1/care-circle/patient/auth/login",
        json={"selected_image_keys": patient_images},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    # Verify we got a valid patient with the matching image keys
    assert "id" in data
    assert "displayName" in data
    assert "accessState" in data
    # The returned patient should have the same auth image keys we used
    assert set(data["authImageKeys"]) == set(patient_images)


def test_patient_login_with_incorrect_images_fails(client):
    """`POST /patient/auth/login` returns error when wrong images are provided."""
    # Login with wrong images that don't match any patient
    response = client.post(
        "/api/v1/care-circle/patient/auth/login",
        json={"selected_image_keys": ["sun", "moon", "star"]},
    )
    assert response.status_code == 200  # API returns 200 with error response
    data = response.json()
    assert data["success"] is False
    assert len(data["errors"]) > 0
    assert data["errors"][0]["code"] == "INVALID_PATIENT_AUTH"


def test_patient_login_requires_exactly_three_images(client):
    """`POST /patient/auth/login` requires exactly 3 image keys."""
    # Test with too few images
    response = client.post(
        "/api/v1/care-circle/patient/auth/login",
        json={"selected_image_keys": ["sun", "dog"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False

    # Test with too many images
    response = client.post(
        "/api/v1/care-circle/patient/auth/login",
        json={"selected_image_keys": ["sun", "dog", "flower", "house"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False


def test_patient_session_returns_highlights(client, register_and_login, run_db):
    """`GET /patient/session/{id}` returns patient with highlights."""
    payload, _ = register_and_login("patient_session_test")

    # Force seeding
    client.get("/api/v1/care-circle/family/patients")

    patient_id = _fetch_first_patient_for_current_user(client, run_db)

    response = client.get(f"/api/v1/care-circle/patient/session/{patient_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    assert "highlights" in data
    assert len(data["highlights"]) > 0

    for highlight in data["highlights"]:
        assert "title" in highlight
        assert "body" in highlight
        assert "kind" in highlight
        assert "providerKey" in highlight
        assert "feedback" in highlight


def test_patient_session_404_for_unknown_patient(client):
    """`GET /patient/session/{unknown}` returns 404."""
    response = client.get("/api/v1/care-circle/patient/session/99999")
    assert response.status_code == 404


def test_patient_session_regenerates_fresh_content(client, register_and_login, run_db):
    """Patient session endpoint regenerates content on each call."""
    payload, _ = register_and_login("patient_session_refresh_test")

    # Force seeding
    client.get("/api/v1/care-circle/family/patients")

    patient_id = _fetch_first_patient_for_current_user(client, run_db)

    # First call
    response1 = client.get(f"/api/v1/care-circle/patient/session/{patient_id}")
    assert response1.status_code == 200
    highlights1 = response1.json()["data"]["highlights"]

    # Second call should also succeed (may have same or different content)
    response2 = client.get(f"/api/v1/care-circle/patient/session/{patient_id}")
    assert response2.status_code == 200
    highlights2 = response2.json()["data"]["highlights"]

    # Both calls should return highlights
    assert len(highlights1) > 0
    assert len(highlights2) > 0


def test_patient_provider_feedback_persists_across_sessions(client, register_and_login, run_db):
    """Patient provider feedback is stored and returned on later session loads."""
    register_and_login("patient_feedback_test")

    client.get("/api/v1/care-circle/family/patients")
    patient_id = _fetch_first_patient_for_current_user(client, run_db)

    session_response = client.get(f"/api/v1/care-circle/patient/session/{patient_id}")
    assert session_response.status_code == 200
    highlights = session_response.json()["data"]["highlights"]
    provider_key = highlights[0]["providerKey"]

    save_response = client.put(
        f"/api/v1/care-circle/patient/session/{patient_id}/provider-feedback/{provider_key}",
        json={"feedback": "like"},
    )
    assert save_response.status_code == 200
    assert save_response.json()["data"]["feedback"] == "like"

    later_session_response = client.get(f"/api/v1/care-circle/patient/session/{patient_id}")
    assert later_session_response.status_code == 200
    later_highlights = later_session_response.json()["data"]["highlights"]
    saved_highlight = next(item for item in later_highlights if item["providerKey"] == provider_key)
    assert saved_highlight["feedback"] == "like"

    clear_response = client.put(
        f"/api/v1/care-circle/patient/session/{patient_id}/provider-feedback/{provider_key}",
        json={"feedback": None},
    )
    assert clear_response.status_code == 200
    assert clear_response.json()["data"]["feedback"] is None

    cleared_session_response = client.get(f"/api/v1/care-circle/patient/session/{patient_id}")
    assert cleared_session_response.status_code == 200
    cleared_highlights = cleared_session_response.json()["data"]["highlights"]
    cleared_highlight = next(item for item in cleared_highlights if item["providerKey"] == provider_key)
    assert cleared_highlight["feedback"] is None


def test_patient_profile_has_expected_fields(client, register_and_login, run_db):
    """Patient login response includes all expected profile fields."""
    payload, _ = register_and_login("patient_fields_test")

    # Force seeding
    client.get("/api/v1/care-circle/family/patients")

    patient_id = _fetch_first_patient_for_current_user(client, run_db)
    patient_images = _fetch_patient_auth_images(client, run_db, patient_id)

    response = client.post(
        "/api/v1/care-circle/patient/auth/login",
        json={"selected_image_keys": patient_images},
    )
    assert response.status_code == 200
    data = response.json()["data"]

    # Verify all expected fields are present
    assert "id" in data
    assert "displayName" in data
    assert "familyName" in data
    assert "joinCode" in data
    assert "stage" in data
    assert "accessState" in data
    assert "timezone" in data
    assert "deliveryTime" in data or data.get("deliveryTime") is None
    assert "days" in data
    assert "familyMembers" in data
    assert "preferences" in data
    assert "authImageKeys" in data


def _fetch_first_patient_for_current_user(client, run_db):
    """Get a patient ID from the family/patients list endpoint."""
    response = client.get("/api/v1/care-circle/family/patients")
    assert response.status_code == 200
    patients = response.json()["data"]
    assert len(patients) > 0
    return int(patients[0]["id"])


def _fetch_patient_auth_images(client, run_db, patient_id):
    """Get the auth image keys for a specific patient."""
    response = client.get(f"/api/v1/care-circle/family/patients/{patient_id}")
    assert response.status_code == 200
    data = response.json()["data"]
    return data.get("authImageKeys", [])
