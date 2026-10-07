"""Algorithm 5.2 - Optimal injection point suggestion (R11-R13). O(M + k log M).

    score(z) = ratio(z) + β·forgotten(z) − γ·overuse(macro(z)) − δ·recent_neighbor(z)

* forgotten: unused for >= ``forgotten_days`` days (or never used)               (R13)
* overuse(m) = max(0, (uses_m − avg_others) / max(avg_others, 1))                (R12)
* recent_neighbor: reached by a BFS (radius r, origin excluded) from a microzone
  used within the last ``neighbor_hours`` hours                                  (E6)

Microzones are ranked with a max-heap (E4); ties: larger h first, then ascending id.
"""

import math
from dataclasses import dataclass
from datetime import datetime

from app.domain.algorithms.recovery import evaluate
from app.domain.models import MACROS, Color, Microzone, Params
from app.domain.structures.graph import Graph
from app.domain.structures.hash_table import HashTable
from app.domain.structures.heap import Heap


@dataclass(frozen=True)
class Suggestion:
    microzone_id: str
    score: float
    color: Color
    ratio: float
    hours_since: float
    forgotten_bonus: float
    overuse_penalty: float
    neighbor_penalty: float


def overuse_by_macro(macro_usage: HashTable[str, int]) -> HashTable[str, float]:
    result: HashTable[str, float] = HashTable()
    for m in MACROS:
        others = [macro_usage.get_or(o, 0) for o in MACROS if o != m]
        avg = sum(others) / len(others)
        result.put(m, max(0.0, (macro_usage.get_or(m, 0) - avg) / max(avg, 1.0)))
    return result


def recent_neighbors(
    microzones: list[Microzone], neighborhood: Graph[str] | None, now: datetime, p: Params
) -> HashTable[str, bool]:
    penalized: HashTable[str, bool] = HashTable()
    if neighborhood is None:
        return penalized
    for z in microzones:
        if z.last_used is None:
            continue
        if (now - z.last_used).total_seconds() / 3600.0 < p.neighbor_hours:
            for n in neighborhood.bfs(z.id, p.neighbor_radius, include_origin=False):
                penalized.put(n, True)
    return penalized


def _before(a: Suggestion, b: Suggestion) -> bool:
    """Max-heap order: score desc, hours_since desc, id asc."""
    if a.score != b.score:
        return a.score > b.score
    if a.hours_since != b.hours_since:
        return a.hours_since > b.hours_since
    return a.microzone_id < b.microzone_id


def suggest(
    microzones: list[Microzone],
    macro_usage: HashTable[str, int],
    neighborhood: Graph[str] | None,
    now: datetime,
    p: Params,
    k: int,
) -> list[Suggestion]:
    overuse = overuse_by_macro(macro_usage)
    penalized = recent_neighbors(microzones, neighborhood, now, p)
    items: list[Suggestion] = []
    for z in microzones:
        ev = evaluate(z, now, p)
        forgotten = math.isinf(ev.hours_since) or ev.hours_since >= p.forgotten_days * 24
        bonus = p.forgotten_beta if forgotten else 0.0
        overuse_pen = p.overuse_gamma * overuse.get(z.macro)
        neighbor_pen = p.neighbor_delta if penalized.contains(z.id) else 0.0
        score = round(ev.ratio + bonus - overuse_pen - neighbor_pen, 9)
        items.append(
            Suggestion(z.id, score, ev.color, ev.ratio, ev.hours_since, bonus, overuse_pen, neighbor_pen)
        )
    heap: Heap[Suggestion] = Heap(_before)
    heap.build(items)
    return heap.top_k(k)
