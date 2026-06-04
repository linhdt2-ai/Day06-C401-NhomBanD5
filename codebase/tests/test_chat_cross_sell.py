from app.schemas.chat import ChatRequest
from app.services.orchestrator import ChatOrchestrator


def test_chat_restaurant_response_includes_cross_sell_utilities() -> None:
    orchestrator = ChatOrchestrator()

    response = orchestrator.handle_chat(
        ChatRequest(
            session_id="sess_cross_sell",
            message="Tìm nhà hàng gần đây",
            current_zone="water_world",
            language="vi",
            user_context={},
        )
    )

    assert response.type == "success"
    assert response.selected_facility is not None
    assert response.selected_facility.type == "restaurant"
    assert response.cross_sell_facilities
    assert all(
        facility.type in {"toilet", "drinking_water", "rest_area"}
        for facility in response.cross_sell_facilities
    )

