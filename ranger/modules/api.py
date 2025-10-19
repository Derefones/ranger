"""API discovery placeholder."""
from __future__ import annotations

from ..util import io
from . import ModuleContext, ModuleOutcome


def run(context: ModuleContext) -> ModuleOutcome:
    outcome = ModuleOutcome(name="api")
    alive_path = context.fs.combined_dir() / "alive.txt"
    if not alive_path.exists():
        outcome.errors.append("no alive hosts")
        return outcome
    live_api_dir = context.fs.subdir("live", "apis")
    endpoints_path = live_api_dir / "api_endpoints.txt"
    io.write_lines(endpoints_path, [])
    outcome.artifacts["api_endpoints"] = str(endpoints_path)
    return outcome
