"""``PatientState``: groups the data structures of one patient (section 3 of the docs).

    grids          : HashTable[(macro, side) -> Grid[Microzone]]   (E2 + E1)
    index          : HashTable[microzone_id -> Microzone]          (E2)
    neighborhood   : Graph[microzone_id]                           (E6)
    undo_stack     : Stack[UndoAction]                             (E3)
    history        : DoublyLinkedList[InjectionView]               (E5) + id -> node (E2)
    macro_usage    : HashTable[macro -> uses within the window]    (E2)

The database is the source of truth: the state is built from it in O(M + I) and kept in
sync by applying every write (register / undo) after the commit.
"""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from app.domain.algorithms.recovery import evaluate
from app.domain.algorithms.suggestion import Suggestion, suggest
from app.domain.models import (
    MACRO_LABELS,
    MACROS,
    SIDES,
    InjectionStatus,
    InjectionView,
    Microzone,
    Params,
    UndoAction,
    format_id,
    parse_id,
)
from app.domain.structures.doubly_linked_list import DNode, DoublyLinkedList
from app.domain.structures.graph import Graph
from app.domain.structures.grid import Grid, project_cell
from app.domain.structures.hash_table import HashTable
from app.domain.structures.stack import Stack


@dataclass(frozen=True)
class InjectionData:
    """Raw injection as read from the database (with the grid size used at registration)."""

    id: str
    macro: str
    side: str
    row: int
    col: int
    grid_size: int
    applied_at: datetime
    registered_at: datetime
    status: InjectionStatus
    undone_at: datetime | None = None


