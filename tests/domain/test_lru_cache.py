from app.domain.structures import LRUCache


def test_evicts_least_recent():
    c: LRUCache[str, int] = LRUCache(2)
    c.put("a", 1)
    c.put("b", 2)
    assert c.get("a") == 1  # refreshes "a"
    c.put("c", 3)
    assert c.get("b") is None
    assert c.get("a") == 1 and c.get("c") == 3


def test_capacity_one_and_invalidate():
    c: LRUCache[str, int] = LRUCache(1)
    c.put("a", 1)
    c.put("b", 2)
    assert not c.contains("a")
    c.invalidate("b")
    assert len(c) == 0


def test_replace_does_not_duplicate():
    c: LRUCache[str, int] = LRUCache(3)
    c.put("a", 1)
    c.put("a", 2)
    assert len(c) == 1 and c.get("a") == 2
