import pytest
import os
from unittest.mock import patch, MagicMock
from src.utils.nim_router import nim_router

def test_nim_router_initialization():
    from src.utils.nim_router import NIMRouter
    test_router = NIMRouter()
    assert test_router.base_url == "http://litellm-proxy:4000/v1"

@patch('src.utils.nim_router.OpenAI')
def test_nim_router_routes_models(mock_openai):
    mock_client = MagicMock()
    mock_openai.return_value = mock_client

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Mocked response"))]
    mock_client.chat.completions.create.return_value = mock_response

    from src.utils.nim_router import NIMRouter
    test_router = NIMRouter()
    test_router.client = mock_client

    # Fast task
    res_fast = test_router.route_task("Help", task_type="fast")
    assert res_fast == "Mocked response"
    mock_client.chat.completions.create.assert_called_with(
        model="nim-coder",
        messages=[{"role": "user", "content": "Help"}],
        temperature=0.2,
        max_tokens=4096,
        extra_body={"metadata": {"task_type": "fast"}}
    )

    # Complex task
    res_complex = test_router.route_task("Help", task_type="complex")
    assert res_complex == "Mocked response"
    mock_client.chat.completions.create.assert_called_with(
        model="nim-architect",
        messages=[{"role": "user", "content": "Help"}],
        temperature=0.2,
        max_tokens=4096,
        extra_body={"metadata": {"task_type": "complex"}}
    )
