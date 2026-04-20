from app.services.care_circle.location_service import _extract_locality, _extract_region, _format_city


def test_location_service_extracts_locality_and_region():
    address = {
        "city": "Montreal",
        "state": "Quebec",
    }

    assert _extract_locality(address) == "Montreal"
    assert _extract_region(address) == "Quebec"
    assert _format_city("Montreal", "Quebec") == "Montreal, Quebec"


def test_location_service_handles_sparse_address():
    address = {
        "village": "Hudson",
    }

    assert _extract_locality(address) == "Hudson"
    assert _extract_region(address) is None
    assert _format_city("Hudson", None) == "Hudson"
