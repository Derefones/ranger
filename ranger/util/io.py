"""Filesystem helpers for atomic writes."""
from __future__ import annotations

import csv
import json
import os
import tempfile
from collections.abc import Iterable, Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=str(path.parent), delete=False) as tmp:
        tmp.write(data)
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def write_text(path: Path, content: str) -> None:
    _atomic_write(path, content.encode("utf-8"))


def write_lines(path: Path, lines: Iterable[str]) -> None:
    items = list(lines)
    suffix = "\n" if items else ""
    write_text(path, "\n".join(items) + suffix)


def write_json(path: Path, payload: object) -> None:
    data = json.dumps(payload, sort_keys=True, indent=2)
    write_text(path, data + "\n")


def write_jsonl(path: Path, rows: Iterable[object]) -> None:
    buf = "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
    write_text(path, buf)


def append_jsonl(path: Path, rows: Iterable[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True))
            handle.write("\n")


@contextmanager
def csv_writer(path: Path, headers: Sequence[str]) -> Iterator[csv.DictWriter[str]]:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        newline="",
        dir=str(path.parent),
        delete=False,
    ) as tmp:
        writer = csv.DictWriter(tmp, fieldnames=list(headers))
        writer.writeheader()
        yield writer
        tmp.flush()
        os.fsync(tmp.fileno())
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def stream_jsonl(path: Path) -> Iterator[dict[str, object]]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue
