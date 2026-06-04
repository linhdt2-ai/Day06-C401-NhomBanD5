"""Rule-based ranking for candidate VinWonders facilities."""

from __future__ import annotations

from .retriever import normalize_text


def _distance_from_zone(facility: dict, current_zone: str | None) -> int | None:
    if not current_zone:
        return None

    distance_map = facility.get("distance_from_zone_meters", {})
    if not isinstance(distance_map, dict):
        return None

    distance = distance_map.get(current_zone)
    return distance if isinstance(distance, int) else None


def _wants_kid_friendly(normalized_message: str) -> bool:
    return any(keyword in normalized_message for keyword in ("con nho", "tre em", "be", "gia dinh"))


def _wants_cool_place(normalized_message: str) -> bool:
    return any(keyword in normalized_message for keyword in ("nong", "mat", "dieu hoa", "trong nha"))


def _wants_low_wait(normalized_message: str) -> bool:
    return any(
        keyword in normalized_message
        for keyword in ("khong phai cho", "it cho", "khong dong", "dung qua dong", "cho lau", "cho it")
    )


def _normalized_blob(facility: dict) -> str:
    parts = [
        str(facility.get("name", "")),
        str(facility.get("category", "")),
        str(facility.get("description", "")),
    ]
    tags = facility.get("tags", [])
    if isinstance(tags, list):
        parts.extend(str(tag) for tag in tags)
    return normalize_text(" ".join(parts))


def _match_tags_in_blob(blob: str, tags: list[str]) -> list[str]:
    return [tag for tag in tags if normalize_text(tag) and normalize_text(tag) in blob]


def _evaluate_hard_constraints(
    facility: dict,
    need_type: str,
    current_zone: str | None,
    constraints: dict | None,
) -> list[str]:
    constraints = constraints or {}
    violations: list[str] = []

    if facility.get("status") == "closed":
        violations.append("closed")

    distance = _distance_from_zone(facility, current_zone)
    max_distance = constraints.get("max_distance_meters")
    if (
        current_zone
        and isinstance(distance, int)
        and isinstance(max_distance, int)
        and distance > max_distance
    ):
        violations.append(f"distance>{max_distance}m")

    if need_type == "medical" or constraints.get("urgency") == "urgent":
        if facility.get("category") != "medical":
            violations.append("not_medical")

    blob = _normalized_blob(facility)
    excluded = constraints.get("exclude_tags", [])
    if isinstance(excluded, list):
        matched_excludes = _match_tags_in_blob(blob, excluded)
        if matched_excludes:
            violations.append("exclude_tags:" + ",".join(matched_excludes))

    return violations


