"""
Care Circle Provider Test Runner
Runs every provider for a sample patient, collects rendered HTML,
assembles it into a single-page document, and exports a PDF via Playwright.
"""

from __future__ import annotations

import asyncio
import importlib
import json
import os
import random
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

# ── path setup ─────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("APP_ENV", "development")

SCRIPTS_DIR = Path(__file__).resolve().parent
FRONTENDV1_DIR = ROOT / "frontendv1"

# ── database patient loader ─────────────────────────────────────────────────────
async def _load_active_patients():
    """Fetch all active patients from the database."""
    from app.db.database import async_session_local
    from app.models.care_circle import CareCirclePatientProfile
    from sqlalchemy import select

    async with async_session_local() as db:
        stmt = select(CareCirclePatientProfile).where(
            CareCirclePatientProfile.access_state == "active"
        ).order_by(CareCirclePatientProfile.id)
        result = await db.execute(stmt)
        patients = list(result.scalars().all())

    if not patients:
        print("No active patients found in database.")
        return []

    print(f"Found {len(patients)} active patient(s) in database.")
    return patients


# ── result record ──────────────────────────────────────────────────────────────
@dataclass
class ProviderResult:
    key: str
    label: str
    uses_llm: bool
    status: str   # llm_ok | fallback_internal | fallback_exception | static | load_error
    elapsed_s: float
    model_used: str = ""
    tokens: int = 0
    error: str = ""
    rendered_html: str = ""


# ── LLM tracker ────────────────────────────────────────────────────────────────
class LLMCallTracker:
    def __init__(self):
        self.reset()

    def reset(self):
        self.called = False
        self.succeeded = False
        self.model = ""
        self.tokens = 0
        self.exception = ""


TRACKER = LLMCallTracker()


# ── provider discovery ─────────────────────────────────────────────────────────
PROVIDERS_DIR = ROOT / "app" / "services" / "care_circle" / "providers"

LLM_PROVIDERS = {
    p.parent.name
    for p in PROVIDERS_DIR.glob("*/provider.py")
    if any(
        kw in p.read_text(encoding="utf-8", errors="ignore")
        for kw in ("generate_json_with_usage", "generate_text_with_usage", "generate_image_url_with_usage")
    )
}

_RAW_PROVIDER_KEYS = sorted(p.parent.name for p in PROVIDERS_DIR.glob("*/provider.py"))

# Header and footer are run explicitly (first / last) outside the main loop
LAYOUT_PROVIDERS = {"newsletter_header", "newsletter_footer"}
ALL_PROVIDER_KEYS = [k for k in _RAW_PROVIDER_KEYS if k not in LAYOUT_PROVIDERS]

ROOT_CONFIG = json.loads((PROVIDERS_DIR / "config.json").read_text(encoding="utf-8"))
LABEL_MAP = {p["name"]: p["label"] for p in ROOT_CONFIG.get("providers", [])}
ICON_MAP  = {p["name"]: p.get("icon", "") for p in ROOT_CONFIG.get("providers", [])}


def _to_camel(snake: str) -> str:
    return "".join(w.title() for w in snake.split("_"))



# ── patched LLM helpers ────────────────────────────────────────────────────────
from app.services.care_circle.llm_helpers import LLMResponse


async def _patched_generate_text(prompt, system=None, max_tokens=512, temperature=0.7):
    TRACKER.called = True
    import app.services.care_circle.llm_helpers as _lh
    result: LLMResponse = await _lh.__dict__["_real_generate_text"](
        prompt, system=system, max_tokens=max_tokens, temperature=temperature
    )
    TRACKER.succeeded = True
    TRACKER.model = result.model
    TRACKER.tokens += result.total_tokens
    return result


async def _patched_generate_json(prompt, system=None, max_tokens=1024, temperature=0.7):
    TRACKER.called = True
    import app.services.care_circle.llm_helpers as _lh
    try:
        data, resp = await _lh.__dict__["_real_generate_json"](
            prompt, system=system, max_tokens=max_tokens, temperature=temperature
        )
        TRACKER.succeeded = True
        TRACKER.model = resp.model
        TRACKER.tokens += resp.total_tokens
        return data, resp
    except Exception as exc:
        TRACKER.exception = str(exc)
        raise


async def _patched_generate_image(prompt):
    TRACKER.called = True
    import app.services.care_circle.llm_helpers as _lh
    try:
        result: LLMResponse = await _lh.__dict__["_real_generate_image"](prompt)
        TRACKER.succeeded = True
        TRACKER.model = result.model
        return result
    except Exception as exc:
        TRACKER.exception = str(exc)
        raise


