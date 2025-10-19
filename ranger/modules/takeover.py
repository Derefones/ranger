"""Subdomain takeover placeholder."""
from __future__ import annotations

from ..util import io
from . import ModuleContext, ModuleOutcome

HEADERS = ["host", "status", "provider", "fingerprint", "verified"]


def run(context: ModuleContext) -> ModuleOutcome:
    outcome = ModuleOutcome(name="takeover")
    subdomains_path = context.fs.combined_dir() / "all_subdomains.txt"
    if not subdomains_path.exists():
        outcome.errors.append("no subdomains")
        return outcome
    takeover_dir = context.fs.subdir("takeover")
    subzy_path = takeover_dir / "subzy.csv"
    with io.csv_writer(subzy_path, HEADERS) as _writer:
        pass
    subjack_path = takeover_dir / "subjack.csv"
    with io.csv_writer(subjack_path, ["host", "status", "reason"]) as _writer:
        pass
    confirmed_path = takeover_dir / "confirmed.txt"
    io.write_lines(confirmed_path, [])
    outcome.artifacts["subzy"] = str(subzy_path)
    return outcome
