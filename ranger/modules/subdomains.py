"""Subdomain discovery module."""
from __future__ import annotations

from ..config import Config
from ..util import io
from ..util.net import dedupe_preserve_order, normalize_host
from . import ModuleContext, ModuleOutcome


def _default_candidates(config: Config) -> list[str]:
    base = normalize_host(config.target)
    return [base, f"www.{base}"]


def run(context: ModuleContext) -> ModuleOutcome:
    outcome = ModuleOutcome(name="subdomains")
    config = context.config
    fs = context.fs
    fs.ensure()
    sources_dir = fs.sources_dir()
    manual_path = sources_dir / "manual.txt"
    seeds = _default_candidates(config)
    io.write_lines(manual_path, seeds)
    in_scope, out_scope = context.scope.partition_scope(seeds)
    combined_path = fs.combined_dir() / "all_subdomains.txt"
    io.write_lines(combined_path, dedupe_preserve_order(in_scope))
    if out_scope:
        oos_path = fs.out_of_scope_dir() / "combined" / "all_subdomains.txt"
        io.write_lines(oos_path, dedupe_preserve_order(out_scope))
        outcome.artifacts["oos_subdomains"] = str(oos_path)
    outcome.artifacts["all_subdomains"] = str(combined_path)
    outcome.counts["in_scope"] = len(in_scope)
    outcome.counts["out_scope"] = len(out_scope)
    return outcome
