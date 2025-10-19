"""CLI entrypoint for ranger."""
from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable
from pathlib import Path

from ranger.config import CLIArgs, build_config, detect_tools
from ranger.fs import PathManager, write_environment, write_run_info, write_tools
from ranger.modules import ModuleContext, module_registry
from ranger.scope import build_scope
from ranger.util.rate import RateLimiter


def str2bool(value: str | None) -> bool:
    if value is None:
        return True
    value = value.lower()
    if value in {"true", "1", "yes", "on"}:
        return True
    if value in {"false", "0", "no", "off"}:
        return False
    raise argparse.ArgumentTypeError(f"invalid boolean: {value}")


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scope-aware reconnaissance orchestrator")
    parser.add_argument("--target", required=True)
    parser.add_argument("--program-name", required=True)
    parser.add_argument("--include-scope", type=Path)
    parser.add_argument("--exclude-scope", type=Path)
    parser.add_argument("--out", type=Path, default=Path("results"))
    parser.add_argument("--rate", type=float, default=50.0)
    parser.add_argument("--threads", type=int, default=32)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--modules", action="append", default=["all"])
    parser.add_argument("--respect-robots", type=str2bool, nargs="?", const=True, default=False)
    parser.add_argument("--ffuf-wordlist", type=Path)
    parser.add_argument("--gf-patterns", type=Path)
    parser.add_argument("--nmap-top-ports", type=int, default=100)
    parser.add_argument("--nuclei-templates", type=Path)
    parser.add_argument("--http-proxy")
    parser.add_argument("--save-raw", type=str2bool, nargs="?", const=True, default=False)
    parser.add_argument("--dry-run", type=str2bool, nargs="?", const=True, default=False)
    parser.add_argument("--self-test", type=str2bool, nargs="?", const=True, default=False)
    return parser.parse_args(list(argv))


def to_cli_args(ns: argparse.Namespace) -> CLIArgs:
    parts: list[str] = []
    for value in ns.modules:
        if isinstance(value, str):
            parts.extend(segment for segment in value.split(",") if segment)
    modules = tuple(parts)
    return CLIArgs(
        target=ns.target,
        program_name=ns.program_name,
        include_scope=ns.include_scope,
        exclude_scope=ns.exclude_scope,
        out=ns.out,
        rate=ns.rate,
        threads=ns.threads,
        timeout=ns.timeout,
        modules=modules,
        respect_robots=ns.respect_robots,
        ffuf_wordlist=ns.ffuf_wordlist,
        gf_patterns=ns.gf_patterns,
        nmap_top_ports=ns.nmap_top_ports,
        nuclei_templates=ns.nuclei_templates,
        http_proxy=ns.http_proxy,
        save_raw=ns.save_raw,
        dry_run=ns.dry_run,
        self_test=ns.self_test,
    )


def run_self_test() -> bool:
    from ranger.scope import Scope, ScopeDefinition

    include = ScopeDefinition(domains=["*.example.com"], urls=[], regex=[], cidrs=[])
    exclude = ScopeDefinition(domains=["admin.example.com"], urls=[], regex=[], cidrs=[])
    scope = Scope(include=include, exclude=exclude)
    in_scope, out_scope = scope.partition_scope(["www.example.com", "admin.example.com"])
    return in_scope == ["www.example.com"] and out_scope == ["admin.example.com"]


def main(argv: Iterable[str] | None = None) -> int:
    namespace = parse_args(argv or sys.argv[1:])
    cli_args = to_cli_args(namespace)
    tools = detect_tools()
    config = build_config(cli_args, tools)
    scope = build_scope(config.target, config.include_scope_path, config.exclude_scope_path)
    fs = PathManager(config)
    if config.self_test:
        ok = run_self_test()
        if not ok:
            print("self-test failed", file=sys.stderr)
            return 1
        print("self-test ok")
        if config.dry_run:
            return 0
    if config.dry_run:
        print("Dry run")
        print("Modules:", ", ".join(config.enabled_modules()))
        return 0
    rate_limiter = RateLimiter(rate=config.rate, burst=max(1, int(config.rate)))
    fs.ensure()
    write_run_info(fs)
    tool_payload = tools.as_dict() if hasattr(tools, "as_dict") else {}
    write_environment(fs, tool_payload)
    write_tools(fs, tool_payload)
    registry = module_registry()
    context = ModuleContext(config=config, scope=scope, fs=fs, rate_limiter=rate_limiter)
    for name in config.enabled_modules():
        runner = registry.get(name)
        if not runner:
            print(f"Skipping unknown module: {name}")
            continue
        try:
            outcome = runner(context)
        except Exception as exc:  # noqa: BLE001
            print(f"Module {name} failed: {exc}", file=sys.stderr)
            continue
        if outcome.errors:
            for err in outcome.errors:
                print(f"[{name}] {err}")
    summary_path = fs.subdir("summary") / "highlights.md"
    if summary_path.exists():
        print(summary_path)
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
