"""Directed Chinese Postman Problem (CPP) solver.

Given a strongly connected directed multigraph whose every edge must be
traversed at least once, find a minimum-length closed walk starting and
ending at ``start``.

Algorithm (exact, polynomial time):
  1. For every node, imbalance = out_degree - in_degree.
  2. Nodes with in > out must get extra *outgoing* edges (sources),
     nodes with out > in must get extra *incoming* edges (sinks).
  3. Solve a min-cost transportation problem between sources and sinks, where
     the cost of sending one unit is the shortest-path length between them.
  4. Duplicate the edges of those shortest paths -> graph is balanced.
  5. A balanced, strongly connected digraph has an Eulerian circuit
     (Hierholzer, via networkx) -> that circuit is the optimal CPP tour.
"""
from __future__ import annotations

import time
from collections import Counter
from dataclasses import dataclass, field

import networkx as nx


@dataclass
class CPPResult:
    # (u, v, key, repeat) in traversal order. ``key`` refers to the edge in the
    # ORIGINAL graph; repeat=False the first time that edge is driven.
    circuit: list = field(default_factory=list)
    required_length: float = 0.0   # every edge once
    total_length: float = 0.0      # required + repeated
    added_edges: int = 0           # number of duplicated edge copies
    unbalanced_nodes: int = 0
    solve_time: float = 0.0        # seconds


def _cheapest_parallel(G: nx.MultiDiGraph) -> nx.DiGraph:
    """Collapse parallel edges, keeping the shortest one (and remembering its key)."""
    H = nx.DiGraph()
    for u, v, k, d in G.edges(keys=True, data=True):
        w = float(d.get("length", 0.0))
        if not H.has_edge(u, v) or w < H[u][v]["length"]:
            H.add_edge(u, v, length=w, key=k)
    return H


def solve_directed_cpp(G: nx.MultiDiGraph, start) -> CPPResult:
    t0 = time.perf_counter()
    if start not in G:
        raise ValueError("start node is not in the graph")
    if G.number_of_edges() == 0:
        return CPPResult(solve_time=time.perf_counter() - t0)
    if not nx.is_strongly_connected(G):
        raise ValueError("graph must be strongly connected (restrict to the base's SCC first)")

    required = sum(float(d.get("length", 0.0)) for _, _, d in G.edges(data=True))

    # nx convention: demand < 0 means the node supplies flow.
    # demand = out - in  ->  nodes with in > out are the sources.
    demand = {n: G.out_degree(n) - G.in_degree(n) for n in G}
    sources = [n for n, b in demand.items() if b < 0]
    sinks = [n for n, b in demand.items() if b > 0]

    M = G.copy()
    added = 0
    if sources:
        H = _cheapest_parallel(G)
        F = nx.DiGraph()
        for n in sources + sinks:
            F.add_node(n, demand=demand[n])
        paths = {}
        for s in sources:
            dist, path = nx.single_source_dijkstra(H, s, weight="length")
            for t in sinks:
                if t in dist:
                    # integer costs (decimetres) keep network simplex exact
                    F.add_edge(s, t, weight=int(round(dist[t] * 10)))
                    paths[(s, t)] = path[t]
        flow = nx.min_cost_flow(F)

        extra = Counter()
        for s, targets in flow.items():
            for t, f in targets.items():
                if f > 0:
                    p = paths[(s, t)]
                    for a, b in zip(p, p[1:]):
                        extra[(a, b)] += f
        for (a, b), mult in extra.items():
            ed = H[a][b]
            for _ in range(mult):
                M.add_edge(a, b, length=ed["length"], dup=True, orig_key=ed["key"])
                added += 1

    if not nx.is_eulerian(M):
        raise RuntimeError("internal error: balanced graph is not Eulerian")

    circuit, seen = [], set()
    for u, v, k in nx.eulerian_circuit(M, source=start, keys=True):
        d = M[u][v][k]
        base = d["orig_key"] if d.get("dup") else k
        repeat = (u, v, base) in seen
        seen.add((u, v, base))
        circuit.append((u, v, base, repeat))

    total = sum(float(G[u][v][k].get("length", 0.0)) for u, v, k, _ in circuit)
    return CPPResult(
        circuit=circuit,
        required_length=required,
        total_length=total,
        added_edges=added,
        unbalanced_nodes=len(sources) + len(sinks),
        solve_time=time.perf_counter() - t0,
    )