def score_facility(
    facility: dict,
    need_type: str,
    current_zone: str | None,
    message: str,
    constraints: dict | None = None,
) -> tuple[int, list[str]]:
    """Score a facility and collect short reasoning strings."""
    normalized_message = normalize_text(message)
    constraints = constraints or {}
    score = 0
    reasons: list[str] = []
    tags = facility.get("tags", [])
    tags = tags if isinstance(tags, list) else []
    blob = _normalized_blob(facility)

    if facility.get("category") == need_type:
        score += 40
        reasons.append("Dung category nhu cau")

    if current_zone and facility.get("zone") == current_zone:
        score += 25
        reasons.append("Cung zone hien tai")

    distance = _distance_from_zone(facility, current_zone)
    if distance is not None:
        if distance <= 300:
            score += 20
            reasons.append("Gan, <= 300m")
        elif distance <= 600:
            score += 15
            reasons.append("Tuong doi gan, <= 600m")
        elif distance > 800:
            score -= 15
            reasons.append("Kha xa, > 800m")

    max_distance = constraints.get("max_distance_meters")
    if (
        current_zone
        and isinstance(distance, int)
        and isinstance(max_distance, int)
        and distance > max_distance
    ):
        score -= 45
        reasons.append(f"Vuot gioi han {max_distance}m")

    wants_children = constraints.get("has_children") or _wants_kid_friendly(
        normalized_message
    )
    if wants_children and any(
        tag in tags for tag in ("kids", "family", "family_with_children")
    ):
        score += 10
        reasons.append("Phu hop tre nho/gia dinh")

    wants_cool_place = constraints.get("need_air_conditioner") or _wants_cool_place(
        normalized_message
    )
    if wants_cool_place and any(
        tag in tags for tag in ("air_conditioner", "indoor", "hot_weather")
    ):
        score += 10
        reasons.append("Phu hop nhu cau mat/trong nha")

    wait_minutes = facility.get("estimated_wait_minutes")
    if isinstance(wait_minutes, int) and wait_minutes <= 10:
        score += 10
        reasons.append("Thoi gian cho thap")
    if constraints.get("prefer_short_wait") and isinstance(wait_minutes, int):
        if wait_minutes <= 10:
            score += 10
            reasons.append("Hop voi uu tien cho ngan")
        elif wait_minutes > 15:
            score -= 15
            reasons.append("Cho lau hon mong muon")

    if facility.get("status") == "closed":
        score -= 30
        reasons.append("Dang dong cua")

    crowd_level = facility.get("crowd_level")
    wants_less_crowd = constraints.get("avoid_crowded") or _wants_low_wait(
        normalized_message
    )
    if crowd_level == "high" and wants_less_crowd:
        score -= 20
        reasons.append("Dong trong khi nguoi dung muon it cho/khong dong")
    elif crowd_level == "low" and constraints.get("avoid_crowded"):
        score += 8
        reasons.append("It dong")

    preferred_tags = constraints.get("preferred_tags", [])
    if isinstance(preferred_tags, list):
        matched_preferred = _match_tags_in_blob(blob, preferred_tags)
        if matched_preferred:
            score += 20
            reasons.append(
                "Khop so thich: " + ", ".join(matched_preferred[:2])
            )

    excluded_tags = constraints.get("exclude_tags", [])
    if isinstance(excluded_tags, list):
        matched_excluded = _match_tags_in_blob(blob, excluded_tags)
        if matched_excluded:
            score -= 35
            reasons.append(
                "Vi pham loai tru: " + ", ".join(matched_excluded[:2])
            )

    if need_type == "medical" or constraints.get("urgency") == "urgent":
        if facility.get("category") == "medical":
            score += 35
            reasons.append("Uu tien y te khan cap")
            if facility.get("status") == "open":
                score += 20
                reasons.append("Dang mo")
            if isinstance(distance, int) and distance <= 300:
                score += 20
                reasons.append("Gan cho xu ly gap")
        else:
            score -= 80
            reasons.append("Khong phai diem y te")

    return score, reasons


def rank_candidates(
    candidates: list[dict],
    need_type: str,
    current_zone: str | None,
    message: str,
    top_k: int = 3,
    constraints: dict | None = None,
) -> list[dict]:
    """Rank facilities and keep open places above closed ones whenever possible."""
    ranked: list[dict] = []
    for facility in candidates:
        score, reasons = score_facility(
            facility,
            need_type,
            current_zone,
            message,
            constraints=constraints,
        )
        enriched = dict(facility)
        enriched["score"] = score
        enriched["score_reasons"] = reasons
        enriched["distance_from_current_zone"] = _distance_from_zone(
            facility, current_zone
        )
        enriched["hard_constraint_violations"] = _evaluate_hard_constraints(
            facility,
            need_type,
            current_zone,
            constraints,
        )
        enriched["matches_all_constraints"] = not enriched[
            "hard_constraint_violations"
        ]
        ranked.append(enriched)

    ranked.sort(
        key=lambda item: (
            item.get("status") == "closed",
            -item.get("score", 0),
            item.get("distance_from_current_zone")
            if item.get("distance_from_current_zone") is not None
            else 10**9,
            item.get("name", ""),
        )
    )
    return ranked[:top_k]


def estimate_confidence(
    ranked_results: list[dict],
    need_type: str,
    current_zone: str | None,
    constraints: dict | None = None,
) -> str:
    """Estimate answer confidence from the ranked results."""
    constraints = constraints or {}
    if need_type in {"unknown", "out_of_scope"} or not ranked_results:
        return "low"

    top_result = ranked_results[0]
    if top_result.get("status") == "closed":
        return "low"

    if top_result.get("category") != need_type:
        return "low"

    distance = top_result.get("distance_from_current_zone")
    crowd_level = top_result.get("crowd_level")
    wait_minutes = top_result.get("estimated_wait_minutes")
    if top_result.get("hard_constraint_violations"):
        return "low"

    if current_zone and isinstance(distance, int) and distance > 800:
        return "low"

    if (
        current_zone
        and isinstance(distance, int)
        and distance <= 300
        and crowd_level != "high"
        and isinstance(wait_minutes, int)
        and wait_minutes <= 10
    ):
        return "high"

    if constraints.get("avoid_crowded") and crowd_level == "high":
        return "low"

    return "medium"
