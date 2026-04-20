"""
Classic Art provider — Metropolitan Museum of Art Open Access API.

Fetches a random public-domain painting or artwork from the Met's collection,
including the image, title, artist, date, and medium.
All artworks returned are confirmed CC0 (no rights reserved).
"""

import logging
import random
from typing import Any, Dict

import httpx

from app.services.care_circle.provider_base import BaseCareCircleProvider, WIKIMEDIA_USER_AGENT

logger = logging.getLogger(__name__)

# Base URL for the Met's public API
_MET_SEARCH_URL = "https://collectionapi.metmuseum.org/public/collection/v1/search"
_MET_OBJECT_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"

# Curated search terms that reliably return beautiful, patient-friendly artworks
_SEARCH_TERMS = [
    "landscape",
    "flowers",
    "portrait",
    "still life",
    "garden",
    "countryside",
    "sunset",
    "seascape",
    "spring",
    "village",
    "pastoral",
    "harvest",
    "orchard",
    "meadow",
    "river",
]

# Fallback artworks — Wikimedia Commons public-domain images.
# All URLs are verified thumbnail links that resolve reliably.
# Used when the Met API is unavailable or returns an object without an image.
_FALLBACK_ARTWORKS = [
    {
        "title": "The Starry Night",
        "artist": "Vincent van Gogh",
        "date": "1889",
        "medium": "Oil on canvas",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ea/Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg/800px-Van_Gogh_-_Starry_Night_-_Google_Art_Project.jpg",
        "met_url": "https://www.moma.org/collection/works/79802",
        "description": "A swirling night sky blazes over a quiet village — one of the most beloved paintings in the world.",
    },
    {
        "title": "The Milkmaid",
        "artist": "Johannes Vermeer",
        "date": "ca. 1658",
        "medium": "Oil on canvas",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Johannes_Vermeer_-_Het_melkmeisje_-_Google_Art_Project.jpg/800px-Johannes_Vermeer_-_Het_melkmeisje_-_Google_Art_Project.jpg",
        "met_url": "https://www.rijksmuseum.nl/en/collection/SK-A-2344",
        "description": "Warm golden light fills a kitchen as a young woman carefully pours milk — a perfect moment of everyday peace.",
    },
    {
        "title": "The Death of Socrates",
        "artist": "Jacques-Louis David",
        "date": "1787",
        "medium": "Oil on canvas",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/David_-_The_Death_of_Socrates.jpg/800px-David_-_The_Death_of_Socrates.jpg",
        "met_url": "https://www.metmuseum.org/art/collection/search/436105",
        "description": "A scene of calm courage — the philosopher Socrates surrounded by mourning friends as he faces his final moments.",
    },
    {
        "title": "Washington Crossing the Delaware",
        "artist": "Emanuel Leutze",
        "date": "1851",
        "medium": "Oil on canvas",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/95/Washington_Crossing_the_Delaware_by_Emanuel_Leutze%2C_MMA-NYC%2C_1851.jpg/800px-Washington_Crossing_the_Delaware_by_Emanuel_Leutze%2C_MMA-NYC%2C_1851.jpg",
        "met_url": "https://www.metmuseum.org/art/collection/search/11417",
        "description": "George Washington leads his troops across an icy river on Christmas night, 1776 — a defining moment of the American Revolution.",
    },
    {
        "title": "The Harvesters",
        "artist": "Pieter Bruegel the Elder",
        "date": "1565",
        "medium": "Oil on wood",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b3/Pieter_Bruegel_the_Elder-_The_Harvesters_-_Metropolitan_Museum_of_Art.jpg/800px-Pieter_Bruegel_the_Elder-_The_Harvesters_-_Metropolitan_Museum_of_Art.jpg",
        "met_url": "https://www.metmuseum.org/art/collection/search/435809",
        "description": "Farmers rest under a pear tree while others cut golden wheat under a warm late-summer sun.",
    },
    {
        "title": "Luncheon of the Boating Party",
        "artist": "Pierre-Auguste Renoir",
        "date": "1880–81",
        "medium": "Oil on canvas",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Pierre-Auguste_Renoir_-_Luncheon_of_the_Boating_Party.jpg/800px-Pierre-Auguste_Renoir_-_Luncheon_of_the_Boating_Party.jpg",
        "met_url": "https://www.phillipscollection.org/collection/luncheon-of-the-boating-party",
        "description": "Friends laugh and talk over a sunny riverside lunch — a joyful celebration of good company.",
    },
    {
        "title": "Water Lilies",
        "artist": "Claude Monet",
        "date": "1906",
        "medium": "Oil on canvas",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Claude_Monet_-_Water_Lilies_-_1906%2C_Ryerson.jpg/800px-Claude_Monet_-_Water_Lilies_-_1906%2C_Ryerson.jpg",
        "met_url": "https://www.artic.edu/artworks/16568",
        "description": "Soft reflections of sky and floating lily pads shimmer on the surface of Monet's beloved garden pond.",
    },
]


