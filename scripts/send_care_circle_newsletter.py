r"""Generate Care Circle newsletter artifacts and email one patient.

Examples:
    .\.venv\Scripts\python.exe .\scripts\send_care_circle_newsletter.py
    .\.venv\Scripts\python.exe .\scripts\send_care_circle_newsletter.py --patient-id 20 --date 2026-04-23
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import date
from pathlib import Path
import sys
from typing import Any

from sqlalchemy import select

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.db.database import async_session_local
from app.models.care_circle import CareCirclePatientProfile
from app.services.care_circle.newsletter_delivery_service import deliver_newsletter_to_patient
from app.services.care_circle.newsletter_pdf_service import newsletter_pdf_service
from app.services.care_circle.session_assembler import assemble_daily_patient_session


def parse_reference_date(value: str) -> date:
    """Parse a YYYY-MM-DD reference date for deterministic newsletter generation."""
    try:
        return date.fromisoformat(value.strip())
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Date must be in YYYY-MM-DD format") from exc


def _prompt_patient_id() -> int:
    while True:
        raw_value = input("Patient id: ").strip()
        try:
            patient_id = int(raw_value)
        except ValueError:
            print("Please enter a numeric patient id.")
            continue
        if patient_id > 0:
            return patient_id
        print("Please enter a positive patient id.")


def _prompt_reference_date() -> date:
    default_value = date.today().isoformat()
    while True:
        raw_value = input(f"Reference date [{default_value}]: ").strip() or default_value
        try:
            return parse_reference_date(raw_value)
        except argparse.ArgumentTypeError as exc:
            print(str(exc))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Care Circle newsletter artifacts and email one patient.",
    )
    parser.add_argument(
        "--patient-id",
        type=int,
        help="Care Circle patient id. If omitted, the script prompts for it.",
    )
    parser.add_argument(
        "--date",
        dest="reference_date",
        type=parse_reference_date,
        help="Newsletter reference date in YYYY-MM-DD format. If omitted, the script prompts for it.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Regenerate provider cache before mailing.",
    )
    parser.add_argument(
        "--skip-pdf",
        action="store_true",
        help="Send the email without creating newsletter.html and newsletter.pdf artifacts.",
    )
    return parser


async def generate_and_mail(
    patient_id: int,
    reference_date: date,
    *,
    force_regenerate: bool = False,
    create_artifacts: bool = True,
) -> dict[str, Any]:
    async with async_session_local() as db:
        patient = await db.scalar(
            select(CareCirclePatientProfile).where(CareCirclePatientProfile.id == patient_id)
        )
        if patient is None:
            raise ValueError(f"Patient {patient_id} was not found")

        assembly_result = await assemble_daily_patient_session(
            db,
            patient_id,
            force_regenerate=force_regenerate,
            for_date=reference_date,
        )
        if not assembly_result or not assembly_result.get("success"):
            raise RuntimeError(f"Newsletter assembly failed for patient {patient_id}")

        artifact_result: dict[str, str] | None = None
        if create_artifacts:
            artifact_paths = await newsletter_pdf_service.generate_artifacts_for_patient_date(
                db,
                patient_id,
                reference_date,
            )
            artifact_result = {
                "html_path": str(artifact_paths["html_path"]),
                "pdf_path": str(artifact_paths["pdf_path"]),
            }

        delivery_result = await deliver_newsletter_to_patient(
            db,
            patient,
            reference_date,
            force_regenerate=False,
        )

    return {
        "patient_id": patient_id,
        "reference_date": reference_date.isoformat(),
        "artifacts": artifact_result,
        "delivery": delivery_result,
    }


async def async_main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    patient_id = args.patient_id or _prompt_patient_id()
    reference_date = args.reference_date or _prompt_reference_date()

    result = await generate_and_mail(
        patient_id,
        reference_date,
        force_regenerate=args.force,
        create_artifacts=not args.skip_pdf,
    )
    print(json.dumps(result, indent=2))
    return 0 if result["delivery"].get("success") else 1


def main() -> int:
    return asyncio.run(async_main())


if __name__ == "__main__":
    raise SystemExit(main())
