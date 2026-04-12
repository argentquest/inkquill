"""
Tests for external provider data files.

These tests validate the structure and content of JSON data files
used by static providers like country_spotlight, famous_face, etc.
"""

import json
from pathlib import Path

import pytest

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class TestCountrySpotlightData:
    """Validate country_spotlight.json structure and content."""

    @pytest.fixture
    def countries(self):
        """Load country data from external JSON file."""
        data_file = DATA_DIR / "country_spotlight.json"
        assert data_file.exists(), f"Data file not found: {data_file}"
        raw = data_file.read_text(encoding="utf-8")
        return json.loads(raw)

    def test_is_list(self, countries):
        assert isinstance(countries, list)

    def test_has_entries(self, countries):
        assert len(countries) > 0, "Country data file should have at least one entry"

    def test_entry_structure(self, countries):
        required_keys = {"country", "flag", "capital", "fun_fact"}
        for i, entry in enumerate(countries):
            assert isinstance(entry, dict), f"Entry {i} is not a dict"
            missing = required_keys - set(entry.keys())
            assert not missing, f"Entry {i} missing keys: {missing}"

    def test_no_empty_values(self, countries):
        for i, entry in enumerate(countries):
            for key in ("country", "flag", "capital", "fun_fact"):
                value = entry.get(key, "")
                assert value, f"Entry {i} has empty value for '{key}'"

    def test_no_duplicate_countries(self, countries):
        names = [entry["country"] for entry in countries]
        duplicates = {name for name in names if names.count(name) > 1}
        assert not duplicates, f"Duplicate countries found: {duplicates}"

    def test_reasonable_count(self, countries):
        """Ensure we have a meaningful number of entries."""
        assert len(countries) >= 10, f"Only {len(countries)} countries — expected at least 10"
