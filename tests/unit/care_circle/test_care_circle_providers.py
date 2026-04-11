import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import types

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


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_llm_response(content="Generated content here"):
    resp = MagicMock()
    resp.content = content
    return resp


def _inject_llm(module, response_content="Generated LLM content.", raises=False):
    """
    Inject generate_text_with_usage / generate_json_with_usage and
    DEMENTIA_SYSTEM_PROMPT into *module* so the LLM path can be exercised.
    Also patches log_llm_response onto the provider base class temporarily.
    Returns the AsyncMock so callers can inspect calls if needed.
    """
    from app.services.care_circle.provider_base import BaseCareCircleProvider

    if raises:
        async_mock = AsyncMock(side_effect=Exception("LLM unavailable"))
    else:
        llm_resp = _make_llm_response(response_content)
        async_mock = AsyncMock(return_value=llm_resp)

    json_resp = MagicMock()
    json_resp.content = '{"name":"Test","ingredients":"a,b","steps":"1. Do it."}'
    json_async = AsyncMock(return_value=({"name": "Test", "ingredients": "a,b", "steps": "1. Do it."}, json_resp))

    module.generate_text_with_usage = async_mock
    module.generate_json_with_usage = json_async
    module.DEMENTIA_SYSTEM_PROMPT = "You are a caring assistant."

    # Patch log_llm_response on the base class (it's called as self.log_llm_response)
    if not hasattr(BaseCareCircleProvider, "log_llm_response"):
        BaseCareCircleProvider.log_llm_response = MagicMock()

    return async_mock


