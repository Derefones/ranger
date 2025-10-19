"""Generic resilient parsers."""
from __future__ import annotations

import csv
import json
from collections.abc import Iterator
from pathlib import Path


def iter_csv(path: Path) -> Iterator[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield {key: (value or "") for key, value in row.items()}


def iter_jsonl(path: Path) -> Iterator[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip().lstrip("\ufeff")
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue
