"""
Base provider interface for Care Circle.

This restores the DailyNewsletter-style template and theme rendering contract
while keeping the execution wrapper safe for the React CareCircle frontend.
"""

from __future__ import annotations

import datetime
import inspect
import json
import logging
import traceback
from pathlib import Path
from typing import Any, Optional

import re

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

# Maps provider_key → provenance kind.  Used to auto-inject a badge above the
# section__title without touching individual templates.
_PROVIDER_PROVENANCE: dict[str, str] = {
    # ── AI-generated ──────────────────────────────────────────────────────────
    "weather": "auto", "joke": "auto", "nostalgia": "auto",
    "puzzle": "auto", "brain_booster": "auto", "sensory": "auto",
    "ai_trivia": "auto", "daily_quote": "auto", "dog_photo": "auto",
    "cat_fact": "auto", "gratitude": "auto", "gentle_exercise": "auto",
    "daily_affirmation": "auto", "nature_scene": "auto",
    "simple_recipe": "auto", "this_day_history": "auto", "riddle": "auto",
    "missing_vowels": "auto", "finish_phrase": "auto", "odd_one_out": "auto",
    "word_scramble": "auto", "song_of_the_day": "auto",
    "complete_the_duo": "auto", "spot_the_difference": "auto",
    "pen_pal_letter": "auto", "gridless_crossword": "auto",
    "hobby_spotlight": "auto", "local_history": "auto",
    "personal_affirmation": "auto", "activity_suggestion": "auto",
    "animal_friend": "auto", "bingo": "auto", "color_match": "auto",
    "simple_math": "auto", "word_connect": "auto",
    "morning_stretch": "auto", "word_of_the_day": "auto",
    "country_spotlight": "auto", "number_sequence": "auto",
    "mindful_moment": "auto", "old_saying_match": "auto",
    "famous_face": "auto",
    # ── Curated / sourced ─────────────────────────────────────────────────────
    "world_news": "curated", "hymn_of_the_day": "curated",
    "daily_blessing": "curated", "seasonal_poem": "curated",
    "classic_art": "curated", "wikimedia_gallery": "curated",
    "nature_park": "curated",
    "comic_abe_martin": "curated", "comic_brownies": "curated",
    "comic_dino_cartoons": "curated", "comic_mr_skygack": "curated",
    "comic_wuffle": "curated", "comic_buster_brown": "curated",
    "comic_gasoline_alley": "curated", "comic_little_nemo": "curated",
    "comic_dream_rarebit_fiend": "curated",
    "comic_polly_and_her_pals": "curated", "comic_pepper_carrot": "curated",
    "comic_happy_hooligan": "curated", "comic_moose_lake": "curated",
    # ── From the family ───────────────────────────────────────────────────────
    "family_greeting": "family", "letter_to_family": "family",
    "memory_lane_photo": "family",
}

_PROV_BADGE: dict[str, str] = {
    "auto":    '<span class="prov-pill prov-pill--auto">AI Generated</span>',
    "curated": '<span class="prov-pill prov-pill--curated">Curated</span>',
    "family":  '<span class="prov-pill prov-pill--family">From Your Family</span>',
}

_SECTION_TITLE_RE = re.compile(
    r'(<[^>]+class="[^"]*\bsection__title\b[^"]*"[^>]*>)',
    re.IGNORECASE,
)

# Strips any leading emoji / pictograph characters from inside the section title.
# Unicode ranges covered: Emoticons, Misc Symbols, Dingbats, Supplemental Symbols,
# enclosed alphanumerics, transport/map symbols, and the common emoji modifier range.
_SECTION_TITLE_EMOJI_RE = re.compile(
    r'(class="[^"]*\bsection__title\b[^"]*"[^>]*>)'
    r'([\U0001F000-\U0001FFFF☀-➿⌀-⏿⭐️⃣][️⃣]?'
    r'[\s‍]*)+',
    re.IGNORECASE,
)

def _svg(body: str, color: str, size: int = 32) -> str:
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 56 56" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" '
        f'style="display:inline-block;vertical-align:middle;margin-right:8px">'
        f'{body}</svg>'
    )

