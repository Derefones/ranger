"""Parser for subzy CSV output."""
from __future__ import annotations

import csv


def parse_subzy(path: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    with open(path, encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            normalised = {key: (value or "") for key, value in row.items()}
            verified = normalised.get("verified", "").lower() in {"true", "1", "yes"}
            normalised["verified"] = str(verified)
            rows.append(normalised)
    return rows
