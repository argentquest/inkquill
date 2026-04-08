import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock

from app.services.care_circle.providers.daily_quote.provider import DailyQuoteProvider
from app.services.care_circle.providers.weather.provider import WeatherProvider


class MockPatientProfile:
    def __init__(self, id, display_name, preferences):
        self.id = id
        self.display_name = display_name
        self.preferences = preferences


@pytest.mark.asyncio
async def test_daily_quote_provider_fallback():
    # Provide bad url so it triggers a fallback
    provider = DailyQuoteProvider(patient_config={
        "api_url": "http://invalid-url.local/api",
        "fallback_quote": "A safe fallback quote.",
        "fallback_author": "Testing"
    })

    patient = MockPatientProfile(id=1, display_name="Test", preferences={})
    result = await provider.execute(patient)

    # Notice this is True, because our sub-class caught the URL failure elegantly
    assert result["success"] is True
    assert result["provider_key"] == "daily_quote"
    # Fallback should be triggered because the URL is guaranteed to fail
    assert "A safe fallback quote" in result["data"]["text"]


@pytest.mark.asyncio
async def test_weather_provider_no_city():
    # Test with no city in preferences
    provider = WeatherProvider()
    patient = MockPatientProfile(id=1, display_name="Test", preferences={"city_for_weather": None})

    result = await provider.execute(patient)
    assert result["success"] is True
    assert result["data"]["city"] == "Unknown"
    assert "unavailable" in result["data"]["text"]


@pytest.mark.asyncio
async def test_session_assembler_filtering_and_fallback():
    from app.services.care_circle.session_assembler import assemble_daily_patient_session

    # Mock DB - patient not found, should return False
    mock_db = AsyncMock()
    mock_db.get = AsyncMock(return_value=None)

    result = await assemble_daily_patient_session(mock_db, 1)
    # The assembler gracefully handles missing patient and returns False
    assert result is False
