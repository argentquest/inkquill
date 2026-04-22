"""Mock-based unit tests for the care-circle router."""

from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

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


# ── Provider config — display_order ───────────────────────────────────────────

def test_get_provider_configs_returns_display_order(unit_client_factory, mock_db_session):
    """GET /provider-configs includes display_order in each config entry."""
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    configs = [
        {
            "id": 1,
            "patient_id": 1,
            "provider_key": "joke",
            "is_enabled": True,
            "display_order": 2,
            "custom_parameters": {},
        },
        {
            "id": 2,
            "patient_id": 1,
            "provider_key": "weather",
            "is_enabled": True,
            "display_order": 0,
            "custom_parameters": {},
        },
    ]
    # db.scalar is used by the router to confirm patient ownership
    mock_db_session.scalar.return_value = MagicMock(id=1, family_id=1)

    with patch("app.routers.care_circle.care_circle_crud.get_or_create_family_for_user", new=AsyncMock(return_value=MagicMock(id=1))), \
         patch("app.routers.care_circle.care_circle_crud.get_patient_provider_configs", new=AsyncMock(return_value=configs)):
        response = client.get("/api/v1/care-circle/family/patients/1/provider-configs")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert len(data) == 2
    keys_orders = {c["provider_key"]: c["display_order"] for c in data}
    assert keys_orders["joke"] == 2
    assert keys_orders["weather"] == 0


