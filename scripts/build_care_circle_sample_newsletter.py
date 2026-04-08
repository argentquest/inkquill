"""Build a sample Care Circle newsletter HTML snapshot from rendered provider cards."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import sys

from sqlalchemy import select

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.db.database import async_session_local
from app.models.care_circle import (
    CareCircleFamily,
    CareCirclePatientContentCard,
    CareCirclePatientProfile,
)
from app.services.care_circle.session_assembler import assemble_daily_patient_session


def _slugify(value: str) -> str:
    cleaned = "".join(ch.lower() if ch.isalnum() else "-" for ch in value)
    return "-".join(part for part in cleaned.split("-") if part)


def _build_document(patient: CareCirclePatientProfile, family: CareCircleFamily | None, cards: list[CareCirclePatientContentCard]) -> str:
    sections: list[str] = []
    for card in cards:
        rendered_html = (card.rendered_html or "").strip()
        if not rendered_html:
            rendered_html = (
                f"<section class='newsletter-card fallback-card'>"
                f"<h2>{card.title}</h2><p>{card.body}</p></section>"
            )
        sections.append(f"<article class='newsletter-card-wrapper'>{rendered_html}</article>")

    body_html = "\n".join(sections)
    family_name = family.name if family else "Care Circle"
    join_code = family.join_code if family else ""
    delivery_time = patient.delivery_time or "Not scheduled"
    delivery_days = ", ".join(patient.delivery_days or []) or "Daily"
    preferences = patient.preferences or {}
    preference_tags = preferences.get("preference_tags", [])
    family_members = preferences.get("family_members", [])

    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <title>Care Circle Sample Newsletter</title>
    <style>
      @page {{
        size: Letter;
        margin: 0.5in;
      }}
      body {{
        margin: 0;
        font-family: Georgia, "Times New Roman", serif;
        background: #f4efe4;
        color: #1f2937;
      }}
      .page {{
        max-width: 8in;
        margin: 0 auto;
        background: white;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
      }}
      .cover {{
        padding: 32px 36px 24px;
        border-bottom: 1px solid #e5e7eb;
        background: linear-gradient(135deg, #fff7ed 0%, #fef3c7 100%);
      }}
      .eyebrow {{
        margin: 0 0 8px;
        font-size: 11px;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: #92400e;
      }}
      h1 {{
        margin: 0;
        font-size: 34px;
        line-height: 1.1;
      }}
      .meta {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px 18px;
        margin-top: 18px;
        font-size: 13px;
      }}
      .meta strong {{
        display: block;
        font-size: 11px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #6b7280;
      }}
      .summary {{
        padding: 20px 36px 8px;
        font-size: 14px;
        color: #374151;
      }}
      .summary p {{
        margin: 0 0 10px;
      }}
      .cards {{
        padding: 8px 24px 28px;
      }}
      .newsletter-card-wrapper {{
        break-inside: avoid;
        page-break-inside: avoid;
        margin: 0 0 18px;
      }}
      .fallback-card {{
        border: 1px solid #d1d5db;
        border-radius: 18px;
        padding: 16px 18px;
      }}
    </style>
  </head>
  <body>
    <main class="page">
      <header class="cover">
        <p class="eyebrow">Care Circle Sample Newsletter</p>
        <h1>{patient.display_name}</h1>
        <div class="meta">
          <div><strong>Family</strong>{family_name}</div>
          <div><strong>Join Code</strong>{join_code}</div>
          <div><strong>Timezone</strong>{patient.timezone}</div>
          <div><strong>Delivery</strong>{delivery_time}</div>
          <div><strong>Delivery Days</strong>{delivery_days}</div>
          <div><strong>Providers Rendered</strong>{len(cards)}</div>
        </div>
      </header>
      <section class="summary">
        <p><strong>Family circle:</strong> {", ".join(family_members) if family_members else "Not set"}</p>
        <p><strong>Preference tags:</strong> {", ".join(preference_tags) if preference_tags else "Not set"}</p>
      </section>
      <section class="cards">
        {body_html}
      </section>
    </main>
  </body>
</html>
"""


async def _run(patient_id: int | None, output_dir: Path) -> tuple[Path, int, str]:
    async with async_session_local() as db:
        patient: CareCirclePatientProfile | None
        if patient_id is None:
            patient = await db.scalar(
                select(CareCirclePatientProfile)
                .where(CareCirclePatientProfile.access_state == "active")
                .order_by(CareCirclePatientProfile.id.asc())
            )
        else:
            patient = await db.get(CareCirclePatientProfile, patient_id)

        if patient is None:
            raise RuntimeError("No Care Circle patient profile was found for the requested export.")

        await assemble_daily_patient_session(db, patient.id)

        cards = (
            await db.execute(
                select(CareCirclePatientContentCard)
                .where(
                    CareCirclePatientContentCard.patient_id == patient.id,
                    CareCirclePatientContentCard.is_active.is_(True),
                )
                .order_by(CareCirclePatientContentCard.display_order.asc(), CareCirclePatientContentCard.id.asc())
            )
        ).scalars().all()
        family = await db.get(CareCircleFamily, patient.family_id)

        if not cards:
            raise RuntimeError("No rendered Care Circle cards were available after session assembly.")

        output_dir.mkdir(parents=True, exist_ok=True)
        slug = _slugify(patient.display_name) or f"patient-{patient.id}"
        html_path = output_dir / f"care-circle-sample-newsletter-{slug}.html"
        html_path.write_text(_build_document(patient, family, cards), encoding="utf-8")
        return html_path, len(cards), patient.display_name


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a sample Care Circle newsletter HTML snapshot.")
    parser.add_argument("--patient-id", type=int, default=None, help="Patient id to export. Defaults to first active patient.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts"),
        help="Directory where the newsletter HTML will be written.",
    )
    args = parser.parse_args()

    html_path, card_count, patient_name = asyncio.run(_run(args.patient_id, args.output_dir))
    print(f"Built sample newsletter HTML for {patient_name} with {card_count} provider cards.")
    print(html_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
