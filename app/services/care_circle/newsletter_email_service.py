"""
Care Circle Newsletter Email Service.

Sends the full HTML newsletter to a patient's email address.
Wraps the rendered provider HTML inside a mobile-friendly email shell,
then dispatches via the existing IONOS SMTP service.

In test mode (EMAIL_TEST_MODE=true) the email is redirected to
EMAIL_TEST_ADDRESS regardless of the patient's address.
"""

from __future__ import annotations

import asyncio
import logging
import mimetypes
import re
import smtplib
import uuid
from pathlib import Path
from datetime import datetime
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from typing import Any

import httpx

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
{hoisted_css}
</style>
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

  /* Inner container — full-width at all sizes */
  .email-body {{
    width: 100%;
    background: #ffffff;
    overflow: hidden;
  }}

  /* Content area where provider HTML is injected */
  .email-content {{
    padding: 0 16px;
    box-sizing: border-box;
  }}

  .email-content table {{
    border-collapse: collapse !important;
    border-spacing: 0 !important;
    border: none !important;
  }}

  .email-content table td,
  .email-content table th {{
    border: none !important;
    padding: 10px !important;
  }}

  /* Make sure comics and images use full available width */
  .comic-strip-card,
  .email-content img {{
    max-width: 100%;
    width: 100%;
    height: auto;
    box-sizing: border-box;
  }}

  /* Ensure provider images stay within bounds */
  .email-content img {{
    max-width: 100%;
    height: auto;
  }}

  /* Mobile tweaks */
  @media only screen and (max-width: 680px) {{
    .email-content {{
      padding: 0 8px !important;
    }}
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


_STYLE_BLOCK_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.DOTALL | re.IGNORECASE)


def _build_email_html(body_html: str, subject: str) -> str:
    """Wrap rendered newsletter HTML in the email shell, then inline all CSS.

    Premailer converts every CSS class rule to inline style="" attributes,
    which is the only approach that survives Gmail and most other clients.
    """
    from premailer import transform

    extracted_css: list[str] = []

    def _pull_style(m: re.Match) -> str:
        extracted_css.append(m.group(1))
        return ""

    clean_body = _STYLE_BLOCK_RE.sub(_pull_style, body_html)
    hoisted = "\n".join(extracted_css)
    full_html = _EMAIL_SHELL.format(subject=subject, body_html=clean_body, hoisted_css=hoisted)

    # Add small comic attribution footer (updated from user input)
    attribution = '''
    <div style="margin-top: 32px; padding-top: 16px; border-top: 1px solid #ddd; font-size: 0.78em; color: #555; text-align: center; line-height: 1.4;">
        Comics: Cat and Bot, Fodongo, Mimi &amp; Eunice (CC-BY-SA • Nina Paley), Wuffle Comics (CC0 • Piti Yindee).<br>
        All strips used under open licenses with gratitude to the creators.
    </div>
    '''
    full_html = full_html.replace('</body>', attribution + '\n</body>')

    try:
        full_html = transform(
            full_html,
            remove_classes=False,
            keep_style_tags=True,
            cssutils_logging_level=logging.CRITICAL,
        )
    except Exception as exc:
        logger.warning("premailer CSS inlining failed, sending without inlining: %s", exc)

    return full_html


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


# ── Image embedding ─────────────────────────────────────────────────────────────

_SRC_REMOTE_RE = re.compile(r'src=(["\'])(https?://[^"\'> ]+)\1', re.IGNORECASE)
_SRC_LOCAL_RE = re.compile(r'src=(["\'])([^"\'> ]+\.(?:jpg|jpeg|png|gif|webp))\1', re.IGNORECASE)
_SRC_SERVED_RE = re.compile(r'src=(["\'])(/api/v1/care-circle/cached-image/[^"\'> ]+\.(?:jpg|jpeg|png|gif|webp))\1', re.IGNORECASE)


def _resolve_served_images(html: str) -> str:
    """Replace served cache-image API URLs with their local filesystem paths for CID embedding."""
    from app.services.care_circle.provider_cache import local_path_for_served_url

    def _replace(m: re.Match) -> str:
        quote, url = m.group(1), m.group(2)
        local = local_path_for_served_url(url)
        return f"src={quote}{local}{quote}" if local else m.group(0)

    return _SRC_SERVED_RE.sub(_replace, html)


async def _download_one(
    client: httpx.AsyncClient, url: str
) -> tuple[str, bytes | None, str | None]:
    try:
        resp = await client.get(url, follow_redirects=True)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "image/jpeg").split(";")[0].strip()
        return url, resp.content, content_type
    except Exception as exc:
        logger.warning("Could not download image %s for embedding: %s", url, exc)
        return url, None, None


