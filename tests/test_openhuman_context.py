import httpx

from src.domain.agents.base import BaseAgent


class DummyAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="Dummy", role="Test", system_prompt="Base")


def test_successful_context_retrieval(monkeypatch):
    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {"jsonrpc": "2.0", "id": 1, "result": {"context": "Remember style guide"}}

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: Response())

    agent = DummyAgent()
    context = agent._get_dynamic_context()

    assert "Remember style guide" in context
    assert agent.last_openhuman_observability["openhuman_available"] is True
    assert agent.last_openhuman_observability["openhuman_error"] is None


def test_malformed_jsonrpc_payload_falls_back(monkeypatch):
    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {"jsonrpc": "2.0", "id": 1, "result": {"unexpected": "shape"}}

    monkeypatch.setattr(httpx, "post", lambda *args, **kwargs: Response())

    agent = DummyAgent()
    context = agent._get_dynamic_context()

    assert "Stateless fallback mode enabled" in context
    assert agent.last_openhuman_observability["openhuman_available"] is False
    assert agent.last_openhuman_observability["openhuman_error"] == "malformed_jsonrpc_payload"


def test_timeout_fallback_path(monkeypatch):
    def _raise_timeout(*args, **kwargs):
        raise httpx.TimeoutException("timed out")

    monkeypatch.setattr(httpx, "post", _raise_timeout)

    agent = DummyAgent()
    agent.openhuman_max_retries = 2
    context = agent._get_dynamic_context()

    assert "Stateless fallback mode enabled" in context
    assert agent.last_openhuman_observability["openhuman_available"] is False
    assert agent.last_openhuman_observability["openhuman_error"] == "timeout"
    assert agent.last_openhuman_observability["openhuman_attempts"] == 3
