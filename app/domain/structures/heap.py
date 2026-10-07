"""E4 - Array-based binary heap with an injected comparator (max or min).

* ``Heap``: generic priority queue. Used as the **max-heap** of suggestions (R11-R13).
* ``IndexedHeap``: adds a ``HashTable[key -> position]`` to update priorities or remove
  by key in O(log n). Used as the **min-heap** of reminders (R14-R16).
"""

from collections.abc import Callable, Hashable, Iterable
from typing import Generic, TypeVar

from app.domain.structures.hash_table import HashTable

T = TypeVar("T")
K = TypeVar("K", bound=Hashable)


class EmptyHeapError(IndexError):
    pass


class Heap(Generic[T]):
    """``before(a, b)`` returns True when ``a`` must be closer to the root than ``b``."""

    def __init__(self, before: Callable[[T, T], bool]) -> None:
        self._before = before
        self._arr: list[T] = []

    # --- internals ---------------------------------------------------------------
    def _swap(self, i: int, j: int) -> None:
        self._arr[i], self._arr[j] = self._arr[j], self._arr[i]

    def _sift_up(self, i: int) -> None:
        """O(log n)."""
        while i > 0:
            parent = (i - 1) // 2
            if self._before(self._arr[i], self._arr[parent]):
                self._swap(i, parent)
                i = parent
            else:
                break

    def _sift_down(self, i: int) -> None:
        """O(log n)."""
        n = len(self._arr)
        while True:
            best = i
            left, right = 2 * i + 1, 2 * i + 2
            if left < n and self._before(self._arr[left], self._arr[best]):
                best = left
            if right < n and self._before(self._arr[right], self._arr[best]):
                best = right
            if best == i:
                return
            self._swap(i, best)
            i = best

    def _on_build(self) -> None:
        """Hook for subclasses that keep indexes."""

    def _on_push(self, position: int) -> None:
        """Hook for subclasses that keep indexes."""

    def _on_pop(self, value: T) -> None:
        """Hook for subclasses that keep indexes."""

    # --- public API ----------------------------------------------------------------
    def build(self, items: Iterable[T]) -> None:
        """Floyd's heapify; replaces the content. O(n)."""
        self._arr = list(items)
        self._on_build()
        for i in range(len(self._arr) // 2 - 1, -1, -1):
            self._sift_down(i)

    def push(self, value: T) -> None:
        """O(log n)."""
        self._arr.append(value)
        self._on_push(len(self._arr) - 1)
        self._sift_up(len(self._arr) - 1)

    def peek(self) -> T:
        """O(1)."""
        if not self._arr:
            raise EmptyHeapError("Heap is empty")
        return self._arr[0]

    def pop(self) -> T:
        """O(log n)."""
        if not self._arr:
            raise EmptyHeapError("Heap is empty")
        top = self._arr[0]
        self._swap(0, len(self._arr) - 1)
        self._arr.pop()
        self._on_pop(top)
        if self._arr:
            self._sift_down(0)
        return top

    def top_k(self, k: int) -> list[T]:
        """Best ``k`` items without modifying the heap. O(n + k log n)."""
        copy: Heap[T] = Heap(self._before)
        copy._arr = list(self._arr)
        result: list[T] = []
        while copy._arr and len(result) < k:
            result.append(copy.pop())
        return result

    def is_empty(self) -> bool:
        return not self._arr

    def is_valid(self) -> bool:
        """Check the heap property (for tests). O(n)."""
        n = len(self._arr)
        for i in range(n):
            for child in (2 * i + 1, 2 * i + 2):
                if child < n and self._before(self._arr[child], self._arr[i]):
                    return False
        return True

    def __len__(self) -> int:
        return len(self._arr)


class _Entry(Generic[K]):
    __slots__ = ("key", "priority")

    def __init__(self, key: K, priority: float) -> None:
        self.key = key
        self.priority = priority


class IndexedHeap(Heap[_Entry[K]], Generic[K]):
    """Heap of keys with numeric priority and access by key. ``minimum=True`` -> min-heap."""

    def __init__(self, minimum: bool = True) -> None:
        if minimum:
            super().__init__(lambda a, b: a.priority < b.priority)
        else:
            super().__init__(lambda a, b: a.priority > b.priority)
        self._pos: HashTable[K, int] = HashTable()

    def _swap(self, i: int, j: int) -> None:
        super()._swap(i, j)
        self._pos.put(self._arr[i].key, i)
        self._pos.put(self._arr[j].key, j)

    def _on_build(self) -> None:
        self._pos = HashTable()
        for i, entry in enumerate(self._arr):
            self._pos.put(entry.key, i)

    def _on_push(self, position: int) -> None:
        self._pos.put(self._arr[position].key, position)

    def _on_pop(self, value: _Entry[K]) -> None:
        self._pos.remove(value.key)

    def contains(self, key: K) -> bool:
        return self._pos.contains(key)

    def push_key(self, key: K, priority: float) -> None:
        """Insert, or update the priority if the key already exists. O(log n)."""
        if self.contains(key):
            self.update_priority(key, priority)
        else:
            self.push(_Entry(key, priority))

    def update_priority(self, key: K, priority: float) -> None:
        """O(log n): sifts the entry up or down."""
        i = self._pos.get(key)
        self._arr[i].priority = priority
        self._sift_up(i)
        self._sift_down(self._pos.get(key))

    def remove(self, key: K) -> None:
        """O(log n)."""
        i = self._pos.get(key)
        self._swap(i, len(self._arr) - 1)
        removed = self._arr.pop()
        self._pos.remove(removed.key)
        if i < len(self._arr):
            moved = self._arr[i].key
            self._sift_up(i)
            self._sift_down(self._pos.get(moved))

    def peek_key(self) -> tuple[K, float]:
        entry = self.peek()
        return entry.key, entry.priority

    def pop_key(self) -> tuple[K, float]:
        entry = self.pop()
        return entry.key, entry.priority
