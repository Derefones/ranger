"""Misconfiguration checks placeholder."""
from __future__ import annotations

from ..util import io
from . import ModuleContext, ModuleOutcome


def run(context: ModuleContext) -> ModuleOutcome:
    outcome = ModuleOutcome(name="misconfig")
    live_path = context.fs.live_dir() / "httpx.csv"
    if not live_path.exists():
        outcome.errors.append("no probe results")
        return outcome
    vulns_dir = context.fs.subdir("vulns", "misconfig")
    security_headers = context.fs.live_dir() / "security_headers.csv"
    with io.csv_writer(security_headers, ["host", "header", "value"]) as _writer:
        pass
    placeholder = vulns_dir / "generic.jsonl"
    io.write_lines(placeholder, [])
    outcome.artifacts["security_headers"] = str(security_headers)
    return outcome
