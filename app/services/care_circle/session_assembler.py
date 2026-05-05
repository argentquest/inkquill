"""
Patient Session Assembly Service.
Takes a patient profile, queries their active providers, executes them securely,
and creates the daily patient content cards.
"""

import logging
import importlib
import json
import re
import time
from datetime import date, datetime, time as dt_time
from html import unescape
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.config import settings
from app.services.care_circle.provider_cache import CACHE_ROOT, get_cached_result, save_cached_result

from app.models.care_circle import (
    CareCircleFamily,
    CareCircleFamilyMembership,
    CareCirclePatientProfile,
    CareCirclePatientContentCard,
    CareCircleProviderCatalog,
    CareCircleProviderPatientConfig
)
from app.models.ai_model_config import AIModelConfiguration, AIModelTypeEnum, AIProviderEnum
from app.models.job_status import JobStatus
from app.services.care_circle.provider_base import BaseCareCircleProvider
from app.crud.care_circle import OBSOLETE_PROVIDER_KEYS, ensure_provider_catalog_seeded
from app.services.cost_tracker_service import log_ai_call

logger = logging.getLogger(__name__)

FOOTER_PROVIDER_KEY = "newsletter_footer"
HEADER_PROVIDER_KEY = "newsletter_header"

# Providers that render best in a narrow sidebar column.
# Everything else (rich content, photos, audio, featured stories) goes in the main column.
_SIDE_PROVIDERS: frozenset[str] = frozenset({
    "weather", "garden_almanac",
    "world_news", "world-news",
    "daily_affirmation", "personal_affirmation", "gratitude",
    "joke", "puzzle", "brain_booster", "riddle",
    "missing-vowels", "word-scramble", "gridless-crossword",
    "finish-phrase", "complete-the-duo", "odd-one-out", "spot-the-difference",
    "hymn_of_the_day", "daily_blessing", "seasonal_poem",
    "cat_fact", "dog_photo", "sensory",
    "local_history", "daily_quote", "ai_trivia",
})

# Injected once at the top of the assembled HTML so the email service can hoist it.
_LAYOUT_CSS = """
.cc-newsletter { background: #fcfaf6; font-family: Georgia, "Times New Roman", serif; color: #231913; }
.cc-cols { display: flex; align-items: flex-start; gap: 16px; }
.cc-main { flex: 1.45; min-width: 0; }
.cc-side { flex: 1;    min-width: 0; }
@media only screen and (max-width: 600px) {
    .cc-cols { flex-direction: column !important; }
}
"""


def _build_newsletter_html(cards: list) -> str:
    """Group cards into header / two-column body / footer and wrap in .cc-newsletter."""
    header_html = ""
    footer_html = ""
    main_parts: list[str] = []
    side_parts: list[str] = []

    for card in cards:
        html = (card.rendered_html or "").strip()
        if not html:
            continue
        key = card.provider_key
        if key == HEADER_PROVIDER_KEY:
            header_html = html
        elif key == FOOTER_PROVIDER_KEY:
            footer_html = html
        elif key in _SIDE_PROVIDERS:
            side_parts.append(html)
        else:
            main_parts.append(html)

    if main_parts or side_parts:
        cols_html = (
            '<div class="cc-cols">'
            f'<div class="cc-main">{"".join(main_parts)}</div>'
            f'<div class="cc-side">{"".join(side_parts)}</div>'
            '</div>'
        )
    else:
        cols_html = ""

    inner = "\n".join(filter(None, [header_html, cols_html, footer_html]))
    layout_style = f"<style>\n{_LAYOUT_CSS}\n</style>"
    return f"{layout_style}\n<div class='cc-newsletter'>\n{inner}\n</div>"


_HTML_TAG_RE = re.compile(r"<[^>]+>")
_STRUCTURED_SKIP_KEYS = {
    "type",
    "grid",
    "template",
    "slots",
    "solution",
    "cell_numbers",
    "puzzle_content",
    "custom_parameters",
    "rows",
    "cols",
}
_PRIMARY_TEXT_KEYS = (
    "text",
    "message",
    "instruction",
    "prompt",
    "phrase",
    "summary",
    "description",
    "body",
)
_SECONDARY_TEXT_KEYS = (
    "answer",
    "words",
    "items",
    "clues",
    "across",
    "down",
    "temperature",
    "condition",
    "city",
    "category",
)

