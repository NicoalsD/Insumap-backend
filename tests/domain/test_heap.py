import random

import pytest

from app.domain.structures import EmptyHeapError, Heap, IndexedHeap


def max_heap() -> Heap[int]:
    return Heap(lambda a, b: a > b)


def test_empty():
    with pytest.raises(EmptyHeapError):
        max_heap().pop()


def test_property_after_every_operation():
    rnd = random.Random(1)
    h = max_heap()
    for _ in range(500):
        h.push(rnd.randint(0, 1000))
        assert h.is_valid()
    prev = 10**9
    while not h.is_empty():
        x = h.pop()
        assert x <= prev
        prev = x
        assert h.is_valid()


def test_build_and_top_k_against_sorted():
    data = random.Random(2).sample(range(10_000), 1000)
    h = max_heap()
    h.build(data)
    assert h.is_valid()
    assert h.top_k(10) == sorted(data, reverse=True)[:10]
    assert len(h) == 1000  # top_k does not mutate


def test_build_matches_pushes():
    data = random.Random(3).sample(range(500), 200)
    a, b = max_heap(), max_heap()
    a.build(data)
    for x in data:
        b.push(x)
    assert a.top_k(200) == b.top_k(200)


def test_indexed_update_up_and_down():
    h: IndexedHeap[str] = IndexedHeap(minimum=True)
    for i, k in enumerate("abcdef"):
        h.push_key(k, float(i))
    h.update_priority("f", -1.0)
    assert h.peek_key() == ("f", -1.0)
    h.update_priority("f", 100.0)
    assert h.peek_key() == ("a", 0.0)
    assert h.is_valid()


def test_indexed_remove_by_key():
    rnd = random.Random(4)
    h: IndexedHeap[int] = IndexedHeap(minimum=True)
    ref = {i: rnd.random() for i in range(300)}
    for k, p in ref.items():
        h.push_key(k, p)
    for k in rnd.sample(list(ref), 150):
        h.remove(k)
        del ref[k]
        assert h.is_valid()
    order = [h.pop_key()[0] for _ in range(len(h))]
    assert order == sorted(ref, key=ref.__getitem__)
