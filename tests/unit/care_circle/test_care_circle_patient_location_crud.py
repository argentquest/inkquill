from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.crud import care_circle as care_circle_crud


@pytest.mark.asyncio
async def test_update_family_patient_detail_resolves_postal_code_to_coordinates():
    family = SimpleNamespace(id=7, name="Family", join_code="ABC123")
    patient = SimpleNamespace(
        id=17,
        family_id=7,
        display_name="Rose",
        stage="moderate",
        access_state="active",
        timezone="America/Chicago",
        preferred_language="en",
        country="CA",
        postal_code=None,
        latitude=None,
        longitude=None,
        delivery_time=None,
        delivery_days=[],
        auth_image_keys=["sun", "dog", "house"],
        email=None,
        phone_number=None,
        preferences={},
    )
    db = AsyncMock()
    db.scalar = AsyncMock(side_effect=[patient, None])
    db.commit = AsyncMock()

    payload = {
        "familyName": "Family",
        "joinCode": "ABC123",
        "displayName": "Rose",
        "stage": "moderate",
        "accessState": "active",
        "timezone": "America/Toronto",
        "preferredLanguage": "en",
        "country": "CA",
        "postalCode": "H2Y 1C6",
        "deliveryTime": None,
        "days": ["Mon"],
        "authImageKeys": ["sun", "dog", "house"],
        "email": None,
        "phoneNumber": None,
        "preferences": {},
    }

    resolved = SimpleNamespace(
        latitude=45.5033,
        longitude=-73.5561,
        formatted_city="Montreal, Quebec",
    )

    with patch.object(care_circle_crud, "get_or_create_family_for_user", new=AsyncMock(return_value=family)), \
         patch.object(care_circle_crud, "resolve_postal_location", new=AsyncMock(return_value=resolved)), \
         patch.object(care_circle_crud, "get_family_patient_detail", new=AsyncMock(return_value={"id": "17"})):
        result = await care_circle_crud.update_family_patient_detail(db, MagicMock(), 17, payload)

    assert result == {"id": "17"}
    assert patient.postal_code == "H2Y 1C6"
    assert patient.latitude == 45.5033
    assert patient.longitude == -73.5561
    assert patient.preferences["city_for_weather"] == "Montreal, Quebec"


@pytest.mark.asyncio
async def test_create_family_patient_resolves_postal_code_to_coordinates():
    family = SimpleNamespace(id=7, name="Family", join_code="ABC123")
    db = AsyncMock()
    db.add = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()

    payload = {
        "displayName": "Rose",
        "country": "CA",
        "postalCode": "H2Y 1C6",
    }

    resolved = SimpleNamespace(
        latitude=45.5033,
        longitude=-73.5561,
        formatted_city="Montreal, Quebec",
    )

    with patch.object(care_circle_crud, "get_or_create_family_for_user", new=AsyncMock(return_value=family)), \
         patch.object(care_circle_crud, "resolve_postal_location", new=AsyncMock(return_value=resolved)):
        result = await care_circle_crud.create_family_patient(db, MagicMock(id=9), payload)

    created_patient = db.add.call_args.args[0]
    assert created_patient.postal_code == "H2Y 1C6"
    assert created_patient.latitude == 45.5033
    assert created_patient.longitude == -73.5561
    assert created_patient.preferences["city_for_weather"] == "Montreal, Quebec"
    assert result["postalCode"] == "H2Y 1C6"
