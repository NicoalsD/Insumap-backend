import random

import pytest

from app.domain.structures import HashTable


class Collides:
    """Every instance lands in the same bucket."""

    def __init__(self, v: int) -> None:
        self.v = v

    def __hash__(self) -> int:
        return 7

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Collides) and o.v == self.v


def test_put_get_replace():
    t: HashTable[str, int] = HashTable()
    t.put("a", 1)
    t.put("a", 2)
    assert t.get("a") == 2
    assert len(t) == 1


def test_forced_collisions():
    t: HashTable[Collides, int] = HashTable()
    for i in range(50):
        t.put(Collides(i), i)
    assert all(t.get(Collides(i)) == i for i in range(50))
    assert t.remove(Collides(25)) == 25
    assert not t.contains(Collides(25))
    assert len(t) == 49


def test_rehash_over_load_factor():
    t: HashTable[int, int] = HashTable(capacity=4)
    for i in range(4):
        t.put(i, i)
    assert t.capacity == 8
    assert all(t.get(i) == i for i in range(4))


def test_missing_key():
    t: HashTable[str, int] = HashTable()
    with pytest.raises(KeyError):
        t.remove("x")
    with pytest.raises(KeyError):
        t.get("x")


def test_against_reference_dict():
    rnd = random.Random(42)
    t: HashTable[int, int] = HashTable()
    ref: dict[int, int] = {}
    for _ in range(10_000):
        k = rnd.randint(0, 2000)
        if rnd.random() < 0.7:
            v = rnd.randint(0, 10**6)
            t.put(k, v)
            ref[k] = v
        elif k in ref:
            assert t.remove(k) == ref.pop(k)
    assert len(t) == len(ref)
    assert dict(t.items()) == ref