_PROVIDER_SVG_ICONS: dict[str, str] = {
    # ── Comics ───────────────────────────────────────────────────────────────
    **{k: _svg(
        '<rect x="6" y="6" width="44" height="32" rx="6" fill="#6366f1" opacity="0.15" stroke="#6366f1" stroke-width="2.5"/>'
        '<line x1="6" y1="22" x2="50" y2="22" stroke="#6366f1" stroke-width="1.5" opacity="0.4"/>'
        '<line x1="28" y1="6" x2="28" y2="38" stroke="#6366f1" stroke-width="1.5" opacity="0.4"/>'
        '<path d="M14 44l6-6h10" stroke="#8b5cf6" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="16" cy="16" r="3" fill="#8b5cf6" opacity="0.6"/>',
        "#6366f1",
    ) for k in (
        "comic_abe_martin", "comic_ascii", "comic_brownies", "comic_buster_brown",
        "comic_dino_cartoons", "comic_dream_rarebit_fiend", "comic_gasoline_alley",
        "comic_happy_hooligan", "comic_little_nemo", "comic_moose_lake",
        "comic_mr_skygack", "comic_pepper_carrot", "comic_polly_and_her_pals",
        "comic_wuffle",
    )},

    # ── Animals ──────────────────────────────────────────────────────────────
    **{k: _svg(
        '<circle cx="28" cy="30" r="14" fill="#0d9488" opacity="0.12" stroke="#0d9488" stroke-width="2.5"/>'
        '<circle cx="20" cy="18" r="5" fill="#0d9488" opacity="0.25" stroke="#0d9488" stroke-width="2"/>'
        '<circle cx="36" cy="18" r="5" fill="#0d9488" opacity="0.25" stroke="#0d9488" stroke-width="2"/>'
        '<circle cx="22" cy="32" r="3" fill="#0d9488"/>'
        '<circle cx="34" cy="32" r="3" fill="#0d9488"/>'
        '<circle cx="28" cy="36" r="2.5" fill="#f97316"/>',
        "#0d9488",
    ) for k in ("animal_friend", "cat_fact", "dog_photo")},

    # ── Nature / weather ─────────────────────────────────────────────────────
    **{k: _svg(
        '<circle cx="28" cy="24" r="16" fill="#059669" opacity="0.12" stroke="#059669" stroke-width="2.5"/>'
        '<path d="M28 44V28" stroke="#059669" stroke-width="2.5" stroke-linecap="round"/>'
        '<path d="M28 34c-6 0-10-4-10-10 6 0 10 4 10 10z" fill="#10b981" opacity="0.3" stroke="#059669" stroke-width="2"/>'
        '<path d="M28 30c6 0 10-4 10-10-6 0-10 4-10 10z" fill="#10b981" opacity="0.3" stroke="#059669" stroke-width="2"/>',
        "#059669",
    ) for k in ("nature_park", "nature_scene", "seasonal_poem")},

    "weather": _svg(
        '<circle cx="24" cy="22" r="10" fill="#f59e0b" opacity="0.18" stroke="#f59e0b" stroke-width="2.5"/>'
        '<path d="M24 10v-4M24 38v-4M10 24H6M42 24h-4M14.1 13.1l-2.8-2.8M36.7 35.7l-2.8-2.8" stroke="#f59e0b" stroke-width="2" stroke-linecap="round"/>'
        '<circle cx="34" cy="34" r="10" fill="#60a5fa" opacity="0.2" stroke="#3b82f6" stroke-width="2.5"/>',
        "#f59e0b",
    ),

    # ── Bingo ────────────────────────────────────────────────────────────────
    "bingo": _svg(
        '<rect x="8" y="8" width="40" height="40" rx="5" fill="#e11d48" opacity="0.08" stroke="#e11d48" stroke-width="2.5"/>'
        '<line x1="8" y1="21" x2="48" y2="21" stroke="#e11d48" stroke-width="1.5" opacity="0.35"/>'
        '<line x1="8" y1="34" x2="48" y2="34" stroke="#e11d48" stroke-width="1.5" opacity="0.35"/>'
        '<line x1="21" y1="8" x2="21" y2="48" stroke="#e11d48" stroke-width="1.5" opacity="0.35"/>'
        '<line x1="34" y1="8" x2="34" y2="48" stroke="#e11d48" stroke-width="1.5" opacity="0.35"/>'
        '<circle cx="28" cy="28" r="4.5" fill="#e11d48"/>',
        "#e11d48",
    ),

    "color_match": _svg(
        '<circle cx="20" cy="22" r="12" fill="#f43f5e" opacity="0.25"/>'
        '<circle cx="36" cy="22" r="12" fill="#2563eb" opacity="0.25"/>'
        '<circle cx="28" cy="36" r="12" fill="#f59e0b" opacity="0.25"/>',
        "#9333ea",
    ),

    "spot_the_difference": _svg(
        '<rect x="4" y="12" width="22" height="32" rx="4" fill="#6366f1" opacity="0.1" stroke="#6366f1" stroke-width="2.5"/>'
        '<rect x="30" y="12" width="22" height="32" rx="4" fill="#6366f1" opacity="0.1" stroke="#6366f1" stroke-width="2.5"/>'
        '<circle cx="15" cy="28" r="5" fill="#6366f1" opacity="0.3" stroke="#6366f1" stroke-width="2"/>'
        '<circle cx="41" cy="28" r="5" fill="#f43f5e" opacity="0.45" stroke="#f43f5e" stroke-width="2.5"/>',
        "#6366f1",
    ),

    # ── Puzzles / grids ───────────────────────────────────────────────────────
    **{k: _svg(
        '<rect x="8" y="8" width="16" height="16" rx="3" fill="#f59e0b" opacity="0.2" stroke="#f59e0b" stroke-width="2.5"/>'
        '<rect x="32" y="8" width="16" height="16" rx="3" fill="#d86c3d" opacity="0.18" stroke="#d86c3d" stroke-width="2.5"/>'
        '<rect x="8" y="32" width="16" height="16" rx="3" fill="#d86c3d" opacity="0.18" stroke="#d86c3d" stroke-width="2.5"/>'
        '<rect x="32" y="32" width="16" height="16" rx="3" fill="#f59e0b" opacity="0.2" stroke="#f59e0b" stroke-width="2.5"/>',
        "#f59e0b",
    ) for k in ("gridless_crossword", "number_sequence", "odd_one_out", "puzzle")},

    # ── Word games ────────────────────────────────────────────────────────────
    **{k: _svg(
        '<rect x="6" y="12" width="44" height="32" rx="6" fill="#0891b2" opacity="0.1" stroke="#0891b2" stroke-width="2.5"/>'
        '<line x1="14" y1="24" x2="42" y2="24" stroke="#0891b2" stroke-width="2.5" stroke-linecap="round"/>'
        '<line x1="14" y1="32" x2="36" y2="32" stroke="#0891b2" stroke-width="2" stroke-linecap="round" opacity="0.6"/>'
        '<line x1="14" y1="38" x2="28" y2="38" stroke="#0891b2" stroke-width="2" stroke-linecap="round" opacity="0.4"/>',
        "#0891b2",
    ) for k in ("complete_the_duo", "finish_phrase", "missing_vowels", "old_saying_match",
                "word_connect", "word_of_the_day", "word_scramble")},

    # ── Brain / trivia ────────────────────────────────────────────────────────
    **{k: _svg(
        '<path d="M28 8c-8.8 0-16 7.2-16 16 0 5.5 2.8 10.4 7 13.3V44h18v-6.7c4.2-2.9 7-7.8 7-13.3 0-8.8-7.2-16-16-16z" '
        'fill="#7c3aed" opacity="0.1" stroke="#7c3aed" stroke-width="2.5" stroke-linejoin="round"/>'
        '<path d="M22 24c0-3.3 2.7-6 6-6" stroke="#7c3aed" stroke-width="2" stroke-linecap="round" opacity="0.6"/>'
        '<circle cx="28" cy="22" r="2.5" fill="#f59e0b"/>'
        '<path d="M20 44h16" stroke="#7c3aed" stroke-width="2.5" stroke-linecap="round"/>',
        "#7c3aed",
    ) for k in ("ai_trivia", "brain_booster", "riddle", "simple_math")},

    # ── Wellness / mindfulness ────────────────────────────────────────────────
    **{k: _svg(
        '<circle cx="28" cy="28" r="20" fill="#f43f5e" opacity="0.08" stroke="#f43f5e" stroke-width="2.5"/>'
        '<path d="M28 38s-12-7-12-16a8 8 0 0 1 12-6.9A8 8 0 0 1 40 22c0 9-12 16-12 16z" '
        'fill="#f43f5e" opacity="0.2" stroke="#f43f5e" stroke-width="2.5" stroke-linejoin="round"/>',
        "#f43f5e",
    ) for k in ("daily_affirmation", "daily_blessing", "mindful_moment",
                "personal_affirmation", "sensory")},

    # ── Activity / exercise ───────────────────────────────────────────────────
    **{k: _svg(
        '<circle cx="28" cy="14" r="6" fill="#0891b2" opacity="0.25" stroke="#0891b2" stroke-width="2.5"/>'
        '<path d="M28 20v16" stroke="#0891b2" stroke-width="2.5" stroke-linecap="round"/>'
        '<path d="M16 28h24" stroke="#0891b2" stroke-width="2.5" stroke-linecap="round"/>'
        '<path d="M20 36l8 10 8-10" stroke="#0891b2" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>',
        "#0891b2",
    ) for k in ("activity_suggestion", "gentle_exercise", "hobby_spotlight", "morning_stretch")},

    # ── Quote / gratitude ─────────────────────────────────────────────────────
    "daily_quote": _svg(
        '<rect x="6" y="10" width="44" height="36" rx="6" fill="#1f3b36" opacity="0.08" stroke="#1f3b36" stroke-width="2.5"/>'
        '<path d="M16 28c0-4 2.5-7 6-8v4c-1.5.5-2.5 2-2.5 4v4H16v-4z" fill="#1f3b36" opacity="0.4"/>'
        '<path d="M28 28c0-4 2.5-7 6-8v4c-1.5.5-2.5 2-2.5 4v4H28v-4z" fill="#1f3b36" opacity="0.4"/>',
        "#1f3b36",
    ),

    "gratitude": _svg(
        '<path d="M28 46s-18-10-18-24a10 10 0 0 1 18-6 10 10 0 0 1 18 6c0 14-18 24-18 24z" '
        'fill="#10b981" opacity="0.15" stroke="#10b981" stroke-width="2.5" stroke-linejoin="round"/>'
        '<path d="M20 26l4 4 8-8" stroke="#10b981" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>',
        "#10b981",
    ),

    # ── Music ─────────────────────────────────────────────────────────────────
    **{k: _svg(
        '<rect x="6" y="10" width="44" height="36" rx="6" fill="#7c3aed" opacity="0.1" stroke="#7c3aed" stroke-width="2.5"/>'
        '<path d="M22 38V20l20-4v18" stroke="#7c3aed" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="18" cy="38" r="4" fill="#7c3aed" opacity="0.4" stroke="#7c3aed" stroke-width="2"/>'
        '<circle cx="38" cy="34" r="4" fill="#7c3aed" opacity="0.4" stroke="#7c3aed" stroke-width="2"/>',
        "#7c3aed",
    ) for k in ("hymn_of_the_day", "song_of_the_day")},

    # ── Art / classic ─────────────────────────────────────────────────────────
    **{k: _svg(
        '<rect x="8" y="8" width="40" height="34" rx="5" fill="#d97706" opacity="0.1" stroke="#d97706" stroke-width="2.5"/>'
        '<path d="M14 30l10-10 8 8 6-6 8 8" stroke="#d86c3d" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="20" cy="20" r="3" fill="#f59e0b"/>',
        "#d97706",
    ) for k in ("classic_art", "famous_face", "wikimedia_gallery")},

    # ── Family / letters ──────────────────────────────────────────────────────
    **{k: _svg(
        '<rect x="6" y="14" width="44" height="32" rx="5" fill="#d86c3d" opacity="0.12" stroke="#d86c3d" stroke-width="2.5"/>'
        '<path d="M6 19l22 14 22-14" stroke="#d86c3d" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="28" cy="10" r="5" fill="#1f3b36" opacity="0.2" stroke="#1f3b36" stroke-width="2"/>',
        "#d86c3d",
    ) for k in ("family_greeting", "letter_to_family", "pen_pal_letter")},

    # ── Recipe ────────────────────────────────────────────────────────────────
    "simple_recipe": _svg(
        '<path d="M10 22c0-8.8 7.2-16 18-16s18 7.2 18 16H10z" fill="#059669" opacity="0.15" stroke="#059669" stroke-width="2.5" stroke-linejoin="round"/>'
        '<rect x="10" y="22" width="36" height="22" rx="4" fill="#059669" opacity="0.1" stroke="#059669" stroke-width="2.5"/>'
        '<path d="M18 32h8M30 32h8" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/>',
        "#059669",
    ),

    # ── History / nostalgia ───────────────────────────────────────────────────
    **{k: _svg(
        '<circle cx="28" cy="28" r="20" fill="#92400e" opacity="0.08" stroke="#92400e" stroke-width="2.5"/>'
        '<circle cx="28" cy="28" r="14" fill="#92400e" opacity="0.06" stroke="#d97706" stroke-width="2"/>'
        '<path d="M28 16v12l8 4" stroke="#d97706" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>'
        '<circle cx="28" cy="28" r="2" fill="#d97706"/>',
        "#d97706",
    ) for k in ("country_spotlight", "local_history", "nostalgia", "this_day_history")},

    "memory_lane_photo": _svg(
        '<rect x="6" y="12" width="44" height="34" rx="5" fill="#92400e" opacity="0.1" stroke="#92400e" stroke-width="2.5"/>'
        '<circle cx="28" cy="28" r="9" fill="#92400e" opacity="0.15" stroke="#d97706" stroke-width="2.5"/>'
        '<circle cx="28" cy="28" r="4" fill="#d97706"/>'
        '<path d="M6 38l12-12 8 8 6-6 14 16" stroke="#d97706" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" opacity="0.4"/>',
        "#92400e",
    ),

    # ── News ──────────────────────────────────────────────────────────────────
    **{k: _svg(
        '<path d="M10 8h28l8 8v32a4 4 0 0 1-4 4H10a4 4 0 0 1-4-4V12a4 4 0 0 1 4-4z" fill="#2563eb" opacity="0.1" stroke="#2563eb" stroke-width="2.5"/>'
        '<path d="M38 8v8h8" stroke="#2563eb" stroke-width="2.5" stroke-linejoin="round"/>'
        '<line x1="16" y1="26" x2="40" y2="26" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round"/>'
        '<line x1="16" y1="34" x2="32" y2="34" stroke="#2563eb" stroke-width="2.5" stroke-linecap="round"/>',
        "#2563eb",
    ) for k in ("gnews", "world_news")},

    # ── Newsletter structure ──────────────────────────────────────────────────
    **{k: _svg(
        '<rect x="6" y="6" width="44" height="44" rx="6" fill="#231913" opacity="0.06" stroke="#43311f" stroke-width="2" opacity="0.2"/>'
        '<rect x="12" y="12" width="32" height="8" rx="2" fill="#d86c3d" opacity="0.3" stroke="#d86c3d" stroke-width="2"/>'
        '<line x1="12" y1="26" x2="44" y2="26" stroke="#635048" stroke-width="2" stroke-linecap="round" opacity="0.4"/>'
        '<line x1="12" y1="32" x2="38" y2="32" stroke="#635048" stroke-width="2" stroke-linecap="round" opacity="0.3"/>',
        "#d86c3d",
    ) for k in ("newsletter_footer", "newsletter_header")},

    # ── Joke ──────────────────────────────────────────────────────────────────
    "joke": _svg(
        '<circle cx="28" cy="28" r="20" fill="#f59e0b" opacity="0.12" stroke="#f59e0b" stroke-width="2.5"/>'
        '<circle cx="22" cy="24" r="3" fill="#f59e0b"/>'
        '<circle cx="34" cy="24" r="3" fill="#f59e0b"/>'
        '<path d="M18 34c2 4 6 6 10 6s8-2 10-6" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round"/>',
        "#f59e0b",
    ),
}

