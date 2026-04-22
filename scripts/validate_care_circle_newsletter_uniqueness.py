"""Generate Care Circle newsletters for multiple days and report duplicate outputs.

This script runs the real session assembly path for active patients (or a subset),
stores the next N days of cache, and then compares provider JSON payloads across
days for each patient. Providers with identical normalized output are flagged in
the report.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
import sys
from typing import Any

from sqlalchemy import select

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.db.database import async_session_local
from app.models.care_circle import CareCirclePatientProfile
from app.services.care_circle.provider_cache import CACHE_ROOT
from app.services.care_circle.session_assembler import assemble_daily_patient_session

LAYOUT_PROVIDER_KEYS = {"newsletter_header", "newsletter_footer"}
VOLATILE_DATA_KEYS = {
    "rendered_html",
    "generated_at",
    "generation_date",
    "elapsed_s",
    "total_tokens",
    "total_providers",
    "llm_providers",
    "model_used",
}


@dataclass
class DuplicateFinding:
    patient_id: int
    patient_name: str
    provider_key: str
    dates: list[str]


def _normalize_value(value: Any) -> Any:
    if isinstance(value, dict):
        return _normalize_payload(value)
    if isinstance(value, list):
        return [_normalize_value(item) for item in value]
    if isinstance(value, str):
        if value.startswith("/api/v1/care-circle/cached-image/"):
            parts = value.split("/")
            if len(parts) >= 8:
                return "/".join(parts[:6] + ["<date>", parts[-1]])
        return value
    return value


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized: dict[str, Any] = {}
    for key, value in payload.items():
        if key in VOLATILE_DATA_KEYS:
            continue
        if key.endswith("_remote"):
            base_key = key[:-7]
            normalized[base_key] = _normalize_value(value)
            continue
        if f"{key}_remote" in payload:
            continue
        normalized[key] = _normalize_value(value)
    return normalized


def _load_normalized_provider_payload(
    patient_id: int,
    for_date: date,
    provider_key: str,
) -> dict[str, Any] | None:
    path = CACHE_ROOT / str(patient_id) / for_date.isoformat() / f"{provider_key}.json"
    if not path.exists():
        return None
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    data = raw.get("data")
    if not isinstance(data, dict):
        return None
    return _normalize_payload(data)


async def _fetch_patients(patient_ids: list[int] | None) -> list[CareCirclePatientProfile]:
    async with async_session_local() as db:
        query = select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.access_state == "active"
        ).order_by(CareCirclePatientProfile.id.asc())
        if patient_ids:
            query = query.where(CareCirclePatientProfile.id.in_(patient_ids))
        rows = (await db.execute(query)).scalars().all()
        return list(rows)


async def _generate_for_days(
    patients: list[CareCirclePatientProfile],
    target_dates: list[date],
    force_regenerate: bool,
) -> dict[int, dict[str, Any]]:
    results: dict[int, dict[str, Any]] = {}
    for target_date in target_dates:
        print(f"Generating Care Circle sessions for {target_date.isoformat()}...")
        for patient in patients:
            async with async_session_local() as db:
                result = await assemble_daily_patient_session(
                    db,
                    patient.id,
                    force_regenerate=force_regenerate,
                    for_date=target_date,
                )
            results.setdefault(patient.id, {})[target_date.isoformat()] = result
            status = "ok" if result and result.get("success") else "failed"
            print(f"  patient {patient.id:>3} {patient.display_name:<30} {status}")
    return results


def _find_duplicate_outputs(
    patients: list[CareCirclePatientProfile],
    target_dates: list[date],
) -> list[DuplicateFinding]:
    findings: list[DuplicateFinding] = []

    for patient in patients:
        by_provider: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
        for target_date in target_dates:
            day_dir = CACHE_ROOT / str(patient.id) / target_date.isoformat()
            if not day_dir.exists():
                continue
            for json_file in sorted(day_dir.glob("*.json")):
                provider_key = json_file.stem
                if provider_key in LAYOUT_PROVIDER_KEYS:
                    continue
                payload = _load_normalized_provider_payload(patient.id, target_date, provider_key)
                if payload is None:
                    continue
                signature = json.dumps(payload, ensure_ascii=False, sort_keys=True)
                by_provider[provider_key][signature].append(target_date.isoformat())

        for provider_key, signature_map in sorted(by_provider.items()):
            for dates_with_same_output in signature_map.values():
                if len(dates_with_same_output) > 1:
                    findings.append(
                        DuplicateFinding(
                            patient_id=patient.id,
                            patient_name=patient.display_name,
                            provider_key=provider_key,
                            dates=sorted(dates_with_same_output),
                        )
                    )

    findings.sort(key=lambda item: (item.patient_id, item.provider_key, item.dates))
    return findings


def _build_report(
    patients: list[CareCirclePatientProfile],
    target_dates: list[date],
    findings: list[DuplicateFinding],
) -> str:
    lines = [
        "# Care Circle Newsletter Uniqueness Report",
        "",
        f"- Patients checked: {len(patients)}",
        f"- Dates checked: {', '.join(day.isoformat() for day in target_dates)}",
        f"- Duplicate findings: {len(findings)}",
        "- Comparison method: normalized provider `data` payloads only",
        "- Ignored for comparison: `newsletter_header`, `newsletter_footer`, cache metadata, rendered HTML, token/runtime/footer stats, and date-stamped local image URLs",
        "",
    ]

    if not findings:
        lines.append("## Result")
        lines.append("")
        lines.append("No duplicate provider outputs were found across the checked days.")
        return "\n".join(lines) + "\n"

    current_patient_id: int | None = None
    for finding in findings:
        if finding.patient_id != current_patient_id:
            if current_patient_id is not None:
                lines.append("")
            lines.append(f"## Patient {finding.patient_id} - {finding.patient_name}")
            lines.append("")
            current_patient_id = finding.patient_id
        joined_dates = ", ".join(finding.dates)
        lines.append(f"- `{finding.provider_key}` produced the same normalized output on: {joined_dates}")

    return "\n".join(lines) + "\n"


async def _run(args: argparse.Namespace) -> int:
    start_date = date.fromisoformat(args.start_date) if args.start_date else date.today()
    target_dates = [start_date + timedelta(days=offset) for offset in range(args.days)]
    patients = await _fetch_patients(args.patient_id)

    if not patients:
        print("No matching active patients were found.")
        return 1

    await _generate_for_days(
        patients=patients,
        target_dates=target_dates,
        force_regenerate=not args.reuse_cache,
    )
    findings = _find_duplicate_outputs(patients, target_dates)
    report = _build_report(patients, target_dates, findings)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(report, encoding="utf-8")
    print()
    print(f"Report written to {args.report}")
    print(f"Duplicate findings: {len(findings)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Care Circle newsletters for several days and report duplicate provider output."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=3,
        help="Number of consecutive days to generate, starting from --start-date.",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Start date in YYYY-MM-DD format. Defaults to today.",
    )
    parser.add_argument(
        "--patient-id",
        type=int,
        action="append",
        default=None,
        help="Optional patient id filter. Repeat to validate more than one patient.",
    )
    parser.add_argument(
        "--reuse-cache",
        action="store_true",
        help="Reuse existing cache instead of forcing regeneration.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("artifacts") / "care_circle_uniqueness_report.md",
        help="Where to write the markdown report.",
    )
    args = parser.parse_args()
    return asyncio.run(_run(args))


if __name__ == "__main__":
    raise SystemExit(main())
