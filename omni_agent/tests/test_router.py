import pytest
import os
from unittest.mock import patch
from omni_agent.utils.nim_router import nim_router

@patch.dict(os.environ, {}, clear=True)
def test_nim_router_mock_fallback():
    # Force re-initialization of router to pick up cleared env
    from omni_agent.utils.nim_router import NIMRouter
    test_router = NIMRouter()
    assert "mock-key-1" in test_router.api_keys

@patch.dict(os.environ, {}, clear=True)
def test_nim_router_routes_models():
    from omni_agent.utils.nim_router import NIMRouter
    test_router = NIMRouter()

    # Fast task
    res_fast = test_router.route_task("Help", task_type="fast")
    assert "minimax-text-01" in res_fast

    # Coding task
    res_coding = test_router.route_task("Help", task_type="coding")
    assert "glm-4-plus" in res_coding

    # Complex task
    res_complex = test_router.route_task("Help", task_type="complex")
    assert "moonshot-v1-128k" in res_complex
