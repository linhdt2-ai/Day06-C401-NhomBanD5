from app.schemas.chat import ChatRequest
from app.services.orchestrator import ChatOrchestrator
from app.services.intent_service import IntentService
from app.services.response_service import ResponseService


class DummyLLMAdapter:
    def extract_intent(self, message: str) -> None:
        return None

    def generate_response(self, payload: dict) -> None:
        return None


ZONE_SUGGESTIONS = {
    "harbor_corner": [
        "Tìm nhà hàng gần đây",
        "Nhà vệ sinh gần nhất",
        "Quầy hỗ trợ vé ở đâu",
    ],
    "water_world": [
        "Thuê tủ đồ ở đâu",
        "Khát quá",
        "Nhà vệ sinh gần nhất",
    ],
    "adventure_land": [
        "Chỗ nghỉ chân",
        "Khát quá",
        "Nhà vệ sinh ở đâu",
    ],
    "river_safari": [
        "WC ở đâu",
        "Mua nước ở đâu",
        "Tôi cần sơ cứu",
    ],
    "indoor_games": [
        "Có quán nào cho trẻ em không",
        "Nhà vệ sinh gần nhất",
        "Khát quá",
    ],
    "folk_culture_island": [
        "Ăn món Việt",
        "Đi vệ sinh",
        "Có quà lưu niệm không",
    ],
}


def build_orchestrator() -> ChatOrchestrator:
    adapter = DummyLLMAdapter()
    return ChatOrchestrator(
        intent_service=IntentService(llm_adapter=adapter),
        response_service=ResponseService(llm_adapter=adapter),
    )


def test_all_zone_suggestions_resolve_to_supported_response() -> None:
    orchestrator = build_orchestrator()

    for zone, suggestions in ZONE_SUGGESTIONS.items():
        for suggestion in suggestions:
            response = orchestrator.handle_chat(
                ChatRequest(
                    session_id=f"{zone}-{suggestion}",
                    message=suggestion,
                    current_zone=zone,
                    language="vi",
                    user_context={},
                )
            )

            assert response.type in {"success", "fast_track"}, (zone, suggestion, response)
