"""Run: python test_solver.py"""
import random

import networkx as nx

import network
import route
from cpp_solver import solve_directed_cpp


def check_circuit(G, start, res):
    c = res.circuit
    assert c[0][0] == start and c[-1][1] == start, "must start and end at base"
    for (a, b, _, _), (c2, d2, _, _) in zip(c, c[1:]):
        assert b == c2, "circuit must be contiguous"
    first = {(u, v, k) for u, v, k, rep in c if not rep}
    assert first == set(G.edges(keys=True)), "every edge covered exactly once as 'collect'"
    assert abs(res.total_length - sum(G[u][v][k]["length"] for u, v, k, _ in c)) < 1e-6
    assert res.total_length >= res.required_length - 1e-6


def test_known_optimum():
    G = nx.MultiDiGraph()
    for u, v, w in [(0, 1, 1), (1, 2, 1), (2, 0, 1), (0, 2, 5)]:
        G.add_edge(u, v, length=w)
    res = solve_directed_cpp(G, 0)
    assert abs(res.total_length - 9) < 1e-9, res.total_length   # 8 required + 1 repeat (2->0)
    check_circuit(G, 0, res)


def test_already_eulerian():
    G = nx.MultiDiGraph()
    for u, v in [(0, 1), (1, 2), (2, 0)]:
        G.add_edge(u, v, length=2.0)
    res = solve_directed_cpp(G, 1)
    assert res.added_edges == 0 and res.total_length == 6.0
    check_circuit(G, 1, res)


def test_random_graphs():
    rng = random.Random(1)
    for _ in range(30):
        n = rng.randint(4, 25)
        G = nx.MultiDiGraph()
        order = list(range(n))
        rng.shuffle(order)
        for a, b in zip(order, order[1:] + order[:1]):      # ring => strongly connected
            G.add_edge(a, b, length=rng.uniform(1, 50))
        for _ in range(rng.randint(0, 3 * n)):
            a, b = rng.sample(range(n), 2)
            G.add_edge(a, b, length=rng.uniform(1, 50))
        start = rng.randrange(n)
        res = solve_directed_cpp(G, start)
        check_circuit(G, start, res)


def test_demo_pipeline():
    G = network.make_demo_graph()
    sub, base, info = network.build_service_graph(G, -7.2575, 112.7521, 1.5)
    assert nx.is_strongly_connected(sub)
    res = solve_directed_cpp(sub, base)
    check_circuit(sub, base, res)
    steps = route.build_steps(sub, res.circuit)
    runs = route.group_runs(steps)
    assert abs(sum(r["length_m"] for r in runs) - res.total_length) < 1e-6
    print(f"demo: {info['edges']} edges, total {res.total_length/1000:.2f} km, "
          f"solver {res.solve_time*1000:.1f} ms, {len(runs)} runs")


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
