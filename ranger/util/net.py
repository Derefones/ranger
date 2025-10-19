"""Network helpers."""
from __future__ import annotations

import ipaddress
import re
from collections.abc import Iterable
from urllib.parse import urljoin as _urljoin
from urllib.parse import urlparse

_HOST_RE = re.compile(r"^[A-Za-z0-9.-]+$")


def normalize_host(host: str) -> str:
    host = host.strip().lower().rstrip('.')
    return host


def is_ip(value: str) -> bool:
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return False
    return True


def extract_host(url: str) -> str | None:
    parsed = urlparse(url)
    if parsed.hostname:
        return normalize_host(parsed.hostname)
    return None


def url_join(base: str, *paths: str) -> str:
    result = base
    for path in paths:
        result = _urljoin(result.rstrip('/') + '/', path)
    return result


def dedupe_preserve_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            output.append(item)
    return output


def looks_like_host(value: str) -> bool:
    return bool(_HOST_RE.match(value))
