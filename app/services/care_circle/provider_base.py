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

from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

PROVIDERS_ROOT = Path(__file__).resolve().parent / "providers"
ROOT_CONFIG_PATH = PROVIDERS_ROOT / "config.json"
THEMES_DIR = PROVIDERS_ROOT / "themes"
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
            loader=FileSystemLoader(str(self.template_dir)),
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
