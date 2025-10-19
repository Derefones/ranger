"""Archive URL gathering."""
from __future__ import annotations

from ..util import io
from . import ModuleContext, ModuleOutcome


def run(context: ModuleContext) -> ModuleOutcome:
    outcome = ModuleOutcome(name="archive")
    subdomains_path = context.fs.combined_dir() / "all_subdomains.txt"
    if not subdomains_path.exists():
        outcome.errors.append("no subdomains")
        return outcome
    lines = subdomains_path.read_text(encoding="utf-8").splitlines()
    hosts = [line.strip() for line in lines if line.strip()]
    urls = [f"http://{host}/" for host in hosts]
    in_scope, out_scope = context.scope.partition_scope(urls)
    combined_path = context.fs.combined_dir() / "urls.txt"
    io.write_lines(combined_path, in_scope)
    if out_scope:
        oos_path = context.fs.out_of_scope_dir() / "combined" / "urls.txt"
        io.write_lines(oos_path, out_scope)
        outcome.artifacts["oos_urls"] = str(oos_path)
    outcome.artifacts["urls"] = str(combined_path)
    outcome.counts["urls"] = len(urls)
    return outcome
