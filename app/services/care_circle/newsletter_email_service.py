"""
Care Circle Newsletter Email Service.

Sends the full HTML newsletter to a patient's email address.
Wraps the rendered provider HTML inside a mobile-friendly email shell,
then dispatches via the existing IONOS SMTP service.

In test mode (EMAIL_TEST_MODE=true) the email is redirected to
EMAIL_TEST_ADDRESS regardless of the patient's address.
"""

from __future__ import annotations

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


# ── Email shell ─────────────────────────────────────────────────────────────────
# A lightweight, broadly-compatible email wrapper.
# Provider HTML is injected as-is; the wrapper handles mobile width + fonts.

_EMAIL_SHELL = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>{subject}</title>
<style>
  /* Reset */
  body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
  table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; border-collapse: collapse; }}
  img {{ -ms-interpolation-mode: bicubic; border: 0; height: auto; line-height: 100%;
         outline: none; text-decoration: none; }}

  /* Body */
  body {{
    margin: 0 !important;
    padding: 0 !important;
    background-color: #f1f5f9;
    font-family: Georgia, 'Times New Roman', serif;
    color: #1e293b;
  }}

  /* Outer wrapper */
  .email-wrapper {{
    width: 100%;
    background-color: #f1f5f9;
    padding: 24px 0;
  }}

  /* Inner container — capped at 680px for desktop, full-width on mobile */
  .email-body {{
    max-width: 680px;
    margin: 0 auto;
    background: #ffffff;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  }}

  /* Content area where provider HTML is injected */
  .email-content {{
    padding: 0;
  }}

  /* Ensure provider images stay within bounds */
  .email-content img {{
    max-width: 100%;
    height: auto;
  }}

  /* Mobile tweaks */
  @media only screen and (max-width: 680px) {{
    .email-body {{ border-radius: 0; }}
  }}
</style>
</head>
<body>
<div class="email-wrapper">
  <div class="email-body">
    <div class="email-content">
      {body_html}
    </div>
  </div>
</div>
</body>
</html>
"""


def _build_email_html(body_html: str, subject: str) -> str:
    """Wrap rendered newsletter HTML in the email shell."""
    return _EMAIL_SHELL.format(subject=subject, body_html=body_html)


def _html_to_plain(html: str) -> str:
    """Minimal HTML → plain text for the text/plain part."""
    import re
    text = re.sub(r"<style[^>]*>.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _build_subject(patient_name: str, family_name: str | None) -> str:
    date_str = datetime.now().strftime("%B %d, %Y")
    if family_name:
        return f"Your Care Circle Newsletter — {date_str} | {family_name} Family"
    return f"Your Care Circle Newsletter — {date_str}"


# ── SMTP send ───────────────────────────────────────────────────────────────────

def _send_via_smtp(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str,
    text_content: str,
) -> bool:
    """Send a multipart email via the configured IONOS SMTP server."""
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = formataddr((settings.FROM_NAME or "Care Circle", settings.FROM_EMAIL or ""))
        msg["To"] = formataddr((to_name, to_email))
        msg["Reply-To"] = settings.FROM_EMAIL or ""
        msg["X-Mailer"] = "Ink & Quill Care Circle"

        msg.attach(MIMEText(text_content, "plain", "utf-8"))
        msg.attach(MIMEText(html_content, "html", "utf-8"))

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(msg)

        logger.info("Newsletter email sent to %s (%s)", to_email, subject)
        return True

    except Exception as exc:
        logger.error("Failed to send newsletter email to %s: %s", to_email, exc)
        return False


# ── Public API ──────────────────────────────────────────────────────────────────

async def send_newsletter_email(
    patient: Any,
    newsletter_html: str,
) -> dict[str, Any]:
    """
    Send the full Care Circle newsletter to the patient's email address.

    Args:
        patient: CareCirclePatientProfile ORM object.
        newsletter_html: Fully assembled newsletter HTML (header + providers + footer).

    Returns:
        dict with keys: success, to_email, subject, test_mode
    """
    patient_name: str = getattr(patient, "display_name", "Friend")
    family_name: str | None = getattr(patient, "family_name", None)
    patient_email: str | None = getattr(patient, "email", None)

    if not patient_email:
        logger.warning("Patient %s has no email address — skipping newsletter email.", patient_name)
        return {"success": False, "reason": "no_email", "to_email": None}

    subject = _build_subject(patient_name, family_name)
    html_content = _build_email_html(newsletter_html, subject)
    text_content = _html_to_plain(html_content)

    # Test mode: redirect to the configured test address
    test_mode = getattr(settings, "EMAIL_TEST_MODE", False)
    actual_to = settings.EMAIL_TEST_ADDRESS if test_mode else patient_email

    success = _send_via_smtp(
        to_email=actual_to,
        to_name=patient_name,
        subject=subject,
        html_content=html_content,
        text_content=text_content,
    )

    return {
        "success": success,
        "to_email": actual_to,
        "original_email": patient_email,
        "subject": subject,
        "test_mode": test_mode,
    }
