from app.schemas.chat import ChatRequest
from app.services.orchestrator import ChatOrchestrator


def test_chat_happy_path_returns_success() -> None:
    orchestrator = ChatOrchestrator()

    response = orchestrator.handle_chat(
        ChatRequest(
            session_id="sess_happy",
            message="Có nhà hàng nào gần đây cho trẻ em không?",
            current_zone="water_world",
            language="vi",
            user_context={"has_child": True},
        )
    )

    assert response.type == "success"
    assert response.selected_facility is not None
    assert response.selected_facility.id == "fac_rest_008"
    assert response.navigation is not None
    assert response.navigation.distance_m == 60
