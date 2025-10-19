"""Token bucket rate limiter."""
from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field


@dataclass(slots=True)
class RateLimiter:
    """Simple token bucket limiter."""

    rate: float
    burst: int
    _tokens: float = field(default=0.0, init=False)
    _last: float = field(default=0.0, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def __post_init__(self) -> None:
        if self.rate <= 0:
            raise ValueError("rate must be positive")
        if self.burst <= 0:
            raise ValueError("burst must be positive")
        self._tokens = float(self.burst)
        self._last = time.monotonic()

    def acquire(self, tokens: float = 1.0) -> None:
        if tokens <= 0:
            return
        with self._lock:
            while True:
                now = time.monotonic()
                elapsed = now - self._last
                self._last = now
                self._tokens = min(self.burst, self._tokens + elapsed * self.rate)
                if self._tokens >= tokens:
                    self._tokens -= tokens
                    return
                deficit = tokens - self._tokens
                wait_time = deficit / self.rate
                time.sleep(wait_time)

    def await_or_sleep(self) -> None:
        self.acquire(1.0)
