"""Directory brute-force placeholder."""
from __future__ import annotations

from ..util import io
from . import ModuleContext, ModuleOutcome

HEADERS = ["url", "status", "length", "words", "lines", "redirect", "time"]


def run(context: ModuleContext) -> ModuleOutcome:
    outcome = ModuleOutcome(name="dirb")
    alive_path = context.fs.combined_dir() / "alive.txt"
    if not alive_path.exists():
        outcome.errors.append("no alive hosts")
        return outcome
    lines = alive_path.read_text(encoding="utf-8").splitlines()
    hosts = [line.split(":")[0] for line in lines if line.strip()]
    for host in hosts:
        host_dir = context.fs.subdir("dirb", host)
        ffuf_path = host_dir / "ffuf.csv"
        with io.csv_writer(ffuf_path, HEADERS) as _writer:
            # placeholder, no findings
            pass
        found_path = host_dir / "found.txt"
        io.write_lines(found_path, [])
    outcome.counts["hosts"] = len(hosts)
    return outcome
