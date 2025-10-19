"""Resolution module."""
from __future__ import annotations

import socket

from ..util import io
from ..util.net import dedupe_preserve_order
from . import ModuleContext, ModuleOutcome


def run(context: ModuleContext) -> ModuleOutcome:
    outcome = ModuleOutcome(name="resolve")
    fs = context.fs
    subdomains_path = fs.combined_dir() / "all_subdomains.txt"
    if not subdomains_path.exists():
        outcome.errors.append("missing subdomains list")
        return outcome
    lines = subdomains_path.read_text(encoding="utf-8").splitlines()
    hosts = [line.strip() for line in lines if line.strip()]
    resolved_rows: list[tuple[str, str]] = []
    errors: list[str] = []
    for host in hosts:
        try:
            infos = socket.getaddrinfo(host, None)
        except socket.gaierror:
            errors.append(host)
            continue
        ips = dedupe_preserve_order(str(info[4][0]) for info in infos if info and info[4])
        for ip in ips:
            resolved_rows.append((host, ip))
    resolved_path = fs.combined_dir() / "resolved.txt"
    with io.csv_writer(resolved_path, ["host", "ip"]) as writer:
        for host, ip in resolved_rows:
            writer.writerow({"host": host, "ip": ip})
    if errors:
        error_path = fs.meta_dir() / "resolution_errors.txt"
        io.write_lines(error_path, errors)
        outcome.artifacts["resolution_errors"] = str(error_path)
    outcome.artifacts["resolved"] = str(resolved_path)
    outcome.counts["resolved"] = len(resolved_rows)
    outcome.counts["errors"] = len(errors)
    return outcome