def _install_patches():
    import app.services.care_circle.llm_helpers as lh
    lh.__dict__.setdefault("_real_generate_text", lh.generate_text_with_usage)
    lh.__dict__.setdefault("_real_generate_json", lh.generate_json_with_usage)
    lh.__dict__.setdefault("_real_generate_image", lh.generate_image_url_with_usage)
    lh.generate_text_with_usage = _patched_generate_text
    lh.generate_json_with_usage = _patched_generate_json
    lh.generate_image_url_with_usage = _patched_generate_image


# ── run one provider ───────────────────────────────────────────────────────────
async def run_provider(key: str, patient, patient_config: dict | None = None) -> ProviderResult:
    label = LABEL_MAP.get(key, key)
    uses_llm = key in LLM_PROVIDERS

    module_path = f"app.services.care_circle.providers.{key}.provider"
    if module_path in sys.modules:
        del sys.modules[module_path]

    try:
        module = importlib.import_module(module_path)
    except Exception as exc:
        return ProviderResult(key=key, label=label, uses_llm=uses_llm,
                              status="load_error", elapsed_s=0.0, error=str(exc))

    class_name = _to_camel(key) + "Provider"
    cls = getattr(module, class_name, None)
    if cls is None:
        return ProviderResult(key=key, label=label, uses_llm=uses_llm,
                              status="load_error", elapsed_s=0.0,
                              error=f"Class {class_name} not found")

    TRACKER.reset()
    instance = cls(patient_config=patient_config or {})

    t0 = time.perf_counter()
    try:
        result = await instance.execute(patient)
    except Exception as exc:
        elapsed = time.perf_counter() - t0
        return ProviderResult(key=key, label=label, uses_llm=uses_llm,
                              status="fallback_exception", elapsed_s=elapsed, error=str(exc))
    elapsed = time.perf_counter() - t0

    # Status
    if not result.get("success", True):
        status = "fallback_exception"
        error = result.get("error_detail", "")
    elif uses_llm:
        status = "llm_ok" if (TRACKER.called and TRACKER.succeeded) else "fallback_internal"
    else:
        status = "static"

    # Rendered HTML
    data = result.get("data", {})
    rendered_html = ""
    if isinstance(data, dict):
        rendered_html = (
            data.get("rendered_html") or
            data.get("html") or
            data.get("puzzle_content") or ""
        )

    return ProviderResult(
        key=key, label=label, uses_llm=uses_llm,
        status=status,
        elapsed_s=round(elapsed, 2),
        model_used=TRACKER.model,
        tokens=TRACKER.tokens,
        error=TRACKER.exception,
        rendered_html=rendered_html,
    )


# ── HTML assembly ──────────────────────────────────────────────────────────────
STATUS_COLOR = {
    "llm_ok":             "#22c55e",
    "static":             "#60a5fa",
    "fallback_internal":  "#f97316",
    "fallback_exception": "#ef4444",
    "load_error":         "#7c3aed",
}
STATUS_LABEL = {
    "llm_ok":             "LLM OK",
    "static":             "Static",
    "fallback_internal":  "Fallback (internal)",
    "fallback_exception": "Fallback (exception)",
    "load_error":         "Load Error",
}


