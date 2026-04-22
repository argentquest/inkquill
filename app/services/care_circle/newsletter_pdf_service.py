"""Generate Care Circle newsletter artifacts from cached daily provider output."""

import asyncio
import json
import logging
import re
from datetime import date
from html import escape
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.care_circle import CareCirclePatientProfile, CareCircleProviderCatalog
from app.services.care_circle import provider_cache
from app.services.care_circle.session_assembler import (
    _provider_sort_order,
    get_newsletter_html_for_date,
)

logger = logging.getLogger(__name__)

_IMG_SRC_RE = re.compile(r'src=(["\'])([^"\']+)\1', re.IGNORECASE)


class CareCircleNewsletterPDFService:
    """Build newsletter artifacts from cached provider output."""

    def __init__(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        self.frontend_root = repo_root / "frontendv1"
        self.playwright_script = self.frontend_root / "scripts" / "render_newsletter_pdf.js"

    async def generate_for_patient_date(
        self,
        db: AsyncSession,
        patient_id: int,
        for_date: date,
    ) -> Path:
        patient = await db.get(CareCirclePatientProfile, patient_id)
        if patient is None:
            raise ValueError(f"Patient {patient_id} not found")

        artifacts = await self.generate_artifacts_for_patient_date(db, patient_id, for_date)
        return artifacts["pdf_path"]

    async def generate_artifacts_for_patient_date(
        self,
        db: AsyncSession,
        patient_id: int,
        for_date: date,
    ) -> dict[str, Path]:
        patient = await db.get(CareCirclePatientProfile, patient_id)
        if patient is None:
            raise ValueError(f"Patient {patient_id} not found")

        cache_dir = provider_cache.CACHE_ROOT / str(patient_id) / for_date.isoformat()
        cache_dir.mkdir(parents=True, exist_ok=True)
        pdf_path = cache_dir / "newsletter.pdf"
        html_path = cache_dir / "newsletter.html"

        newsletter_html = await get_newsletter_html_for_date(db, patient_id, for_date)
        if not newsletter_html:
            raise ValueError(
                f"No assembled newsletter HTML found for patient {patient_id} on {for_date.isoformat()}"
            )

        html_document = self._build_html_document(
            patient,
            for_date,
            self._rewrite_cached_image_urls_for_local_html(newsletter_html),
        )
        html_path.write_text(html_document, encoding="utf-8")

        await self._render_pdf_with_playwright(html_path, pdf_path)
        logger.info(
            "Generated Care Circle newsletter artifacts for patient %s at %s and %s",
            patient_id,
            pdf_path,
            html_path,
        )
        return {
            "pdf_path": pdf_path,
            "html_path": html_path,
        }

    def _build_html_document(
        self,
        patient: CareCirclePatientProfile,
        for_date: date,
        newsletter_html: str,
    ) -> str:
        title = escape(self._safe_text(f"Care Circle Newsletter for {patient.display_name}"))
        generated_date = escape(for_date.strftime("%B %d, %Y"))
        return (
            "<!DOCTYPE html>\n"
            "<html lang=\"en\">\n"
            "<head>\n"
            "  <meta charset=\"utf-8\">\n"
            f"  <title>{title}</title>\n"
            "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            "</head>\n"
            "<body>\n"
            f"<!-- Generated for patient {patient.id} on {generated_date} -->\n"
            f"{newsletter_html}\n"
            "</body>\n"
            "</html>\n"
        )

    def _rewrite_cached_image_urls_for_local_html(self, html: str) -> str:
        def _replace(match: re.Match) -> str:
            quote = match.group(1)
            url = match.group(2)
            local_path = provider_cache.local_path_for_served_url(url)
            if local_path is None:
                return match.group(0)
            return f"src={quote}{escape(local_path.name, quote=False)}{quote}"

        return _IMG_SRC_RE.sub(_replace, html)

    async def _render_pdf_with_playwright(self, html_path: Path, pdf_path: Path) -> None:
        if not self.playwright_script.exists():
            raise FileNotFoundError(
                f"Playwright render script not found at {self.playwright_script}"
            )

        process = await asyncio.create_subprocess_exec(
            "node",
            str(self.playwright_script),
            str(html_path),
            str(pdf_path),
            cwd=str(self.frontend_root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await process.communicate()
        if process.returncode != 0:
            raise RuntimeError(
                "Playwright newsletter PDF render failed: "
                + (stderr.decode("utf-8", errors="ignore") or stdout.decode("utf-8", errors="ignore")).strip()
            )
        if not pdf_path.exists():
            raise RuntimeError("Playwright finished without creating newsletter.pdf")

    def _safe_text(self, text: str) -> str:
        return text.encode("latin-1", "ignore").decode("latin-1")


newsletter_pdf_service = CareCircleNewsletterPDFService()
