"""E7 - LRU cache = HashTable (E2) + DoublyLinkedList (E5).

The table points to list nodes ordered from most recently used (front) to least
recently used (back). Every operation is O(1).
"""

from collections.abc import Hashable
from typing import Generic, TypeVar

from app.domain.structures.doubly_linked_list import DNode, DoublyLinkedList
from app.domain.structures.hash_table import HashTable

K = TypeVar("K", bound=Hashable)
V = TypeVar("V")


class LRUCache(Generic[K, V]):
    def __init__(self, capacity: int = 128) -> None:
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self._capacity = capacity
        self._map: HashTable[K, DNode[tuple[K, V]]] = HashTable()
        self._order: DoublyLinkedList[tuple[K, V]] = DoublyLinkedList()

    def _node(self, key: K) -> DNode[tuple[K, V]] | None:
        return self._map.get(key) if self._map.contains(key) else None

    def get(self, key: K) -> V | None:
        """Return the value and mark it as most recent. O(1)."""
        node = self._node(key)
        if node is None:
            return None
        pair = self._order.remove(node)
        self._map.put(key, self._order.push_front(pair))
        return pair[1]

    def put(self, key: K, value: V) -> None:
        """Insert or replace; evict the least recent one when over capacity. O(1)."""
        existing = self._node(key)
        if existing is not None:
            self._order.remove(existing)
        self._map.put(key, self._order.push_front((key, value)))
        if len(self._order) > self._capacity:
            last = self._order.last()
            assert last is not None
            old_key, _ = self._order.remove(last)
            self._map.remove(old_key)

    def invalidate(self, key: K) -> None:
        """O(1)."""
        node = self._node(key)
        if node is not None:
            self._order.remove(node)
            self._map.remove(key)

    def clear(self) -> None:
        self._map = HashTable()
        self._order = DoublyLinkedList()

    def contains(self, key: K) -> bool:
        return self._map.contains(key)

    def __len__(self) -> int:
        return len(self._order)