def _embed_local_images(html: str) -> tuple[str, list[MIMEImage]]:
    """Embed local file-path image srcs as inline CID attachments."""
    seen: dict[str, None] = {}
    for m in _SRC_LOCAL_RE.finditer(html):
        src = m.group(2)
        if not src.startswith("http"):
            seen[src] = None
    if not seen:
        return html, []

    path_to_cid: dict[str, str] = {}
    parts: list[MIMEImage] = []
    for src in seen:
        p = Path(src)
        if not p.exists():
            continue
        cid = uuid.uuid4().hex
        mime_type, _ = mimetypes.guess_type(src)
        subtype = (mime_type or "image/jpeg").split("/")[-1]
        if subtype.lower() == "jpg":
            subtype = "jpeg"
        part = MIMEImage(p.read_bytes(), _subtype=subtype)
        part["Content-ID"] = f"<{cid}>"
        part["Content-Disposition"] = "inline"
        parts.append(part)
        path_to_cid[src] = cid

    def replace_local(match: re.Match) -> str:
        quote, src = match.group(1), match.group(2)
        return f"src={quote}cid:{path_to_cid[src]}{quote}" if src in path_to_cid else match.group(0)

    return _SRC_LOCAL_RE.sub(replace_local, html), parts


async def _embed_images(html: str) -> tuple[str, list[MIMEImage]]:
    """
    Embed all images — local file paths first, then any remaining remote URLs.
    Local images (from the provider cache) are read directly from disk.
    Remote URLs are downloaded in parallel; failures leave the src unchanged.
    """
    # Local images (already cached to disk by provider_cache.py)
    html, local_parts = _embed_local_images(html)

    # Any remaining remote URLs
    seen: dict[str, None] = {}
    for m in _SRC_REMOTE_RE.finditer(html):
        seen[m.group(2)] = None
    remote_urls = list(seen.keys())

    if not remote_urls:
        return html, local_parts

    from app.services.care_circle.provider_base import WIKIMEDIA_USER_AGENT
    async with httpx.AsyncClient(
        timeout=20.0,
        follow_redirects=True,
        headers={"User-Agent": WIKIMEDIA_USER_AGENT},
    ) as client:
        results = await asyncio.gather(*(_download_one(client, url) for url in remote_urls))

    url_to_cid: dict[str, str] = {}
    remote_parts: list[MIMEImage] = []
    for url, data, content_type in results:
        if data is None:
            continue
        cid = uuid.uuid4().hex
        mime_type, _ = mimetypes.guess_type(url)
        subtype = (mime_type or content_type or "image/jpeg").split("/")[-1]
        if subtype.lower() == "jpg":
            subtype = "jpeg"
        part = MIMEImage(data, _subtype=subtype)
        part["Content-ID"] = f"<{cid}>"
        part["Content-Disposition"] = "inline"
        remote_parts.append(part)
        url_to_cid[url] = cid

    def replace_remote(match: re.Match) -> str:
        quote, url = match.group(1), match.group(2)
        return f"src={quote}cid:{url_to_cid[url]}{quote}" if url in url_to_cid else match.group(0)

    html = _SRC_REMOTE_RE.sub(replace_remote, html)
    return html, local_parts + remote_parts


# ── SMTP send ───────────────────────────────────────────────────────────────────

def _smtp_send_blocking(msg: MIMEMultipart) -> None:
    """Run the blocking SMTP handshake. Called via run_in_executor."""
    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        smtp.send_message(msg)


async def _send_via_smtp(
    to_email: str,
    to_name: str,
    subject: str,
    html_content: str,
    text_content: str,
) -> bool:
    """
    Send a multipart email via the configured IONOS SMTP server.

    All http(s) images in the HTML are downloaded in parallel and embedded as
    inline CID attachments.  The blocking SMTP call is run in a thread executor
    so it does not stall the event loop.
    """
    try:
        html_with_cids, image_parts = await _embed_images(html_content)

        # Structure: multipart/mixed > multipart/related > multipart/alternative
        # This satisfies strict clients while keeping inline images working.
        msg = MIMEMultipart("mixed")
        msg["Subject"] = subject
        msg["From"] = formataddr((settings.FROM_NAME or "Care Circle", settings.FROM_EMAIL or ""))
        msg["To"] = formataddr((to_name, to_email))
        msg["Reply-To"] = settings.FROM_EMAIL or ""
        msg["X-Mailer"] = "Ink & Quill Care Circle"

        related = MIMEMultipart("related")

        alternative = MIMEMultipart("alternative")
        alternative.attach(MIMEText(text_content, "plain", "utf-8"))
        alternative.attach(MIMEText(html_with_cids, "html", "utf-8"))

        related.attach(alternative)
        for image_part in image_parts:
            related.attach(image_part)

        msg.attach(related)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _smtp_send_blocking, msg)

        logger.info(
            "Newsletter email sent to %s (%s) — %d image(s) embedded",
            to_email, subject, len(image_parts),
        )
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
    # Restore local file paths so CID embedding works (web view uses served URLs)
    email_html = _resolve_served_images(newsletter_html)
    html_content = _build_email_html(email_html, subject)
    text_content = _html_to_plain(html_content)

    # Test mode: redirect to the configured test address
    test_mode = getattr(settings, "EMAIL_TEST_MODE", False)
    actual_to = settings.EMAIL_TEST_ADDRESS if test_mode else patient_email

    success = await _send_via_smtp(
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
