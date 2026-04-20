"""
Weather provider adapted for Care Circle patient sessions.
Fetches real weather from wttr.in and generates a warm message.
"""

from __future__ import annotations

import logging
import time
import urllib.parse
from typing import Any

import httpx

from app.services.care_circle.provider_base import BaseCareCircleProvider

logger = logging.getLogger(__name__)


class WeatherProvider(BaseCareCircleProvider):
    provider_key = "weather"
    is_safe_for_patient = True

    _weather_cache: dict[str, tuple[float, dict[str, Any]]] = {}
    CACHE_TTL_SECONDS = 900

    @classmethod
    def _load_cached_weather(cls, location_key: str) -> dict[str, Any] | None:
        cached = cls._weather_cache.get(location_key.lower())
        if not cached:
            return None
        expires_at, payload = cached
        if time.time() >= expires_at:
            cls._weather_cache.pop(location_key.lower(), None)
            return None
        return dict(payload)

    @classmethod
    def _save_cached_weather(cls, location_key: str, payload: dict[str, Any]) -> None:
        cls._weather_cache[location_key.lower()] = (
            time.time() + cls.CACHE_TTL_SECONDS,
            dict(payload),
        )

    @staticmethod
    def _build_weather_payload(
        *,
        city: str,
        recipient_name: str,
        temperature: str,
        condition: str,
    ) -> dict[str, Any]:
        weather_summary = f"{temperature}\u00b0F and {condition}"
        return {
            "text": f"Good morning, {recipient_name}! It is {weather_summary} in {city} today.",
            "subheading": f"{city} Weather",
            "type": "weather",
            "city": city,
            "temperature": temperature,
            "condition": condition,
            "weather": weather_summary,
        }

    async def _generate_payload(self, patient_profile: Any) -> dict[str, Any]:
        prefs = self.get_patient_preferences(patient_profile)
        city = str(
            prefs.get("city_for_weather")
            or self.patient_config.get("default_city")
            or "Unknown"
        ).strip()
        latitude = getattr(patient_profile, "latitude", None)
        longitude = getattr(patient_profile, "longitude", None)
        query_target = city
        cache_key = city
        if latitude is not None and longitude is not None:
            query_target = f"{latitude},{longitude}"
            cache_key = query_target
        recipient_name = self.get_recipient_name(patient_profile)
        fallback_msg = self.patient_config.get("fallback", "Weather currently unavailable.")

        if (not city or city == "Unknown") and (latitude is None or longitude is None):
            return {
                "text": "Weather unavailable. Please set a city in the Family portal.",
                "subheading": "Update Profile",
                "type": "weather",
                "city": "Unknown",
            }

        cached_payload = self._load_cached_weather(cache_key)
        if cached_payload is not None:
            cached_payload["text"] = (
                f"Good morning, {recipient_name}! It is "
                f"{cached_payload['temperature']}\u00b0F and {cached_payload['condition']} in {city} today."
            )
            return cached_payload

        try:
            location_encoded = urllib.parse.quote(query_target)
            url = f"https://wttr.in/{location_encoded}?format=j1"

            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url, headers={"Accept": "application/json"})
                resp.raise_for_status()
                data = resp.json()

            current = data.get("current_condition", [{}])[0]
            temp_f = str(current.get("temp_F", "")).strip()
            desc = str(current.get("weatherDesc", [{}])[0].get("value", "")).strip()

            if not temp_f or not desc:
                raise ValueError("Weather response missing temperature or condition")

            payload = self._build_weather_payload(
                city=city,
                recipient_name=recipient_name,
                temperature=temp_f,
                condition=desc,
            )
            self._save_cached_weather(cache_key, payload)
            return payload

        except Exception as exc:
            logger.warning("Weather fetch failed for location %s: %s", query_target, exc)
            return {
                "text": fallback_msg,
                "subheading": "Weather",
                "type": "weather",
                "city": city,
            }
