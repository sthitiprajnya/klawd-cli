import pytest
import os
from src.domain.skills import SkillManager

def test_skill_manager_load():
    manager = SkillManager(skills_dir="tests/test_skills")

    mock_skill = "def mock_func():\n    return True\n"
    success = manager.load_skill("test_skill", mock_skill)
    assert success is True

    skills = manager.list_skills()
    assert "test_skill" in skills
    assert "mock_func" in skills["test_skill"]

    # cleanup
    os.remove("tests/test_skills/test_skill.py")
