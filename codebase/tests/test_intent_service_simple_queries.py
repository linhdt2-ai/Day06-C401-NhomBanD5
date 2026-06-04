from app.schemas.chat import SessionState, UserContext
from app.services.intent_service import IntentService


class DummyLLMAdapter:
    def extract_intent(self, message: str) -> None:
        return None


class OutOfScopeLLMAdapter:
    def extract_intent(self, message: str) -> str:
        return (
            '{"intent_type":"out_of_scope","facility_type":null,'
            '"current_zone":"water_world","constraints":{},'
            '"needs_clarification":true,"confidence":0.2}'
        )


def build_service() -> IntentService:
    return IntentService(llm_adapter=DummyLLMAdapter())


def test_detects_simple_ticket_question() -> None:
    service = build_service()

    result = service.extract_intent(
        message="Vé ở đâu?",
        current_zone="water_world",
        user_context=UserContext(),
        session_state=SessionState(),
    )

    assert result.intent_type == "facility_search"
    assert result.facility_type == "ticket_support"


def test_detects_colloquial_water_question() -> None:
    service = build_service()

    result = service.extract_intent(
        message="Khát quá",
        current_zone="water_world",
        user_context=UserContext(),
        session_state=SessionState(),
    )

    assert result.intent_type == "facility_search"
    assert result.facility_type == "drinking_water"


def test_detects_colloquial_rest_request() -> None:
    service = build_service()

    result = service.extract_intent(
        message="Mệt quá muốn ngồi nghỉ",
        current_zone="water_world",
        user_context=UserContext(),
        session_state=SessionState(),
    )

    assert result.intent_type == "facility_search"
    assert result.facility_type == "rest_area"


def test_heuristic_overrides_llm_out_of_scope_for_supported_phrase() -> None:
    service = IntentService(llm_adapter=OutOfScopeLLMAdapter())

    result = service.extract_intent(
        message="Tôi khát nước",
        current_zone="water_world",
        user_context=UserContext(),
        session_state=SessionState(),
    )

    assert result.intent_type == "facility_search"
    assert result.facility_type == "drinking_water"


def test_detects_buy_water_question() -> None:
    service = build_service()

    result = service.extract_intent(
        message="Mua nước ở đâu?",
        current_zone="river_safari",
        user_context=UserContext(),
        session_state=SessionState(),
    )

    assert result.intent_type == "facility_search"
    assert result.facility_type == "drinking_water"


def test_detects_vietnamese_food_question() -> None:
    service = build_service()

    result = service.extract_intent(
        message="Ăn món Việt",
        current_zone="folk_culture_island",
        user_context=UserContext(),
        session_state=SessionState(),
    )

    assert result.intent_type == "facility_search"
    assert result.facility_type == "restaurant"
