"""CVE scanning placeholder."""
from __future__ import annotations

from ..util import io
from . import ModuleContext, ModuleOutcome


def run(context: ModuleContext) -> ModuleOutcome:
    outcome = ModuleOutcome(name="cves")
    live_path = context.fs.live_dir() / "httpx.csv"
    if not live_path.exists():
        outcome.errors.append("no probe results")
        return outcome
    vulns_dir = context.fs.subdir("vulns")
    nuclei_path = vulns_dir / "nuclei.jsonl"
    io.write_lines(nuclei_path, [])
    (vulns_dir / "cves").mkdir(parents=True, exist_ok=True)
    (vulns_dir / "misconfig").mkdir(parents=True, exist_ok=True)
    (vulns_dir / "interesting").mkdir(parents=True, exist_ok=True)
    outcome.artifacts["nuclei"] = str(nuclei_path)
    return outcome
