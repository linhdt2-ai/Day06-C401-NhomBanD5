from app.schemas.chat import ChatRequest
from app.services.orchestrator import ChatOrchestrator


def test_chat_low_confidence_path_returns_clarification() -> None:
    orchestrator = ChatOrchestrator()

    response = orchestrator.handle_chat(
        ChatRequest(
            session_id="sess_low_confidence",
            message="Tìm nhà hàng chay gần đây",
            current_zone="water_world",
            language="vi",
            user_context={"has_child": False},
        )
    )

    assert response.type == "clarification"
    assert response.selected_facility is not None
    assert response.selected_facility.id == "fac_rest_002"
    assert response.navigation is not None
    assert response.navigation.distance_m > 800
