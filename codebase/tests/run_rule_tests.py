"""Run simple rule-based smoke tests for the VinWonders prototype."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from codebase.backend.main import answer_with_rules


TEST_CASES = [
    (
        "TC01",
        "Toi dang o Ben cang giao thoa, di voi con nho, muon tim cho an gan day, co dieu hoa va khong phai cho lau.",
    ),
    (
        "TC02",
        "Toi muon an mon nhe, cho nao cung duoc nhung dung qua dong.",
    ),
    (
        "TC03",
        "Toi dang o River Safari, muon tim nha hang Nhat trong vong 100m.",
    ),
    (
        "TC04",
        "Khong, toi muon tim nha ve sinh gan nhat chu khong phai nha hang.",
    ),
    (
        "TC05",
        "Con toi bi nga o The gioi nuoc, can so cuu gap.",
    ),
    (
        "TC06",
        "Toi dang o River Safari, muon mua kem gan nhat cho con.",
    ),
    (
        "TC07",
        "Toi muon dat khach san o Da Nang toi nay.",
    ),
    (
        "TC08",
        "Toi dang o River Safari, muon tim nha hang trong vong 100m.",
    ),
    (
        "TC09",
        "Toi dang o Ben cang giao thoa, muon an nhanh, khong dong, co dieu hoa.",
    ),
    (
        "TC10",
        "Toi di voi con nho, khong muon an do cay.",
    ),
    (
        "TC11",
        "Toi dang o River Safari, muon mua kem gan nhat cho con.",
    ),
    (
        "TC12",
        "Con toi bi nga o The gioi nuoc, can so cuu gap.",
    ),
]


def main() -> None:
    """Print smoke-test results for the rule-based prototype."""
    for test_id, message in TEST_CASES:
        result = answer_with_rules(message)
        selected_place = result["selected_place"]
        selected_name = selected_place.get("name") if selected_place else None

        print(f"=== {test_id} ===")
        print(f"input: {message}")
        print(f"need_type: {result['need_type']}")
        print(f"current_zone: {result['current_zone']}")
        print(f"confidence: {result['confidence']}")
        print(f"selected_place: {selected_name}")
        print(f"fallback_used: {result['fallback_used']}")
        print(f"fallback_reason: {result['fallback_reason']}")
        print(f"debug_trace: {result['debug_trace']}")
        print(f"answer_draft: {result['answer_draft']}")
        print()


if __name__ == "__main__":
    main()
