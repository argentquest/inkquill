"""
World News Summary Provider.

Fetches the top 3 headlines from a public RSS feed and uses the LLM to
produce a short, plain-language summary (≤ 20 words) for each story.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import httpx

import logging
app_logger = logging.getLogger(__name__)
from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.services.care_circle.llm_helpers import (
    DEMENTIA_SYSTEM_PROMPT,
    generate_image_url_with_usage,
    generate_json_with_usage,
    generate_text_with_usage,
)
from typing import Any, Dict



class WorldNewsProvider(BaseCareCircleProvider):
    is_safe_for_patient = True

    """3 top world-news headlines with brief, easy-to-read summaries."""

    async def _generate_payload(self, patient_profile: Any) -> Dict[str, Any]:
        cfg = self.patient_config
        feed_url = cfg.get(
            "rss_url", "https://feeds.bbci.co.uk/news/world/rss.xml"
        )
        count = cfg.get("item_count", 3)
        fallback_stories = cfg.get("fallback_stories", [])

        raw_items = await self._fetch_rss(feed_url, count)
        if not raw_items:
            return {"stories": fallback_stories}

        stories = []
        for item in raw_items:
            title = item["title"]
            raw_summary = item["description"] or title
            short_summary = await self._simplify(title, raw_summary)
            stories.append({"title": title, "summary": short_summary})

        return {"stories": stories}

    async def _fetch_rss(self, url: str, count: int) -> list[dict]:
        """Fetch and parse the RSS feed, returning up to *count* items."""
        headers = {"User-Agent": "DailyNewsletter/1.0"}
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(
                    url, headers=headers, follow_redirects=True
                )
                resp.raise_for_status()
        except Exception as exc:
            app_logger.warning(
                f"WorldNewsProvider: RSS fetch failed: {exc}"
            )
            return []

        try:
            root = ET.fromstring(resp.text)
        except ET.ParseError as exc:
            app_logger.warning(
                f"WorldNewsProvider: RSS parse failed: {exc}"
            )
            return []

        items = []
        for elem in root.iter("item"):
            title = (elem.findtext("title") or "").strip()
            description = (elem.findtext("description") or "").strip()
            if title:
                items.append({"title": title, "description": description})
            if len(items) >= count:
                break

        return items

    async def _simplify(self, title: str, description: str) -> str:
        """Use the LLM to produce a ≤ 20-word plain-language summary."""
        prompt = (
            f"News headline: {title}\n"
            f"Details: {description}\n\n"
            "Write ONE sentence of 20 words or fewer. Rules:\n"
            "- One idea only — do not combine multiple facts.\n"
            "- Short, common words — no jargon or complex vocabulary.\n"
            "- Present tense (e.g. 'Leaders meet' not 'Leaders met').\n"
            "- Plain English only — as if explaining to a 10-year-old.\n"
            "Output the sentence only, no preamble."
        )
        try:
            response = await generate_text_with_usage(
                prompt, system=DEMENTIA_SYSTEM_PROMPT
            )
            self.log_llm_response(
                response,
                prompt=prompt,
                system_prompt=DEMENTIA_SYSTEM_PROMPT,
            )
            if response.content:
                return response.content.strip()
        except Exception as exc:
            app_logger.warning(
                f"WorldNewsProvider: LLM simplify failed: {exc}"
            )

        # Fallback: truncate raw description to ~20 words
        words = description.split()
        return " ".join(words[:20]) + ("…" if len(words) > 20 else "")