PROVIDERS_ROOT = Path(__file__).resolve().parent / "providers"
ROOT_CONFIG_PATH = PROVIDERS_ROOT / "config.json"
THEMES_DIR = PROVIDERS_ROOT / "themes"
SHARED_TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
HTML_CACHE_DIR = Path(__file__).resolve().parents[2] / "logs" / "care_circle_render_cache"

# Wikimedia requires a descriptive User-Agent or it returns 403.
# Format: <app>/<version> (<url>; <email>)
WIKIMEDIA_USER_AGENT = "InkAndQuill-CareCircle/1.0 (https://inkandquill.com; contact@inkandquill.com)"

PROVIDER_TABLE_BASE_CSS = """
table {
    border-collapse: collapse;
    border-spacing: 0;
    border: none !important;
}

table td,
table th {
    border: none !important;
    padding: 10px !important;
}
"""


class BaseCareCircleProvider:
    """
    All ported DailyNewsletter providers inherit from this base class.

    Providers return structured JSON data from `_generate_payload`. The base
    class then binds that payload into the provider template and emits
    `rendered_html` for the patient UI.
    """

    _config_cache: dict | None = None
    _root_config_cache: dict | None = None

    provider_key: str = "base"
    is_safe_for_patient: bool = False

    def __init__(self, patient_config: Optional[dict[str, Any]] = None):
        patient_config = patient_config or {}
        merged_config = dict(self.config)
        difficulty = merged_config.get("difficulty", {})
        difficulty_level = str(
            patient_config.get("difficulty") or difficulty.get("default") or "easy"
        )
        difficulty_config = difficulty.get(difficulty_level, {})
        if isinstance(difficulty_config, dict):
            merged_config.update(difficulty_config)
        merged_config.update(patient_config)
        self.patient_config = merged_config
        self._template_name = str(self.patient_config.get("template", "default") or "default")
        self._token_usage: dict[str, Any] = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0, "model": ""}

    def get_generation_date(self) -> datetime.date:
        configured = self.patient_config.get("_for_date")
        if isinstance(configured, datetime.date):
            return configured
        if isinstance(configured, str):
            try:
                return datetime.date.fromisoformat(configured)
            except ValueError:
                pass
        return datetime.date.today()

    def get_generation_datetime(self) -> datetime.datetime:
        configured = self.patient_config.get("_generated_at")
        if isinstance(configured, datetime.datetime):
            return configured
        if isinstance(configured, str):
            try:
                return datetime.datetime.fromisoformat(configured)
            except ValueError:
                pass
        return datetime.datetime.now()

    @property
    def config(self) -> dict[str, Any]:
        cls = self.__class__
        if cls._config_cache is None:
            config_path = Path(inspect.getfile(cls)).parent / "config.json"
            if config_path.exists():
                cls._config_cache = json.loads(config_path.read_text(encoding="utf-8-sig"))
            else:
                cls._config_cache = {}
        return cls._config_cache

    @classmethod
    def load_root_config(cls) -> dict[str, Any]:
        if cls._root_config_cache is None:
            if ROOT_CONFIG_PATH.exists():
                cls._root_config_cache = json.loads(ROOT_CONFIG_PATH.read_text(encoding="utf-8"))
            else:
                cls._root_config_cache = {}
        return cls._root_config_cache

    @property
    def template_name(self) -> str:
        return self._template_name

    @template_name.setter
    def template_name(self, value: str) -> None:
        self._template_name = value or "default"

    @property
    def template_dir(self) -> Path:
        return Path(inspect.getfile(self.__class__)).parent / "templates"

    @property
    def provider_theme_dir(self) -> Path:
        return Path(inspect.getfile(self.__class__)).parent / "themes"

    @property
    def common(self) -> bool:
        return bool(self.config.get("common", False))

    @property
    def is_enabled(self) -> bool:
        """Respect per-provider 'enabled' flag from its config.json (for dev/testing fallback).
        DB catalog and patient configs take precedence in production flows.
        """
        return bool(self.config.get("enabled", True))

    @property
    def difficulty_level(self) -> str:
        difficulty = self.config.get("difficulty", {})
        return str(self.patient_config.get("difficulty") or difficulty.get("default") or "easy")

    @property
    def difficulty_config(self) -> dict[str, Any]:
        difficulty = self.config.get("difficulty", {})
        return difficulty.get(self.difficulty_level, {})

    @property
    def default_theme(self) -> str:
        root_config = self.load_root_config()
        return str(self.patient_config.get("theme") or root_config.get("default_theme") or "classic")

    @staticmethod
    def get_raw_patient_preferences(patient_profile: Any) -> dict[str, Any]:
        raw_preferences = getattr(patient_profile, "preferences", {}) or {}
        return raw_preferences if isinstance(raw_preferences, dict) else {}

    @classmethod
    def get_patient_preferences(cls, patient_profile: Any) -> dict[str, Any]:
        raw_preferences = cls.get_raw_patient_preferences(patient_profile)
        normalized = dict(raw_preferences)
        nested_preferences = raw_preferences.get("preferences")
        if isinstance(nested_preferences, dict):
            normalized.update(nested_preferences)
        normalized.pop("preferences", None)
        return normalized

    @classmethod
    def get_recipient_name(cls, patient_profile: Any, default: str = "Friend") -> str:
        raw_preferences = cls.get_raw_patient_preferences(patient_profile)
        return str(
            raw_preferences.get("recipient_name")
            or getattr(patient_profile, "display_name", default)
            or default
        )

    def list_templates(self) -> list[str]:
        if not self.template_dir.exists():
            return []
        return [template.stem for template in self.template_dir.glob("*.html")]

    def get_template_html(self, name: str | None = None) -> str:
        template_name = name or self.template_name
        template_path = self.template_dir / f"{template_name}.html"
        if not template_path.exists():
            return ""
        return template_path.read_text(encoding="utf-8")

    @staticmethod
    def list_themes() -> list[str]:
        """List all available theme names from the shared themes directory."""
        if not THEMES_DIR.exists():
            return []
        return [theme.stem for theme in THEMES_DIR.glob("*.css")]

    def list_provider_themes(self) -> list[str]:
        """List theme names available from this provider's themes directory."""
        if not self.provider_theme_dir.exists():
            return []
        # Map provider CSS names to theme names
        theme_map = {
            "master_online": "classic",
            "master_print": "grid_print",
        }
        themes = []
        for css_file in self.provider_theme_dir.glob("*.css"):
            stem = css_file.stem
            if stem in theme_map:
                themes.append(theme_map[stem])
            else:
                themes.append(stem)
        return themes

    @staticmethod
    def get_theme_css(theme_name: str = "classic") -> str:
        css_path = THEMES_DIR / f"{theme_name}.css"
        if not css_path.exists():
            return ""
        return css_path.read_text(encoding="utf-8")

    def get_provider_theme_css(self, theme_name: str = "classic") -> str:
        """
        Load provider-specific theme CSS.

        Provider theme files are conventionally named master_online.css (for
        screen/online rendering) and master_print.css (for print layouts).
        This method maps any theme name to the appropriate provider file.
        """
        # Map theme names to provider CSS files
        # Most providers use master_online.css for all online themes
        if not self.provider_theme_dir.exists():
            return ""

        # Try exact theme name first (e.g., classic.css, high_contrast.css)
        css_path = self.provider_theme_dir / f"{theme_name}.css"
        if css_path.exists():
            return css_path.read_text(encoding="utf-8")

        # Fall back to master_online.css for online/print themes
        if theme_name in ("classic", "high_contrast", "soft_pastel"):
            online_path = self.provider_theme_dir / "master_online.css"
            if online_path.exists():
                return online_path.read_text(encoding="utf-8")

        # Fall back to master_print.css for print themes
        if theme_name in ("grid_print",):
            print_path = self.provider_theme_dir / "master_print.css"
            if print_path.exists():
                return print_path.read_text(encoding="utf-8")

        return ""

    def get_combined_theme_css(self, theme_name: str = "classic") -> str:
        css_parts = [self.get_theme_css(theme_name), self.get_provider_theme_css(theme_name)]
        return "\n\n".join(part for part in css_parts if part.strip())

    def _common_dir(self) -> Path:
        return HTML_CACHE_DIR / self.provider_key

    def _common_html_path(self, theme_name: str = "classic") -> Path:
        date_str = self.get_generation_date().strftime("%Y%m%d")
        return self._common_dir() / f"common_{date_str}_{theme_name}.html"

    def _load_common_html_cache(self, theme_name: str = "classic") -> str | None:
        path = self._common_html_path(theme_name)
        if not path.exists():
            return None
        try:
            return path.read_text(encoding="utf-8")
        except OSError:
            return None

    def _save_common_html_cache(self, html: str, theme_name: str = "classic") -> None:
        path = self._common_html_path(theme_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(html, encoding="utf-8")

    def _build_template_context(
        self,
        payload: dict[str, Any],
        patient_profile: Any,
    ) -> dict[str, Any]:
        context = dict(payload)
        patient_name = self.get_recipient_name(patient_profile)
        prefs = self.get_patient_preferences(patient_profile)

        context.setdefault("patient_name", patient_name)
        context.setdefault("recipient_name", patient_name)
        context.setdefault("preferences", prefs)

        if self.provider_key == "daily_quote":
            quote = str(payload.get("text", "")).strip().strip('"')
            author = str(payload.get("subheading", "")).strip()
            if author.startswith("-"):
                author = author[1:].strip()
            context.setdefault("quote", quote)
            context.setdefault("author", author or "Unknown")

        if self.provider_key == "weather":
            city = payload.get("city") or str(payload.get("subheading", "")).replace(" Weather", "").strip()
            if not city:
                city = prefs.get("city_for_weather", "Unknown")

            weather = payload.get("weather")
            if not weather:
                temperature = payload.get("temperature")
                condition = payload.get("condition")
                if temperature and condition:
                    weather = f"{temperature}\u00b0F and {condition}"
                else:
                    weather = payload.get("text", "")

            context.setdefault("city", city)
            context.setdefault("weather", weather)

        return context

    def render_template(
        self,
        payload: dict[str, Any],
        patient_profile: Any,
        name: str | None = None,
        theme: str | None = None,
    ) -> str:
        template_name = name or self.template_name
        theme_name = theme or self.default_theme
        template_path = self.template_dir / f"{template_name}.html"

        if not template_path.exists():
            return ""

        if self.common:
            cached = self._load_common_html_cache(theme_name)
            if cached is not None:
                return cached

        environment = Environment(
            loader=FileSystemLoader([str(self.template_dir), str(SHARED_TEMPLATES_DIR)]),
            autoescape=select_autoescape(["html"]),
        )
        template = environment.get_template(f"{template_name}.html")
        context = self._build_template_context(payload, patient_profile)
        try:
            html = template.render(**context)
        except Exception as exc:
            logger.warning(
                "Template render failed for provider %s template %s: %s",
                self.provider_key,
                template_name,
                exc,
            )
            return ""

        kind = _PROVIDER_PROVENANCE.get(self.provider_key)
        if kind:
            badge = _PROV_BADGE[kind]
            html = _SECTION_TITLE_RE.sub(badge + r"\1", html, count=1)

        # Strip leading emoji from section titles and inject the provider SVG icon.
        icon_svg = _PROVIDER_SVG_ICONS.get(self.provider_key)
        if icon_svg:
            # Remove any leading emoji/pictograph characters from inside the title tag.
            html = _SECTION_TITLE_EMOJI_RE.sub(r'\1', html)
            # Prepend the SVG before the opening title tag.
            html = _SECTION_TITLE_RE.sub(icon_svg + r"\1", html, count=1)

        theme_css = self.get_combined_theme_css(theme_name)
        combined_css = "\n\n".join(
            part for part in (PROVIDER_TABLE_BASE_CSS, theme_css) if part.strip()
        )
        if combined_css:
            html = f"<style>\n{combined_css}\n</style>\n{html}"

        if self.common:
            self._save_common_html_cache(html, theme_name)

        return html

    async def execute(self, patient_profile: Any) -> dict[str, Any]:
        try:
            logger.info("Executing provider %s for patient %s", self.provider_key, patient_profile.id)
            result = await self._generate_payload(patient_profile)
            if not isinstance(result, dict):
                result = {"content": result}

            rendered_html = result.get("rendered_html")
            if not isinstance(rendered_html, str) or not rendered_html.strip():
                rendered_html = self.render_template(result, patient_profile)

            if rendered_html:
                result["rendered_html"] = rendered_html

            return {
                "success": True,
                "provider_key": self.provider_key,
                "data": result,
                "token_usage": dict(self._token_usage),
            }
        except Exception as exc:
            logger.error("Provider %s failed: %s", self.provider_key, str(exc))
            logger.error(traceback.format_exc())
            return self._build_fallback_payload(patient_profile, error=str(exc))

    async def _generate_payload(self, patient_profile: Any) -> dict[str, Any]:
        if self.__class__.get_content is not BaseCareCircleProvider.get_content:
            result = await self.get_content(patient_profile=patient_profile)
            if isinstance(result, dict):
                return result
            return {"content": result}
        raise NotImplementedError("Subclasses must implement _generate_payload")

    async def get_content(self, **kwargs: Any) -> dict[str, Any] | Any:
        raise NotImplementedError("Subclasses must implement _generate_payload or get_content")

    def log_llm_response(
        self,
        llm_response: Any,
        *,
        prompt: str = "",
        system_prompt: str = "",
    ) -> None:
        """Log token usage from an LLMResponse for debugging and cost tracking."""
        try:
            prompt_tokens = getattr(llm_response, "prompt_tokens", 0) or 0
            completion_tokens = getattr(llm_response, "completion_tokens", 0) or 0
            total_tokens = getattr(llm_response, "total_tokens", 0) or 0
            model = getattr(llm_response, "model", "") or ""
            self._token_usage["prompt_tokens"] += prompt_tokens
            self._token_usage["completion_tokens"] += completion_tokens
            self._token_usage["total_tokens"] += total_tokens
            if model:
                self._token_usage["model"] = model
            logger.debug(
                "Provider %s LLM call - model=%s tokens=%s prompt_len=%d",
                self.provider_key,
                model,
                total_tokens,
                len(prompt),
            )
        except Exception:
            pass

    def _build_fallback_payload(self, patient_profile: Any, error: str) -> dict[str, Any]:
        fallback_data = {
            "text": "Content temporarily unavailable.",
            "type": "error_state",
        }
        rendered_html = self.render_template(fallback_data, patient_profile)
        if rendered_html:
            fallback_data["rendered_html"] = rendered_html

        return {
            "success": False,
            "provider_key": self.provider_key,
            "error_detail": error,
            "data": fallback_data,
        }
