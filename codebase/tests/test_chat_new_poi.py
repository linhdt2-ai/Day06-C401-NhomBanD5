import pytest
from app.schemas.chat import ChatRequest
from app.services.orchestrator import ChatOrchestrator
from app.services.intent_service import IntentService
from app.services.facility_service import FacilityService
from app.services.ranking_service import RankingService
from app.services.navigation_service import NavigationService
from app.services.response_service import ResponseService
from app.services.session_service import SessionService
from app.engines.rule_engine import RuleEngine
from app.engines.query_engine import QueryEngine

@pytest.fixture
def orchestrator():
    return ChatOrchestrator()

@pytest.fixture
def valid_session_id():
    return "test-session-123"

def test_chat_find_souvenir(orchestrator: ChatOrchestrator, valid_session_id: str):
    request = ChatRequest(
        session_id=valid_session_id,
        message="Tôi muốn mua quà lưu niệm",
        current_zone="harbor_corner",
        language="vi",
        user_context={}
    )
    response = orchestrator.handle_chat(request)
    assert response.type == "success"
    assert response.selected_facility is not None
    assert response.selected_facility.type == "souvenir"
    assert response.selected_facility.id == "fac_souvenir_001"

def test_chat_find_lost_found(orchestrator: ChatOrchestrator, valid_session_id: str):
    request = ChatRequest(
        session_id=valid_session_id,
        message="Tôi bị mất đồ, tìm ở đâu",
        current_zone="harbor_corner",
        language="vi",
        user_context={}
    )
    response = orchestrator.handle_chat(request)
    assert response.type == "success"
    assert response.selected_facility is not None
    assert response.selected_facility.type == "lost_found"
    assert response.selected_facility.id == "fac_lostfound_001"

def test_chat_ticket_support(orchestrator: ChatOrchestrator, valid_session_id: str):
    request = ChatRequest(
        session_id=valid_session_id,
        message="Tôi muốn hỗ trợ vé",
        current_zone="harbor_corner",
        language="vi",
        user_context={}
    )
    response = orchestrator.handle_chat(request)
    assert response.type == "success"
    assert response.selected_facility is not None
    assert response.selected_facility.type == "ticket_support"
    assert response.selected_facility.id == "fac_ticket_001"
