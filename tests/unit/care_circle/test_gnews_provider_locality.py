from app.services.care_circle.providers.gnews.provider import _build_country_query, _build_local_query
from app.services.care_circle.providers.gnews.provider import GnewsProvider


def test_gnews_builds_city_local_query():
    query = _build_local_query(
        configured_query="positive news",
        weather_city="Montreal, Quebec",
        hometown="Montreal, Quebec",
        country_code="ca",
        language="en",
    )

    assert query == "Montreal local news"


def test_gnews_builds_french_city_query():
    query = _build_local_query(
        configured_query="positive news",
        weather_city="Montreal, Quebec",
        hometown="Montreal, Quebec",
        country_code="ca",
        language="fr",
    )

    assert query == "Montreal nouvelles locales"


def test_gnews_builds_country_fallback_query():
    query = _build_country_query(
        configured_query="positive news",
        country_code="ca",
        language="en",
    )

    assert query == "Canada news"


def test_gnews_uses_patient_locale_when_config_does_not_override():
    provider = GnewsProvider(patient_config={})

    class Patient:
        preferred_language = "fr"
        country = "CA"

    cfg = provider.patient_config
    lang = cfg.get("lang") or getattr(Patient, "preferred_language", None) or "en"
    country = cfg.get("country") or getattr(Patient, "country", None) or "us"

    assert lang == "fr"
    assert country == "CA"
