"""
Unit tests for care-circle provider registry loading, filtering, ordering, and fallback behavior.
Covers the tasks:
- add backend unit tests for provider registry loading, filtering, and failure fallback
"""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from app.routers.care_circle import router as care_circle_router


pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# Router-level provider catalog tests
# ---------------------------------------------------------------------------

def test_list_providers_returns_wrapped_catalog_with_all_fields(unit_client_factory):
    """`GET /care-circle/providers` returns ApiResponse with full provider fields."""
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
        },
        {
            "providerKey": "joke",
            "label": "Daily Joy",
            "icon": "smile",
            "category": "wellbeing",
            "enabled": True,
            "displayOrder": 2,
            "patientVisible": True,
            "familyVisible": True,
        },
    ]

    with patch("app.routers.care_circle.care_circle_crud.list_provider_catalog", new=AsyncMock(return_value=providers)):
        response = client.get("/api/v1/care-circle/providers")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert len(body["data"]) == 2
    assert body["data"][0]["providerKey"] == "weather"
    assert body["data"][1]["providerKey"] == "joke"


def test_update_provider_toggles_enabled_and_patient_visible(unit_client_factory):
    """`PUT /care-circle/providers/{key}` updates catalog flags."""
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")

    with patch("app.routers.care_circle.care_circle_crud.update_provider_catalog", new=AsyncMock(return_value=MagicMock())):
        response = client.put(
            "/api/v1/care-circle/providers/weather",
            json={"enabled": False, "patient_visible": False},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["message"] == "Updated successfully"


def test_update_provider_returns_404_for_unknown_key(unit_client_factory):
    """`PUT /care-circle/providers/{unknown}` returns 404."""
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")

    with patch("app.routers.care_circle.care_circle_crud.update_provider_catalog", new=AsyncMock(return_value=None)):
        response = client.put(
            "/api/v1/care-circle/providers/nonexistent_provider",
            json={"enabled": False, "patient_visible": False},
        )

    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Per-patient provider config CRUD tests
# ---------------------------------------------------------------------------

def test_upsert_patient_provider_config_creates_new_record(unit_client_factory):
    """`PUT /family/patients/{id}/provider-configs/{key}` creates a new config."""
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")

    mock_config = MagicMock(
        id=1,
        patient_id=1,
        provider_key="weather",
        is_enabled=False,
        custom_parameters={},
    )

    with patch(
        "app.routers.care_circle.care_circle_crud.get_or_create_family_for_user",
        new=AsyncMock(return_value=MagicMock(id=1)),
    ), patch(
        "app.routers.care_circle.care_circle_crud.upsert_patient_provider_config",
        new=AsyncMock(return_value=mock_config),
    ):
        response = client.put(
            "/api/v1/care-circle/family/patients/1/provider-configs/weather",
            json={"is_enabled": False, "custom_parameters": {}},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"]["provider_key"] == "weather"
    assert body["data"]["is_enabled"] is False


def test_list_patient_provider_configs_returns_empty_for_new_patient(unit_client_factory):
    """`GET /family/patients/{id}/provider-configs` returns empty list when no configs exist."""
    client = unit_client_factory(care_circle_router, router_prefix="/api/v1")

    with patch(
        "app.routers.care_circle.care_circle_crud.get_or_create_family_for_user",
        new=AsyncMock(return_value=MagicMock(id=1)),
    ), patch(
        "app.routers.care_circle.care_circle_crud.get_patient_provider_configs",
        new=AsyncMock(return_value=[]),
    ):
        response = client.get("/api/v1/care-circle/family/patients/1/provider-configs")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["success"] is True
    assert body["data"] == []


# ---------------------------------------------------------------------------
# Session assembler filtering and fallback tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_session_assembler_returns_false_for_archived_patient():
    """`assemble_daily_patient_session` returns False for archived patients."""
    from app.services.care_circle.session_assembler import assemble_daily_patient_session

    mock_patient = MagicMock()
    mock_patient.access_state = "archived"

    mock_db = AsyncMock()
    mock_db.get = AsyncMock(return_value=mock_patient)

    result = await assemble_daily_patient_session(mock_db, 999)
    assert result is False


@pytest.mark.asyncio
async def test_session_assembler_returns_false_for_missing_patient():
    """`assemble_daily_patient_session` returns False when patient not found."""
    from app.services.care_circle.session_assembler import assemble_daily_patient_session

    mock_db = AsyncMock()
    mock_db.get = AsyncMock(return_value=None)

    result = await assemble_daily_patient_session(mock_db, 999)
    assert result is False


@pytest.mark.asyncio
async def test_session_assembler_handles_empty_catalog():
    """`assemble_daily_patient_session` gracefully handles empty provider catalog."""
    from app.services.care_circle.session_assembler import assemble_daily_patient_session

    mock_patient = MagicMock()
    mock_patient.id = 1
    mock_patient.access_state = "active"
    mock_patient.preferences = {}

    mock_db = AsyncMock()
    mock_db.get = AsyncMock(return_value=mock_patient)

    # Simulate a catalog query returning no providers
    mock_scalars = MagicMock()
    mock_scalars.all = MagicMock(return_value=[])
    mock_result = MagicMock()
    mock_result.scalars = MagicMock(return_value=mock_scalars)
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.flush = AsyncMock()
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()

    result = await assemble_daily_patient_session(mock_db, 1)
    # With no active providers, returns False
    assert result is False


def test_get_provider_class_returns_none_for_unknown_provider():
    """`get_provider_class` returns None for non-existent provider key."""
    from app.services.care_circle.session_assembler import get_provider_class

    result = get_provider_class("nonexistent_provider_xyz")
    assert result is None


def test_get_provider_class_returns_provider_for_known_weather():
    """`get_provider_class` returns a class for the weather provider."""
    from app.services.care_circle.session_assembler import get_provider_class

    result = get_provider_class("weather")
    assert result is not None


# ---------------------------------------------------------------------------
# CRUD async function tests (using pytest.mark.asyncio)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crud_update_provider_catalog_respects_flags():
    """`update_provider_catalog` correctly sets enabled and patient_visible."""
    from app.crud import care_circle as care_circle_crud

    mock_db = AsyncMock()
    mock_provider = MagicMock()
    mock_provider.provider_key = "weather"
    mock_provider.enabled = True
    mock_provider.patient_visible = True
    mock_db.scalar = AsyncMock(return_value=mock_provider)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    await care_circle_crud.update_provider_catalog(mock_db, "weather", False, False)

    assert mock_provider.enabled is False
    assert mock_provider.patient_visible is False


@pytest.mark.asyncio
async def test_crud_update_provider_catalog_returns_none_for_missing():
    """`update_provider_catalog` returns None when provider not found."""
    from app.crud import care_circle as care_circle_crud

    mock_db = AsyncMock()
    mock_db.scalar = AsyncMock(return_value=None)

    result = await care_circle_crud.update_provider_catalog(mock_db, "unknown", True, True)
    assert result is None


@pytest.mark.asyncio
async def test_crud_list_provider_catalog_orders_by_display_order():
    """`list_provider_catalog` returns providers ordered by display_order."""
    from app.crud import care_circle as care_circle_crud

    mock_provider_1 = MagicMock()
    mock_provider_1.provider_key = "weather"
    mock_provider_1.label = "Weather"
    mock_provider_1.icon = "sun"
    mock_provider_1.category = "core"
    mock_provider_1.enabled = True
    mock_provider_1.display_order = 1
    mock_provider_1.patient_visible = True
    mock_provider_1.family_visible = True

    mock_provider_2 = MagicMock()
    mock_provider_2.provider_key = "joke"
    mock_provider_2.label = "Daily Joy"
    mock_provider_2.icon = "smile"
    mock_provider_2.category = "wellbeing"
    mock_provider_2.enabled = True
    mock_provider_2.display_order = 2
    mock_provider_2.patient_visible = True
    mock_provider_2.family_visible = True

    mock_scalars = MagicMock()
    mock_scalars.all = MagicMock(return_value=[mock_provider_1, mock_provider_2])
    mock_result = MagicMock()
    mock_result.scalars = MagicMock(return_value=mock_scalars)

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)
    mock_db.scalar = AsyncMock(return_value=0)  # Catalog not seeded
    mock_db.add = Mock()
    mock_db.commit = AsyncMock()

    result = await care_circle_crud.list_provider_catalog(mock_db)

    assert len(result) == 2
    assert result[0]["providerKey"] == "weather"
    assert result[1]["providerKey"] == "joke"


@pytest.mark.asyncio
async def test_crud_patient_provider_configs_upsert_creates_new():
    """`upsert_patient_provider_config` creates a new config record."""
    from app.crud import care_circle as care_circle_crud

    mock_db = AsyncMock()
    mock_db.scalar = AsyncMock(return_value=None)  # No existing config
    mock_db.add = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    await care_circle_crud.upsert_patient_provider_config(
        mock_db, patient_id=1, provider_key="weather", is_enabled=False, custom_parameters={"key": "value"}
    )

    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_crud_patient_provider_configs_upsert_updates_existing():
    """`upsert_patient_provider_config` updates existing config record."""
    from app.crud import care_circle as care_circle_crud

    existing_config = MagicMock()
    existing_config.id = 1
    existing_config.patient_id = 1
    existing_config.provider_key = "weather"
    existing_config.is_enabled = True
    existing_config.custom_parameters = {}

    mock_db = AsyncMock()
    mock_db.scalar = AsyncMock(return_value=existing_config)
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    await care_circle_crud.upsert_patient_provider_config(
        mock_db, patient_id=1, provider_key="weather", is_enabled=False
    )

    assert existing_config.is_enabled is False
    mock_db.commit.assert_called_once()


@pytest.mark.asyncio
async def test_crud_patient_provider_configs_list():
    """`get_patient_provider_configs` returns all configs for a patient."""
    from app.crud import care_circle as care_circle_crud

    mock_config_1 = MagicMock()
    mock_config_1.id = 1
    mock_config_1.patient_id = 1
    mock_config_1.provider_key = "weather"
    mock_config_1.is_enabled = True
    mock_config_1.custom_parameters = {}

    mock_config_2 = MagicMock()
    mock_config_2.id = 2
    mock_config_2.patient_id = 1
    mock_config_2.provider_key = "joke"
    mock_config_2.is_enabled = False
    mock_config_2.custom_parameters = {"theme": "blue"}

    mock_scalars = MagicMock()
    mock_scalars.all = MagicMock(return_value=[mock_config_1, mock_config_2])
    mock_result = MagicMock()
    mock_result.scalars = MagicMock(return_value=mock_scalars)

    mock_db = AsyncMock()
    mock_db.execute = AsyncMock(return_value=mock_result)

    configs = await care_circle_crud.get_patient_provider_configs(mock_db, patient_id=1)

    assert len(configs) == 2
    assert configs[0]["provider_key"] == "weather"
    assert configs[0]["is_enabled"] is True
    assert configs[1]["provider_key"] == "joke"
    assert configs[1]["is_enabled"] is False
    assert configs[1]["custom_parameters"] == {"theme": "blue"}
