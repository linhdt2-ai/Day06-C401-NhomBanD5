from app.schemas.chat import ChatRequest
from app.services.orchestrator import ChatOrchestrator


def test_chat_correction_path_reuses_session_context() -> None:
    orchestrator = ChatOrchestrator()
    session_id = "sess_correction"

    first_response = orchestrator.handle_chat(
        ChatRequest(
            session_id=session_id,
            message="Tìm nhà hàng gần đây",
            current_zone="water_world",
            language="vi",
            user_context={"has_child": False},
        )
    )
    second_response = orchestrator.handle_chat(
        ChatRequest(
            session_id=session_id,
            message="đổi sang món cho trẻ em",
            current_zone="water_world",
            language="vi",
            user_context={"has_child": True},
        )
    )

    assert first_response.selected_facility is not None
    assert second_response.type == "success"
    assert second_response.selected_facility is not None
    assert second_response.selected_facility.kid_friendly is True
