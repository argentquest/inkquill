"""Mini Care Circle newsletter — daily scheduled send.

Picks 5 random cached providers for the patient's current date, wraps them
with a fresh header and footer, and sends the assembled email.

Runs at 9:00 AM daily (after the 2 AM precache and 6 AM session assembly).
"""

import json
import logging
import random
from datetime import date, datetime, time as dt_time
from pathlib import Path
from sqlalchemy import select

from app.scheduler.registry import register_task
from app.scheduler.logging import task_execution_context
from app.db.database import async_session_local
from app.models.care_circle import CareCirclePatientProfile
from app.services.care_circle.provider_cache import CACHE_ROOT
from app.services.care_circle.session_assembler import get_provider_class

logger = logging.getLogger(__name__)

_SKIP_KEYS = {"newsletter_header", "newsletter_footer"}
_PICK_COUNT = 5


async def _render_provider(provider_key: str, patient, patient_config: dict | None = None) -> str:
    """Instantiate a provider, execute it, and return its rendered_html."""
    cls = get_provider_class(provider_key)
    if not cls:
        return ""
    try:
        instance = cls(patient_config=patient_config or {})
        result = await instance.execute(patient)
        return result.get("data", {}).get("rendered_html", "")
    except Exception as exc:
        logger.warning("Mini newsletter: failed to render %s: %s", provider_key, exc)
        return ""


def _load_cached_html(patient_id: int, today: date) -> list[tuple[str, str]]:
    """Return list of (provider_key, rendered_html) from today's cache."""
    cache_dir = CACHE_ROOT / str(patient_id) / today.isoformat()
    if not cache_dir.exists():
        return []

    results = []
    for f in cache_dir.glob("*.json"):
        key = f.stem
        if key in _SKIP_KEYS:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            html = data.get("data", {}).get("rendered_html", "")
            if html and data.get("success", True):
                results.append((key, html))
        except Exception:
            pass
    return results


async def _build_mini_newsletter(patient, today: date, limit: int | None = None) -> str:
    """Assemble header + selected providers + footer into a single HTML body.
    
    Args:
        patient: The patient profile.
        today: The target date.
        limit: Maximum number of providers to include. None means all available.
    """

    # Load and shuffle cached providers
    available = _load_cached_html(patient.id, today)
    random.shuffle(available)
    selected = available[:limit] if limit else available

    if not selected:
        logger.warning("Mini newsletter: no cached providers for patient %s on %s", patient.id, today)

    reference_config = {
        "_for_date": today,
        "_generated_at": datetime.combine(today, dt_time(hour=9, minute=0)),
    }
    header_html = await _render_provider(
        "newsletter_header",
        patient,
        patient_config=reference_config,
    )

    # Fresh footer with basic stats
    footer_html = await _render_provider(
        "newsletter_footer",
        patient,
        patient_config={
            **reference_config,
            "total_providers": len(selected),
            "generation_date": today.strftime("%B %d, %Y"),
        },
    )

    parts = (
        [header_html]
        + [html for _, html in selected]
        + [footer_html]
    )
    return "\n".join(p for p in parts if p.strip())


async def _send_mini_to_patient(patient, today: date) -> dict:
    from app.services.care_circle.newsletter_email_service import send_newsletter_email

    if not getattr(patient, "email", None):
        return {
            "patient_id": patient.id,
            "status": "skipped",
            "reason": "no email address",
        }

    body_html = await _build_mini_newsletter(patient, today)
    if not body_html.strip():
        return {
            "patient_id": patient.id,
            "status": "skipped",
            "reason": "no content available",
        }

    result = await send_newsletter_email(patient, body_html, today)
    return {
        "patient_id": patient.id,
        "patient_name": patient.display_name,
        "status": "sent" if result.get("success") else "failed",
        "email_result": result,
    }


@register_task(
    key="care_circle.mini_newsletter",
    name="Mini Care Circle Newsletter",
    default_cron="0 9 * * *",  # 9:00 AM daily — after precache (2 AM) and session assembly (6 AM)
    description="Sends a mini newsletter to each active patient with 5 randomly selected providers from today's cache.",
    enabled_by_default=True,
    max_instances=1,
    misfire_grace_time=600,
)
async def dispatch_mini_newsletter(reference_date: date | None = None) -> dict:
    """Send mini newsletter to all active patients."""
    today = reference_date or date.today()

    async with task_execution_context(
        task_key="care_circle.mini_newsletter",
        task_name="Mini Care Circle Newsletter",
    ) as ctx:
        async with async_session_local() as db:
            patients = (await db.execute(
                select(CareCirclePatientProfile).where(
                    CareCirclePatientProfile.access_state == "active"
                )
            )).scalars().all()
            patients = list(patients)

        results = []
        success_count = 0
        failure_count = 0

        for patient in patients:
            try:
                result = await _send_mini_to_patient(patient, today)
                results.append(result)
                if result["status"] in ("sent", "skipped"):
                    success_count += 1
                else:
                    failure_count += 1
            except Exception as exc:
                logger.error("Mini newsletter failed for patient %s: %s", patient.id, exc)
                results.append({
                    "patient_id": patient.id,
                    "status": "failed",
                    "error": str(exc),
                })
                failure_count += 1

        ctx["total_patients"] = len(patients)
        ctx["reference_date"] = today.isoformat()
        ctx["success_count"] = success_count
        ctx["failure_count"] = failure_count
        ctx["results"] = results

    return {
        "task": "care_circle.mini_newsletter",
        "reference_date": today.isoformat(),
        "total_patients": len(patients),
        "success_count": success_count,
        "failure_count": failure_count,
        "results": results,
    }
