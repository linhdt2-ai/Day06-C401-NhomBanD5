"""Rule-based retrieval helpers for the VinWonders mock database."""

from __future__ import annotations

import re
import unicodedata


NEED_TYPE_KEYWORDS = {
    "restaurant": ["an", "nha hang", "com", "do an", "an trua"],
    "drink": ["nuoc", "cafe", "ca phe", "do uong", "snack", "kem"],
    "restroom": ["ve sinh", "toilet", "wc"],
    "medical": ["y te", "so cuu", "dau", "nga", "chan thuong", "khan cap"],
    "rest_area": ["nghi", "ghe", "bong mat", "met"],
    "kids_activity": ["tre em", "con nho", "vui choi trong nha"],
    "out_of_scope": ["khach san", "ve may bay", "dat phong"],
}


def _contains_keyword(normalized_text: str, keyword: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
    return re.search(pattern, normalized_text) is not None


def normalize_text(text: str) -> str:
    """Normalize Vietnamese text for simple keyword matching."""
    if not text:
        return ""

    normalized = unicodedata.normalize("NFD", text.casefold())
    without_diacritics = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )
    without_diacritics = without_diacritics.replace("đ", "d")
    return re.sub(r"\s+", " ", without_diacritics).strip()


def infer_need_type(message: str) -> str:
    """Infer the user's need type from Vietnamese keywords."""
    normalized_message = normalize_text(message)
    if not normalized_message:
        return "unknown"

    priority = [
        "out_of_scope",
        "medical",
        "restroom",
        "restaurant",
        "drink",
        "rest_area",
        "kids_activity",
    ]
    matched_scores = {need_type: 0 for need_type in NEED_TYPE_KEYWORDS}

    for need_type, keywords in NEED_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if _contains_keyword(normalized_message, keyword):
                matched_scores[need_type] += 1

    best_need_type = "unknown"
    best_score = 0
    for need_type in priority:
        score = matched_scores.get(need_type, 0)
        if score > best_score:
            best_need_type = need_type
            best_score = score

    if best_score > 0:
        return best_need_type
    return "unknown"


def infer_current_zone(message: str, zones: list[dict]) -> str | None:
    """Infer the current zone from zone names and aliases in the message."""
    normalized_message = normalize_text(message)
    if not normalized_message:
        return None

    best_match: tuple[int, str] | None = None
    for zone in zones:
        zone_name = zone.get("name")
        if not isinstance(zone_name, str):
            continue

        candidates = [zone_name]
        aliases = zone.get("aliases", [])
        if isinstance(aliases, list):
            candidates.extend(alias for alias in aliases if isinstance(alias, str))

        for candidate in candidates:
            normalized_candidate = normalize_text(candidate)
            if normalized_candidate and normalized_candidate in normalized_message:
                match_length = len(normalized_candidate)
                if best_match is None or match_length > best_match[0]:
                    best_match = (match_length, zone_name)

    return best_match[1] if best_match else None


def retrieve_candidates(message: str, database: dict) -> dict:
    """Retrieve candidate facilities based on inferred need type and zone."""
    zones = database.get("zones", [])
    facilities = database.get("facilities", [])

    need_type = infer_need_type(message)
    current_zone = infer_current_zone(message, zones if isinstance(zones, list) else [])

    candidates: list[dict] = []
    if isinstance(facilities, list) and need_type not in {"unknown", "out_of_scope"}:
        candidates = [
            facility
            for facility in facilities
            if isinstance(facility, dict) and facility.get("category") == need_type
        ]

    return {
        "message": message,
        "need_type": need_type,
        "current_zone": current_zone,
        "candidates": candidates,
    }
