"""
Test runner for the mini Care Circle newsletter.

Usage:
    # Run for all active patients (sends real emails unless EMAIL_TEST_MODE=true)
    python scripts/test_mini_newsletter.py

    # Run for a specific patient ID only
    python scripts/test_mini_newsletter.py --patient 4

    # Preview the assembled HTML in a browser without sending
    python scripts/test_mini_newsletter.py --preview

    # Preview for a specific patient
    python scripts/test_mini_newsletter.py --patient 4 --preview

    # Send email with all providers (not just 5)
    python scripts/test_mini_newsletter.py --patient 4 --send
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("APP_ENV", "development")


async def _load_patients(patient_id: int | None):
    from app.db.database import async_session_local
    from app.models.care_circle import CareCirclePatientProfile
    from sqlalchemy import select

    async with async_session_local() as db:
        stmt = select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.access_state == "active"
        )
        if patient_id:
            stmt = stmt.where(CareCirclePatientProfile.id == patient_id)
        patients = (await db.execute(stmt)).scalars().all()

    return list(patients)


async def run_preview(patient, today: date):
    """Build the newsletter HTML and open it in the default browser."""
    import webbrowser
    import tempfile
    from app.scheduler.tasks.care_circle_mini_newsletter import _build_mini_newsletter, _load_cached_html
    from app.services.care_circle.newsletter_email_service import _build_email_html, _build_subject

    print(f"\n  Building preview for {patient.display_name} (id={patient.id})...")

    # Show all assigned providers for this patient
    cached = _load_cached_html(patient.id, today)
    if cached:
        print(f"\n  Assigned providers ({len(cached)} total):")
        for key, _ in sorted(cached):
            print(f"    - {key}")
        print()

    body_html = await _build_mini_newsletter(patient, today, limit=None)

    if not body_html.strip():
        print("  ✗  No content — is the cache populated for today?")
        print(f"     Expected cache dir: cache/{patient.id}/{today.isoformat()}/")
        return

    subject = _build_subject(
        patient.display_name,
        getattr(patient, "family_name", None),
    )
    full_html = _build_email_html(body_html, subject)

    out_path = ROOT / "logs" / f"mini_newsletter_preview_patient{patient.id}.html"
    out_path.parent.mkdir(exist_ok=True)
    out_path.write_text(full_html, encoding="utf-8")

    print(f"  OK  Preview written -> {out_path}")
    webbrowser.open(out_path.as_uri())


async def run_send(patient, today: date, all_providers: bool = False):
    """Send the mini newsletter for one patient."""
    from app.scheduler.tasks.care_circle_mini_newsletter import _build_mini_newsletter
    from app.services.care_circle.newsletter_email_service import send_newsletter_email, _build_email_html, _build_subject

    print(f"\n  Sending to {patient.display_name} (id={patient.id}, email={patient.email})...")

    if not getattr(patient, "email", None):
        print(f"  --  Skipped -- no email address")
        return {"patient_id": patient.id, "status": "skipped", "reason": "no email address"}

    body_html = await _build_mini_newsletter(patient, today, limit=None if all_providers else 5)
    if not body_html.strip():
        print(f"  --  Skipped -- no content available")
        return {"patient_id": patient.id, "status": "skipped", "reason": "no content available"}

    subject = _build_subject(
        patient.display_name,
        getattr(patient, "family_name", None),
    )
    full_html = _build_email_html(body_html, subject)

    result = await send_newsletter_email(patient, body_html)
    status = "sent" if result.get("success") else "failed"
    if status == "sent":
        print(f"  OK  Sent  -- {result}")
    else:
        print(f"  FAIL  Failed -- {result}")
    return {"patient_id": patient.id, "status": status, "email_result": result}


async def main(patient_id: int | None, preview: bool, send: bool):
    today = date.today()
    if preview:
        mode = "PREVIEW (no email)"
    elif send:
        mode = "SEND (all providers)"
    else:
        mode = "SEND (5 providers)"
    print(f"Mini Newsletter Test — {today.isoformat()}")
    print(f"Mode: {mode}")

    patients = await _load_patients(patient_id)
    if not patients:
        print("No active patients found." + (f" (patient_id={patient_id})" if patient_id else ""))
        return

    print(f"Patients: {[p.display_name for p in patients]}\n")

    for patient in patients:
        if preview:
            await run_preview(patient, today)
        else:
            await run_send(patient, today, all_providers=send)

    print("\nDone.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--patient", type=int, default=None, help="Patient ID (default: all active)")
    parser.add_argument("--preview", action="store_true", help="Write HTML to file and open in browser instead of sending")
    parser.add_argument("--send", action="store_true", help="Send email with all providers instead of just 5")
    args = parser.parse_args()
    asyncio.run(main(args.patient, args.preview, args.send))
