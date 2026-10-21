"""Road-network loading and radius filtering."""
from __future__ import annotations

import math
import os
import random

import networkx as nx
import numpy as np

CACHE_PATH = os.path.join("data", "surabaya_roads.graphml")
HIGHWAY_FILTER = (
    '["highway"~"^(trunk|primary|secondary|tertiary|'
    'trunk_link|primary_link|secondary_link|tertiary_link)$"]'
)
PLACES = ["Surabaya, East Java, Indonesia", "Surabaya, Indonesia"]
EARTH_R = 6371008.8


def haversine_m(lat1, lon1, lat2, lon2):
    """Great-circle distance in metres (works with numpy arrays)."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dl = np.radians(lon2) - np.radians(lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * EARTH_R * np.arcsin(np.sqrt(a))


def load_surabaya(cache_path: str = CACHE_PATH, force: bool = False) -> nx.MultiDiGraph:
    """Directed (MultiDiGraph) road network of Surabaya: trunk..tertiary (+links).

    Downloaded from OpenStreetMap through OSMnx on first use, then cached.
    One-way streets are respected, so the result is a true digraph.
    """
    import osmnx as ox

    if os.path.exists(cache_path) and not force:
        return ox.load_graphml(cache_path)

    last_err = None
    G = None
    for place in PLACES:
        try:
            G = ox.graph_from_place(
                place, custom_filter=HIGHWAY_FILTER, retain_all=True, simplify=True
            )
            break
        except Exception as e:  # geocoding / Overpass hiccup -> try next name
            last_err = e
    if G is None:
        raise RuntimeError(f"Could not download the Surabaya network: {last_err}")

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    ox.save_graphml(G, cache_path)
    return G


def make_demo_graph(center=(-7.2575, 112.7521), n=22, spacing_m=280, seed=7) -> nx.MultiDiGraph:
    """Offline synthetic grid with one-way/two-way streets, for trying the app
    without internet access."""
    rng = random.Random(seed)
    lat0, lon0 = center
    dlat = spacing_m / 111_320
    dlon = spacing_m / (111_320 * math.cos(math.radians(lat0)))
    G = nx.MultiDiGraph()
    nid = lambda i, j: i * n + j
    for i in range(n):
        for j in range(n):
            G.add_node(nid(i, j), y=lat0 + (i - n / 2) * dlat, x=lon0 + (j - n / 2) * dlon)
    classes = ["trunk", "primary", "secondary", "tertiary"]

    def add(a, b, name, hw):
        L = float(haversine_m(G.nodes[a]["y"], G.nodes[a]["x"], G.nodes[b]["y"], G.nodes[b]["x"]))
        G.add_edge(a, b, length=L, name=name, highway=hw)

    for i in range(n):          # east-west streets
        hw = classes[i % 4]
        two_way = i % 3 == 0
        east = rng.random() < 0.5
        for j in range(n - 1):
            a, b = nid(i, j), nid(i, j + 1)
            add(a, b, f"Demo Rd {i}", hw) if (two_way or east) else add(b, a, f"Demo Rd {i}", hw)
            if two_way:
                add(b, a, f"Demo Rd {i}", hw)
    for j in range(n):          # north-south streets
        hw = classes[(j + 1) % 4]
        two_way = j % 3 == 1
        north = rng.random() < 0.5
        for i in range(n - 1):
            a, b = nid(i, j), nid(i + 1, j)
            add(a, b, f"Demo Ave {j}", hw) if (two_way or north) else add(b, a, f"Demo Ave {j}", hw)
            if two_way:
                add(b, a, f"Demo Ave {j}", hw)
    return G


def build_service_graph(G: nx.MultiDiGraph, lat: float, lon: float, radius_km: float):
    """Sub-network the truck must cover.

    * snaps the base to the nearest graph node
    * keeps edges whose BOTH endpoints are within ``radius_km`` of the base
    * keeps only the strongly connected component containing the base node
      (everything else is unreachable/ignorable)
    Returns (subgraph, base_node, info_dict).
    """
    nodes = list(G.nodes)
    ys = np.array([G.nodes[n]["y"] for n in nodes], dtype=float)
    xs = np.array([G.nodes[n]["x"] for n in nodes], dtype=float)
    dist = haversine_m(lat, lon, ys, xs)

    i0 = int(np.argmin(dist))
    base_node = nodes[i0]
    inside = {nodes[i] for i in np.where(dist <= radius_km * 1000)[0]}
    inside.add(base_node)

    sub = G.subgraph(inside).copy()
    edges_in_radius = sub.number_of_edges()
    comp = next(c for c in nx.strongly_connected_components(sub) if base_node in c)
    sub = sub.subgraph(comp).copy()

    info = {
        "snap_distance_m": float(dist[i0]),
        "nodes": sub.number_of_nodes(),
        "edges": sub.number_of_edges(),
        "edges_in_radius": edges_in_radius,
        "edges_dropped": edges_in_radius - sub.number_of_edges(),
    }
    return sub, base_node, info
