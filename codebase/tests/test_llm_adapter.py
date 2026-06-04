from app.adapters.llm_adapter import LLMAdapter
from app.config import get_settings


class _FakeResponse:
    def __init__(self, content: str) -> None:
        self._content = content

    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {
            "choices": [
                {
                    "message": {
                        "content": self._content,
                    }
                }
            ]
        }


class _FakeGeminiResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict:
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "text": '```json\n{"intent_type":"facility_search","facility_type":"restaurant","current_zone":"water_world","constraints":{},"priority":"normal","needs_clarification":false,"confidence":0.91}\n```'
                            }
                        ]
                    }
                }
            ]
        }


class _FakeClient:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def post(self, url: str, headers: dict, json: dict) -> _FakeResponse:
        assert url.endswith("/chat/completions")
        assert headers["Authorization"] == "Bearer test-key"
        assert json["model"] == "test-model"
        assert json["temperature"] == 0
        return _FakeResponse('{"facility_type":"restaurant"}')


class _FakeGeminiClient:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def post(self, url: str, headers: dict | None = None, json: dict | None = None) -> _FakeGeminiResponse:
        assert ":generateContent?key=test-key" in url
        assert "gemini-3-flash" in url
        assert json is not None
        assert json["generationConfig"]["temperature"] == 0
        return _FakeGeminiResponse()


def test_llm_adapter_returns_none_when_disabled(monkeypatch) -> None:
    monkeypatch.setenv("LLM_ENABLED", "false")
    monkeypatch.setenv("LLM_PROVIDER", "auto")
    get_settings.cache_clear()

    adapter = LLMAdapter()

    assert adapter.extract_intent("test") is None
    assert adapter.generate_response({"message": "test"}) is None


def test_llm_adapter_calls_openai_compatible_api(monkeypatch) -> None:
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.com/v1")
    monkeypatch.setenv("LLM_INTENT_MODEL", "test-model")
    monkeypatch.setenv("LLM_RESPONSE_MODEL", "test-model")
    get_settings.cache_clear()

    import app.adapters.llm_adapter as llm_module

    monkeypatch.setattr(llm_module.httpx, "Client", _FakeClient)

    adapter = LLMAdapter()

    assert adapter.extract_intent("Có nhà hàng nào gần đây không?") == '{"facility_type":"restaurant"}'
    assert adapter.generate_response({"message": "fallback"}) == '{"facility_type":"restaurant"}'


def test_llm_adapter_calls_gemini_native_api(monkeypatch) -> None:
    monkeypatch.setenv("LLM_ENABLED", "true")
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta")
    monkeypatch.setenv("LLM_INTENT_MODEL", "gemini-3-flash")
    monkeypatch.setenv("LLM_RESPONSE_MODEL", "gemini-3-flash")
    get_settings.cache_clear()

    import app.adapters.llm_adapter as llm_module

    monkeypatch.setattr(llm_module.httpx, "Client", _FakeGeminiClient)

    adapter = LLMAdapter()

    result = adapter.extract_intent("Có nhà hàng nào gần đây không?")
    assert result is not None
    assert '"facility_type":"restaurant"' in result
