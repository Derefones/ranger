"""Module interfaces."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from ..config import Config
from ..fs import PathManager
from ..scope import Scope
from ..util.logging import LogRecord, info
from ..util.rate import RateLimiter


@dataclass(slots=True)
class ModuleOutcome:
    name: str
    counts: dict[str, int] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    logs: list[LogRecord] = field(default_factory=list)


@dataclass(slots=True)
class ModuleContext:
    config: Config
    scope: Scope
    fs: PathManager
    rate_limiter: RateLimiter

    def log(self, message: str, **fields: object) -> LogRecord:
        record = info(message, module=self.__class__.__name__, **fields)
        return record


ModuleRunner = Callable[[ModuleContext], ModuleOutcome]


def module_registry() -> Mapping[str, ModuleRunner]:
    from . import (
        api,
        archive,
        cves,
        dirb,
        misconfig,
        params,
        ports,
        probe,
        resolve,
        secrets,
        subdomains,
        summary,
        takeover,
    )

    return {
        "subdomains": subdomains.run,
        "resolve": resolve.run,
        "probe": probe.run,
        "ports": ports.run,
        "archive": archive.run,
        "dirb": dirb.run,
        "api": api.run,
        "params": params.run,
        "cves": cves.run,
        "misconfig": misconfig.run,
        "takeover": takeover.run,
        "secrets": secrets.run,
        "summary": summary.run,
    }
