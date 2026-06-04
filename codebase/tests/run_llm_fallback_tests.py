"""Simple checks for LLM fallback behavior."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from codebase.backend.main import answer_with_rules


TEST_MESSAGE = (
    "Toi dang o Ben cang giao thoa, di voi con nho, muon tim cho an gan day, "
    "co dieu hoa va khong phai cho lau."
)


def _set_env(provider: str | None, model: str | None, gemini_key: str | None) -> None:
    if provider is None:
        os.environ.pop("LLM_PROVIDER", None)
    else:
        os.environ["LLM_PROVIDER"] = provider

    if model is None:
        os.environ.pop("LLM_MODEL", None)
    else:
        os.environ["LLM_MODEL"] = model

    if gemini_key is None:
        os.environ.pop("GEMINI_API_KEY", None)
    else:
        os.environ["GEMINI_API_KEY"] = gemini_key

    os.environ.pop("OPENROUTER_API_KEY", None)


def _print_case(case_id: str, passed: bool, note: str) -> None:
    status = "PASS" if passed else "FAIL"
    print(f"{case_id}: {status} - {note}")


def main() -> None:
    original_env = {
        key: os.environ.get(key)
        for key in (
            "LLM_PROVIDER",
            "LLM_MODEL",
            "GEMINI_API_KEY",
            "OPENROUTER_API_KEY",
        )
    }
    try:
        _set_env("none", None, None)
        result_none = answer_with_rules(TEST_MESSAGE)
        _print_case(
            "LLM00",
            isinstance(result_none, dict) and "answer_draft" in result_none,
            "Co hoac khong co .env thi app van khong crash",
        )
        _print_case(
            "LLM01",
            result_none["final_answer"] == result_none["answer_draft"]
            and not result_none["llm_used"],
            "LLM_PROVIDER=none thi final_answer fallback ve answer_draft",
        )

        _set_env("gemini", "gemini-test-model", None)
        result_missing_key = answer_with_rules(TEST_MESSAGE)
        _print_case(
            "LLM02",
            result_missing_key["final_answer"] == result_missing_key["answer_draft"]
            and not result_missing_key["llm_used"]
            and bool(result_missing_key["llm_error"]),
            "Thieu API key thi he thong khong crash va fallback an toan",
        )

        _set_env("gemini", "gemini-test-model", "dummy-key")
        result_llm_off = answer_with_rules(TEST_MESSAGE, use_llm=False)
        _print_case(
            "LLM03",
            result_llm_off["final_answer"] == result_llm_off["answer_draft"]
            and not result_llm_off["llm_used"]
            and result_llm_off["llm_error"] == "",
            "use_llm=false thi bo qua LLM",
        )

        _print_case(
            "LLM04",
            all(
                field in result_llm_off
                for field in ("selected_place", "confidence", "fallback_used")
            ),
            "Cac field rule-based van duoc giu lai",
        )

        _print_case(
            "LLM05",
            result_none["final_answer"] == result_none["answer_draft"],
            "Khi LLM khong san sang thi final_answer van bang answer_draft",
        )
    finally:
        for key, value in original_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


if __name__ == "__main__":
    main()
