"""Algorithm 5.4 - Reminder scheduler backed by an indexed min-heap (E4, R14-R16).

Priority is the ``scheduled_for`` timestamp. ``due`` pops every reminder that is due;
snoozing updates the priority in O(log n).
"""

from datetime import datetime
from threading import RLock

from app.domain.structures.heap import IndexedHeap


class ReminderScheduler:
    def __init__(self) -> None:
        self._heap: IndexedHeap[str] = IndexedHeap(minimum=True)
        self._lock = RLock()

    def schedule(self, reminder_id: str, when: datetime) -> None:
        """Insert or reschedule. O(log n)."""
        with self._lock:
            self._heap.push_key(reminder_id, when.timestamp())

    def snooze(self, reminder_id: str, when: datetime) -> None:
        self.schedule(reminder_id, when)

    def cancel(self, reminder_id: str) -> None:
        with self._lock:
            if self._heap.contains(reminder_id):
                self._heap.remove(reminder_id)

    def due(self, now: datetime) -> list[str]:
        """Pop reminders with ``scheduled_for <= now``. O(d log n)."""
        limit = now.timestamp()
        result: list[str] = []
        with self._lock:
            while not self._heap.is_empty() and self._heap.peek_key()[1] <= limit:
                result.append(self._heap.pop_key()[0])
        return result

    def next(self) -> tuple[str, float] | None:
        with self._lock:
            return None if self._heap.is_empty() else self._heap.peek_key()

    def contains(self, reminder_id: str) -> bool:
        return self._heap.contains(reminder_id)

    def clear(self) -> None:
        with self._lock:
            self._heap = IndexedHeap(minimum=True)

    def __len__(self) -> int:
        return len(self._heap)
