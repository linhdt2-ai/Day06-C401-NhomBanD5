from app.schemas.chat import ChatRequest
from app.services.orchestrator import ChatOrchestrator


def test_chat_failure_path_returns_fallback() -> None:
    orchestrator = ChatOrchestrator()

    response = orchestrator.handle_chat(
        ChatRequest(
            session_id="sess_failure",
            message="Tìm quán lẩu băng chuyền Hàn Quốc ít cay có khu chơi trẻ em",
            current_zone="water_world",
            language="vi",
            user_context={"has_child": True},
        )
    )

    assert response.type == "fallback"
    assert response.selected_facility is None
    assert len(response.alternatives) == 3
