from pathlib import Path

import pytest

from src.infrastructure.security.execution_adapter import NemoClawExecutionAdapter, PolicyRejectionError


def test_allowed_command_path(tmp_path: Path):
    policy = tmp_path / "nemoclaw-policy.yaml"
    policy.write_text("allow: true\n")
    adapter = NemoClawExecutionAdapter(policy_file=str(policy))

    adapter.execute(prompt="echo hello", task_type="coding", command="echo hello")


def test_blocked_command_path(tmp_path: Path):
    policy = tmp_path / "nemoclaw-policy.yaml"
    policy.write_text("allow: true\n")
    adapter = NemoClawExecutionAdapter(policy_file=str(policy))

    with pytest.raises(PolicyRejectionError) as exc:
        adapter.execute(prompt="sudo whoami", task_type="coding", command="sudo whoami")

    assert exc.value.payload["reason"].startswith("command_blocked")


def test_sandbox_down_degraded_mode_allows_documentation_only(tmp_path: Path):
    missing_policy = tmp_path / "missing-policy.yaml"
    adapter = NemoClawExecutionAdapter(policy_file=str(missing_policy))

    with pytest.raises(PolicyRejectionError):
        adapter.execute(prompt="run python", task_type="coding", command="python main.py")

    adapter.execute(prompt="Write docs", task_type="documentation")


def test_spawn_command_uses_shlex_split_and_shell_false(tmp_path: Path, monkeypatch):
    policy = tmp_path / "nemoclaw-policy.yaml"
    policy.write_text("allow: true\n")
    adapter = NemoClawExecutionAdapter(policy_file=str(policy))

    observed = {}

    class DummyProc:
        pass

    def fake_popen(argv, shell):
        observed["argv"] = argv
        observed["shell"] = shell
        return DummyProc()

    monkeypatch.setattr("src.infrastructure.security.execution_adapter.subprocess.Popen", fake_popen)

    proc = adapter.spawn_command("python -c 'print(\"hi there\")'")

    assert isinstance(proc, DummyProc)
    assert observed["argv"] == ["python", "-c", 'print("hi there")']
    assert observed["shell"] is False


def test_spawn_command_rejects_injection_background_pattern(tmp_path: Path):
    policy = tmp_path / "nemoclaw-policy.yaml"
    policy.write_text("allow: true\n")
    adapter = NemoClawExecutionAdapter(policy_file=str(policy))

    with pytest.raises(PolicyRejectionError) as exc:
        adapter.spawn_command("echo ok && nohup sleep 30 &")

    assert exc.value.payload["reason"] == "unsafe_background_process_pattern"
