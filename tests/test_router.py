import importlib
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch, call


def _load_router_module(mock_client=None):
    """Load LLMRouter with mocked OpenAI client(s)."""
    if mock_client is None:
        mock_client = MagicMock()
    sys.modules['openai'] = SimpleNamespace(OpenAI=MagicMock(return_value=mock_client))
    sys.modules.pop('src.infrastructure.llm_router', None)
    return importlib.import_module('src.infrastructure.llm_router'), mock_client


class TestLLMRouterInitialization:
    """Test LLMRouter initialization and configuration."""
    
    def test_llm_router_initialization(self):
        """Test router initializes with correct base_url and models."""
        module, _ = _load_router_module()
        test_router = module.LLMRouter()
        
        assert test_router.base_url == "http://litellm-proxy:4000/v1"
        assert test_router.MODELS["coding"] == "nim-coder"
        assert test_router.MODELS["complex"] == "nim-architect"
        assert test_router.MODELS["fast"] == "nim-coder"
        assert test_router.MODELS["reflection"] == "nim-architect"
    
    def test_router_client_pool_creation(self):
        """Test router creates client pool from API keys."""
        module, mock_client = _load_router_module()
        
        with patch.dict('os.environ', {'LITELLM_API_KEY': 'test-key-1', 'NIM_API_KEYS': 'test-key-2,test-key-3'}):
            test_router = module.LLMRouter()
            
            # Should create one client per key
            assert len(test_router.clients) >= 1
            assert test_router.api_keys in [['test-key-1'], ['test-key-1', 'test-key-2', 'test-key-3']]


class TestLLMRouterRouting:
    """Test normal routing behavior."""
    
    def test_normal_route_selection_fast_task(self):
        """Test successful route with fast task type."""
        module, mock_client = _load_router_module()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Mocked response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        test_router = module.LLMRouter()
        test_router.clients = [mock_client]  # Use clients list, not client attribute
        
        res_fast = test_router.route("Help", task_type="fast", job_id="job-1", token_budget=1024)
        
        assert res_fast == "Mocked response"
        mock_client.chat.completions.create.assert_called_once()
        
        # Verify call arguments
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == "nim-coder"
        assert call_kwargs['temperature'] == 0.2
        assert call_kwargs['max_tokens'] == 1024
        assert call_kwargs['messages'] == [{"role": "user", "content": "Help"}]
    
    def test_normal_route_selection_complex_task(self):
        """Test successful route with complex task type."""
        module, mock_client = _load_router_module()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Complex response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        test_router = module.LLMRouter()
        test_router.clients = [mock_client]
        
        res = test_router.route("Implement complex feature", task_type="complex", job_id="job-2")
        
        assert res == "Complex response"
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == "nim-architect"
    
    def test_metadata_includes_pool_size(self):
        """Test that metadata includes api_key_pool_size."""
        module, mock_client = _load_router_module()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        test_router = module.LLMRouter()
        test_router.clients = [mock_client, MagicMock(), MagicMock()]  # 3 clients
        
        test_router.route("Test", task_type="coding", job_id="job-3")
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        metadata = call_kwargs['extra_body']['metadata']
        assert metadata['api_key_pool_size'] == 3

    test_router = module.LLMRouter()
    test_router.client = mock_client
    # Explicitly mock self.clients to bypass the array initialization logic inside LLMRouter
    test_router.clients = [mock_client]
    res_fast = test_router.route("Help", task_type="fast", job_id="job-1", token_budget=1024)

    assert res_fast == "Mocked response"
    mock_client.chat.completions.create.assert_called_with(
        model="nim-coder",
        messages=[{"role": "user", "content": "Help"}],
        temperature=0.2,
        max_tokens=1024,
        extra_body={"metadata": {"task_type": "fast", "job_id": "job-1", "token_budget": 1024, "prompt_chars": 4, "api_key_pool_size": 1}},
    )