def test_upsert_provider_config_with_display_order(unit_client_factory, mock_db_session):
    """PUT /provider-configs/{key} persists and returns display_order."""
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    mock_config = MagicMock(
        id=5,
        patient_id=1,
        provider_key="joke",
        is_enabled=True,
        display_order=3,
        custom_parameters={},
    )
    mock_db_session.scalar.return_value = MagicMock(id=1, family_id=1)

    with patch("app.routers.care_circle.care_circle_crud.get_or_create_family_for_user", new=AsyncMock(return_value=MagicMock(id=1))), \
         patch("app.routers.care_circle.care_circle_crud.upsert_patient_provider_config", new=AsyncMock(return_value=mock_config)):
        response = client.put(
            "/api/v1/care-circle/family/patients/1/provider-configs/joke",
            json={"is_enabled": True, "custom_parameters": {}, "display_order": 3},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["display_order"] == 3
    assert body["data"]["provider_key"] == "joke"


def test_upsert_provider_config_without_display_order_returns_none(unit_client_factory, mock_db_session):
    """PUT /provider-configs/{key} accepts missing display_order (defaults to None)."""
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    mock_config = MagicMock(
        id=6,
        patient_id=1,
        provider_key="weather",
        is_enabled=False,
        display_order=None,
        custom_parameters={"city": "Austin"},
    )
    mock_db_session.scalar.return_value = MagicMock(id=1, family_id=1)

    with patch("app.routers.care_circle.care_circle_crud.get_or_create_family_for_user", new=AsyncMock(return_value=MagicMock(id=1))), \
         patch("app.routers.care_circle.care_circle_crud.upsert_patient_provider_config", new=AsyncMock(return_value=mock_config)):
        response = client.put(
            "/api/v1/care-circle/family/patients/1/provider-configs/weather",
            json={"is_enabled": False, "custom_parameters": {"city": "Austin"}},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["display_order"] is None


# ── Provider config reorder endpoint ──────────────────────────────────────────

def test_reorder_provider_configs_success(unit_client_factory, mock_db_session):
    """POST /provider-configs/reorder saves new order and returns success."""
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    mock_db_session.scalar.return_value = MagicMock(id=1, family_id=1)

    ordering = [
        {"provider_key": "joke", "display_order": 0},
        {"provider_key": "weather", "display_order": 1},
        {"provider_key": "nostalgia", "display_order": 2},
    ]

    with patch("app.routers.care_circle.care_circle_crud.get_or_create_family_for_user", new=AsyncMock(return_value=MagicMock(id=1))), \
         patch("app.routers.care_circle.care_circle_crud.reorder_patient_provider_configs", new=AsyncMock(return_value=None)) as mock_reorder:
        response = client.post(
            "/api/v1/care-circle/family/patients/1/provider-configs/reorder",
            json={"ordering": ordering},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["message"] == "Order saved"
    mock_reorder.assert_awaited_once()


def test_reorder_provider_configs_passes_correct_ordering_to_crud(unit_client_factory, mock_db_session):
    """POST /provider-configs/reorder passes the ordering list to the CRUD function."""
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    mock_db_session.scalar.return_value = MagicMock(id=1, family_id=1)

    ordering = [
        {"provider_key": "brain_booster", "display_order": 0},
        {"provider_key": "joke", "display_order": 1},
    ]

    captured_args = {}

    async def fake_reorder(db, patient_id, ordering_list):
        captured_args["patient_id"] = patient_id
        captured_args["ordering"] = ordering_list

    with patch("app.routers.care_circle.care_circle_crud.get_or_create_family_for_user", new=AsyncMock(return_value=MagicMock(id=1))), \
         patch("app.routers.care_circle.care_circle_crud.reorder_patient_provider_configs", new=fake_reorder):
        response = client.post(
            "/api/v1/care-circle/family/patients/1/provider-configs/reorder",
            json={"ordering": ordering},
        )

    assert response.status_code == 200, response.text
    assert captured_args["patient_id"] == 1
    assert len(captured_args["ordering"]) == 2
    assert captured_args["ordering"][0]["provider_key"] == "brain_booster"
    assert captured_args["ordering"][0]["display_order"] == 0


def test_reorder_provider_configs_returns_404_when_patient_not_found(unit_client_factory, mock_db_session):
    """POST /provider-configs/reorder returns 404 if patient doesn't belong to family."""
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    mock_db_session.scalar.return_value = None  # patient not found / not owned

    with patch("app.routers.care_circle.care_circle_crud.get_or_create_family_for_user", new=AsyncMock(return_value=MagicMock(id=1))):
        response = client.post(
            "/api/v1/care-circle/family/patients/99/provider-configs/reorder",
            json={"ordering": [{"provider_key": "joke", "display_order": 0}]},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Patient not found"


def test_reorder_provider_configs_empty_ordering_is_noop(unit_client_factory, mock_db_session):
    """POST /provider-configs/reorder with empty list succeeds (no-op)."""
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")
    mock_db_session.scalar.return_value = MagicMock(id=1, family_id=1)

    with patch("app.routers.care_circle.care_circle_crud.get_or_create_family_for_user", new=AsyncMock(return_value=MagicMock(id=1))), \
         patch("app.routers.care_circle.care_circle_crud.reorder_patient_provider_configs", new=AsyncMock(return_value=None)):
        response = client.post(
            "/api/v1/care-circle/family/patients/1/provider-configs/reorder",
            json={"ordering": []},
        )

    assert response.status_code == 200, response.text
    assert response.json()["success"] is True


# ── Newsletter email service ──────────────────────────────────────────────────

def test_send_newsletter_email_sends_to_patient_address():
    """send_newsletter_email sends to the patient's own email address."""
    import asyncio
    from app.services.care_circle.newsletter_email_service import send_newsletter_email

    mock_patient = MagicMock()
    mock_patient.display_name = "Rose Ellis"
    mock_patient.family_name = None
    mock_patient.email = "rose@example.com"

    with patch("app.services.care_circle.newsletter_email_service.settings") as mock_settings, \
         patch("app.services.care_circle.newsletter_email_service.smtplib") as mock_smtplib:
        mock_settings.EMAIL_TEST_MODE = False
        mock_settings.FROM_NAME = "Care Circle"
        mock_settings.FROM_EMAIL = "noreply@inkandquill.com"
        mock_settings.SMTP_SERVER = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USERNAME = "user@example.com"
        mock_settings.SMTP_PASSWORD = "secret"

        mock_smtp_instance = MagicMock()
        mock_smtplib.SMTP.return_value.__enter__ = MagicMock(return_value=mock_smtp_instance)
        mock_smtplib.SMTP.return_value.__exit__ = MagicMock(return_value=False)

        result = asyncio.run(send_newsletter_email(mock_patient, "<h1>Hello Rose</h1>", date.today()))

    assert result["success"] is True
    assert result["to_email"] == "rose@example.com"
    assert result["test_mode"] is False


def test_send_newsletter_email_redirects_in_test_mode():
    """send_newsletter_email sends to EMAIL_TEST_ADDRESS when EMAIL_TEST_MODE=True."""
    import asyncio
    from app.services.care_circle.newsletter_email_service import send_newsletter_email

    mock_patient = MagicMock()
    mock_patient.display_name = "Rose Ellis"
    mock_patient.family_name = "Ellis"
    mock_patient.email = "rose@example.com"

    with patch("app.services.care_circle.newsletter_email_service.settings") as mock_settings, \
         patch("app.services.care_circle.newsletter_email_service.smtplib") as mock_smtplib:
        mock_settings.EMAIL_TEST_MODE = True
        mock_settings.EMAIL_TEST_ADDRESS = "dev@example.com"
        mock_settings.FROM_NAME = "Care Circle"
        mock_settings.FROM_EMAIL = "noreply@inkandquill.com"
        mock_settings.SMTP_SERVER = "smtp.example.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.SMTP_USERNAME = "user@example.com"
        mock_settings.SMTP_PASSWORD = "secret"

        mock_smtp_instance = MagicMock()
        mock_smtplib.SMTP.return_value.__enter__ = MagicMock(return_value=mock_smtp_instance)
        mock_smtplib.SMTP.return_value.__exit__ = MagicMock(return_value=False)

        result = asyncio.run(send_newsletter_email(mock_patient, "<h1>Hello Rose</h1>", date.today()))

    assert result["success"] is True
    assert result["to_email"] == "dev@example.com"
    assert result["original_email"] == "rose@example.com"
    assert result["test_mode"] is True


def test_send_newsletter_email_skips_when_no_email():
    """send_newsletter_email returns failure when patient has no email set."""
    import asyncio
    from app.services.care_circle.newsletter_email_service import send_newsletter_email

    mock_patient = MagicMock()
    mock_patient.display_name = "Rose Ellis"
    mock_patient.family_name = None
    mock_patient.email = None

    with patch("app.services.care_circle.newsletter_email_service.settings") as mock_settings:
        mock_settings.EMAIL_TEST_MODE = False

        result = asyncio.run(send_newsletter_email(mock_patient, "<h1>Hello Rose</h1>", date.today()))

    assert result["success"] is False
    assert result["reason"] == "no_email"
    assert result["to_email"] is None


# ── Newsletter SMS service ────────────────────────────────────────────────────

def test_send_sms_newsletter_sends_to_patient_number():
    """send_sms_newsletter sends to the patient's own phone number."""
    import asyncio
    from app.services.care_circle.newsletter_sms_service import send_sms_newsletter

    mock_patient = MagicMock()
    mock_patient.display_name = "Rose Ellis"
    mock_patient.family_name = "Ellis"
    mock_patient.phone_number = "+15125550001"

    # Provider results use {"key": ..., "data": {...}} format
    provider_results = [
        {"key": "daily_blessing", "data": {"blessing": "May you have a wonderful day!"}},
    ]

    with patch("app.services.care_circle.newsletter_sms_service.settings") as mock_settings, \
         patch("app.services.care_circle.newsletter_sms_service._send_via_twilio", return_value=True) as mock_send:
        mock_settings.SMS_TEST_MODE = False
        mock_settings.SMS_TEST_NUMBER = None

        result = asyncio.run(send_sms_newsletter(mock_patient, provider_results))

    assert result["success"] is True
    assert result["to_number"] == "+15125550001"
    assert result["test_mode"] is False
    mock_send.assert_called_once_with("+15125550001", mock_send.call_args[0][1])


def test_send_sms_newsletter_redirects_in_test_mode():
    """send_sms_newsletter sends to SMS_TEST_NUMBER when SMS_TEST_MODE=True."""
    import asyncio
    from app.services.care_circle.newsletter_sms_service import send_sms_newsletter

    mock_patient = MagicMock()
    mock_patient.display_name = "Rose Ellis"
    mock_patient.family_name = None
    mock_patient.phone_number = "+15125550001"

    provider_results = [
        {"key": "joke", "data": {"setup": "Why did the chicken", "punchline": "To get to the other side!"}},
    ]

    with patch("app.services.care_circle.newsletter_sms_service.settings") as mock_settings, \
         patch("app.services.care_circle.newsletter_sms_service._send_via_twilio", return_value=True) as mock_send:
        mock_settings.SMS_TEST_MODE = True
        mock_settings.SMS_TEST_NUMBER = "+15005550099"

        result = asyncio.run(send_sms_newsletter(mock_patient, provider_results))

    assert result["success"] is True
    assert result["to_number"] == "+15005550099"
    assert result["original_number"] == "+15125550001"
    assert result["test_mode"] is True
    mock_send.assert_called_once_with("+15005550099", mock_send.call_args[0][1])


def test_send_sms_newsletter_skips_when_no_phone():
    """send_sms_newsletter returns failure when patient has no phone number."""
    import asyncio
    from app.services.care_circle.newsletter_sms_service import send_sms_newsletter

    mock_patient = MagicMock()
    mock_patient.display_name = "Rose Ellis"
    mock_patient.family_name = None
    mock_patient.phone_number = None

    with patch("app.services.care_circle.newsletter_sms_service.settings") as mock_settings:
        mock_settings.SMS_TEST_MODE = False

        result = asyncio.run(send_sms_newsletter(mock_patient, []))

    assert result["success"] is False
    assert result["reason"] == "no_phone"
    assert result["to_number"] is None


def test_send_sms_newsletter_filters_to_sms_provider_keys():
    """send_sms_newsletter only sends content from SMS_PROVIDER_KEYS, not all providers."""
    import asyncio
    from app.services.care_circle.newsletter_sms_service import send_sms_newsletter, SMS_PROVIDER_KEYS

    mock_patient = MagicMock()
    mock_patient.display_name = "Rose Ellis"
    mock_patient.family_name = None
    mock_patient.phone_number = "+15125550001"

    # Mix SMS-eligible and non-eligible providers
    provider_results = [
        {"key": "daily_blessing", "data": {"blessing": "Have a great day!"}},
        {"key": "weather", "data": {"summary": "Sunny, 72°F"}},    # NOT in SMS_PROVIDER_KEYS
        {"key": "joke", "data": {"setup": "Knock knock", "punchline": "Who's there?"}},
    ]

    assert "weather" not in SMS_PROVIDER_KEYS, "Test assumption: weather is not an SMS provider"

    captured = {}

    def fake_send(to_number, body):
        captured["body"] = body
        return True

    with patch("app.services.care_circle.newsletter_sms_service.settings") as mock_settings, \
         patch("app.services.care_circle.newsletter_sms_service._send_via_twilio", side_effect=fake_send):
        mock_settings.SMS_TEST_MODE = False
        mock_settings.SMS_TEST_NUMBER = None

        result = asyncio.run(send_sms_newsletter(mock_patient, provider_results))

    assert result["success"] is True
    # Weather content must not appear in the SMS body
    assert "Sunny" not in captured["body"]
    # Both SMS-eligible snippets should appear
    assert "Have a great day" in captured["body"] or "Knock knock" in captured["body"]


# ── CRUD: reorder_patient_provider_configs ─────────────────────────────────────

@pytest.mark.asyncio
async def test_reorder_patient_provider_configs_updates_existing_records(mock_db_session):
    """reorder_patient_provider_configs updates display_order for existing configs."""
    from app.crud.care_circle import reorder_patient_provider_configs
    from app.models.care_circle import CareCircleProviderPatientConfig

    # Mock existing configs - use a call counter to return different configs
    config1 = MagicMock(
        id=1,
        patient_id=1,
        provider_key="joke",
        is_enabled=True,
        display_order=0,
        custom_parameters={},
    )
    config2 = MagicMock(
        id=2,
        patient_id=1,
        provider_key="weather",
        is_enabled=True,
        display_order=1,
        custom_parameters={},
    )

    # Track call count to return configs in order (weather first, then joke)
    call_count = {"count": 0}
    configs_to_return = [config2, config1]

    async def mock_scalar(stmt):
        idx = call_count["count"]
        call_count["count"] += 1
        if idx < len(configs_to_return):
            return configs_to_return[idx]
        return None

    mock_db_session.scalar = AsyncMock(side_effect=mock_scalar)

    ordering = [
        {"provider_key": "weather", "display_order": 0},
        {"provider_key": "joke", "display_order": 1},
    ]

    await reorder_patient_provider_configs(mock_db_session, 1, ordering)

    # Verify display_order was updated
    assert config2.display_order == 0  # weather now first
    assert config1.display_order == 1  # joke now second
    mock_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_reorder_patient_provider_configs_creates_missing_records(mock_db_session):
    """reorder_patient_provider_configs creates new config records when they don't exist."""
    from app.crud.care_circle import reorder_patient_provider_configs
    from app.models.care_circle import CareCircleProviderPatientConfig

    # No existing configs
    mock_db_session.scalar = AsyncMock(return_value=None)

    ordering = [
        {"provider_key": "new_provider", "display_order": 0},
        {"provider_key": "another_provider", "display_order": 1},
    ]

    await reorder_patient_provider_configs(mock_db_session, 1, ordering)

    # Verify two new configs were added
    assert mock_db_session.add.call_count == 2
    mock_db_session.commit.assert_awaited_once()

    # Check the added configs have correct attributes
    added_calls = mock_db_session.add.call_args_list
    first_added = added_calls[0][0][0]
    assert first_added.patient_id == 1
    assert first_added.provider_key == "new_provider"
    assert first_added.display_order == 0
    assert first_added.is_enabled is True
    assert first_added.custom_parameters == {}


@pytest.mark.asyncio
async def test_reorder_patient_provider_configs_mixed_update_and_create(mock_db_session):
    """reorder_patient_provider_configs handles mix of existing and new configs."""
    from app.crud.care_circle import reorder_patient_provider_configs

    existing_config = MagicMock(
        id=1,
        patient_id=1,
        provider_key="joke",
        is_enabled=True,
        display_order=0,
        custom_parameters={},
    )

    # Return existing config first call, None for second
    call_count = {"count": 0}

    async def mock_scalar(stmt):
        call_count["count"] += 1
        if call_count["count"] == 1:
            return existing_config
        return None

    mock_db_session.scalar = AsyncMock(side_effect=mock_scalar)

    ordering = [
        {"provider_key": "joke", "display_order": 1},  # Update existing
        {"provider_key": "new_provider", "display_order": 0},  # Create new
    ]

    await reorder_patient_provider_configs(mock_db_session, 1, ordering)

    # Existing config should be updated
    assert existing_config.display_order == 1
    # One new config should be added
    assert mock_db_session.add.call_count == 1
    mock_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_reorder_patient_provider_configs_empty_ordering_is_noop(mock_db_session):
    """reorder_patient_provider_configs with empty list is a no-op but still commits."""
    from app.crud.care_circle import reorder_patient_provider_configs

    await reorder_patient_provider_configs(mock_db_session, 1, [])

    mock_db_session.scalar.assert_not_called()
    mock_db_session.add.assert_not_called()
    mock_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_reorder_patient_provider_configs_single_item(mock_db_session):
    """reorder_patient_provider_configs handles single item ordering."""
    from app.crud.care_circle import reorder_patient_provider_configs

    existing_config = MagicMock(
        id=1,
        patient_id=1,
        provider_key="joke",
        is_enabled=True,
        display_order=5,
        custom_parameters={},
    )

    mock_db_session.scalar = AsyncMock(return_value=existing_config)

    ordering = [
        {"provider_key": "joke", "display_order": 0},
    ]

    await reorder_patient_provider_configs(mock_db_session, 1, ordering)

    assert existing_config.display_order == 0
    mock_db_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_reorder_patient_provider_configs_preserves_other_fields(mock_db_session):
    """reorder_patient_provider_configs only updates display_order, not other fields."""
    from app.crud.care_circle import reorder_patient_provider_configs

    existing_config = MagicMock(
        id=1,
        patient_id=1,
        provider_key="joke",
        is_enabled=False,
        display_order=0,
        custom_parameters={"theme": "dark"},
    )

    mock_db_session.scalar = AsyncMock(return_value=existing_config)

    ordering = [
        {"provider_key": "joke", "display_order": 5},
    ]

    await reorder_patient_provider_configs(mock_db_session, 1, ordering)

    # Only display_order should change
    assert existing_config.display_order == 5
    assert existing_config.is_enabled is False
    assert existing_config.custom_parameters == {"theme": "dark"}
    mock_db_session.commit.assert_awaited_once()
