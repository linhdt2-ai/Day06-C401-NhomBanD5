"""Rule-based backend entrypoint for the VinWonders prototype."""

from __future__ import annotations

import os

from .ai_service import generate_llm_answer, is_llm_enabled
from .constraints import parse_constraints
from .data_loader import (
    load_mock_database,
    validate_mock_database,
)
from .ranking import estimate_confidence, rank_candidates
from .retriever import retrieve_candidates


def _has_exact_matches(ranked_candidates: list[dict]) -> bool:
    return any(candidate.get("matches_all_constraints") for candidate in ranked_candidates)


def _build_fallback_reason(
    need_type: str,
    current_zone: str | None,
    constraints: dict,
    selected_place: dict | None,
    top_candidates: list[dict],
) -> str | None:
    if need_type in {"unknown", "out_of_scope"}:
        return None

    if not top_candidates:
        return "no_candidates_found"

    if _has_exact_matches(top_candidates):
        return None

    max_distance = constraints.get("max_distance_meters")
    preferred_tags = constraints.get("preferred_tags", [])
    if isinstance(max_distance, int) and current_zone:
        return (
            f"Khong co dia diem khop day du trong gioi han {max_distance}m "
            f"tu {current_zone}."
        )

    if preferred_tags:
        return (
            "Khong co dia diem khop hoan toan voi cac so thich/tag uu tien: "
            + ", ".join(preferred_tags)
            + "."
        )

    if selected_place and selected_place.get("hard_constraint_violations"):
        return (
            "Dia diem goi y gan nhat van vi pham mot so rang buoc: "
            + ", ".join(selected_place["hard_constraint_violations"])
            + "."
        )

    return "Khong co ket qua khop hoan toan; dang dung phuong an gan/phu hop nhat."


def _build_answer_draft(
    message: str,
    need_type: str,
    current_zone: str | None,
    confidence: str,
    selected_place: dict | None,
    top_candidates: list[dict],
    constraints: dict,
    fallback_used: bool,
    fallback_reason: str | None,
) -> str:
    if need_type == "out_of_scope":
        return (
            "Yeu cau nay dang nam ngoai pham vi prototype VinWonders Nam Hoi An. "
            "Minh hien chi ho tro tim diem an uong, ve sinh, so cuu, cho nghi "
            "va khu vui choi cho tre trong cong vien."
        )

    if need_type == "unknown":
        return (
            "Minh chua xac dinh ro nhu cau tu cau hoi nay. "
            "Ban co the noi ro hon ban muon tim cho an, do uong, nha ve sinh, "
            "so cuu, cho nghi hay khu cho tre em khong?"
        )

    if not selected_place:
        return (
            f"Minh chua tim thay diem phu hop cho nhu cau '{need_type}'"
            + (f" gan khu {current_zone}" if current_zone else "")
            + " trong mock data hien tai."
        )

    place_name = selected_place.get("name", "dia diem phu hop")
    distance = selected_place.get("distance_from_current_zone")
    wait_minutes = selected_place.get("estimated_wait_minutes")
    directions = None
    if current_zone:
        direction_map = selected_place.get("direction_hint_from_zone", {})
        if isinstance(direction_map, dict):
            directions = direction_map.get(current_zone)

    reasons = selected_place.get("score_reasons", [])
    reason_text = ", ".join(reasons[:3]) if reasons else "co muc do phu hop tot"
    max_distance = constraints.get("max_distance_meters")

    if fallback_used and top_candidates:
        alternatives = ", ".join(
            candidate.get("name", "dia diem khac") for candidate in top_candidates[:3]
        )
        if isinstance(max_distance, int) and current_zone:
            return (
                f"Hien chua co dia diem khop hoan toan trong vong {max_distance}m "
                f"tu {current_zone} trong du lieu mock. Goi y gan/phu hop nhat hien co "
                f"la {place_name}"
                + (f", cach khoang {distance}m" if isinstance(distance, int) else "")
                + f", nhung dia diem nay khong khop hoan toan yeu cau ban dau. "
                + (f"Ly do fallback: {fallback_reason} " if fallback_reason else "")
                + f"Ban co the xem them: {alternatives}."
            )
        return (
            f"Minh chua co ket qua that chac. Tam thoi uu tien {place_name}"
            + (f" cach khoang {distance}m" if isinstance(distance, int) else "")
            + f" vi {reason_text}. "
            + (f"Ly do fallback: {fallback_reason} " if fallback_reason else "")
            + f"Ban co the xem them cac lua chon: {alternatives}."
        )

    answer = f"De xuat uu tien la {place_name}"
    if isinstance(distance, int):
        answer += f", cach ban khoang {distance}m"
    answer += f", vi {reason_text}."

    if isinstance(wait_minutes, int):
        answer += f" Thoi gian cho uoc tinh: {wait_minutes} phut."
    if directions:
        answer += f" Huong di goi y: {directions}"
    return answer


def answer_with_rules(
    message: str,
    data_path: str = "codebase/data/mock_database.json",
    use_llm: bool = True,
) -> dict:
    """Load data, retrieve, rank, and return a rule-based answer draft."""
    database = load_mock_database(data_path)
    warnings = validate_mock_database(database)
    constraints = parse_constraints(message)

    retrieved = retrieve_candidates(message, database)
    need_type = retrieved["need_type"]
    current_zone = retrieved["current_zone"]
    ranked = rank_candidates(
        retrieved["candidates"],
        need_type=need_type,
        current_zone=current_zone,
        message=message,
        top_k=3,
        constraints=constraints,
    )
    confidence = estimate_confidence(
        ranked,
        need_type,
        current_zone,
        constraints=constraints,
    )
    selected_place = ranked[0] if ranked else None
    fallback_reason = _build_fallback_reason(
        need_type=need_type,
        current_zone=current_zone,
        constraints=constraints,
        selected_place=selected_place,
        top_candidates=ranked,
    )
    fallback_used = fallback_reason is not None
    answer_draft = _build_answer_draft(
        message=message,
        need_type=need_type,
        current_zone=current_zone,
        confidence=confidence,
        selected_place=selected_place,
        top_candidates=ranked,
        constraints=constraints,
        fallback_used=fallback_used,
        fallback_reason=fallback_reason,
    )

    result = {
        "message": message,
        "need_type": need_type,
        "current_zone": current_zone,
        "confidence": confidence,
        "selected_place": selected_place,
        "top_candidates": ranked,
        "fallback_used": fallback_used,
        "fallback_reason": fallback_reason,
        "warnings": warnings,
        "debug_trace": {
            "inferred_need_type": need_type,
            "inferred_current_zone": current_zone,
            "constraints": constraints,
            "candidate_count": len(retrieved["candidates"]),
            "ranked_count": len(ranked),
        },
        "answer_draft": answer_draft,
    }

    llm_used = False
    llm_error = ""
    final_answer = answer_draft
    if use_llm:
        if is_llm_enabled():
            llm_answer = generate_llm_answer(result)
            if llm_answer:
                final_answer = llm_answer
                llm_used = True
            else:
                llm_error = "LLM khong tra ve ket qua hop le hoac bi loi API."
        else:
            provider = (os.getenv("LLM_PROVIDER") or "none").strip().lower()
            if provider not in {"", "none"}:
                llm_error = "LLM chua duoc cau hinh day du (provider/model/api key)."
    else:
        llm_error = ""

    result["final_answer"] = final_answer
    result["llm_used"] = llm_used
    result["llm_error"] = llm_error
    return result
