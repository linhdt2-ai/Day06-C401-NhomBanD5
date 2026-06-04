"""LLM helpers for rewriting the final answer without changing rule decisions."""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


LLM_TIMEOUT_SECONDS = 30
_ENV_LOADED = False


def load_local_env() -> None:
    """
    Load local .env for development if available.
    Must not crash if .env or python-dotenv is missing.
    """
    global _ENV_LOADED
    if _ENV_LOADED:
        return

    _ENV_LOADED = True

    root_dir = Path(__file__).resolve().parents[2]
    candidate_paths = [
        root_dir / ".env",
        root_dir / "codebase" / ".env",
    ]
    env_path = next((path for path in candidate_paths if path.exists()), None)
    if env_path is None:
        return

    try:
        from dotenv import load_dotenv  # type: ignore
    except ImportError:
        return

    try:
        load_dotenv(dotenv_path=env_path, override=False)
    except Exception:
        return


def is_llm_enabled() -> bool:
    """Return True only when provider, model, and matching API key are present."""
    load_local_env()
    provider = (os.getenv("LLM_PROVIDER") or "none").strip().lower()
    model = (os.getenv("LLM_MODEL") or "").strip()
    if provider in {"", "none"} or not model:
        return False

    if provider == "gemini":
        return bool((os.getenv("GEMINI_API_KEY") or "").strip())
    if provider == "openrouter":
        return bool((os.getenv("OPENROUTER_API_KEY") or "").strip())
    return False


def build_response_prompt(rule_result: dict) -> str:
    """Build a tightly grounded prompt from the rule-based result."""
    selected_place = rule_result.get("selected_place") or {}
    constraints = (rule_result.get("debug_trace") or {}).get("constraints", {})
    prompt_lines = [
        "Ban la AI Assistant tai VinWonders Nam Hoi An.",
        "Chi duoc viet lai cau tra loi tu nhien hon dua tren context ben duoi.",
        "Khong duoc tao dia diem moi.",
        "Khong duoc sua khoang cach, status, wait time, crowd level, zone, huong di.",
        "Khong duoc thay doi selected_place do backend da quyet dinh.",
        "Neu fallback_used = true thi phai noi ro khong co ket qua khop hoan toan.",
        "Neu confidence = low thi phai tra loi than trong va nhac nguoi dung kiem tra voi nhan vien neu can.",
        "Neu need_type = medical hoac urgency = urgent thi phai tra loi ngan, ro, uu tien hanh dong nhanh.",
        "",
        "Context:",
        f"- original_message: {rule_result.get('message')}",
        f"- need_type: {rule_result.get('need_type')}",
        f"- current_zone: {rule_result.get('current_zone')}",
        f"- confidence: {rule_result.get('confidence')}",
        f"- fallback_used: {rule_result.get('fallback_used')}",
        f"- fallback_reason: {rule_result.get('fallback_reason')}",
        f"- urgency: {constraints.get('urgency')}",
        f"- selected_place_name: {selected_place.get('name')}",
        f"- selected_place_category: {selected_place.get('category')}",
        f"- selected_place_zone: {selected_place.get('zone')}",
        f"- selected_place_status: {selected_place.get('status')}",
        f"- selected_place_distance_m: {selected_place.get('distance_from_current_zone')}",
        f"- selected_place_wait_minutes: {selected_place.get('estimated_wait_minutes')}",
        f"- selected_place_crowd_level: {selected_place.get('crowd_level')}",
        f"- selected_place_reasons: {selected_place.get('score_reasons')}",
        f"- answer_draft: {rule_result.get('answer_draft')}",
        "",
        "Hay viet mot cau tra loi cuoi cung bang tieng Viet, ngan gon, de hanh dong, va trung thanh 100% voi context.",
    ]
    return "\n".join(prompt_lines)


def _call_gemini(prompt: str, model: str, api_key: str) -> str | None:
    endpoint = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 300,
        },
    }
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=LLM_TIMEOUT_SECONDS) as response:
        body = response.read().decode("utf-8")
    data = json.loads(body)
    candidates = data.get("candidates", [])
    if not candidates:
        return None
    parts = (((candidates[0] or {}).get("content") or {}).get("parts") or [])
    texts = [part.get("text", "").strip() for part in parts if isinstance(part, dict)]
    final_text = "\n".join(text for text in texts if text).strip()
    return final_text or None


def _call_openrouter(prompt: str, model: str, api_key: str) -> str | None:
    endpoint = "https://openrouter.ai/api/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.2,
        "max_tokens": 300,
    }
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with urlopen(request, timeout=LLM_TIMEOUT_SECONDS) as response:
        body = response.read().decode("utf-8")
    data = json.loads(body)
    choices = data.get("choices", [])
    if not choices:
        return None
    message = (choices[0] or {}).get("message") or {}
    content = message.get("content")
    return content.strip() if isinstance(content, str) and content.strip() else None


def generate_llm_answer(rule_result: dict) -> str | None:
    """Generate a natural-language answer or return None on any configuration/API issue."""
    load_local_env()
    provider = (os.getenv("LLM_PROVIDER") or "none").strip().lower()
    model = (os.getenv("LLM_MODEL") or "").strip()
    if provider in {"", "none"} or not model:
        return None

    prompt = build_response_prompt(rule_result)

    try:
        if provider == "gemini":
            api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
            if not api_key:
                return None
            return _call_gemini(prompt, model, api_key)

        if provider == "openrouter":
            api_key = (os.getenv("OPENROUTER_API_KEY") or "").strip()
            if not api_key:
                return None
            return _call_openrouter(prompt, model, api_key)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError, ValueError):
        return None

    return None