# ---------------------------------------------------------------------------
# pen_pal_letter
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_pen_pal_letter_fallback_path():
    """LLM raises -> fallback letter from config."""
    from app.services.care_circle.providers.pen_pal_letter import provider as mod
    from app.services.care_circle.providers.pen_pal_letter.provider import PenPalLetterProvider

    # Ensure no LLM names injected so NameError triggers fallback
    mod.__dict__.pop("generate_text_with_usage", None)

    provider = PenPalLetterProvider()
    patient = MockPatientProfile(
        id=1,
        display_name="Rose",
        preferences={"recipient_name": "Rose", "preferences": {"era_of_youth": "1950s"}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert "letter" in result["data"]
    assert "friend_name" in result["data"]


@pytest.mark.asyncio
async def test_pen_pal_letter_llm_success_path():
    """LLM returns valid content -> letter comes from LLM."""
    from app.services.care_circle.providers.pen_pal_letter import provider as mod
    from app.services.care_circle.providers.pen_pal_letter.provider import PenPalLetterProvider

    _inject_llm(mod, response_content="Dear Rose,\n\nWhat a lovely autumn day! " + "x" * 80)
    try:
        provider = PenPalLetterProvider()
        patient = MockPatientProfile(
            id=1,
            display_name="Rose",
            preferences={"recipient_name": "Rose", "preferences": {
                "era_of_youth": "1950s",
                "favorite_activities": ["gardening", "knitting"],
                "hometown": "Springfield",
                "life_roles": ["mother"],
                "pets": ["Biscuit"],
                "favourite_foods": ["apple pie"],
                "favourite_tv_shows": ["I Love Lucy"],
            }}
        )
        result = await provider.execute(patient)
        assert result["success"] is True
        assert "letter" in result["data"]
    finally:
        mod.__dict__.pop("generate_text_with_usage", None)
        mod.__dict__.pop("generate_json_with_usage", None)
        mod.__dict__.pop("DEMENTIA_SYSTEM_PROMPT", None)


@pytest.mark.asyncio
async def test_pen_pal_letter_llm_short_response_uses_fallback():
    """LLM returns content that is too short -> falls back to config/default letter."""
    from app.services.care_circle.providers.pen_pal_letter import provider as mod
    from app.services.care_circle.providers.pen_pal_letter.provider import PenPalLetterProvider

    _inject_llm(mod, response_content="Hi")  # too short
    try:
        provider = PenPalLetterProvider(patient_config={
            "fallback_letters": ["Dear {name}, Thinking of you! With love, {friend}"]
        })
        patient = MockPatientProfile(
            id=1,
            display_name="Rose",
            preferences={"recipient_name": "Rose", "preferences": {}}
        )
        result = await provider.execute(patient)
        assert result["success"] is True
        assert "letter" in result["data"]
        # Should use fallback_letters from patient_config
        assert "Thinking of you" in result["data"]["letter"]
    finally:
        mod.__dict__.pop("generate_text_with_usage", None)
        mod.__dict__.pop("generate_json_with_usage", None)
        mod.__dict__.pop("DEMENTIA_SYSTEM_PROMPT", None)


@pytest.mark.asyncio
async def test_pen_pal_letter_no_fallback_letters():
    """No fallback_letters and LLM fails -> hardcoded default letter."""
    from app.services.care_circle.providers.pen_pal_letter import provider as mod
    from app.services.care_circle.providers.pen_pal_letter.provider import PenPalLetterProvider

    mod.__dict__.pop("generate_text_with_usage", None)

    provider = PenPalLetterProvider(patient_config={"fallback_letters": [], "friend_names": ["Betty"]})
    patient = MockPatientProfile(
        id=1,
        display_name="Dorothy",
        preferences={"recipient_name": "Dorothy", "preferences": {}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert "Dear Dorothy" in result["data"]["letter"]
    assert result["data"]["friend_name"] == "Betty"


# ---------------------------------------------------------------------------
# world_news
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_world_news_rss_fetch_failure_returns_fallback():
    """HTTP request fails -> returns fallback_stories."""
    from app.services.care_circle.providers.world_news.provider import WorldNewsProvider
    import httpx

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)
        mock_client.get = AsyncMock(side_effect=httpx.RequestError("timeout", request=MagicMock()))

        provider = WorldNewsProvider(patient_config={
            "fallback_stories": [{"title": "Good news", "summary": "All is well."}]
        })
        patient = MockPatientProfile(id=1, display_name="Test", preferences={})
        result = await provider.execute(patient)

    assert result["success"] is True
    assert result["data"]["stories"] == [{"title": "Good news", "summary": "All is well."}]


@pytest.mark.asyncio
async def test_world_news_rss_parse_failure_returns_fallback():
    """HTTP OK but malformed XML -> returns fallback_stories."""
    from app.services.care_circle.providers.world_news.provider import WorldNewsProvider

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.text = "<not valid xml <<<"

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        provider = WorldNewsProvider(patient_config={
            "fallback_stories": [{"title": "Fallback", "summary": "Nothing today."}]
        })
        patient = MockPatientProfile(id=1, display_name="Test", preferences={})
        result = await provider.execute(patient)

    assert result["success"] is True
    assert result["data"]["stories"][0]["title"] == "Fallback"


@pytest.mark.asyncio
async def test_world_news_rss_with_items_llm_fallback_simplify():
    """RSS returns items, LLM simplify fails -> uses truncated description."""
    from app.services.care_circle.providers.world_news import provider as mod
    from app.services.care_circle.providers.world_news.provider import WorldNewsProvider

    rss_xml = """<?xml version="1.0"?>
<rss><channel>
<item><title>Big Event Happens</title><description>Something important happened today in the world.</description></item>
</channel></rss>"""

    mod.__dict__.pop("generate_text_with_usage", None)  # ensure LLM path fails

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.text = rss_xml

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        provider = WorldNewsProvider(patient_config={"item_count": 1})
        patient = MockPatientProfile(id=1, display_name="Test", preferences={})
        result = await provider.execute(patient)

    assert result["success"] is True
    stories = result["data"]["stories"]
    assert len(stories) == 1
    assert stories[0]["title"] == "Big Event Happens"
    assert "Something" in stories[0]["summary"]


@pytest.mark.asyncio
async def test_world_news_rss_with_items_llm_success():
    """RSS returns items, LLM simplify succeeds."""
    from app.services.care_circle.providers.world_news import provider as mod
    from app.services.care_circle.providers.world_news.provider import WorldNewsProvider

    rss_xml = """<?xml version="1.0"?>
<rss><channel>
<item><title>Leaders Meet</title><description>World leaders met to discuss climate change.</description></item>
</channel></rss>"""

    _inject_llm(mod, response_content="Leaders meet to discuss the climate.")
    try:
        with patch("httpx.AsyncClient") as mock_client_cls:
            mock_resp = MagicMock()
            mock_resp.raise_for_status = MagicMock()
            mock_resp.text = rss_xml

            mock_client = AsyncMock()
            mock_client.get = AsyncMock(return_value=mock_resp)
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            provider = WorldNewsProvider(patient_config={"item_count": 1})
            patient = MockPatientProfile(id=1, display_name="Test", preferences={})
            result = await provider.execute(patient)
    finally:
        mod.__dict__.pop("generate_text_with_usage", None)
        mod.__dict__.pop("generate_json_with_usage", None)
        mod.__dict__.pop("DEMENTIA_SYSTEM_PROMPT", None)

    assert result["success"] is True
    stories = result["data"]["stories"]
    assert len(stories) == 1
    assert stories[0]["title"] == "Leaders Meet"
    assert "climate" in stories[0]["summary"]


@pytest.mark.asyncio
async def test_world_news_simplify_truncation_long_description():
    """_simplify truncates a long description when LLM fails."""
    from app.services.care_circle.providers.world_news import provider as mod
    from app.services.care_circle.providers.world_news.provider import WorldNewsProvider

    mod.__dict__.pop("generate_text_with_usage", None)

    provider = WorldNewsProvider()
    long_desc = " ".join(f"word{i}" for i in range(30))
    result = await provider._simplify("Test Title", long_desc)

    assert result.endswith("…")
    assert len(result.split()) <= 21  # 20 words + ellipsis


# ---------------------------------------------------------------------------
# family_greeting
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_family_greeting_no_family_members_returns_fallback():
    """No family members -> returns fallback message."""
    from app.services.care_circle.providers.family_greeting.provider import FamilyGreetingProvider

    provider = FamilyGreetingProvider()
    patient = MockPatientProfile(
        id=1,
        display_name="Rose",
        preferences={"recipient_name": "Rose", "preferences": {}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert result["data"]["sender"] == "Your family"
    assert "Rose" in result["data"]["message"] or "loved" in result["data"]["message"]


@pytest.mark.asyncio
async def test_family_greeting_llm_success():
    """Family members present, LLM succeeds -> uses LLM content."""
    from app.services.care_circle.providers.family_greeting import provider as mod
    from app.services.care_circle.providers.family_greeting.provider import FamilyGreetingProvider

    _inject_llm(mod, response_content="Hi Mum! We love you so much and miss you every day.")
    try:
        provider = FamilyGreetingProvider()
        patient = MockPatientProfile(
            id=1,
            display_name="Rose",
            preferences={"recipient_name": "Rose", "preferences": {
                "family_members": ["Alice", "Bob"],
                "life_roles": ["mother"],
                "pets": ["Fluffball"],
                "favourite_foods": ["scones"],
                "hometown": "Leeds",
            }}
        )
        result = await provider.execute(patient)
        assert result["success"] is True
        assert result["data"]["sender"] in ["Alice", "Bob"]
        assert len(result["data"]["message"]) > 10
    finally:
        mod.__dict__.pop("generate_text_with_usage", None)
        mod.__dict__.pop("generate_json_with_usage", None)
        mod.__dict__.pop("DEMENTIA_SYSTEM_PROMPT", None)


@pytest.mark.asyncio
async def test_family_greeting_llm_failure_uses_fallback():
    """Family members present, LLM fails -> uses fallback_text."""
    from app.services.care_circle.providers.family_greeting import provider as mod
    from app.services.care_circle.providers.family_greeting.provider import FamilyGreetingProvider

    mod.__dict__.pop("generate_text_with_usage", None)

    provider = FamilyGreetingProvider(patient_config={"fallback_text": "We are thinking of you!"})
    patient = MockPatientProfile(
        id=1,
        display_name="Rose",
        preferences={"recipient_name": "Rose", "preferences": {"family_members": ["Alice"]}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert result["data"]["message"] == "We are thinking of you!"
    assert result["data"]["sender"] == "Alice"


# ---------------------------------------------------------------------------
# simple_recipe
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_simple_recipe_llm_failure_returns_fallback():
    """LLM fails -> returns a recipe from config."""
    from app.services.care_circle.providers.simple_recipe import provider as mod
    from app.services.care_circle.providers.simple_recipe.provider import SimpleRecipeProvider

    mod.__dict__.pop("generate_json_with_usage", None)

    provider = SimpleRecipeProvider()
    patient = MockPatientProfile(
        id=1, display_name="Test",
        preferences={"preferences": {"era_of_youth": "1950s"}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert "name" in result["data"]
    assert "steps" in result["data"]


@pytest.mark.asyncio
async def test_simple_recipe_llm_success():
    """LLM succeeds -> returns generated recipe."""
    from app.services.care_circle.providers.simple_recipe import provider as mod
    from app.services.care_circle.providers.simple_recipe.provider import SimpleRecipeProvider
    from app.services.care_circle.provider_base import BaseCareCircleProvider

    json_resp = MagicMock()
    mock_json_async = AsyncMock(return_value=(
        {"name": "Fairy Cakes", "ingredients": "flour, sugar, butter", "steps": "Mix, bake, enjoy!"},
        json_resp
    ))
    mod.generate_json_with_usage = mock_json_async
    mod.DEMENTIA_SYSTEM_PROMPT = "You are a caring assistant."
    if not hasattr(BaseCareCircleProvider, "log_llm_response"):
        BaseCareCircleProvider.log_llm_response = MagicMock()
    try:
        provider = SimpleRecipeProvider()
        patient = MockPatientProfile(
            id=1, display_name="Test",
            preferences={"preferences": {"era_of_youth": "1950s"}}
        )
        result = await provider.execute(patient)
        assert result["success"] is True
        assert result["data"]["name"] == "Fairy Cakes"
    finally:
        mod.__dict__.pop("generate_json_with_usage", None)
        mod.__dict__.pop("DEMENTIA_SYSTEM_PROMPT", None)


@pytest.mark.asyncio
async def test_simple_recipe_llm_returns_incomplete_data():
    """LLM returns dict missing 'name' -> uses fallback recipe."""
    from app.services.care_circle.providers.simple_recipe import provider as mod
    from app.services.care_circle.providers.simple_recipe.provider import SimpleRecipeProvider
    from app.services.care_circle.provider_base import BaseCareCircleProvider

    json_resp = MagicMock()
    mod.generate_json_with_usage = AsyncMock(return_value=({"ingredients": "just flour"}, json_resp))
    mod.DEMENTIA_SYSTEM_PROMPT = "You are a caring assistant."
    if not hasattr(BaseCareCircleProvider, "log_llm_response"):
        BaseCareCircleProvider.log_llm_response = MagicMock()
    try:
        provider = SimpleRecipeProvider(patient_config={
            "recipes": [{"name": "Hot Cocoa", "ingredients": "Milk", "steps": "Warm milk."}]
        })
        patient = MockPatientProfile(
            id=1, display_name="Test",
            preferences={"preferences": {}}
        )
        result = await provider.execute(patient)
        assert result["success"] is True
        assert result["data"]["name"] == "Hot Cocoa"
    finally:
        mod.__dict__.pop("generate_json_with_usage", None)
        mod.__dict__.pop("DEMENTIA_SYSTEM_PROMPT", None)


# ---------------------------------------------------------------------------
# local_history
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_local_history_no_location_returns_fallback():
    """No hometown or city -> returns generic fallback."""
    from app.services.care_circle.providers.local_history.provider import LocalHistoryProvider

    provider = LocalHistoryProvider()
    patient = MockPatientProfile(
        id=1, display_name="Test",
        preferences={"preferences": {}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert result["data"]["location"] == "your town"
    assert "history" in result["data"]["fact"].lower() or "wonderful" in result["data"]["fact"].lower()


@pytest.mark.asyncio
async def test_local_history_llm_success():
    """Hometown present, LLM succeeds -> returns LLM fact."""
    from app.services.care_circle.providers.local_history import provider as mod
    from app.services.care_circle.providers.local_history.provider import LocalHistoryProvider

    _inject_llm(mod, response_content="Springfield was famous for its annual flower show, " +
                "drawing visitors from all over the county.")
    try:
        provider = LocalHistoryProvider()
        patient = MockPatientProfile(
            id=1, display_name="Test",
            preferences={"preferences": {
                "hometown": "Springfield",
                "era_of_youth": "1960s",
                "nationality_or_background": "Irish",
                "life_roles": ["teacher"],
            }}
        )
        result = await provider.execute(patient)
        assert result["success"] is True
        assert result["data"]["location"] == "Springfield"
        assert len(result["data"]["fact"]) > 10
    finally:
        mod.__dict__.pop("generate_text_with_usage", None)
        mod.__dict__.pop("generate_json_with_usage", None)
        mod.__dict__.pop("DEMENTIA_SYSTEM_PROMPT", None)


@pytest.mark.asyncio
async def test_local_history_llm_failure_uses_fallback():
    """Hometown present, LLM fails -> returns fallback fact."""
    from app.services.care_circle.providers.local_history import provider as mod
    from app.services.care_circle.providers.local_history.provider import LocalHistoryProvider

    mod.__dict__.pop("generate_text_with_usage", None)

    provider = LocalHistoryProvider(patient_config={"fallback_text": "A lovely place with rich history."})
    patient = MockPatientProfile(
        id=1, display_name="Test",
        preferences={"preferences": {"hometown": "Bristol"}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert result["data"]["location"] == "Bristol"
    assert result["data"]["fact"] == "A lovely place with rich history."


@pytest.mark.asyncio
async def test_local_history_uses_city_when_no_hometown():
    """No hometown but city_for_weather present -> uses city."""
    from app.services.care_circle.providers.local_history import provider as mod
    from app.services.care_circle.providers.local_history.provider import LocalHistoryProvider

    mod.__dict__.pop("generate_text_with_usage", None)

    provider = LocalHistoryProvider()
    patient = MockPatientProfile(
        id=1, display_name="Test",
        preferences={"preferences": {"city_for_weather": "Manchester"}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert result["data"]["location"] == "Manchester"


# ---------------------------------------------------------------------------
# weather (additional coverage)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_weather_provider_with_city_success():
    """City provided, HTTP call succeeds -> returns temperature and condition."""
    from app.services.care_circle.providers.weather.provider import WeatherProvider

    mock_weather_data = {
        "current_condition": [{"temp_F": "72", "weatherDesc": [{"value": "Sunny"}]}]
    }

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json = MagicMock(return_value=mock_weather_data)

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_resp)
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        provider = WeatherProvider()
        patient = MockPatientProfile(
            id=1, display_name="Alice",
            preferences={"city_for_weather": "Denver"}
        )
        result = await provider.execute(patient)

    assert result["success"] is True
    assert result["data"]["temperature"] == "72"
    assert result["data"]["condition"] == "Sunny"
    assert "Denver" in result["data"]["text"]
    assert "Alice" in result["data"]["text"]


@pytest.mark.asyncio
async def test_weather_provider_http_failure_uses_fallback():
    """HTTP call fails -> returns fallback message."""
    from app.services.care_circle.providers.weather.provider import WeatherProvider
    import httpx

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=httpx.RequestError("timeout", request=MagicMock()))
        mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        provider = WeatherProvider(patient_config={"fallback": "Sorry, weather unavailable right now."})
        patient = MockPatientProfile(
            id=1, display_name="Alice",
            preferences={"city_for_weather": "Boston"}
        )
        result = await provider.execute(patient)

    assert result["success"] is True
    assert result["data"]["text"] == "Sorry, weather unavailable right now."
    assert result["data"]["city"] == "Boston"


# ---------------------------------------------------------------------------
# word_scramble
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_word_scramble_basic():
    """Default word pool -> returns puzzle with required keys."""
    from app.services.care_circle.providers.word_scramble.provider import WordScrambleProvider

    provider = WordScrambleProvider()
    patient = MockPatientProfile(id=1, display_name="Test", preferences={"preferences": {}})
    result = await provider.execute(patient)
    assert result["success"] is True
    data = result["data"]
    assert "puzzle" in data
    assert "answer" in data
    assert data["type"] == "word_scramble"


@pytest.mark.asyncio
async def test_word_scramble_with_family_names():
    """Family names in 3-6 char range added to pool."""
    from app.services.care_circle.providers.word_scramble.provider import WordScrambleProvider

    provider = WordScrambleProvider(patient_config={"words": ["APPLE"]})
    patient = MockPatientProfile(
        id=1, display_name="Test",
        preferences={"preferences": {"family_members": ["Ann", "Bob", "Elizabeth"]}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    # Answer should be one of APPLE, ANN, BOB (Elizabeth is too long)
    assert result["data"]["answer"] in ["APPLE", "ANN", "BOB"]


@pytest.mark.asyncio
async def test_word_scramble_three_letter_word():
    """3-letter words scramble all letters."""
    from app.services.care_circle.providers.word_scramble.provider import WordScrambleProvider

    import random
    with patch.object(random, "choice", return_value="DAM"):
        provider = WordScrambleProvider(patient_config={"words": ["DAM"]})
        patient = MockPatientProfile(id=1, display_name="Test", preferences={"preferences": {}})
        result = await provider.execute(patient)

    assert result["success"] is True
    data = result["data"]
    assert data["answer"] == "DAM"
    assert data["hint"] is None  # 3-letter words have no hint


@pytest.mark.asyncio
async def test_word_scramble_longer_word_has_hint():
    """Words > 3 letters have a hint with first letter."""
    from app.services.care_circle.providers.word_scramble.provider import WordScrambleProvider

    import random
    with patch.object(random, "choice", return_value="MAPLE"):
        provider = WordScrambleProvider(patient_config={"words": ["MAPLE"]})
        patient = MockPatientProfile(id=1, display_name="Test", preferences={"preferences": {}})
        result = await provider.execute(patient)

    assert result["success"] is True
    data = result["data"]
    assert data["answer"] == "MAPLE"
    assert "M" in data["hint"]


# ---------------------------------------------------------------------------
# spot_the_difference
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_spot_the_difference_llm_failure_uses_fallback():
    """LLM fails -> uses fallback_sets from config."""
    from app.services.care_circle.providers.spot_the_difference import provider as mod
    from app.services.care_circle.providers.spot_the_difference.provider import SpotTheDifferenceProvider

    mod.__dict__.pop("generate_json_with_usage", None)

    provider = SpotTheDifferenceProvider()
    patient = MockPatientProfile(id=1, display_name="Test", preferences={})
    result = await provider.execute(patient)
    assert result["success"] is True
    data = result["data"]
    assert "list_a" in data
    assert "list_b" in data
    assert len(data["list_a"]) == 5
    assert len(data["list_b"]) == 5
    assert data["title"] == "Spot the Difference"


@pytest.mark.asyncio
async def test_spot_the_difference_llm_success():
    """LLM returns valid 5-item lists -> uses LLM result."""
    from app.services.care_circle.providers.spot_the_difference import provider as mod
    from app.services.care_circle.providers.spot_the_difference.provider import SpotTheDifferenceProvider

    llm_data = {
        "list_a": ["Cat", "Dog", "Fish", "Bird", "Frog"],
        "list_b": ["Cat", "Dog", "Fish", "Bird", "Toad"],
        "changed_in_a": "Frog",
        "changed_in_b": "Toad",
    }
    json_resp = MagicMock()
    mod.generate_json_with_usage = AsyncMock(return_value=(llm_data, json_resp))
    mod.DEMENTIA_SYSTEM_PROMPT = "You are a caring assistant."
    from app.services.care_circle.provider_base import BaseCareCircleProvider
    if not hasattr(BaseCareCircleProvider, "log_llm_response"):
        BaseCareCircleProvider.log_llm_response = MagicMock()
    try:
        provider = SpotTheDifferenceProvider()
        patient = MockPatientProfile(id=1, display_name="Test", preferences={})
        result = await provider.execute(patient)
        assert result["success"] is True
        assert result["data"]["changed_in_a"] == "Frog"
        assert result["data"]["changed_in_b"] == "Toad"
        assert result["data"]["list_a"] == ["Cat", "Dog", "Fish", "Bird", "Frog"]
    finally:
        mod.__dict__.pop("generate_json_with_usage", None)
        mod.__dict__.pop("DEMENTIA_SYSTEM_PROMPT", None)


@pytest.mark.asyncio
async def test_spot_the_difference_llm_returns_invalid_data():
    """LLM returns incomplete data -> falls back to config sets."""
    from app.services.care_circle.providers.spot_the_difference import provider as mod
    from app.services.care_circle.providers.spot_the_difference.provider import SpotTheDifferenceProvider

    # Missing changed_in_a/b
    llm_data = {
        "list_a": ["Cat", "Dog"],
        "list_b": ["Cat", "Dog"],
        "changed_in_a": "",
        "changed_in_b": "",
    }
    json_resp = MagicMock()
    mod.generate_json_with_usage = AsyncMock(return_value=(llm_data, json_resp))
    mod.DEMENTIA_SYSTEM_PROMPT = "You are a caring assistant."
    from app.services.care_circle.provider_base import BaseCareCircleProvider
    if not hasattr(BaseCareCircleProvider, "log_llm_response"):
        BaseCareCircleProvider.log_llm_response = MagicMock()
    try:
        provider = SpotTheDifferenceProvider()
        patient = MockPatientProfile(id=1, display_name="Test", preferences={})
        result = await provider.execute(patient)
        assert result["success"] is True
        # Should fall back to config
        assert len(result["data"]["list_a"]) == 5
    finally:
        mod.__dict__.pop("generate_json_with_usage", None)
        mod.__dict__.pop("DEMENTIA_SYSTEM_PROMPT", None)


# ---------------------------------------------------------------------------
# personal_affirmation
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_personal_affirmation_llm_failure_returns_fallback():
    """LLM fails -> returns fallback affirmation."""
    from app.services.care_circle.providers.personal_affirmation import provider as mod
    from app.services.care_circle.providers.personal_affirmation.provider import PersonalAffirmationProvider

    mod.__dict__.pop("generate_text_with_usage", None)

    provider = PersonalAffirmationProvider()
    patient = MockPatientProfile(
        id=1, display_name="Alice",
        preferences={"recipient_name": "Alice", "preferences": {}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert "name" in result["data"]
    assert "affirmation" in result["data"]
    assert "Alice" in result["data"]["affirmation"] or result["data"]["name"] == "Alice"


@pytest.mark.asyncio
async def test_personal_affirmation_llm_success():
    """LLM returns content -> uses LLM affirmation."""
    from app.services.care_circle.providers.personal_affirmation import provider as mod
    from app.services.care_circle.providers.personal_affirmation.provider import PersonalAffirmationProvider

    _inject_llm(mod, response_content="Alice, your love of painting brings joy to everyone. You are a wonderful mother.")
    try:
        provider = PersonalAffirmationProvider()
        patient = MockPatientProfile(
            id=1, display_name="Alice",
            preferences={"recipient_name": "Alice", "preferences": {
                "favorite_activities": ["painting", "reading"],
                "life_roles": ["mother"],
                "pets": ["Whiskers"],
                "preferred_pronoun": "she/her",
            }}
        )
        result = await provider.execute(patient)
        assert result["success"] is True
        assert result["data"]["name"] == "Alice"
        assert len(result["data"]["affirmation"]) > 10
    finally:
        mod.__dict__.pop("generate_text_with_usage", None)
        mod.__dict__.pop("generate_json_with_usage", None)
        mod.__dict__.pop("DEMENTIA_SYSTEM_PROMPT", None)


@pytest.mark.asyncio
async def test_personal_affirmation_custom_fallback():
    """Custom fallback_text in config is used when LLM fails."""
    from app.services.care_circle.providers.personal_affirmation import provider as mod
    from app.services.care_circle.providers.personal_affirmation.provider import PersonalAffirmationProvider

    mod.__dict__.pop("generate_text_with_usage", None)

    provider = PersonalAffirmationProvider(patient_config={"fallback_text": "You are truly wonderful!"})
    patient = MockPatientProfile(
        id=1, display_name="Betty",
        preferences={"recipient_name": "Betty", "preferences": {}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert result["data"]["affirmation"] == "You are truly wonderful!"


# ---------------------------------------------------------------------------
# nostalgia
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_nostalgia_llm_failure_returns_fallback():
    """LLM fails -> returns fallback nostalgia from config."""
    from app.services.care_circle.providers.nostalgia import provider as mod
    from app.services.care_circle.providers.nostalgia.provider import NostalgiaProvider

    mod.__dict__.pop("generate_text_with_usage", None)

    provider = NostalgiaProvider()
    patient = MockPatientProfile(
        id=1, display_name="Rose",
        preferences={"recipient_name": "Rose", "preferences": {"era_of_youth": "1950s"}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert "nostalgia" in result["data"]
    assert len(result["data"]["nostalgia"]) > 5


@pytest.mark.asyncio
async def test_nostalgia_llm_success():
    """LLM returns content -> uses LLM nostalgia text."""
    from app.services.care_circle.providers.nostalgia import provider as mod
    from app.services.care_circle.providers.nostalgia.provider import NostalgiaProvider

    _inject_llm(mod, response_content="Remember the smell of fresh bread from the corner bakery on Saturday mornings.")
    try:
        provider = NostalgiaProvider()
        patient = MockPatientProfile(
            id=1, display_name="Rose",
            preferences={"recipient_name": "Rose", "preferences": {
                "era_of_youth": "1960s",
                "nationality_or_background": "British",
                "hometown": "Leeds",
                "life_roles": ["nurse", "mother"],
                "favourite_foods": ["fish and chips", "scones"],
                "favourite_tv_shows": ["Coronation Street"],
            }}
        )
        result = await provider.execute(patient)
        assert result["success"] is True
        assert "nostalgia" in result["data"]
        assert len(result["data"]["nostalgia"]) > 10
    finally:
        mod.__dict__.pop("generate_text_with_usage", None)
        mod.__dict__.pop("generate_json_with_usage", None)
        mod.__dict__.pop("DEMENTIA_SYSTEM_PROMPT", None)


@pytest.mark.asyncio
async def test_nostalgia_era_facts_fallback():
    """Uses era-specific facts from config when LLM not available."""
    from app.services.care_circle.providers.nostalgia import provider as mod
    from app.services.care_circle.providers.nostalgia.provider import NostalgiaProvider

    mod.__dict__.pop("generate_text_with_usage", None)

    provider = NostalgiaProvider(patient_config={
        "default_era": "1940s",
        "facts": {"1940s": ["Victory gardens were very popular in the 1940s."]},
        "fallback": "Those were wonderful times."
    })
    patient = MockPatientProfile(
        id=1, display_name="Vera",
        preferences={"recipient_name": "Vera", "preferences": {"era_of_youth": "1940s"}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert result["data"]["nostalgia"] == "Victory gardens were very popular in the 1940s."


@pytest.mark.asyncio
async def test_nostalgia_era_facts_string_not_list():
    """Era facts value is a string, not a list -> returned directly."""
    from app.services.care_circle.providers.nostalgia import provider as mod
    from app.services.care_circle.providers.nostalgia.provider import NostalgiaProvider

    mod.__dict__.pop("generate_text_with_usage", None)

    provider = NostalgiaProvider(patient_config={
        "default_era": "1930s",
        "facts": {"1930s": "Big band music filled dance halls everywhere."},
        "fallback": "Those were wonderful times."
    })
    patient = MockPatientProfile(
        id=1, display_name="Vera",
        preferences={"recipient_name": "Vera", "preferences": {"era_of_youth": "1930s"}}
    )
    result = await provider.execute(patient)
    assert result["success"] is True
    assert result["data"]["nostalgia"] == "Big band music filled dance halls everywhere."
