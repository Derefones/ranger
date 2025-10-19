"""Subprocess helpers."""
from __future__ import annotations

import shutil
import subprocess
import time
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(slots=True)
class WhichResult:
    name: str
    path: str


@dataclass(slots=True)
class WhichVersionResult:
    name: str
    path: str
    version: str | None


@dataclass(slots=True)
class RunResult:
    returncode: int
    stdout: str
    stderr: str
    duration: float


class SubprocessError(RuntimeError):
    pass


def which(cmd: str) -> WhichResult | None:
    path = shutil.which(cmd)
    if not path:
        return None
    return WhichResult(name=cmd, path=path)


def which_version(cmd: str) -> WhichVersionResult | None:
    info = which(cmd)
    if not info:
        return None
    version: str | None = None
    try:
        completed = subprocess.run(
            [info.path, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        output = completed.stdout.strip() or completed.stderr.strip()
        version = output.splitlines()[0] if output else None
    except (OSError, subprocess.SubprocessError):
        version = None
    return WhichVersionResult(name=cmd, path=info.path, version=version)


def run(args: Sequence[str], timeout: float, stdout_limit: int = 50 * 1024 * 1024) -> RunResult:
    """Run a subprocess with timeout and output caps."""
    start = time.monotonic()
    try:
        completed = subprocess.run(
            list(args),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise SubprocessError(f"command timed out: {' '.join(args)}") from exc
    duration = time.monotonic() - start
    stdout = completed.stdout[:stdout_limit]
    stderr = completed.stderr[:stdout_limit]
    return RunResult(
        returncode=completed.returncode,
        stdout=stdout,
        stderr=stderr,
        duration=duration,
    )
