"""E5 - Doubly linked list with ``head`` and ``tail`` sentinels.

Used for the injection history (R17-R19): O(1) insertion at the front, traversal in
both directions and O(1) removal of a known node.
"""

from collections.abc import Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class DNode(Generic[T]):
    __slots__ = ("value", "prev", "next")

    def __init__(self, value: T | None) -> None:
        self.value = value
        self.prev: DNode[T] | None = None
        self.next: DNode[T] | None = None

    def data(self) -> T:
        if self.value is None:
            raise ValueError("Sentinel node has no value")
        return self.value


class DoublyLinkedList(Generic[T]):
    def __init__(self) -> None:
        self._head: DNode[T] = DNode(None)
        self._tail: DNode[T] = DNode(None)
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0

    def _insert_between(self, value: T, before: DNode[T], after: DNode[T]) -> DNode[T]:
        node: DNode[T] = DNode(value)
        node.prev, node.next = before, after
        before.next = node
        after.prev = node
        self._size += 1
        return node

    def push_front(self, value: T) -> DNode[T]:
        """O(1)."""
        assert self._head.next is not None
        return self._insert_between(value, self._head, self._head.next)

    def push_back(self, value: T) -> DNode[T]:
        """O(1)."""
        assert self._tail.prev is not None
        return self._insert_between(value, self._tail.prev, self._tail)

    def remove(self, node: DNode[T]) -> T:
        """Unlink a known node. O(1)."""
        if node is self._head or node is self._tail or node.prev is None or node.next is None:
            raise ValueError("Cannot remove a sentinel or an unlinked node")
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = node.next = None
        self._size -= 1
        return node.data()

    def first(self) -> DNode[T] | None:
        n = self._head.next
        return None if n is self._tail else n

    def last(self) -> DNode[T] | None:
        n = self._tail.prev
        return None if n is self._head else n

    def iter_forward(self) -> Iterator[T]:
        """Head to tail. O(n)."""
        node = self._head.next
        while node is not None and node is not self._tail:
            yield node.data()
            node = node.next

    def iter_backward(self) -> Iterator[T]:
        """Tail to head. O(n)."""
        node = self._tail.prev
        while node is not None and node is not self._head:
            yield node.data()
            node = node.prev

    def iter_from(self, after: DNode[T] | None, forward: bool = True) -> Iterator[DNode[T]]:
        """Nodes strictly after ``after`` (or from the edge when None). O(1) per step."""
        if after is None:
            node = self._head.next if forward else self._tail.prev
        else:
            node = after.next if forward else after.prev
        while node is not None and node is not self._tail and node is not self._head:
            yield node
            node = node.next if forward else node.prev

    def page(self, after: DNode[T] | None, limit: int, forward: bool = True) -> list[T]:
        """Up to ``limit`` items **after** ``after`` (or from the edge when None). O(limit)."""
        if after is None:
            node = self._head.next if forward else self._tail.prev
        else:
            node = after.next if forward else after.prev
        result: list[T] = []
        while node is not None and node is not self._tail and node is not self._head and len(result) < limit:
            result.append(node.data())
            node = node.next if forward else node.prev
        return result

    def __len__(self) -> int:
        return self._size
