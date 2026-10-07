import pytest

from app.domain.structures import DoublyLinkedList


def test_push_and_iterate():
    lst: DoublyLinkedList[int] = DoublyLinkedList()
    for i in range(5):
        lst.push_front(i)
    lst.push_back(-1)
    assert list(lst.iter_forward()) == [4, 3, 2, 1, 0, -1]
    assert list(lst.iter_backward()) == list(reversed(list(lst.iter_forward())))


def test_remove_head_middle_tail():
    lst: DoublyLinkedList[int] = DoublyLinkedList()
    nodes = [lst.push_back(i) for i in range(5)]
    lst.remove(nodes[0])
    lst.remove(nodes[2])
    lst.remove(nodes[4])
    assert list(lst.iter_forward()) == [1, 3]
    assert len(lst) == 2
    with pytest.raises(ValueError):
        lst.remove(nodes[0])


def test_cursor_pagination():
    lst: DoublyLinkedList[int] = DoublyLinkedList()
    nodes = [lst.push_back(i) for i in range(10)]
    assert lst.page(None, 3) == [0, 1, 2]
    assert lst.page(nodes[2], 3) == [3, 4, 5]
    assert lst.page(nodes[8], 5) == [9]
    assert lst.page(None, 2, forward=False) == [9, 8]
