import pytest
from unittest.mock import MagicMock
from omni_agent.utils.nim_router import NIMRouter

def test_nim_router_prompt_length_fallback():
    router = NIMRouter()
    long_prompt = "A" * 8001

    # Mock the client to prevent actual API calls
    router.client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Mocked response"))]
    router.client.chat.completions.create.return_value = mock_response

    response = router.route_task(long_prompt, task_type="coding")

    router.client.chat.completions.create.assert_called_with(
        model="nim-architect",
        messages=[{"role": "user", "content": long_prompt}],
        temperature=0.2,
        max_tokens=4096,
        extra_body={"metadata": {"task_type": "complex"}}
    )

    assert response == "Mocked response"
