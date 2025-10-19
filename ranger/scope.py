"""Scope management."""
from __future__ import annotations

import fnmatch
import ipaddress
import json
import re
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from .util.net import extract_host, normalize_host


@dataclass(slots=True)
class ScopeDefinition:
    domains: list[str]
    urls: list[str]
    regex: list[str]
    cidrs: list[str]


def _load_simple_yaml(path: Path) -> dict[str, list[str]]:
    data: dict[str, list[str]] = {}
    current: str | None = None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.endswith(":"):
            current = line[:-1].strip()
            data.setdefault(current, [])
            continue
        if line.startswith("-") and current:
            value = line[1:].strip()
            value = value.strip('"')
            value = value.strip("'")
            data.setdefault(current, []).append(value)
    return data


def load_scope_file(path: Path) -> ScopeDefinition:
    text = path.read_text(encoding="utf-8")
    data: dict[str, list[str]]
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            data = {
                key: [str(item) for item in value]
                for key, value in parsed.items()
                if isinstance(value, list)
            }
        else:
            data = {}
    except json.JSONDecodeError:
        data = _load_simple_yaml(path)
    return ScopeDefinition(
        domains=data.get("domains", []),
        urls=data.get("urls", []),
        regex=data.get("regex", []),
        cidrs=data.get("cidrs", []),
    )


@dataclass(slots=True)
class Scope:
    include: ScopeDefinition
    exclude: ScopeDefinition

    def _matches_domains(self, value: str, patterns: list[str]) -> bool:
        host = normalize_host(value)
        for pattern in patterns:
            if fnmatch.fnmatch(host, pattern.lower()):
                return True
        return False

    def _matches_urls(self, value: str, patterns: list[str]) -> bool:
        for pattern in patterns:
            if fnmatch.fnmatch(value, pattern):
                return True
        return False

    def _matches_regex(self, value: str, patterns: list[str]) -> bool:
        for pattern in patterns:
            try:
                if re.search(pattern, value):
                    return True
            except re.error:
                continue
        return False

    def _matches_cidrs(self, value: str, patterns: list[str]) -> bool:
        try:
            ip = ipaddress.ip_address(value)
        except ValueError:
            return False
        for pattern in patterns:
            try:
                net = ipaddress.ip_network(pattern, strict=False)
            except ValueError:
                continue
            if ip in net:
                return True
        return False

    def _value_candidates(self, item: str) -> list[str]:
        host = extract_host(item)
        candidates = [item]
        if host:
            candidates.append(host)
        return candidates

    def is_oos(self, item: str) -> bool:
        for candidate in self._value_candidates(item):
            if self._matches_domains(candidate, self.exclude.domains):
                return True
            if self._matches_urls(candidate, self.exclude.urls):
                return True
            if self._matches_regex(candidate, self.exclude.regex):
                return True
            if self._matches_cidrs(candidate, self.exclude.cidrs):
                return True
        return False

    def is_in_scope(self, item: str) -> bool:
        if self.is_oos(item):
            return False
        for candidate in self._value_candidates(item):
            if self._matches_domains(candidate, self.include.domains):
                return True
            if self._matches_urls(candidate, self.include.urls):
                return True
            if self._matches_regex(candidate, self.include.regex):
                return True
        return False

    def partition_scope(self, items: Iterable[str]) -> tuple[list[str], list[str]]:
        in_scope: list[str] = []
        out_scope: list[str] = []
        for item in items:
            if self.is_in_scope(item):
                in_scope.append(item)
            else:
                out_scope.append(item)
        return in_scope, out_scope


def build_scope(target: str, include_path: Path | None, exclude_path: Path | None) -> Scope:
    include = (
        load_scope_file(include_path)
        if include_path
        else ScopeDefinition(domains=[f"*.{target}", target], urls=[], regex=[], cidrs=[])
    )
    exclude = (
        load_scope_file(exclude_path)
        if exclude_path
        else ScopeDefinition(domains=[], urls=[], regex=[], cidrs=[])
    )
    return Scope(include=include, exclude=exclude)
