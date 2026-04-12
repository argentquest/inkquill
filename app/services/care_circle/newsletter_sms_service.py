"""
Care Circle Newsletter SMS Service.

Sends a mini-newsletter as an SMS text message to a patient's phone number.
Uses Twilio as the SMS provider.

The mini-newsletter is a curated subset of providers whose content
translates well to plain text — typically a greeting, a blessing,
a joke, and a word of the day.

In test mode (SMS_TEST_MODE=true) all messages are redirected to
SMS_TEST_NUMBER regardless of the patient's actual phone number.

Setup:
    pip install twilio
    Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER in .env.
"""

from __future__ import annotations

import logging
import textwrap
from datetime import datetime
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)

# Providers whose rendered data maps well to a short SMS snippet.
# Order determines how they appear in the message.
SMS_PROVIDER_KEYS = [
    "daily_blessing",     # One warm sentence
    "joke",               # Setup + punchline
    "word_of_the_day",    # Word + definition
    "daily_quote",        # Short quote
    "old_saying_match",   # Saying + meaning
]

# Max SMS characters. Twilio concatenates long messages automatically
# but we keep it under ~480 chars (3 SMS segments) to keep costs down.
SMS_MAX_CHARS = 480


def _extract_sms_text(key: str, data: dict[str, Any]) -> str | None:
    """Pull a short plain-text snippet from a provider's data payload."""
    if key == "daily_blessing":
        return data.get("blessing", "")

    if key == "joke":
        setup = data.get("setup") or data.get("question") or ""
        punchline = data.get("punchline") or data.get("answer") or ""
        if setup and punchline:
            return f"{setup}\n{punchline}"
        return data.get("text", "")

    if key == "word_of_the_day":
        word = data.get("word", "")
        definition = data.get("definition", "")
        if word and definition:
            return f"Word of the Day: {word}\n{definition}"
        return ""

    if key == "daily_quote":
        text = data.get("text") or data.get("quote", "")
        author = data.get("subheading") or data.get("author", "")
        if author:
            return f'"{text}"\n— {author}'
        return f'"{text}"' if text else ""

    if key == "old_saying_match":
        saying = data.get("saying", "")
        meaning = data.get("meaning", "")
        if saying:
            return f"{saying}\n{meaning}" if meaning else saying
        return ""

    # Generic fallback — try common text fields
    for field in ("text", "content", "body", "message"):
        val = data.get(field, "")
        if val:
            return str(val)

    return None


def _build_sms_body(
    patient_name: str,
    family_name: str | None,
    provider_results: list[dict[str, Any]],
) -> str:
    """Compose the full SMS message from collected provider snippets."""
    date_str = datetime.now().strftime("%b %d")

    lines: list[str] = []
    if family_name:
        lines.append(f"Good morning {patient_name}! ({family_name} Family, {date_str})")
    else:
        lines.append(f"Good morning {patient_name}! ({date_str})")
    lines.append("")  # blank line separator

    snippet_count = 0
    for entry in provider_results:
        key = entry.get("key", "")
        data = entry.get("data", {})
        text = _extract_sms_text(key, data)
        if not text:
            continue

        snippet = text.strip()
        # Trim very long snippets
        if len(snippet) > 160:
            snippet = textwrap.shorten(snippet, width=160, placeholder="…")

        lines.append(snippet)
        lines.append("")
        snippet_count += 1

    if snippet_count == 0:
        lines.append("Here's your daily Care Circle message. Have a wonderful day!")
        lines.append("")

    lines.append("— Ink & Quill Care Circle")

    body = "\n".join(lines).strip()

    # Truncate if over the character limit
    if len(body) > SMS_MAX_CHARS:
        body = body[: SMS_MAX_CHARS - 1] + "…"

    return body


def _send_via_twilio(to_number: str, body: str) -> bool:
    """Dispatch the SMS via the Twilio REST API."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.error(
            "Twilio not configured — set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in .env"
        )
        return False

    if not settings.TWILIO_FROM_NUMBER:
        logger.error("TWILIO_FROM_NUMBER not set in .env")
        return False

    try:
        from twilio.rest import Client  # type: ignore[import]

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=body,
            from_=settings.TWILIO_FROM_NUMBER,
            to=to_number,
        )
        logger.info("SMS sent sid=%s to=%s chars=%d", message.sid, to_number, len(body))
        return True

    except ImportError:
        logger.error(
            "twilio package not installed. Run: pip install twilio"
        )
        return False
    except Exception as exc:
        logger.error("Twilio send failed to %s: %s", to_number, exc)
        return False


# ── Public API ──────────────────────────────────────────────────────────────────

async def send_sms_newsletter(
    patient: Any,
    provider_results: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Send a mini Care Circle newsletter as an SMS to the patient's phone.

    Args:
        patient: CareCirclePatientProfile ORM object.
        provider_results: List of dicts, each with keys 'key' and 'data'
                          (the raw payload dict from each provider's execute()).

    Returns:
        dict with keys: success, to_number, test_mode, char_count, reason
    """
    patient_name: str = getattr(patient, "display_name", "Friend")
    family_name: str | None = getattr(patient, "family_name", None)
    phone_number: str | None = getattr(patient, "phone_number", None)

    if not phone_number:
        logger.warning("Patient %s has no phone number — skipping SMS.", patient_name)
        return {"success": False, "reason": "no_phone", "to_number": None}

    # Filter to SMS-friendly providers only
    sms_entries = [
        r for r in provider_results
        if r.get("key") in SMS_PROVIDER_KEYS
    ]
    # Sort by the preferred display order
    sms_entries.sort(key=lambda r: SMS_PROVIDER_KEYS.index(r["key"]))

    body = _build_sms_body(patient_name, family_name, sms_entries)

    # Test mode: redirect to the configured test number
    test_mode = settings.SMS_TEST_MODE
    actual_to = settings.SMS_TEST_NUMBER if (test_mode and settings.SMS_TEST_NUMBER) else phone_number

    if not actual_to:
        logger.warning("SMS test mode is on but SMS_TEST_NUMBER is not set.")
        return {"success": False, "reason": "no_test_number", "to_number": None}

    success = _send_via_twilio(actual_to, body)

    return {
        "success": success,
        "to_number": actual_to,
        "original_number": phone_number,
        "test_mode": test_mode,
        "char_count": len(body),
        "preview": body[:120] + ("…" if len(body) > 120 else ""),
    }
