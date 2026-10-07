"""E6 - Undirected graph with an adjacency list (``HashTable[node -> neighbors]``).

Connects every microzone with its 4-directional neighbors (same side). A radius-``r``
BFS returns the microzones close to a recently used one (R11).
"""

from collections.abc import Hashable, Iterator
from typing import Generic, TypeVar

from app.domain.structures.hash_table import HashTable

N = TypeVar("N", bound=Hashable)


class _QueueNode(Generic[N]):
    __slots__ = ("value", "next")

    def __init__(self, value: tuple[N, int]) -> None:
        self.value = value
        self.next: _QueueNode[N] | None = None


class _Queue(Generic[N]):
    """Minimal linked FIFO queue for BFS (no ``collections.deque``)."""

    def __init__(self) -> None:
        self._front: _QueueNode[N] | None = None
        self._back: _QueueNode[N] | None = None

    def enqueue(self, value: tuple[N, int]) -> None:
        node = _QueueNode(value)
        if self._back is None:
            self._front = self._back = node
        else:
            self._back.next = node
            self._back = node

    def dequeue(self) -> tuple[N, int]:
        if self._front is None:
            raise IndexError("Queue is empty")
        node = self._front
        self._front = node.next
        if self._front is None:
            self._back = None
        return node.value

    def is_empty(self) -> bool:
        return self._front is None


class Graph(Generic[N]):
    def __init__(self) -> None:
        self._adj: HashTable[N, list[N]] = HashTable()
        self._edges = 0

    def add_node(self, node: N) -> None:
        if not self._adj.contains(node):
            self._adj.put(node, [])

    def add_edge(self, a: N, b: N) -> None:
        """Undirected edge. O(degree)."""
        self.add_node(a)
        self.add_node(b)
        neighbors_a = self._adj.get(a)
        if b not in neighbors_a:
            neighbors_a.append(b)
            self._adj.get(b).append(a)
            self._edges += 1

    def neighbors(self, node: N) -> list[N]:
        return list(self._adj.get(node))

    def degree(self, node: N) -> int:
        return len(self._adj.get(node))

    def bfs(self, origin: N, radius: int, include_origin: bool = False) -> list[N]:
        """Nodes at distance <= ``radius`` from ``origin``. O(V + E)."""
        visited: HashTable[N, bool] = HashTable()
        visited.put(origin, True)
        queue: _Queue[N] = _Queue()
        queue.enqueue((origin, 0))
        result: list[N] = [origin] if include_origin else []
        while not queue.is_empty():
            current, distance = queue.dequeue()
            if distance == radius:
                continue
            for neighbor in self._adj.get(current):
                if not visited.contains(neighbor):
                    visited.put(neighbor, True)
                    result.append(neighbor)
                    queue.enqueue((neighbor, distance + 1))
        return result

    def nodes(self) -> Iterator[N]:
        return self._adj.keys()

    @property
    def node_count(self) -> int:
        return len(self._adj)

    @property
    def edge_count(self) -> int:
        return self._edges
