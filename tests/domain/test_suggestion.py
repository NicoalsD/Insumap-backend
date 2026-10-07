"""Example 5.3 from docs/Estructuras-de-datos-y-algoritmos.md as an acceptance test."""

from datetime import UTC, datetime

import pytest

from app.domain.algorithms.recovery import evaluate
from app.domain.algorithms.suggestion import suggest
from app.domain.models import Color, Microzone, Params
from app.domain.structures import Graph, HashTable

NOW = datetime(2026, 10, 20, 8, 0, tzinfo=UTC)
P = Params()


def reduced_fixture() -> tuple[list[Microzone], HashTable[str, int], Graph[str]]:
    zones = [
        Microzone("ABD-I-1-1", "ABD", "I", 1, 1, datetime(2026, 10, 19, 20, 0, tzinfo=UTC), 5),
        Microzone("ABD-D-2-2", "ABD", "D", 2, 2, datetime(2026, 10, 16, 8, 0, tzinfo=UTC), 4),
        Microzone("MUS-I-1-2", "MUS", "I", 1, 2, datetime(2026, 10, 15, 8, 0, tzinfo=UTC), 2),
        Microzone("GLU-D-1-1", "GLU", "D", 1, 1, None, 0),
    ]
    usage: HashTable[str, int] = HashTable()
    for m, u in {"ABD": 20, "MUS": 6, "BRA": 4, "GLU": 2}.items():
        usage.put(m, u)
    g: Graph[str] = Graph()
    g.add_edge("ABD-I-1-1", "ABD-I-1-2")
    g.add_edge("ABD-I-1-1", "ABD-I-2-1")
    for z in zones:
        g.add_node(z.id)
    return zones, usage, g


def test_example_colors():
    zones, _, _ = reduced_fixture()
    assert {z.id: evaluate(z, NOW, P).color for z in zones} == {
        "ABD-I-1-1": Color.RED,
        "ABD-D-2-2": Color.YELLOW,
        "MUS-I-1-2": Color.GREEN,
        "GLU-D-1-1": Color.GREEN,
    }


def test_example_5_3_scores_and_order():
    zones, usage, g = reduced_fixture()
    result = suggest(zones, usage, g, NOW, P, k=4)
    assert [s.microzone_id for s in result] == ["GLU-D-1-1", "MUS-I-1-2", "ABD-D-2-2", "ABD-I-1-1"]
    scores = {s.microzone_id: s.score for s in result}
    assert scores["GLU-D-1-1"] == pytest.approx(2.5)
    assert scores["MUS-I-1-2"] == pytest.approx(120 / 115.2)
    assert scores["ABD-D-2-2"] == pytest.approx(96 / 100.8 - 2.0)
    assert scores["ABD-I-1-1"] == pytest.approx(12 / 108 - 2.0)
    assert all(s.neighbor_penalty == 0 for s in result)


def test_top_3():
    zones, usage, g = reduced_fixture()
    assert [s.microzone_id for s in suggest(zones, usage, g, NOW, P, k=3)] == [
        "GLU-D-1-1",
        "MUS-I-1-2",
        "ABD-D-2-2",
    ]
