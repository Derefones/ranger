from __future__ import annotations

from ranger.subproc import run, which


def test_run_echo() -> None:
    result = run(["/bin/echo", "hello"], timeout=2)
    assert result.returncode == 0
    assert result.stdout.strip() == "hello"


def test_which_existing() -> None:
    found = which("sh")
    assert found is not None
    assert found.path
