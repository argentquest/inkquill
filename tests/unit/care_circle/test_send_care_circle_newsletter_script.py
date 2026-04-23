from __future__ import annotations

import argparse
from datetime import date

import pytest

from scripts.send_care_circle_newsletter import build_parser, parse_reference_date


def test_parse_reference_date_accepts_iso_date():
    assert parse_reference_date("2026-04-23") == date(2026, 4, 23)


def test_parse_reference_date_rejects_non_iso_date():
    with pytest.raises(argparse.ArgumentTypeError):
        parse_reference_date("04/23/2026")


def test_parser_accepts_patient_date_and_force_flags():
    args = build_parser().parse_args(
        ["--patient-id", "20", "--date", "2026-04-23", "--force", "--skip-pdf"]
    )

    assert args.patient_id == 20
    assert args.reference_date == date(2026, 4, 23)
    assert args.force is True
    assert args.skip_pdf is True
