"""HTTP probing module."""
from __future__ import annotations

from ..util import io
from . import ModuleContext, ModuleOutcome

HEADERS = ["host", "port", "scheme", "status", "title", "tech", "fingerprint", "tls", "cdn"]


def _load_hosts(context: ModuleContext) -> list[str]:
    resolved = context.fs.combined_dir() / "resolved.txt"
    if resolved.exists():
        rows = []
        for line in resolved.read_text(encoding="utf-8").splitlines()[1:]:
            if not line:
                continue
            parts = line.split(",")
            rows.append(parts[0])
        return rows
    subdomains = context.fs.combined_dir() / "all_subdomains.txt"
    if subdomains.exists():
        lines = subdomains.read_text(encoding="utf-8").splitlines()
        return [line.strip() for line in lines if line.strip()]
    return []


def run(context: ModuleContext) -> ModuleOutcome:
    outcome = ModuleOutcome(name="probe")
    hosts = _load_hosts(context)
    if not hosts:
        outcome.errors.append("no hosts to probe")
        return outcome
    live_dir = context.fs.live_dir()
    by_status = live_dir / "by_status"
    by_status.mkdir(parents=True, exist_ok=True)
    httpx_path = live_dir / "httpx.csv"
    alive_path = context.fs.combined_dir() / "alive.txt"
    with io.csv_writer(httpx_path, HEADERS) as writer:
        for host in hosts:
            row = {
                "host": host,
                "port": "80",
                "scheme": "http",
                "status": "0",
                "title": "",
                "tech": "",
                "fingerprint": "",
                "tls": "",
                "cdn": "",
            }
            writer.writerow(row)
    io.write_lines(alive_path, [f"{host}:80" for host in hosts])
    outcome.artifacts["httpx"] = str(httpx_path)
    outcome.artifacts["alive"] = str(alive_path)
    outcome.counts["hosts"] = len(hosts)
    return outcome
