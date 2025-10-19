"""Parser for nuclei JSONL."""
from __future__ import annotations

import json
from collections.abc import Iterable


def parse_nuclei(lines: Iterable[str]) -> list[dict[str, object | None]]:
    results: list[dict[str, object | None]] = []
    for raw in lines:
        raw = raw.strip()
        if not raw:
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        info = data.get("info") if isinstance(data.get("info"), dict) else {}
        entry = {
            "template_id": data.get("templateID"),
            "name": info.get("name"),
            "severity": info.get("severity"),
            "type": data.get("type"),
            "host": data.get("host"),
            "url": data.get("matched-at"),
            "evidence": data.get("matcher-status"),
        }
        results.append(entry)
    return results
