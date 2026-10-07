import pytest

from app.domain.structures import EmptyStackError, Stack


def test_empty_stack():
    s: Stack[int] = Stack()
    assert s.is_empty()
    with pytest.raises(EmptyStackError):
        s.pop()
    with pytest.raises(EmptyStackError):
        s.peek()


def test_lifo_1000():
    s: Stack[int] = Stack()
    for i in range(1000):
        s.push(i)
    assert s.peek() == 999
    assert [s.pop() for _ in range(1000)] == list(range(999, -1, -1))
    assert len(s) == 0
