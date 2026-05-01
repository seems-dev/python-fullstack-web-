from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class TokenBucket:
    capacity: int
    refill_per_sec: float
    tokens: float
    last: float


class RateLimiter:
    """
    Tiny in-memory rate limiter (per-process).

    Good enough for dev/stress demos; for production you'd use Redis, etc.
    """

    def __init__(self) -> None:
        self._buckets: dict[str, TokenBucket] = {}

    def allow(self, key: str, *, capacity: int, refill_per_sec: float, cost: float = 1.0) -> bool:
        now = time.monotonic()
        b = self._buckets.get(key)
        if b is None:
            b = TokenBucket(capacity=capacity, refill_per_sec=refill_per_sec, tokens=float(capacity), last=now)
            self._buckets[key] = b
        else:
            elapsed = max(0.0, now - b.last)
            b.tokens = min(float(b.capacity), b.tokens + elapsed * b.refill_per_sec)
            b.last = now

        if b.tokens < cost:
            return False
        b.tokens -= cost
        return True


limiter = RateLimiter()


__all__ = ["RateLimiter", "limiter"]

