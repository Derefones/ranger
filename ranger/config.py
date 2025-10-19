"""Configuration helpers."""
from __future__ import annotations

from collections.abc import Iterable, Mapping, MutableMapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

from . import __version__
from .subproc import which_version

ModuleName = str

DEFAULT_MODULE_ORDER: tuple[ModuleName, ...] = (
    "subdomains",
    "resolve",
    "probe",
    "ports",
    "archive",
    "dirb",
    "api",
    "params",
    "cves",
    "misconfig",
    "takeover",
    "secrets",
    "summary",
)


@dataclass(slots=True)
class ToolInfo:
    name: str
    path: str
    version: str | None


@dataclass(slots=True)
class Toolset:
    tools: MutableMapping[str, ToolInfo] = field(default_factory=dict)

    def has(self, tool: str) -> bool:
        return tool in self.tools

    def register(self, name: str, path: str, version: str | None) -> None:
        self.tools[name] = ToolInfo(name=name, path=path, version=version)

    def as_dict(self) -> dict[str, Mapping[str, str | None]]:
        return {
            name: {"path": info.path, "version": info.version}
            for name, info in self.tools.items()
        }


@dataclass(slots=True)
class Config:
    target: str
    program_name: str
    include_scope_path: Path | None
    exclude_scope_path: Path | None
    out_dir: Path
    rate: float
    threads: int
    timeout: int
    modules: list[ModuleName]
    disabled_modules: set[ModuleName]
    respect_robots: bool
    ffuf_wordlist: Path | None
    gf_patterns: Path | None
    nmap_top_ports: int
    nuclei_templates: Path | None
    http_proxy: str | None
    save_raw: bool
    dry_run: bool
    self_test: bool
    utc_start: datetime
    tools: Toolset

    def enabled_modules(self) -> list[ModuleName]:
        enabled = [m for m in self.modules if m not in self.disabled_modules]
        return enabled

    def run_label(self) -> str:
        timestamp = self.utc_start.strftime("%Y%m%dT%H%M%SZ")
        safe_target = self.target.replace("/", "-")
        return f"{self.program_name}_{safe_target}_{timestamp}"


def _parse_modules(raw: Iterable[str]) -> tuple[list[ModuleName], set[ModuleName]]:
    modules = list(DEFAULT_MODULE_ORDER)
    disabled: set[ModuleName] = set()
    for item in raw:
        if not item:
            continue
        if item == "all":
            modules = list(DEFAULT_MODULE_ORDER)
            disabled.clear()
            continue
        if item.startswith("-"):
            disabled.add(item[1:])
        else:
            if item not in modules:
                modules.append(item)
    return modules, disabled


@dataclass(slots=True)
class CLIArgs:
    target: str
    program_name: str
    include_scope: Path | None
    exclude_scope: Path | None
    out: Path
    rate: float
    threads: int
    timeout: int
    modules: tuple[str, ...]
    respect_robots: bool
    ffuf_wordlist: Path | None
    gf_patterns: Path | None
    nmap_top_ports: int
    nuclei_templates: Path | None
    http_proxy: str | None
    save_raw: bool
    dry_run: bool
    self_test: bool


def build_config(args: CLIArgs, tools: Toolset | None = None) -> Config:
    modules, disabled = _parse_modules(args.modules)
    return Config(
        target=args.target,
        program_name=args.program_name,
        include_scope_path=args.include_scope,
        exclude_scope_path=args.exclude_scope,
        out_dir=args.out,
        rate=args.rate,
        threads=args.threads,
        timeout=args.timeout,
        modules=modules,
        disabled_modules=disabled,
        respect_robots=args.respect_robots,
        ffuf_wordlist=args.ffuf_wordlist,
        gf_patterns=args.gf_patterns,
        nmap_top_ports=args.nmap_top_ports,
        nuclei_templates=args.nuclei_templates,
        http_proxy=args.http_proxy,
        save_raw=args.save_raw,
        dry_run=args.dry_run,
        self_test=args.self_test,
        utc_start=datetime.now(UTC),
        tools=tools or Toolset(),
    )


KNOWN_TOOLS = (
    "subfinder",
    "amass",
    "assetfinder",
    "dnsx",
    "massdns",
    "httpx",
    "ffuf",
    "waybackurls",
    "gau",
    "katana",
    "nmap",
    "nuclei",
    "gf",
    "subzy",
    "subjack",
    "trufflehog",
)


def detect_tools() -> Toolset:
    toolset = Toolset()
    for tool in KNOWN_TOOLS:
        info = which_version(tool)
        if info:
            toolset.register(name=tool, path=info.path, version=info.version)
    return toolset


def meta_payload(config: Config) -> dict[str, object]:
    return {
        "target": config.target,
        "program": config.program_name,
        "modules": config.enabled_modules(),
        "utc_start": config.utc_start.isoformat(timespec="seconds"),
        "version": __version__,
    }
