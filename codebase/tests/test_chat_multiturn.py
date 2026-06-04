from app.schemas.chat import ChatRequest
from app.services.orchestrator import ChatOrchestrator


def test_chat_new_question_uses_new_intent_not_previous_turn() -> None:
    orchestrator = ChatOrchestrator()
    session_id = "sess_multiturn"

    first_response = orchestrator.handle_chat(
        ChatRequest(
            session_id=session_id,
            message="Có nhà hàng nào gần đây cho trẻ em không?",
            current_zone="water_world",
            language="vi",
            user_context={"has_child": True},
        )
    )
    second_response = orchestrator.handle_chat(
        ChatRequest(
            session_id=session_id,
            message="Cho tôi toilet gần nhất",
            current_zone="water_world",
            language="vi",
            user_context={"has_child": True},
        )
    )

    assert first_response.selected_facility is not None
    assert first_response.selected_facility.id == "fac_rest_008"
    assert second_response.selected_facility is not None
    assert second_response.selected_facility.id == "fac_toilet_001"
