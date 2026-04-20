from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

import httpx

LOCATION_USER_AGENT = (
    "InkAndQuill-CareCircle/1.0 "
    "(https://inkandquill.com; contact@inkandquill.com)"
)

logger = logging.getLogger(__name__)


@dataclass
class ResolvedPostalLocation:
    postal_code: str
    country_code: str
    latitude: float
    longitude: float
    locality: str | None = None
    region: str | None = None
    formatted_city: str | None = None


def _clean_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _extract_locality(address: dict[str, Any]) -> str | None:
    for key in ("city", "town", "village", "municipality", "hamlet", "county"):
        value = _clean_str(address.get(key))
        if value:
            return value
    return None


def _extract_region(address: dict[str, Any]) -> str | None:
    for key in ("state", "province", "region", "state_district"):
        value = _clean_str(address.get(key))
        if value:
            return value
    return None


def _format_city(locality: str | None, region: str | None) -> str | None:
    if locality and region:
        return f"{locality}, {region}"
    return locality or region


async def resolve_postal_location(
    *,
    postal_code: str,
    country_code: str,
    timeout_seconds: float = 10.0,
) -> ResolvedPostalLocation | None:
    normalized_postal_code = _clean_str(postal_code)
    normalized_country = (_clean_str(country_code) or "").lower()
    if not normalized_postal_code or not normalized_country:
        return None

    params = {
        "q": f"{normalized_postal_code}, {normalized_country.upper()}",
        "countrycodes": normalized_country,
        "format": "jsonv2",
        "addressdetails": 1,
        "limit": 1,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params=params,
                headers={
                    "Accept": "application/json",
                    "User-Agent": LOCATION_USER_AGENT,
                },
            )
            response.raise_for_status()
            results = response.json()
    except Exception as exc:
        logger.warning(
            "Postal geocode lookup failed for %s/%s: %s",
            normalized_postal_code,
            normalized_country,
            exc,
        )
        return None

    if not isinstance(results, list) or not results:
        return None

    first = results[0] if isinstance(results[0], dict) else {}
    address = first.get("address", {}) if isinstance(first.get("address", {}), dict) else {}

    try:
        latitude = float(first["lat"])
        longitude = float(first["lon"])
    except (KeyError, TypeError, ValueError):
        return None

    locality = _extract_locality(address)
    region = _extract_region(address)

    return ResolvedPostalLocation(
        postal_code=normalized_postal_code,
        country_code=normalized_country.upper(),
        latitude=latitude,
        longitude=longitude,
        locality=locality,
        region=region,
        formatted_city=_format_city(locality, region),
    )