class PatientState:
    def __init__(self, grid_size: int, params: Params) -> None:
        self.grid_size = grid_size
        self.params = params
        self.grids: HashTable[tuple[str, str], Grid[Microzone]] = HashTable()
        self.index: HashTable[str, Microzone] = HashTable()
        self.neighborhood: Graph[str] = Graph()
        self.undo_stack: Stack[UndoAction] = Stack()
        self.history: DoublyLinkedList[InjectionView] = DoublyLinkedList()
        self.history_nodes: HashTable[str, DNode[InjectionView]] = HashTable()
        self.macro_usage: HashTable[str, int] = HashTable()
        self._create_grids()

    # ------------------------------------------------------------------ build
    def _create_grids(self) -> None:
        n = self.grid_size
        for macro in MACROS:
            self.macro_usage.put(macro, 0)
            for side in SIDES:
                grid: Grid[Microzone] = Grid(n, n, self._factory(macro, side))
                self.grids.put((macro, side), grid)
                for r, c, mz in grid.iterate():
                    self.index.put(mz.id, mz)
                    self.neighborhood.add_node(mz.id)
                    for nr, nc in grid.neighbors(r, c):
                        self.neighborhood.add_edge(mz.id, grid.get(nr, nc).id)

    @staticmethod
    def _factory(macro: str, side: str) -> Callable[[int, int], Microzone]:
        def make(r: int, c: int) -> Microzone:
            return Microzone(format_id(macro, side, r + 1, c + 1), macro, side, r + 1, c + 1)

        return make

    @classmethod
    def build(
        cls, grid_size: int, injections: Iterable[InjectionData], now: datetime, params: Params
    ) -> "PatientState":
        """``injections`` must be sorted by ``registered_at`` ascending. O(M + I)."""
        state = cls(grid_size, params)
        for data in injections:
            state._apply(data, now)
        return state

    def _view(self, d: InjectionData) -> InjectionView:
        r, c = project_cell(d.row, d.col, d.grid_size, self.grid_size)
        return InjectionView(
            id=d.id,
            microzone_id=format_id(d.macro, d.side, r, c),
            macro=d.macro,
            side=d.side,
            row=r,
            col=c,
            applied_at=d.applied_at,
            registered_at=d.registered_at,
            status=d.status,
            undone_at=d.undone_at,
            original_microzone_id=format_id(d.macro, d.side, d.row, d.col),
        )

    def _apply(self, d: InjectionData, now: datetime) -> UndoAction | None:
        view = self._view(d)
        self.history_nodes.put(view.id, self.history.push_front(view))
        if d.status != InjectionStatus.REGISTERED:
            return None
        mz = self.index.get(view.microzone_id)
        in_window = d.applied_at >= now - timedelta(days=self.params.usage_window_days)
        action = UndoAction(
            injection_id=d.id,
            microzone_id=mz.id,
            macro=mz.macro,
            registered_at=d.registered_at,
            previous_last_used=mz.last_used,
            previous_uses_30d=mz.uses_30d,
            counted_in_window=in_window,
        )
        if mz.last_used is None or d.applied_at > mz.last_used:
            mz.last_used = d.applied_at
        if in_window:
            mz.uses_30d += 1
            self.macro_usage.put(mz.macro, self.macro_usage.get(mz.macro) + 1)
        if d.registered_at >= now - timedelta(hours=self.params.undo_window_hours):
            self.undo_stack.push(action)
        return action

    # ------------------------------------------------------------------ writes
    def microzone(self, microzone_id: str) -> Microzone:
        """O(1) hash table lookup; validates the id against the current grid."""
        parse_id(microzone_id, self.grid_size)
        return self.index.get(microzone_id)

    def register(self, data: InjectionData, now: datetime) -> UndoAction:
        action = self._apply(data, now)
        assert action is not None
        return action

    def undoable(self, now: datetime) -> UndoAction | None:
        """Top of the stack if still inside the undo window. O(1)."""
        if self.undo_stack.is_empty():
            return None
        action = self.undo_stack.peek()
        if action.registered_at < now - timedelta(hours=self.params.undo_window_hours):
            return None
        return action

    def apply_undo(self, undone_at: datetime) -> UndoAction:
        """Pop and restore the microzone snapshot (R06). O(1)."""
        action = self.undo_stack.pop()
        mz = self.index.get(action.microzone_id)
        mz.last_used = action.previous_last_used
        mz.uses_30d = action.previous_uses_30d
        if action.counted_in_window:
            self.macro_usage.put(action.macro, max(0, self.macro_usage.get(action.macro) - 1))
        view = self.history_nodes.get(action.injection_id).data()
        view.status = InjectionStatus.UNDONE
        view.undone_at = undone_at
        return action

    # ------------------------------------------------------------------ reads
    def evaluate_microzone(self, mz: Microzone, now: datetime) -> dict[str, Any]:
        ev = evaluate(mz, now, self.params)
        return {
            "id": mz.id,
            "row": mz.row,
            "col": mz.col,
            "color": ev.color.value,
            "ratio": round(ev.ratio, 4),
            "hours_remaining": round(ev.hours_remaining, 1),
            "last_used": mz.last_used,
            "uses_30d": mz.uses_30d,
        }

    def body_map(self, now: datetime, macro: str | None = None) -> list[dict[str, Any]]:
        """Traverse the 8 grids. O(M)."""
        zones: list[dict[str, Any]] = []
        for m in MACROS:
            if macro and m != macro:
                continue
            sides = []
            for side in SIDES:
                grid = self.grids.get((m, side))
                sides.append(
                    {"side": side, "cells": [self.evaluate_microzone(mz, now) for _, _, mz in grid.iterate()]}
                )
            zones.append({"macro": m, "label": MACRO_LABELS[m], "sides": sides})
        return zones

    def suggestions(self, now: datetime, k: int | None = None) -> list[Suggestion]:
        return suggest(
            list(self.index.values()),
            self.macro_usage,
            self.neighborhood,
            now,
            self.params,
            k or self.params.top_k,
        )

    def latest_for(self, microzone_id: str, limit: int = 5) -> list[InjectionView]:
        result: list[InjectionView] = []
        for v in self.history.iter_forward():
            if v.microzone_id == microzone_id:
                result.append(v)
                if len(result) == limit:
                    break
        return result
