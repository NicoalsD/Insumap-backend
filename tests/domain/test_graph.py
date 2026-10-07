from app.domain.structures import Graph, Grid


def grid_graph(n: int) -> Graph[tuple[int, int]]:
    grid = Grid(n, n, lambda r, c: (r, c))
    g: Graph[tuple[int, int]] = Graph()
    for r, c, v in grid.iterate():
        g.add_node(v)
        for nr, nc in grid.neighbors(r, c):
            g.add_edge(v, (nr, nc))
    return g


def test_degrees():
    g = grid_graph(4)
    assert g.degree((0, 0)) == 2
    assert g.degree((0, 1)) == 3
    assert g.degree((1, 1)) == 4
    assert g.node_count == 16
    assert g.edge_count == 24  # 2·n·(n−1)


def test_bfs_radius():
    g = grid_graph(5)
    assert g.bfs((2, 2), 0) == []
    assert g.bfs((2, 2), 0, include_origin=True) == [(2, 2)]
    assert sorted(g.bfs((2, 2), 1)) == [(1, 2), (2, 1), (2, 3), (3, 2)]
    assert len(g.bfs((2, 2), 2)) == 12
