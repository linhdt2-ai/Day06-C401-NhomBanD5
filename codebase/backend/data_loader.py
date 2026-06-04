"""Utilities for loading and validating the mock database."""

from __future__ import annotations

import json
from pathlib import Path


REQUIRED_FACILITY_FIELDS = {
    "id",
    "name",
    "category",
    "zone",
    "tags",
    "status",
    "distance_from_zone_meters",
}


def load_mock_database(path: str) -> dict:
    """Load the UTF-8 mock database JSON from disk."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Mock database file not found: {file_path}")

    try:
        with file_path.open("r", encoding="utf-8") as file:
            database = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in mock database '{file_path}': {error.msg} "
            f"(line {error.lineno}, column {error.colno})"
        ) from error

    if not isinstance(database, dict):
        raise ValueError(
            f"Mock database root must be a JSON object: {file_path}"
        )
    return database


def get_facilities(database: dict) -> list[dict]:
    """Return facilities as a list if present, otherwise an empty list."""
    facilities = database.get("facilities", [])
    return facilities if isinstance(facilities, list) else []


def get_zones(database: dict) -> list[dict]:
    """Return zones as a list if present, otherwise an empty list."""
    zones = database.get("zones", [])
    return zones if isinstance(zones, list) else []


def validate_mock_database(database: dict) -> list[str]:
    """Return non-fatal validation warnings for the current mock database."""
    warnings: list[str] = []

    if not isinstance(database.get("metadata"), dict):
        warnings.append("Missing or invalid 'metadata' object.")

    zones = database.get("zones")
    if not isinstance(zones, list):
        warnings.append("Missing or invalid 'zones' list.")
        zones = []

    facilities = database.get("facilities")
    if not isinstance(facilities, list):
        warnings.append("Missing or invalid 'facilities' list.")
        facilities = []

    zone_names: set[str] = set()
    for index, zone in enumerate(zones):
        if not isinstance(zone, dict):
            warnings.append(f"Zone at index {index} is not an object.")
            continue

        zone_id = zone.get("id")
        zone_name = zone.get("name")
        if not zone_id:
            warnings.append(f"Zone at index {index} is missing 'id'.")
        if not zone_name:
            warnings.append(f"Zone at index {index} is missing 'name'.")
        elif isinstance(zone_name, str):
            zone_names.add(zone_name)

        aliases = zone.get("aliases", [])
        if "aliases" in zone and not isinstance(aliases, list):
            warnings.append(
                f"Zone '{zone_name or zone_id or index}' has invalid 'aliases'; expected list."
            )

    for index, facility in enumerate(facilities):
        if not isinstance(facility, dict):
            warnings.append(f"Facility at index {index} is not an object.")
            continue

        missing = sorted(
            field for field in REQUIRED_FACILITY_FIELDS if field not in facility
        )
        if missing:
            warnings.append(
                f"Facility '{facility.get('id', index)}' missing required fields: "
                + ", ".join(missing)
            )

        facility_id = facility.get("id", index)
        zone_name = facility.get("zone")
        if zone_name is not None and not isinstance(zone_name, str):
            warnings.append(
                f"Facility '{facility_id}' has invalid 'zone'; expected string."
            )
        elif zone_names and isinstance(zone_name, str) and zone_name not in zone_names:
            warnings.append(
                f"Facility '{facility_id}' references unknown zone '{zone_name}'."
            )

        tags = facility.get("tags")
        if tags is not None and not isinstance(tags, list):
            warnings.append(
                f"Facility '{facility_id}' has invalid 'tags'; expected list."
            )

        distance_map = facility.get("distance_from_zone_meters")
        if distance_map is not None and not isinstance(distance_map, dict):
            warnings.append(
                f"Facility '{facility_id}' has invalid 'distance_from_zone_meters'; expected object."
            )

        status = facility.get("status")
        if status is not None and status not in {"open", "closed"}:
            warnings.append(
                f"Facility '{facility_id}' has unexpected status '{status}'."
            )

    return warnings
