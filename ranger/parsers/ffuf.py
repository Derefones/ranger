"""Parser for ffuf CSV output."""
from __future__ import annotations

import csv


def parse_ffuf(path: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append({key: (value or "") for key, value in row.items()})
    return rows
