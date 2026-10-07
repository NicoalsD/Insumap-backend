"""E1 - Grid (2D matrix of microzones).

Fixed-size contiguous array of ``rows * cols``: cell ``(r, c)`` lives at index
``r * cols + c`` (0-indexed internally).
"""

from collections.abc import Callable, Iterator
from typing import Generic, TypeVar

T = TypeVar("T")

_DIRECTIONS: tuple[tuple[int, int], ...] = ((-1, 0), (1, 0), (0, -1), (0, 1))


class Grid(Generic[T]):
    def __init__(self, rows: int, cols: int, factory: Callable[[int, int], T]) -> None:
        if rows <= 0 or cols <= 0:
            raise ValueError("Grid must have at least one row and one column")
        self._rows = rows
        self._cols = cols
        self._data: list[T] = [factory(r, c) for r in range(rows) for c in range(cols)]

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def cols(self) -> int:
        return self._cols

    def _index(self, r: int, c: int) -> int:
        """O(1)."""
        if not (0 <= r < self._rows and 0 <= c < self._cols):
            raise IndexError(f"Cell ({r}, {c}) out of {self._rows}x{self._cols} grid")
        return r * self._cols + c

    def get(self, r: int, c: int) -> T:
        """O(1)."""
        return self._data[self._index(r, c)]

    def set(self, r: int, c: int, value: T) -> None:
        """O(1)."""
        self._data[self._index(r, c)] = value

    def neighbors(self, r: int, c: int) -> list[tuple[int, int]]:
        """Coordinates of the 4-directional neighbors. O(1)."""
        self._index(r, c)
        result: list[tuple[int, int]] = []
        for dr, dc in _DIRECTIONS:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self._rows and 0 <= nc < self._cols:
                result.append((nr, nc))
        return result

    def iterate(self) -> Iterator[tuple[int, int, T]]:
        """Row-major traversal. O(rows·cols)."""
        for i, value in enumerate(self._data):
            yield i // self._cols, i % self._cols, value

    def resize(self, rows: int, cols: int, factory: Callable[[int, int], T]) -> None:
        """Replace the grid with a new ``rows x cols`` one. O(rows·cols)."""
        if rows <= 0 or cols <= 0:
            raise ValueError("Grid must have at least one row and one column")
        self._rows = rows
        self._cols = cols
        self._data = [factory(r, c) for r in range(rows) for c in range(cols)]

    def __len__(self) -> int:
        return len(self._data)


def project_cell(row: int, col: int, from_size: int, to_size: int) -> tuple[int, int]:
    """Project a 1-indexed cell from a ``from_size`` grid to a ``to_size`` grid by
    proportional scaling: ``r' = floor((r-1)·n'/n) + 1``. O(1)."""
    return (row - 1) * to_size // from_size + 1, (col - 1) * to_size // from_size + 1