def _build_html(results: list[ProviderResult], today: str, patient_name: str,
                header_html: str = "", footer_html: str = "") -> str:
    llm_ok  = sum(1 for r in results if r.status == "llm_ok")
    static  = sum(1 for r in results if r.status == "static")
    fb      = sum(1 for r in results if "fallback" in r.status)
    tokens  = sum(r.tokens for r in results)
    model   = next((r.model_used for r in results if r.model_used), "N/A")

    cards_html = []
    for r in results:
        icon = ICON_MAP.get(r.key, "")
        badge_color = STATUS_COLOR.get(r.status, "#94a3b8")
        badge_text  = STATUS_LABEL.get(r.status, r.status)
        type_tag    = "LLM" if r.uses_llm else "Static"
        type_color  = "#8b5cf6" if r.uses_llm else "#64748b"

        meta_parts = [f"{r.elapsed_s}s"]
        if r.tokens:
            meta_parts.append(f"{r.tokens} tokens")
        if r.model_used:
            meta_parts.append(r.model_used)
        meta = " &nbsp;|&nbsp; ".join(meta_parts)

        if r.rendered_html:
            content_block = f'<div class="provider-content">{r.rendered_html}</div>'
        elif r.error:
            content_block = f'<div class="provider-error">Error: {r.error}</div>'
        else:
            content_block = '<div class="provider-error">No rendered content returned.</div>'

        cards_html.append(f"""
        <div class="provider-card">
          <div class="provider-header">
            <span class="provider-icon">{icon}</span>
            <span class="provider-name">{r.label}</span>
            <span class="provider-key">{r.key}</span>
            <span class="badge" style="background:{badge_color}">{badge_text}</span>
            <span class="badge" style="background:{type_color}">{type_tag}</span>
          </div>
          <div class="provider-meta">{meta}</div>
          {content_block}
        </div>
        """)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Care Circle Provider Test - {today}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: Georgia, serif;
    background: #f1f5f9;
    color: #1e293b;
    padding: 24px;
  }}

  /* ── Report header ── */
  .report-header {{
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
    color: white;
    border-radius: 12px;
    padding: 28px 32px;
    margin-bottom: 24px;
  }}
  .report-header h1 {{ font-size: 24px; margin-bottom: 6px; }}
  .report-header p  {{ font-size: 13px; opacity: 0.75; margin-top: 4px; }}
  .summary-row {{
    display: flex; gap: 16px; margin-top: 18px; flex-wrap: wrap;
  }}
  .summary-pill {{
    background: rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: bold;
  }}

  /* ── Provider cards ── */
  .provider-card {{
    background: white;
    border-radius: 10px;
    margin-bottom: 20px;
    overflow: hidden;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    break-inside: avoid;
    page-break-inside: avoid;
  }}
  .provider-header {{
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 16px;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    flex-wrap: wrap;
  }}
  .provider-icon  {{ font-size: 18px; }}
  .provider-name  {{ font-weight: bold; font-size: 14px; }}
  .provider-key   {{ font-size: 11px; color: #94a3b8; font-family: monospace; }}
  .badge {{
    font-size: 10px;
    font-weight: bold;
    color: white;
    padding: 2px 8px;
    border-radius: 10px;
    margin-left: auto;
  }}
  .badge + .badge {{ margin-left: 4px; }}
  .provider-meta {{
    font-size: 10px;
    color: #94a3b8;
    padding: 4px 16px 6px;
    background: #f8fafc;
    border-bottom: 1px solid #f1f5f9;
  }}

  /* ── Provider rendered content ── */
  .provider-content {{
    padding: 16px;
    font-size: 13px;
  }}
  /* Reset aggressive provider styles so they don't bleed */
  .provider-content * {{ max-width: 100%; }}
  .provider-content img {{ max-width: 100%; height: auto; border-radius: 6px; }}
  .provider-content table {{ width: 100%; border-collapse: collapse; }}
  .provider-content td, .provider-content th {{
    border: 1px solid #e2e8f0;
    padding: 4px 8px;
    font-size: 12px;
  }}

  .provider-error {{
    padding: 16px;
    color: #ef4444;
    font-size: 12px;
    font-style: italic;
  }}

  @media print {{
    body {{ background: white; padding: 0; }}
    .provider-card {{ box-shadow: none; border: 1px solid #e2e8f0; }}
  }}
</style>
</head>
<body>

<div class="report-header">
  <h1>Care Circle Provider Test Report</h1>
  <p>Patient: {patient_name} &nbsp;&bull;&nbsp; {today} &nbsp;&bull;&nbsp; Model: {model}</p>
  <div class="summary-row">
    <span class="summary-pill">Total: {len(results)}</span>
    <span class="summary-pill" style="background:rgba(34,197,94,0.4)">LLM OK: {llm_ok}</span>
    <span class="summary-pill" style="background:rgba(96,165,250,0.4)">Static: {static}</span>
    <span class="summary-pill" style="background:rgba(239,68,68,0.4)">Fallback: {fb}</span>
    <span class="summary-pill">Tokens: {tokens:,}</span>
  </div>
</div>

{header_html}

{"".join(cards_html)}

{footer_html}

</body>
</html>"""


# ── PDF via Playwright (Node.js) ───────────────────────────────────────────────
def generate_pdf_via_playwright(html_path: Path, pdf_path: Path):
    # Script must live inside frontendv1/ so node resolves playwright from node_modules
    js_script = FRONTENDV1_DIR / "html_to_pdf.js"
    result = subprocess.run(
        ["node", str(js_script), str(html_path), str(pdf_path)],
        cwd=str(FRONTENDV1_DIR),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Playwright PDF failed:\n{result.stderr}")
    print(result.stdout.strip())


# ── per-provider HTML file ─────────────────────────────────────────────────────
def save_provider_html(result: ProviderResult, run_ts: str, patient_name: str, out_dir: Path) -> Path | None:
    if not result.rendered_html:
        return None
    safe_name = patient_name.lower().replace(" ", "_")
    filename = f"{run_ts}_{safe_name}_{result.key}.html"
    path = out_dir / filename
    # Wrap with minimal chrome so it's a valid standalone file
    wrapped = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8">
<title>{result.label} - {patient_name}</title>
</head>
<body style="margin:0;padding:16px;font-family:Georgia,serif;">
{result.rendered_html}
</body>
</html>"""
    path.write_text(wrapped, encoding="utf-8")
    return path


# ── main ───────────────────────────────────────────────────────────────────────
async def main():
    from datetime import datetime
    import shutil

    # Clear stale render cache so providers don't return each other's cached HTML
    cache_dir = ROOT / "app" / "logs" / "care_circle_render_cache"
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
        print(f"Cleared render cache: {cache_dir}")

    print("Installing LLM patches...")
    _install_patches()

    # Load patients from database and pick one at random
    patients = await _load_active_patients()
    if not patients:
        print("No patients to process. Exiting.")
        return

    patient = random.choice(patients)
    print(f"Selected patient: {patient.display_name or f'Patient {patient.id}'} (id={patient.id})")

    patient_name = patient.display_name or f"Patient {patient.id}"
    safe_name = patient_name.lower().replace(" ", "_").replace(",", "")

    # One folder per run: logs/<safe_name>_<YYYYMMDD_HHMMSS>/
    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = ROOT / "logs" / f"{safe_name}_{run_ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()

    print(f"\n{'=' * 60}")
    print(f"Running {len(ALL_PROVIDER_KEYS)} providers for {patient_name} (id={patient.id})...")
    print(f"Output folder: {run_dir}")
    print(f"{'=' * 60}\n")

    # ── Run newsletter header first ───────────────────────────────────────
    print(f"  [{'newsletter_header':30}] ", end="", flush=True)
    header_result = await run_provider("newsletter_header", patient)
    print(f"-- {header_result.status:<22} {header_result.elapsed_s:5.2f}s")

    results: list[ProviderResult] = []

    for key in ALL_PROVIDER_KEYS:
        print(f"  [{key:30}] ", end="", flush=True)
        r = await run_provider(key, patient)
        tag = {"llm_ok": "OK", "static": "--", "fallback_internal": "FB",
               "fallback_exception": "XX", "load_error": "ER"}.get(r.status, "?")
        print(f"{tag} {r.status:<22} {r.elapsed_s:5.2f}s  tokens={r.tokens}")

        # Save individual provider HTML
        html_file = save_provider_html(r, run_ts, patient_name, run_dir)
        if html_file:
            print(f"    -> {html_file.name}")

        results.append(r)

    # ── Aggregate stats for footer ────────────────────────────────────────
    total_tokens = sum(r.tokens for r in results)
    total_elapsed = round(sum(r.elapsed_s for r in results), 1)
    llm_ok_count = sum(1 for r in results if r.status == "llm_ok")
    model_used = next((r.model_used for r in results if r.model_used), "")

    print("\n" + "=" * 60)
    print(f"  LLM OK:           {llm_ok_count}")
    print(f"  Static (no LLM):  {sum(1 for r in results if r.status == 'static')}")
    print(f"  Fallback used:    {sum(1 for r in results if 'fallback' in r.status)}")
    print(f"  Load errors:      {sum(1 for r in results if r.status == 'load_error')}")
    print(f"  Total tokens:     {total_tokens:,}")
    print("=" * 60)

    # ── Run newsletter footer last with accumulated stats ─────────────────
    from datetime import datetime as _dt
    footer_config = {
        "total_tokens": total_tokens,
        "total_providers": len(results),
        "llm_providers": llm_ok_count,
        "model_used": model_used,
        "elapsed_s": total_elapsed,
        "generation_date": _dt.now().strftime("%B %d, %Y  \u2022  %I:%M %p"),
    }
    print(f"  [{'newsletter_footer':30}] ", end="", flush=True)
    footer_result = await run_provider("newsletter_footer", patient,
                                       patient_config=footer_config)
    print(f"-- {footer_result.status:<22} {footer_result.elapsed_s:5.2f}s")

    header_html = header_result.rendered_html
    footer_html = footer_result.rendered_html

    # Assembled HTML and PDF both go inside the run folder
    assembled_html_path = run_dir / "assembled.html"
    pdf_path = run_dir / "report.pdf"

    print(f"\nAssembling HTML -> {assembled_html_path}")
    html_content = _build_html(results, today, patient_name,
                               header_html=header_html, footer_html=footer_html)
    assembled_html_path.write_text(html_content, encoding="utf-8")

    print(f"Rendering PDF   -> {pdf_path}")
    try:
        generate_pdf_via_playwright(assembled_html_path, pdf_path)
        print(f"PDF written to {pdf_path}")
    except Exception as e:
        print(f"PDF generation failed for {patient_name}: {e}")

    print(f"\nAll files saved to: {run_dir}")
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
