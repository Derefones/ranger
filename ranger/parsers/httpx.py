"""Parser for httpx JSON lines."""
from __future__ import annotations

import json
from collections.abc import Iterable

REQUIRED_FIELDS = {"host", "port", "scheme", "status", "title", "tech", "fingerprint", "tls", "cdn"}


def parse_httpx(lines: Iterable[str]) -> list[dict[str, object | None]]:
    rows: list[dict[str, object | None]] = []
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        row = {key: data.get(key) for key in REQUIRED_FIELDS}
        rows.append(row)
    return rows
