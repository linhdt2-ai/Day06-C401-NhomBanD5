import json
from pathlib import Path


def test_all_facilities_have_coordinates() -> None:
    facilities = json.loads(
        Path("app/data/facilities.json").read_text(encoding="utf-8")
    )

    for facility in facilities:
        assert facility.get("lat") is not None, facility["id"]
        assert facility.get("lng") is not None, facility["id"]


def test_representative_sheet_coordinates_are_synced() -> None:
    facilities = {
        item["id"]: item
        for item in json.loads(Path("app/data/facilities.json").read_text(encoding="utf-8"))
    }

    assert facilities["fac_rest_001"]["lat"] == 15.788222656362159
    assert facilities["fac_rest_001"]["lng"] == 108.41128974411366
    assert facilities["fac_rest_001"]["zone_id"] == "adventure_land"
    assert facilities["fac_rest_008"]["lat"] == 15.788204
    assert facilities["fac_rest_008"]["lng"] == 108.407826
    assert facilities["fac_rest_008"]["zone_id"] == "water_world"
    assert facilities["fac_ticket_001"]["lat"] == 15.786262
    assert facilities["fac_ticket_001"]["lng"] == 108.407787
