from app.schemas.chat import ChatRequest
from app.services.orchestrator import ChatOrchestrator


def test_emergency_fast_track_returns_first_aid() -> None:
    orchestrator = ChatOrchestrator()

    response = orchestrator.handle_chat(
        ChatRequest(
            session_id="sess_emergency",
            message="Bé bị đứt tay cần sơ cứu",
            current_zone="water_world",
            language="vi",
            user_context={"has_child": True},
        )
    )

    assert response.type == "fast_track"
    assert response.navigation is not None
    assert response.reason_summary == "emergency_keyword_detected"
