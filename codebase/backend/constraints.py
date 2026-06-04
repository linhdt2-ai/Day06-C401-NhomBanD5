"""Simple rule-based parsing of user constraints from Vietnamese messages."""

from __future__ import annotations

import re

from .retriever import normalize_text


PREFERRED_TAG_PATTERNS = {
    "mon nhat": ["japanese_food", "japanese", "mon nhat"],
    "do han": ["korean_food", "han quoc", "do han"],
    "cafe": ["cafe"],
    "an nhe": ["snack", "an nhe"],
    "kem": ["ice_cream", "kem"],
}

EXCLUDE_TAG_PATTERNS = {
    "khong hai san": ["seafood", "hai san"],
    "khong cay": ["spicy_options", "cay"],
    "khong muon an do cay": ["spicy_options", "cay"],
    "khong an do cay": ["spicy_options", "cay"],
    "khong ngoai troi": ["outdoor", "ngoai troi"],
}


def _contains(text: str, keyword: str) -> bool:
    pattern = r"(?<!\w)" + re.escape(keyword) + r"(?!\w)"
    return re.search(pattern, text) is not None


def _extract_distance(normalized_message: str) -> int | None:
    patterns = [
        r"trong vong\s+(\d+)\s*m",
        r"duoi\s+(\d+)\s*m",
        r"khong qua\s+(\d+)\s*m",
    ]
    for pattern in patterns:
        match = re.search(pattern, normalized_message)
        if match:
            return int(match.group(1))

    if _contains(normalized_message, "gan nhat"):
        return 200
    if _contains(normalized_message, "gan day"):
        return 300
    return None


def _collect_tags(normalized_message: str, mapping: dict[str, list[str]]) -> list[str]:
    collected: list[str] = []
    for trigger, tags in mapping.items():
        if _contains(normalized_message, trigger):
            for tag in tags:
                if tag not in collected:
                    collected.append(tag)
    return collected


def parse_constraints(message: str) -> dict:
    """Parse simple structured constraints from a Vietnamese user message."""
    normalized_message = normalize_text(message)

    return {
        "max_distance_meters": _extract_distance(normalized_message),
        "prefer_short_wait": any(
            _contains(normalized_message, keyword)
            for keyword in ("khong phai cho lau", "it cho", "nhanh", "an nhanh")
        ),
        "avoid_crowded": any(
            _contains(normalized_message, keyword)
            for keyword in ("khong dong", "dung qua dong", "it nguoi")
        ),
        "has_children": any(
            _contains(normalized_message, keyword)
            for keyword in (
                "con nho",
                "tre nho",
                "di voi con",
                "gia dinh",
                "cho con",
                "cho be",
            )
        ),
        "need_air_conditioner": any(
            _contains(normalized_message, keyword)
            for keyword in ("dieu hoa", "mat", "trong nha", "troi nong")
        ),
        "exclude_tags": _collect_tags(normalized_message, EXCLUDE_TAG_PATTERNS),
        "preferred_tags": _collect_tags(normalized_message, PREFERRED_TAG_PATTERNS),
        "urgency": (
            "urgent"
            if any(
                _contains(normalized_message, keyword)
                for keyword in ("gap", "khan cap", "nga", "dau", "so cuu")
            )
            else "normal"
        ),
    }
