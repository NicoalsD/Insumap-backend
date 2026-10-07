"""E3 - Stack (LIFO) over linked nodes. Used to undo injections (R05, R06)."""

from collections.abc import Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class _Node(Generic[T]):
    __slots__ = ("value", "below")

    def __init__(self, value: T, below: "_Node[T] | None") -> None:
        self.value = value
        self.below = below


class EmptyStackError(IndexError):
    pass


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._top: _Node[T] | None = None
        self._size = 0

    def push(self, value: T) -> None:
        """O(1)."""
        self._top = _Node(value, self._top)
        self._size += 1

    def pop(self) -> T:
        """O(1). Raises ``EmptyStackError`` when empty."""
        if self._top is None:
            raise EmptyStackError("Stack is empty")
        node = self._top
        self._top = node.below
        self._size -= 1
        return node.value

    def peek(self) -> T:
        """O(1)."""
        if self._top is None:
            raise EmptyStackError("Stack is empty")
        return self._top.value

    def is_empty(self) -> bool:
        return self._top is None

    def __iter__(self) -> Iterator[T]:
        """From top to bottom."""
        node = self._top
        while node is not None:
            yield node.value
            node = node.below

    def __len__(self) -> int:
        return self._size
