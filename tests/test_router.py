import importlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


def _load_router_module(mock_client=None):
    if mock_client is None:
        mock_client = MagicMock()
    sys.modules['openai'] = SimpleNamespace(OpenAI=MagicMock(return_value=mock_client))
    sys.modules.pop('src.infrastructure.llm_router', None)
    return importlib.import_module('src.infrastructure.llm_router'), mock_client


def test_llm_router_initialization():
    module, _ = _load_router_module()
    test_router = module.LLMRouter()
    assert test_router.base_url == "http://litellm-proxy:4000/v1"


def test_normal_route_selection():
    module, mock_client = _load_router_module()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Mocked response"))]
    mock_client.chat.completions.create.return_value = mock_response

    test_router = module.LLMRouter()
    test_router.client = mock_client
    res_fast = test_router.route("Help", task_type="fast", job_id="job-1", token_budget=1024)

    assert res_fast == "Mocked response"
    mock_client.chat.completions.create.assert_called_with(
        model="nim-coder",
        messages=[{"role": "user", "content": "Help"}],
        temperature=0.2,
        max_tokens=1024,
        extra_body={"metadata": {"task_type": "fast", "job_id": "job-1", "token_budget": 1024, "prompt_chars": 4, "api_key_pool_size": 1}},
    )


def test_fallback_on_provider_failure():
    module, mock_client = _load_router_module()
    mock_client.chat.completions.create.side_effect = Exception("provider unavailable")
    test_router = module.LLMRouter()
    test_router.client = mock_client

    res = test_router.route("Implement feature", task_type="coding", job_id="job-2")
    assert res.startswith("Error: all model routes failed after failover attempts")


def test_route_prompt_length_fallback():
    module, mock_client = _load_router_module()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Mocked complex response"))]
    mock_client.chat.completions.create.return_value = mock_response

    test_router = module.LLMRouter()
    test_router.client = mock_client

    long_prompt = "A" * 8001
    res = test_router.route(long_prompt, task_type="coding", job_id="job-3", token_budget=2048)

    assert res == "Mocked complex response"
    mock_client.chat.completions.create.assert_called_with(
        model="nim-architect",
        messages=[{"role": "user", "content": long_prompt}],
        temperature=0.2,
        max_tokens=2048,
        extra_body={"metadata": {"task_type": "complex", "job_id": "job-3", "token_budget": 2048, "prompt_chars": 8001, "api_key_pool_size": 1}},
    )


def test_degraded_provider_bypass():
    sys.modules["redis"] = SimpleNamespace(Redis=MagicMock(return_value=MagicMock()))
    mock_post = MagicMock()
    mock_post.return_value = MagicMock(status_code=200, json=lambda: {"providers": [{"api_key": "k1", "available": False}, {"api_key": "k2", "available": True}]})
    sys.modules["httpx"] = SimpleNamespace(put=MagicMock(), post=mock_post, TimeoutException=Exception, HTTPError=Exception)
    from src.infrastructure.llm import thread_parker

    with patch.object(thread_parker, "get_all_configured_keys", return_value=["k1", "k2"]), \
         patch.object(thread_parker, "r") as mock_redis:
        mock_redis.exists.side_effect = lambda key: key.endswith(":k1")
        parker = thread_parker.ThreadParker()
        assert parker._find_available_key("nim-coder") == "k2"