def _to_camel_case(snake_str: str) -> str:
    components = snake_str.split('_')
    return "".join(x.title() for x in components)


def _clean_text(value: str) -> str:
    text = _HTML_TAG_RE.sub(" ", value)
    text = unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _summarize_scalar(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return ""
        if stripped.startswith("{") or stripped.startswith("["):
            try:
                parsed = json.loads(stripped)
                return _summarize_value(parsed)
            except json.JSONDecodeError:
                pass
        return _clean_text(stripped)
    return _clean_text(str(value))


def _summarize_list(values: list[Any]) -> str:
    parts: list[str] = []
    for item in values[:8]:
        summary = _summarize_value(item)
        if summary:
            parts.append(summary)
    return "; ".join(parts)


def _summarize_dict(values: dict[str, Any]) -> str:
    parts: list[str] = []

    for key in _PRIMARY_TEXT_KEYS:
        if key in values:
            summary = _summarize_value(values[key])
            if summary:
                parts.append(summary)

    for key in _SECONDARY_TEXT_KEYS:
        if key in values:
            summary = _summarize_value(values[key])
            if summary:
                label = key.replace("_", " ").capitalize()
                parts.append(f"{label}: {summary}")

    if parts:
        deduped: list[str] = []
        seen = set()
        for part in parts:
            if part not in seen:
                deduped.append(part)
                seen.add(part)
        return " ".join(deduped)

    fallback_parts: list[str] = []
    for key, value in values.items():
        if key in _STRUCTURED_SKIP_KEYS:
            continue
        summary = _summarize_value(value)
        if summary:
            fallback_parts.append(f"{key.replace('_', ' ').capitalize()}: {summary}")
        if len(fallback_parts) >= 4:
            break
    return " ".join(fallback_parts)


def _summarize_value(value: Any) -> str:
    if isinstance(value, dict):
        return _summarize_dict(value)
    if isinstance(value, list):
        return _summarize_list(value)
    return _summarize_scalar(value)


def _normalize_provider_card(result: dict[str, Any]) -> tuple[str, str]:
    data = result.get("data", {})
    title = "Daily Highlight"
    if isinstance(data, dict):
        title = _summarize_scalar(data.get("subheading") or data.get("title")) or title

    body = _summarize_value(data)
    if not body:
        body = "Content temporarily unavailable."
    return title, body


def _extract_rendered_html(result: dict[str, Any]) -> str | None:
    data = result.get("data", {})
    if not isinstance(data, dict):
        return None

    html_value = data.get("rendered_html") or data.get("html") or data.get("puzzle_content")
    if not isinstance(html_value, str):
        return None

    cleaned = html_value.strip()
    if not cleaned:
        return None
    return cleaned


def _provider_sort_order(provider_key: str, display_order: int) -> tuple[int, int]:
    """Keep newsletter footer pinned to the bottom regardless of config ordering."""
    if provider_key == FOOTER_PROVIDER_KEY:
        return (1, display_order)
    return (0, display_order)


def _reference_generated_at(for_date: date) -> datetime:
    return datetime.combine(for_date, dt_time(hour=9, minute=0))


def _purge_obsolete_cached_provider_files(patient_id: int, for_date: date) -> None:
    cache_dir = CACHE_ROOT / str(patient_id) / for_date.isoformat()
    if not cache_dir.exists():
        return

    for provider_key in OBSOLETE_PROVIDER_KEYS:
        for candidate in cache_dir.glob(f"{provider_key}*"):
            try:
                candidate.unlink()
            except FileNotFoundError:
                continue
            except Exception as exc:
                logger.warning("Failed to remove obsolete Care Circle cache file %s: %s", candidate, exc)


async def _get_family_owner_user_id(db: AsyncSession, patient: CareCirclePatientProfile) -> int | None:
    family = await db.get(CareCircleFamily, patient.family_id)
    if family and family.created_by_user_id:
        return family.created_by_user_id

    owner_membership = await db.scalar(
        select(CareCircleFamilyMembership).where(
            CareCircleFamilyMembership.family_id == patient.family_id,
            CareCircleFamilyMembership.role == "owner",
        ).order_by(
            CareCircleFamilyMembership.is_primary.desc(),
            CareCircleFamilyMembership.id.asc(),
        )
    )
    if owner_membership:
        return owner_membership.user_id

    return patient.created_by_user_id


async def _resolve_ai_model_config_for_logging(
    db: AsyncSession,
    model_name: str,
) -> AIModelConfiguration:
    existing = await db.scalar(
        select(AIModelConfiguration).where(
            AIModelConfiguration.model_name == model_name
        ).order_by(AIModelConfiguration.is_active.desc(), AIModelConfiguration.id.asc())
    )
    if existing:
        return existing

    model_config = AIModelConfiguration(
        display_name=model_name,
        model_name=model_name,
        description="Ad hoc Care Circle logging model placeholder",
        provider=AIProviderEnum.OPENAI,
        model_type=AIModelTypeEnum.GENERATION,
        is_active=True,
        is_public_chat_default=False,
        max_tokens=0,
        temperature=0.0,
        top_p=1.0,
        presence_penalty=0.0,
        frequency_penalty=0.0,
        is_json_mode=False,
        provider_cost_input_usd_pm=settings.CARE_CIRCLE_DEFAULT_INPUT_PRICE_USD_PM,
        provider_cost_output_usd_pm=settings.CARE_CIRCLE_DEFAULT_OUTPUT_PRICE_USD_PM,
        user_price_input_usd_pm=settings.CARE_CIRCLE_DEFAULT_INPUT_PRICE_USD_PM,
        user_price_output_usd_pm=settings.CARE_CIRCLE_DEFAULT_OUTPUT_PRICE_USD_PM,
    )
    db.add(model_config)
    await db.flush()
    return model_config


async def _log_provider_token_usage(
    db: AsyncSession,
    patient: CareCirclePatientProfile,
    provider_key: str,
    token_usage: dict[str, Any] | None,
    elapsed_ms: float | None = None,
    job_id: str | None = None,
) -> None:
    if not token_usage:
        return

    total_tokens = int(token_usage.get("total_tokens") or 0)
    model_name = str(token_usage.get("model") or "").strip()
    if total_tokens <= 0 or not model_name:
        return

    owner_user_id = await _get_family_owner_user_id(db, patient)
    if not owner_user_id:
        logger.warning(
            "Skipping Care Circle AI call logging for patient %s provider %s: no family owner user found.",
            patient.id,
            provider_key,
        )
        return

    model_config = await _resolve_ai_model_config_for_logging(db, model_name)
    validated_job_id = await _normalize_job_id_for_logging(db, job_id)
    await log_ai_call(
        user_id=owner_user_id,
        model_config=model_config,
        usage={
            "prompt_tokens": int(token_usage.get("prompt_tokens") or 0),
            "completion_tokens": int(token_usage.get("completion_tokens") or 0),
            "total_tokens": total_tokens,
        },
        call_type="care_circle_provider",
        input_prompt=f"Care Circle provider: {provider_key}",
        duration_ms=int(round(elapsed_ms or 0.0)) or None,
        job_id=validated_job_id,
        object_id=patient.id,
        db=db,
    )


async def _normalize_job_id_for_logging(
    db: AsyncSession,
    job_id: str | None,
) -> str | None:
    if not job_id:
        return None

    existing_job_id = await db.scalar(
        select(JobStatus.job_id).where(JobStatus.job_id == job_id)
    )
    if existing_job_id:
        return job_id

    logger.warning(
        "Skipping Care Circle AI call job_id %s because it does not exist in job_statuses.",
        job_id,
    )
    return None

def get_provider_class(provider_key: str) -> type[BaseCareCircleProvider] | None:
    """Dynamically loads and returns the standardized provider class."""
    module_path = f"app.services.care_circle.providers.{provider_key}.provider"
    try:
        module = importlib.import_module(module_path)
        class_name = _to_camel_case(provider_key) + "Provider"
        provider_class = getattr(module, class_name, None)

        if provider_class and issubclass(provider_class, BaseCareCircleProvider):
            return provider_class
    except ModuleNotFoundError:
        logger.debug("Provider module not found, skipping: %s", provider_key)
    except Exception as e:
        logger.error("Failed to load provider class %s: %s", provider_key, e)
    return None

async def assemble_daily_patient_session(
    db: AsyncSession,
    patient_id: int,
    force_regenerate: bool = False,
    job_id: str | None = None,
    for_date: date | None = None,
) -> bool:
    """
    Core executor orchestrating the day's patient assembly.
    1. Fetches patient.
    2. Identifies enabled, patient_visible providers.
    3. Runs them concurrently or sequentially.
    4. Overwrites the active CareCirclePatientContentCard rows.

    force_regenerate: skip the file cache and re-run every provider.
    for_date: logical newsletter date to generate/cache against. Defaults to today.
    """
    patient = await db.get(CareCirclePatientProfile, patient_id)
    if not patient or patient.access_state == "archived":
        return False

    await ensure_provider_catalog_seeded(db)

    # Find all globally enabled, patient-safe catalog items
    catalog_query = select(CareCircleProviderCatalog).where(
        CareCircleProviderCatalog.enabled == True,
        CareCircleProviderCatalog.patient_visible == True
    )
    catalog_items = (await db.execute(catalog_query)).scalars().all()
    
    # Grab custom configs or disabled states from the family config mappings
    config_query = select(CareCircleProviderPatientConfig).where(
        CareCircleProviderPatientConfig.patient_id == patient_id
    )
    user_configs = (await db.execute(config_query)).scalars().all()
    config_map = {c.provider_key: c for c in user_configs}
    
    target_date = for_date or date.today()
    generated_at = _reference_generated_at(target_date)

    # Select which providers are running for this session
    # For Sprint 2, if no custom config exists, we default allow if they are marked patient_visible
    active_providers = []
    for item in catalog_items:
        conf = config_map.get(item.provider_key)
        if conf and not conf.is_enabled:
            continue # Family explicitly disabled it

        cls = get_provider_class(item.provider_key)
        if cls:
            # Respect per-provider config.json "enabled" flag for dev/testing fallback
            # (DB catalog + patient config take precedence in normal flows)
            if not cls().is_enabled:
                logger.info(f"Skipping {item.provider_key} - disabled in its config.json")
                continue

            # We enforce patient-safe flag at execution mount explicitly!
            if cls.is_safe_for_patient:
                # Mount the provider with any custom family dict
                cfg_dict = dict(conf.custom_parameters or {}) if conf else {}
                cfg_dict["_for_date"] = target_date
                cfg_dict["_generated_at"] = generated_at
                instance = cls(patient_config=cfg_dict)
                active_providers.append((item.provider_key, item.display_order, instance))
            else:
                logger.warning(f"Skipping {item.provider_key} as it is structurally flagged unsafe for patients.")
    
    if not active_providers:
        logger.warning(f"No active safe providers found for patient {patient_id}.")
        return False

    footer_provider: tuple[str, int, BaseCareCircleProvider] | None = None
    content_providers: list[tuple[str, int, BaseCareCircleProvider]] = []
    for provider_tuple in active_providers:
        if provider_tuple[0] == FOOTER_PROVIDER_KEY:
            footer_provider = provider_tuple
        else:
            content_providers.append(provider_tuple)

    content_providers.sort(key=lambda x: _provider_sort_order(x[0], x[1]))

    # Execute the active providers — use file cache when available
    _purge_obsolete_cached_provider_files(patient_id, target_date)
    generated_cards = []
    total_elapsed_ms = 0.0
    total_tokens = 0
    llm_provider_count = 0
    model_used = ""

    for p_key, order, provider_instance in content_providers:
        result = None if force_regenerate else get_cached_result(patient_id, target_date, p_key)
        if result is None:
            t0 = time.monotonic()
            result = await provider_instance.execute(patient)
            elapsed_ms = (time.monotonic() - t0) * 1000
            total_elapsed_ms += elapsed_ms
            token_usage = result.get("token_usage") or {}
            await _log_provider_token_usage(
                db,
                patient,
                p_key,
                token_usage,
                elapsed_ms,
                job_id=job_id,
            )
            total_tokens += int(token_usage.get("total_tokens") or 0)
            if token_usage.get("total_tokens"):
                llm_provider_count += 1
            if token_usage.get("model"):
                model_used = token_usage["model"]
            save_cached_result(
                patient_id, target_date, p_key, result,
                elapsed_ms=elapsed_ms,
                token_usage=token_usage,
                force_regenerate=force_regenerate,
            )
        else:
            token_usage = result.get("token_usage") or {}
            total_tokens += int(token_usage.get("total_tokens") or 0)
            if token_usage.get("total_tokens"):
                llm_provider_count += 1
            if token_usage.get("model"):
                model_used = token_usage["model"]
        title, body = _normalize_provider_card(result)
        rendered_html = _extract_rendered_html(result)
        
        card = CareCirclePatientContentCard(
            patient_id=patient_id,
            provider_key=p_key,
            title=title,
            body=body,
            rendered_html=rendered_html,
            card_kind=p_key, # Use provider key as kind mapping
            display_order=order,
            is_active=True
        )
        generated_cards.append(card)

    if footer_provider:
        footer_key, footer_order, footer_instance = footer_provider
        footer_result = await footer_instance.execute(patient)
        footer_result_data = footer_result.get("data") if isinstance(footer_result, dict) else None
        if isinstance(footer_result_data, dict):
            footer_result_data.update({
                "total_tokens": total_tokens,
                "total_providers": len(content_providers),
                "llm_providers": llm_provider_count,
                "model_used": model_used,
                "elapsed_s": round(total_elapsed_ms / 1000, 1),
                "generation_date": target_date.strftime("%B %d, %Y"),
            })
            footer_result["data"] = footer_result_data
            rendered_html = footer_instance.render_template(footer_result_data, patient)
            if rendered_html:
                footer_result["data"]["rendered_html"] = rendered_html

        save_cached_result(
            patient_id, target_date, footer_key, footer_result,
            elapsed_ms=0.0,
            token_usage=footer_result.get("token_usage"),
            force_regenerate=True,
        )
        title, body = _normalize_provider_card(footer_result)
        rendered_html = _extract_rendered_html(footer_result)
        generated_cards.append(
            CareCirclePatientContentCard(
                patient_id=patient_id,
                provider_key=footer_key,
                title=title,
                body=body,
                rendered_html=rendered_html,
                card_kind=footer_key,
                display_order=max([card.display_order for card in generated_cards], default=footer_order) + 1,
                is_active=True,
            )
        )
        
    if generated_cards:
        # Clear out yesterday's active cards
        await db.execute(
            delete(CareCirclePatientContentCard)
            .where(CareCirclePatientContentCard.patient_id == patient_id)
        )
        # Flush to prevent unique constraint cascades
        await db.flush()

        # Save new cards
        for card in generated_cards:
            db.add(card)

        await db.commit()

    generated_cards.sort(key=lambda c: _provider_sort_order(c.provider_key, c.display_order))
    newsletter_html = _build_newsletter_html(generated_cards)

    return {
        "success": True,
        "html": newsletter_html,
        "card_count": len(generated_cards),
    }


async def get_newsletter_html_for_date(
    db: AsyncSession, patient_id: int, for_date: date
) -> str:
    """Read cached provider outputs for a given date and assemble newsletter HTML.

    Does not trigger any providers — returns only what is already on disk.
    """
    cache_dir = CACHE_ROOT / str(patient_id) / for_date.isoformat()
    if not cache_dir.exists():
        return ""

    _purge_obsolete_cached_provider_files(patient_id, for_date)

    catalog_items = (await db.execute(select(CareCircleProviderCatalog))).scalars().all()
    order_map = {item.provider_key: item.display_order for item in catalog_items}

    entries: list[tuple[str, int, str]] = []
    for json_file in cache_dir.glob("*.json"):
        try:
            data = json.loads(json_file.read_text(encoding="utf-8"))
            html = _extract_rendered_html(data)
            if html:
                provider_key = json_file.stem
                if provider_key in OBSOLETE_PROVIDER_KEYS:
                    continue
                order = order_map.get(provider_key, 50)
                entries.append((provider_key, order, html))
        except Exception:
            pass

    entries.sort(key=lambda x: _provider_sort_order(x[0], x[1]))

    class _SimpleCard:
        def __init__(self, provider_key: str, rendered_html: str):
            self.provider_key = provider_key
            self.rendered_html = rendered_html

    return _build_newsletter_html([_SimpleCard(key, html) for key, _, html in entries])
