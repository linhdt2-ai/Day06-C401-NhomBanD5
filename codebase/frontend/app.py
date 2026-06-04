"""Streamlit demo UI for the VinWonders rule-based prototype."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from codebase.backend.main import answer_with_rules


API_URL = "http://127.0.0.1:8000/api/chat"
SAMPLE_QUESTIONS = [
    "Toi dang o Ben cang giao thoa, di voi con nho, muon tim cho an gan day, co dieu hoa va khong phai cho lau.",
    "Con toi bi nga o The gioi nuoc, can so cuu gap.",
    "Toi dang o River Safari, muon tim nha hang trong vong 100m.",
    "Toi dang o River Safari, muon mua kem gan nhat cho con.",
    "Toi muon dat khach san o Da Nang toi nay.",
]

def _call_api(message: str, use_llm: bool) -> dict:
    """Call the local FastAPI endpoint."""
    payload = json.dumps({"message": message, "use_llm": use_llm}).encode("utf-8")
    request = Request(
        API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=5) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def _resolve_answer(message: str, use_llm: bool) -> tuple[dict, str]:
    """Prefer FastAPI and fall back to the local rule engine."""
    try:
        result = _call_api(message, use_llm)
        return result, "api"
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError):
        return answer_with_rules(message, use_llm=use_llm), "local_fallback"


def _candidate_rows(candidates: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for candidate in candidates:
        rows.append(
            {
                "name": candidate.get("name"),
                "category": candidate.get("category"),
                "zone": candidate.get("zone"),
                "status": candidate.get("status"),
                "distance_m": candidate.get("distance_from_current_zone"),
                "wait_min": candidate.get("estimated_wait_minutes"),
                "crowd_level": candidate.get("crowd_level"),
                "score": candidate.get("score"),
            }
        )
    return rows


def _selected_place_card(place: dict | None) -> None:
    if not place:
        st.info("Chua co dia diem duoc chon.")
        return

    st.subheader("Selected place")
    col1, col2 = st.columns(2)
    distance = place.get("distance_from_current_zone")
    wait_minutes = place.get("estimated_wait_minutes")
    crowd_level = place.get("crowd_level", "-")
    with col1:
        st.metric("Name", place.get("name", "-"))
        st.metric("Category", place.get("category", "-"))
        st.metric("Zone", place.get("zone", "-"))
    with col2:
        st.metric("Status", place.get("status", "-"))
        st.metric(
            "Distance",
            f"{distance} m" if isinstance(distance, int) else "Khong ro",
        )
        st.metric(
            "Wait / Crowd",
            (
                f"{wait_minutes} phut / {crowd_level}"
                if isinstance(wait_minutes, int)
                else f"Khong ro / {crowd_level}"
            ),
        )


def main() -> None:
    """Render the local demo UI."""
    st.set_page_config(
        page_title="AI Assistant tai VinWonders Nam Hoi An",
        layout="wide",
    )

    st.title("AI Assistant tai VinWonders Nam Hoi An")
    st.caption(
        "Prototype dung mock data va rule-based engine, chua dung LLM."
    )

    if "question_input" not in st.session_state:
        st.session_state["question_input"] = SAMPLE_QUESTIONS[0]

    selected_sample = st.selectbox(
        "Cau hoi mau",
        options=["Chon cau hoi mau..."] + SAMPLE_QUESTIONS,
        index=0,
    )
    if selected_sample != "Chon cau hoi mau...":
        st.session_state["question_input"] = selected_sample

    question = st.text_area(
        "Nhap cau hoi",
        key="question_input",
        height=120,
        placeholder="Vi du: Toi dang o Ben cang giao thoa, muon tim cho an gan day...",
    )
    use_llm = st.checkbox(
        "Dung LLM de viet cau tra loi tu nhien hon",
        value=True,
    )

    send_clicked = st.button("Gui cau hoi", type="primary", use_container_width=True)
    if not send_clicked:
        return

    if not question.strip():
        st.warning("Vui long nhap cau hoi truoc khi gui.")
        return

    result, source = _resolve_answer(question.strip(), use_llm)

    st.subheader("Cau tra loi")
    st.write(result["final_answer"])

    if source == "api":
        st.success("UI dang goi FastAPI endpoint.")
    else:
        st.info("API chua san sang. UI dang fallback sang local rule engine.")

    meta_col1, meta_col2, meta_col3 = st.columns(3)
    meta_col1.metric("Confidence", result.get("confidence", "-"))
    meta_col2.metric(
        "Fallback used", "Yes" if result.get("fallback_used") else "No"
    )
    meta_col3.metric("LLM used", "Yes" if result.get("llm_used") else "No")

    if result.get("fallback_used"):
        st.warning(result.get("fallback_reason") or "Dang dung fallback.")
    if result.get("llm_error"):
        st.warning(result.get("llm_error"))

    _selected_place_card(result.get("selected_place"))

    st.subheader("Top candidates")
    st.dataframe(
        _candidate_rows(result.get("top_candidates", [])),
        use_container_width=True,
    )

    with st.expander("Debug trace"):
        st.json(result.get("debug_trace", {}))

    with st.expander("Rule-based draft"):
        st.write(result.get("answer_draft", ""))

    if result.get("warnings"):
        with st.expander("Warnings"):
            st.write(result["warnings"])


if __name__ == "__main__":
    main()
