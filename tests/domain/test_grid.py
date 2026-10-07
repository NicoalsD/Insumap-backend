import pytest

from app.domain.structures import Grid, project_cell


def make(n: int, m: int) -> Grid[tuple[int, int]]:
    return Grid(n, m, lambda r, c: (r, c))


def test_get_and_set():
    g = make(3, 4)
    assert g.get(2, 3) == (2, 3)
    g.set(1, 1, (9, 9))
    assert g.get(1, 1) == (9, 9)
    assert len(g) == 12


@pytest.mark.parametrize("r,c", [(-1, 0), (0, -1), (3, 0), (0, 4)])
def test_out_of_range(r, c):
    with pytest.raises(IndexError):
        make(3, 4).get(r, c)


def test_neighbors_corner_edge_inner():
    g = make(4, 4)
    assert sorted(g.neighbors(0, 0)) == [(0, 1), (1, 0)]
    assert len(g.neighbors(0, 2)) == 3
    assert len(g.neighbors(2, 2)) == 4


def test_resize_2_4_6():
    g = make(2, 2)
    for n in (4, 6):
        g.resize(n, n, lambda r, c: (r, c))
        assert len(g) == n * n
        assert g.get(n - 1, n - 1) == (n - 1, n - 1)


def test_invalid_dimensions():
    with pytest.raises(ValueError):
        Grid(0, 2, lambda r, c: 0)


@pytest.mark.parametrize(
    "r,c,src,dst,expected",
    [
        (1, 1, 2, 4, (1, 1)),
        (2, 2, 2, 4, (3, 3)),
        (4, 4, 4, 2, (2, 2)),
        (3, 1, 4, 2, (2, 1)),
        (6, 6, 6, 2, (2, 2)),
    ],
)
def test_project_cell(r, c, src, dst, expected):
    assert project_cell(r, c, src, dst) == expected