def test_route_with_system_prompt():
    module, mock_client = _load_router_module()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Mocked response"))]
    mock_client.chat.completions.create.return_value = mock_response

    test_router = module.LLMRouter()
    test_router.clients = [mock_client]
    res = test_router.route("Help", task_type="coding", job_id="job-3", system_prompt="You are an AI.")

    assert res == "Mocked response"
    mock_client.chat.completions.create.assert_called_with(
        model="nim-coder",
        messages=[{"role": "system", "content": "You are an AI."}, {"role": "user", "content": "Help"}],
        temperature=0.2,
        max_tokens=4096,
        extra_body={"metadata": {"task_type": "coding", "job_id": "job-3", "token_budget": 4096, "prompt_chars": 18, "api_key_pool_size": 1}},
    )


def test_fallback_on_provider_failure():
    module, mock_client = _load_router_module()
    mock_client.chat.completions.create.side_effect = Exception("provider unavailable")
    test_router = module.LLMRouter()
    test_router.clients = [mock_client]

    res = test_router.route("Implement feature", task_type="coding", job_id="job-2")
    assert res.startswith("Error: all model routes failed after failover attempts")
    assert res == "Error: all model routes failed after failover attempts"
    assert res.startswith("Error: all model routes failed")


def test_degraded_provider_bypass():
    sys.modules["redis"] = SimpleNamespace(Redis=MagicMock(return_value=MagicMock()))
    mock_post_response = MagicMock()
    mock_post_response.status_code = 200
    mock_post_response.json.return_value = {"providers": [{"api_key": "k1", "available": False}, {"api_key": "k2", "available": True}]}
    sys.modules["httpx"] = SimpleNamespace(post=MagicMock(return_value=mock_post_response), TimeoutException=Exception, HTTPError=Exception)
    sys.modules["httpx"] = SimpleNamespace(put=MagicMock(), post=MagicMock())
    from src.infrastructure.llm import thread_parker

    with patch.object(thread_parker, "get_all_configured_keys", return_value=["k1", "k2"]), \
         patch.object(thread_parker, "r") as mock_redis, \
         patch("src.infrastructure.rust_workers.client.httpx.post") as mock_post:

        mock_post.return_value = MagicMock(status_code=200, json=lambda: {
            "providers": [
                {"api_key": "k1", "available": False},
                {"api_key": "k2", "available": True}
            ]
        })

        mock_redis.exists.side_effect = lambda key: key.endswith(":k1")
        parker = thread_parker.ThreadParker()
        assert parker._find_available_key("nim-coder") == "k2"


def test_failover_success_on_subsequent_client():
    module, mock_client1 = _load_router_module()
    _, mock_client2 = _load_router_module()

    mock_client1.chat.completions.create.side_effect = Exception("provider 1 unavailable")
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Success on provider 2"))]
    mock_client2.chat.completions.create.return_value = mock_response

    test_router = module.LLMRouter()
    test_router.clients = [mock_client1, mock_client2]

    res = test_router.route("Implement feature", task_type="coding", job_id="job-3")
    assert res == "Success on provider 2"
class TestLLMRouterPromptUpgrade:
    """Test prompt length-based model upgrading."""
    
    def test_long_prompt_upgrades_to_complex(self):
        """Test that prompts >8000 chars are upgraded to architect model."""
        module, mock_client = _load_router_module()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        test_router = module.LLMRouter()
        test_router.clients = [mock_client]
        
        long_prompt = "x" * 9000  # 9000 characters
        test_router.route(long_prompt, task_type="fast", job_id="job-4")
        
        # Should be upgraded from "nim-coder" to "nim-architect"
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == "nim-architect"


