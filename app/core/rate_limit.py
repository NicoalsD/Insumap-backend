"""In-memory sliding-window counter (login attempts). Single-process deployment."""

from datetime import datetime, timedelta
from threading import Lock

from app.core import clock


class SlidingWindowCounter:
    def __init__(self, max_hits: int, window: timedelta) -> None:
        self.max_hits = max_hits
        self.window = window
        self._hits: dict[str, list[datetime]] = {}
        self._lock = Lock()

    def _recent(self, key: str) -> list[datetime]:
        limit = clock.now() - self.window
        hits = [t for t in self._hits.get(key, []) if t > limit]
        self._hits[key] = hits
        return hits

    def is_blocked(self, key: str) -> bool:
        with self._lock:
            return len(self._recent(key)) >= self.max_hits

    def hit(self, key: str) -> None:
        with self._lock:
            self._recent(key).append(clock.now())

    def reset(self, key: str) -> None:
        with self._lock:
            self._hits.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._hits.clear()