class ClassicArtProvider(BaseCareCircleProvider):
    provider_key = "classic_art"
    is_safe_for_patient = True

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        """
        Fetch a random public-domain artwork from the Metropolitan Museum of Art.

        Strategy:
        1. Pick a random search term from the curated list.
        2. Query the Met search API for public-domain artworks with images.
        3. Pick a random object ID from the first 200 results.
        4. Fetch the full object record for title, artist, date, medium, and image.

        Falls back to a pre-defined list of classic artworks if the API is unavailable.
        """
        cfg = self.patient_config
        search_terms = cfg.get("search_terms", _SEARCH_TERMS)
        fallback_artworks = cfg.get("fallback_artworks", _FALLBACK_ARTWORKS)

        term = random.choice(search_terms)

        try:
            async with httpx.AsyncClient(
                timeout=10.0,
                follow_redirects=True,
                headers={
                    "User-Agent": WIKIMEDIA_USER_AGENT,
                    "Accept": "application/json",
                },
            ) as client:
                # Step 1 — search for public-domain artworks with images
                search_resp = await client.get(
                    _MET_SEARCH_URL,
                    params={
                        "q": term,
                        "isPublicDomain": "true",
                        "hasImages": "true",
                    },
                )
                search_resp.raise_for_status()
                search_data = search_resp.json()

                object_ids: list[int] = search_data.get("objectIDs") or []
                if not object_ids:
                    raise ValueError("No results from Met search API")

                # Pick from the first 200 to keep variety without huge lists
                candidate_ids = object_ids[:200]
                random.shuffle(candidate_ids)

                # Try up to 5 candidates — some objects have empty image fields
                # despite the hasImages=true filter, so we skip those.
                obj = None
                image_url = ""
                for object_id in candidate_ids[:5]:
                    obj_resp = await client.get(_MET_OBJECT_URL.format(object_id=object_id))
                    obj_resp.raise_for_status()
                    candidate = obj_resp.json()
                    url = candidate.get("primaryImageSmall") or candidate.get("primaryImage", "")
                    if url:
                        obj = candidate
                        image_url = url
                        break

                if not obj or not image_url:
                    raise ValueError("No objects with valid image URLs found in sample")

                title: str = obj.get("title") or "Untitled"
                artist: str = obj.get("artistDisplayName") or "Unknown Artist"
                date: str = obj.get("objectDate") or ""
                medium: str = obj.get("medium") or ""
                met_url: str = obj.get("objectURL") or ""
                classification: str = obj.get("classification") or ""
                culture: str = obj.get("culture") or ""

                # Build a short description from available metadata
                description = _build_description(title, artist, date, medium, classification, culture)

                return {
                    "title": title,
                    "artist": artist,
                    "date": date,
                    "medium": medium,
                    "image_url": image_url,
                    "met_url": met_url,
                    "description": description,
                    "search_term": term,
                }

        except Exception as exc:
            logger.warning("ClassicArtProvider API failed (%s) — using fallback artwork.", exc)

        artwork = random.choice(fallback_artworks)
        return {**artwork, "search_term": term}


def _build_description(
    title: str,
    artist: str,
    date: str,
    medium: str,
    classification: str,
    culture: str,
) -> str:
    """Compose a warm, readable one-liner from the object's metadata fields."""
    parts: list[str] = []

    if artist and artist != "Unknown Artist":
        parts.append(f"Painted by {artist}")
        if date:
            parts.append(f"in {date}")
        parts.append("—")

    if medium:
        parts.append(medium + ".")
    elif classification:
        parts.append(classification + ".")

    if culture:
        parts.append(f"From the {culture} tradition.")

    if not parts:
        return f'"{title}" — a treasured work from the Metropolitan Museum of Art collection.'

    return " ".join(parts)
