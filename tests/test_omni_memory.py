import pytest
from omni_agent.utils.memory import AgentMemory


def test_agent_memory_initialization():
    mem = AgentMemory()
    assert mem.index_name == "omni_agent_memory"
    assert mem.mock_db == []


def test_store_outcome_success():
    mem = AgentMemory()
    record_id = mem.store_outcome(
        task="Write a function",
        result="Success",
        feedback="Code works perfectly"
    )

    assert record_id == "mem_0"
    assert len(mem.mock_db) == 1

    record = mem.mock_db[0]
    assert record["id"] == "mem_0"
    assert record["task"] == "Write a function"
    assert record["result"] == "Success"
    assert record["feedback"] == "Code works perfectly"
    assert "timestamp" in record

    record_id2 = mem.store_outcome(
        task="Write another function",
        result="Failed",
        feedback="Syntax error"
    )
    assert record_id2 == "mem_1"
    assert len(mem.mock_db) == 2


def test_retrieve_lessons_empty_db():
    mem = AgentMemory()
    result = mem.retrieve_lessons("function")
    assert result == "No past lessons found."


def test_retrieve_lessons_no_match():
    mem = AgentMemory()
    mem.store_outcome("Task A", "Result A", "Feedback A")
    result = mem.retrieve_lessons("Database")
    assert result == "No past lessons found."


def test_retrieve_lessons_with_match():
    mem = AgentMemory()
    mem.store_outcome("Fix bug 1", "Fixed successfully", "Good job")
    mem.store_outcome("Write test 1", "Success", "Added coverage")
    mem.store_outcome("Fix bug 2", "Failed", "Need better logic")

    # Should retrieve the two bug fixing records, most recent first
    result = mem.retrieve_lessons("bug")
    assert "Fix bug 2" in result
    assert "Failed" in result
    assert "Fix bug 1" in result
    assert "Fixed successfully" in result
    assert "Write test 1" not in result

    # Test top_k parameter
    result_limited = mem.retrieve_lessons("bug", top_k=1)
    assert "Fix bug 2" in result_limited
    assert "Fix bug 1" not in result_limited