class TestLLMRouterFailover:
    """Test failover logic with multiple clients."""
    
    def test_failover_to_next_client_on_exception(self):
        """Test router tries next client when first fails."""
        module, _ = _load_router_module()
        
        # Create 2 mock clients: first fails, second succeeds
        mock_client_1 = MagicMock()
        mock_client_1.chat.completions.create.side_effect = Exception("provider unavailable")
        
        mock_client_2 = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Success from client 2"))]
        mock_client_2.chat.completions.create.return_value = mock_response
        
        test_router = module.LLMRouter()
        test_router.clients = [mock_client_1, mock_client_2]
        
        result = test_router.route("Test", task_type="coding", job_id="job-5")
        
        assert result == "Success from client 2"
        mock_client_1.chat.completions.create.assert_called_once()
        mock_client_2.chat.completions.create.assert_called_once()
    
    def test_failover_round_robin_rotation(self):
        """Test round-robin client selection after successful call."""
        module, _ = _load_router_module()
        
        # Create 3 mock clients, all successful
        mock_clients = []
        for i in range(3):
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.choices = [MagicMock(message=MagicMock(content=f"Response {i}"))]
            mock_client.chat.completions.create.return_value = mock_response
            mock_clients.append(mock_client)
        
        test_router = module.LLMRouter()
        test_router.clients = mock_clients
        test_router._next_client_idx = 0
        
        # Make 3 successful calls
        test_router.route("Test 1", task_type="coding", job_id="job-6")
        test_router.route("Test 2", task_type="coding", job_id="job-7")
        test_router.route("Test 3", task_type="coding", job_id="job-8")
        
        # Verify round-robin: client 0 -> 1 -> 2 -> 0
        assert test_router._next_client_idx == 0  # After 3 calls on 3 clients, wraps to 0
    
    def test_all_clients_exhausted_error(self):
        """Test error message when all clients fail."""
        module, _ = _load_router_module()
        
        # Create 2 mock clients that both fail
        mock_client_1 = MagicMock()
        mock_client_1.chat.completions.create.side_effect = Exception("error1")
        
        mock_client_2 = MagicMock()
        mock_client_2.chat.completions.create.side_effect = Exception("error2")
        
        test_router = module.LLMRouter()
        test_router.clients = [mock_client_1, mock_client_2]
        
        result = test_router.route("Test", task_type="coding", job_id="job-9")
        
        # Should return the standard error message when all routes fail
        assert result == "Error: all model routes failed after failover attempts"
        assert mock_client_1.chat.completions.create.call_count >= 1
        assert mock_client_2.chat.completions.create.call_count >= 1
    
    def test_partial_failover_success(self):
        """Test failover succeeds even after multiple failures."""
        module, _ = _load_router_module()
        
        # Create 3 clients: first 2 fail, third succeeds
        mock_clients = [MagicMock(), MagicMock(), MagicMock()]
        mock_clients[0].chat.completions.create.side_effect = Exception("error1")
        mock_clients[1].chat.completions.create.side_effect = Exception("error2")
        
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Success from client 3"))]
        mock_clients[2].chat.completions.create.return_value = mock_response
        
        test_router = module.LLMRouter()
        test_router.clients = mock_clients
        
        result = test_router.route("Test", task_type="coding", job_id="job-10")
        
        assert result == "Success from client 3"


class TestLLMRouterEdgeCases:
    """Test edge cases and configuration."""
    
    def test_single_client_fallback(self):
        """Test router works with single client (no failover)."""
        module, mock_client = _load_router_module()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        test_router = module.LLMRouter()
        test_router.clients = [mock_client]
        
        result = test_router.route("Test", task_type="coding", job_id="job-11")
        assert result == "Response"
    
    def test_reflection_task_uses_architect(self):
        """Test reflection tasks use architect model."""
        module, mock_client = _load_router_module()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Reflection"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        test_router = module.LLMRouter()
        test_router.clients = [mock_client]
        
        test_router.route("Reflect", task_type="reflection", job_id="job-12")
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == "nim-architect"
    
    def test_unknown_task_type_defaults_to_coding(self):
        """Test unknown task types default to 'coding' model."""
        module, mock_client = _load_router_module()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content="Response"))]
        mock_client.chat.completions.create.return_value = mock_response
        
        test_router = module.LLMRouter()
        test_router.clients = [mock_client]
        
        test_router.route("Test", task_type="unknown_type", job_id="job-13")
        
        call_kwargs = mock_client.chat.completions.create.call_args[1]
        assert call_kwargs['model'] == "nim-coder"  # Default
