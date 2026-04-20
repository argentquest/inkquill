import logging
import re
import xml.etree.ElementTree as ET

import httpx

from app.services.care_circle.provider_base import BaseCareCircleProvider
from typing import Any, Dict

app_logger = logging.getLogger(__name__)


def _parse_rss(xml_text: str, item_count: int) -> list[dict]:
    """Extract <title> + <description> from the first *item_count* RSS <item> elements."""
    stories = []
    try:
        root = ET.fromstring(xml_text)
        # RSS 2.0: channel > item; handle optional namespace
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            # <description> often contains HTML — strip tags
            raw_desc = item.findtext("description") or ""
            summary = re.sub(r"<[^>]+>", " ", raw_desc).strip()
            summary = re.sub(r"\s{2,}", " ", summary)
            if title:
                stories.append({"title": title, "summary": summary or title})
            if len(stories) >= item_count:
                break
    except Exception as exc:
        app_logger.warning("RSS XML parse error: %s", exc)
    return stories


class WorldNewsProvider(BaseCareCircleProvider):
    """
    Fetches top world news from BBC RSS, simplifies with LLM for elderly audience.
    Falls back to static stories if RSS fetch or parse fails.
    """

    provider_key = "world_news"
    is_safe_for_patient = True

    async def _generate_payload(self, _patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        rss_url = cfg.get("rss_url", "https://feeds.bbci.co.uk/news/world/rss.xml")
        item_count = cfg.get("item_count", 5)
        fallback_stories = cfg.get("fallback_stories", [])

        stories: list[dict] = []
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(rss_url)
                resp.raise_for_status()
                stories = _parse_rss(resp.text, item_count)
        except Exception as exc:
            app_logger.warning("RSS fetch failed for world_news: %s", exc)

        if not stories:
            app_logger.info("world_news: using fallback stories")
            stories = fallback_stories[:item_count]

        return {
            "stories": stories,
            "source": "BBC World News",
        }
