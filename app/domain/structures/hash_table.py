"""E2 - Hash table with separate chaining.

Array of buckets; each bucket is a singly linked list of (key, value) nodes.
Capacity doubles (rehash) when the load factor exceeds 0.75.
"""

from collections.abc import Hashable, Iterator
from typing import Generic, TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")

MAX_LOAD_FACTOR = 0.75
_INITIAL_CAPACITY = 16


class _Node(Generic[K, V]):
    __slots__ = ("key", "value", "next")

    def __init__(self, key: K, value: V, next_: "_Node[K, V] | None") -> None:
        self.key = key
        self.value = value
        self.next = next_


class HashTable(Generic[K, V]):
    def __init__(self, capacity: int = _INITIAL_CAPACITY) -> None:
        self._capacity = max(1, capacity)
        self._buckets: list[_Node[K, V] | None] = [None] * self._capacity
        self._size = 0

    def _slot(self, key: K, capacity: int | None = None) -> int:
        return hash(key) % (capacity or self._capacity)

    def _find(self, key: K) -> _Node[K, V] | None:
        node = self._buckets[self._slot(key)]
        while node is not None:
            if node.key == key:
                return node
            node = node.next
        return None

    def get(self, key: K) -> V:
        """O(1) average, O(n) worst case. Raises ``KeyError`` if missing."""
        node = self._find(key)
        if node is None:
            raise KeyError(key)
        return node.value

    def get_or(self, key: K, default: V) -> V:
        node = self._find(key)
        return default if node is None else node.value

    def contains(self, key: K) -> bool:
        return self._find(key) is not None

    def put(self, key: K, value: V) -> None:
        """Insert or replace. O(1) amortized."""
        node = self._find(key)
        if node is not None:
            node.value = value
            return
        slot = self._slot(key)
        self._buckets[slot] = _Node(key, value, self._buckets[slot])
        self._size += 1
        if self._size / self._capacity > MAX_LOAD_FACTOR:
            self._rehash()

    def remove(self, key: K) -> V:
        """O(1) average. Raises ``KeyError`` if missing."""
        slot = self._slot(key)
        prev: _Node[K, V] | None = None
        node = self._buckets[slot]
        while node is not None:
            if node.key == key:
                if prev is None:
                    self._buckets[slot] = node.next
                else:
                    prev.next = node.next
                self._size -= 1
                return node.value
            prev, node = node, node.next
        raise KeyError(key)

    def _rehash(self) -> None:
        """Double the capacity and relocate every node. O(n)."""
        new_capacity = self._capacity * 2
        buckets: list[_Node[K, V] | None] = [None] * new_capacity
        for head in self._buckets:
            node = head
            while node is not None:
                nxt = node.next
                slot = self._slot(node.key, new_capacity)
                node.next = buckets[slot]
                buckets[slot] = node
                node = nxt
        self._buckets = buckets
        self._capacity = new_capacity

    def items(self) -> Iterator[tuple[K, V]]:
        for head in self._buckets:
            node = head
            while node is not None:
                yield node.key, node.value
                node = node.next

    def keys(self) -> Iterator[K]:
        for key, _ in self.items():
            yield key

    def values(self) -> Iterator[V]:
        for _, value in self.items():
            yield value

    @property
    def capacity(self) -> int:
        return self._capacity

    def __len__(self) -> int:
        return self._size
