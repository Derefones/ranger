"""Structured logging helpers."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class LogRecord:
    """A structured log record."""

    level: str
    message: str
    fields: Mapping[str, Any]
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ts": self.timestamp.isoformat(timespec="seconds"),
            "level": self.level,
            "msg": self.message,
        }
        payload.update(self.fields)
        return payload


def _now() -> datetime:
    return datetime.now(UTC)


def log(level: str, message: str, **fields: Any) -> LogRecord:
    """Create a structured log record."""
    record = LogRecord(level=level.upper(), message=message, fields=fields, timestamp=_now())
    return record


def info(message: str, **fields: Any) -> LogRecord:
    return log("INFO", message, **fields)


def warning(message: str, **fields: Any) -> LogRecord:
    return log("WARNING", message, **fields)


def error(message: str, **fields: Any) -> LogRecord:
    return log("ERROR", message, **fields)
