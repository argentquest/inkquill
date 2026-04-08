"""Mock-based unit tests for the care-circle router."""

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from app.routers.care_circle import router as care_circle_router


pytestmark = pytest.mark.unit


def test_list_providers_returns_wrapped_catalog(unit_client_factory):
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    providers = [
        {
            "providerKey": "weather",
            "label": "Weather",
            "icon": "sun",
            "category": "core",
            "enabled": True,
            "displayOrder": 1,
            "patientVisible": True,
            "familyVisible": True,
        }
    ]

    with patch("app.routers.care_circle.care_circle_crud.list_provider_catalog", new=AsyncMock(return_value=providers)):
        response = client.get("/api/v1/care-circle/providers")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"][0]["providerKey"] == "weather"


def test_family_patients_returns_wrapped_profiles(unit_client_factory):
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    patients = [
        {
            "id": "1",
            "displayName": "Rose Ellis",
            "familyName": "Story Maker household",
            "joinCode": "STM111",
            "stage": "moderate",
            "accessState": "active",
            "timezone": "America/Chicago",
            "deliveryTime": "08:30",
            "days": ["Mon", "Wed", "Fri"],
            "familyMembers": ["Nina"],
            "preferences": ["gardening"],
            "authImageKeys": ["sun", "dog", "house"],
            "highlights": [],
        }
    ]

    with patch("app.routers.care_circle.care_circle_crud.list_family_patients", new=AsyncMock(return_value=patients)):
        response = client.get("/api/v1/care-circle/family/patients")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"][0]["displayName"] == "Rose Ellis"
    assert body["data"][0]["joinCode"] == "STM111"


def test_family_patient_detail_returns_404_when_missing(unit_client_factory):
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")

    with patch("app.routers.care_circle.care_circle_crud.get_family_patient_detail", new=AsyncMock(return_value=None)):
        response = client.get("/api/v1/care-circle/family/patients/99")

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"


def test_family_patient_detail_returns_wrapped_record(unit_client_factory):
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    patient = {
        "id": "1",
        "displayName": "Rose Ellis",
        "familyName": "Story Maker household",
        "joinCode": "STM111",
        "stage": "moderate",
        "accessState": "active",
        "timezone": "America/Chicago",
        "deliveryTime": "08:30",
        "days": ["Mon", "Wed", "Fri"],
        "familyMembers": ["Nina"],
        "preferences": ["gardening"],
        "authImageKeys": ["sun", "dog", "house"],
        "highlights": [{"title": "Family hello", "body": "Hi", "kind": "family", "providerKey": "family_greeting", "displayOrder": 1}],
    }

    with patch("app.routers.care_circle.care_circle_crud.get_family_patient_detail", new=AsyncMock(return_value=patient)):
        response = client.get("/api/v1/care-circle/family/patients/1")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["displayName"] == "Rose Ellis"


def test_update_family_patient_detail_returns_wrapped_record(unit_client_factory):
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    patient = {
        "id": "1",
        "displayName": "Rose Ellis",
        "familyName": "Ellis household",
        "joinCode": "ELL123",
        "stage": "moderate",
        "accessState": "active",
        "timezone": "America/Chicago",
        "deliveryTime": "08:30",
        "days": ["Mon", "Wed", "Fri"],
        "familyMembers": ["Nina", "Paul"],
        "preferences": ["gardening"],
        "authImageKeys": ["sun", "dog", "house"],
        "highlights": [],
    }

    with patch("app.routers.care_circle.care_circle_crud.update_family_patient_detail", new=AsyncMock(return_value=patient)):
        response = client.put(
            "/api/v1/care-circle/family/patients/1",
            json={
                "familyName": "Ellis household",
                "joinCode": "ELL123",
                "displayName": "Rose Ellis",
                "stage": "moderate",
                "accessState": "active",
                "timezone": "America/Chicago",
                "deliveryTime": "08:30",
                "days": ["Mon", "Wed", "Fri"],
                "familyMembers": ["Nina", "Paul"],
                "preferences": ["gardening"],
                "authImageKeys": ["sun", "dog", "house"],
            },
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["familyName"] == "Ellis household"
    assert body["data"]["joinCode"] == "ELL123"


def test_update_family_patient_detail_rejects_invalid_auth_keys(unit_client_factory):
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")

    response = client.put(
        "/api/v1/care-circle/family/patients/1",
        json={
            "familyName": "Ellis household",
            "joinCode": "ELL123",
            "displayName": "Rose Ellis",
            "stage": "moderate",
            "accessState": "active",
            "timezone": "America/Chicago",
            "deliveryTime": "08:30",
            "days": ["Mon", "Wed", "Fri"],
            "familyMembers": ["Nina", "Paul"],
            "preferences": ["gardening"],
            "authImageKeys": ["sun", "sun", "house"],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Exactly three unique auth images are required"


def test_patient_auth_catalog_returns_wrapped_catalog(unit_client_factory):
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    catalog = [{"key": "sun", "label": "Sun", "emoji": "sun"}]

    with patch("app.routers.care_circle.care_circle_crud.get_patient_auth_catalog", new=AsyncMock(return_value=catalog)):
        response = client.get("/api/v1/care-circle/patient/auth/catalog")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"][0]["key"] == "sun"


def test_patient_auth_login_returns_wrapped_patient(unit_client_factory):
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    patient = {
        "id": "1",
        "displayName": "Rose Ellis",
        "familyName": "Story Maker household",
        "joinCode": "STM111",
        "stage": "moderate",
        "accessState": "active",
        "timezone": "America/Chicago",
        "deliveryTime": "08:30",
        "days": ["Mon", "Wed", "Fri"],
        "familyMembers": ["Nina"],
        "preferences": ["gardening"],
        "authImageKeys": ["sun", "dog", "house"],
        "highlights": [],
    }

    with patch("app.routers.care_circle.care_circle_crud.authenticate_patient_by_images", new=AsyncMock(return_value=patient)):
        response = client.post(
            "/api/v1/care-circle/patient/auth/login",
            json={"selected_image_keys": ["sun", "dog", "house"]},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["id"] == "1"


def test_patient_auth_login_returns_api_error_payload_for_invalid_selection(unit_client_factory):
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")

    with patch("app.routers.care_circle.care_circle_crud.authenticate_patient_by_images", new=AsyncMock(return_value=None)):
        response = client.post(
            "/api/v1/care-circle/patient/auth/login",
            json={"selected_image_keys": ["sun", "flower", "cake"]},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is False
    assert body["errors"][0]["code"] == "INVALID_PATIENT_AUTH"


def test_patient_session_returns_404_when_missing(unit_client_factory):
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")

    with patch("app.services.care_circle.session_assembler.assemble_daily_patient_session", new=AsyncMock(return_value=False)), \
         patch("app.routers.care_circle.care_circle_crud.get_patient_session", new=AsyncMock(return_value=None)):
        response = client.get("/api/v1/care-circle/patient/session/88")

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient session not found"


def test_patient_session_returns_wrapped_patient(unit_client_factory):
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    patient = {
        "id": "1",
        "displayName": "Rose Ellis",
        "familyName": "Story Maker household",
        "joinCode": "STM111",
        "stage": "moderate",
        "accessState": "active",
        "timezone": "America/Chicago",
        "deliveryTime": "08:30",
        "days": ["Mon", "Wed", "Fri"],
        "familyMembers": ["Nina"],
        "preferences": ["gardening"],
        "authImageKeys": ["sun", "dog", "house"],
        "highlights": [{"title": "Family hello", "body": "Hi", "kind": "family", "providerKey": "family_greeting", "displayOrder": 1}],
    }

    with patch("app.services.care_circle.session_assembler.assemble_daily_patient_session", new=AsyncMock(return_value=True)), \
         patch("app.routers.care_circle.care_circle_crud.get_patient_session", new=AsyncMock(return_value=patient)):
        response = client.get("/api/v1/care-circle/patient/session/1")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["highlights"][0]["title"] == "Family hello"
