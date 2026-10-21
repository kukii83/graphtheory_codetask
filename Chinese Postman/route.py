"""Turn a raw CPP circuit into steps, street runs, and travel-time estimates."""
from __future__ import annotations

import pandas as pd

# typical urban speeds (km/h) used when OSM has no usable `maxspeed`
DEFAULT_SPEEDS = {
    "trunk": 50, "trunk_link": 30,
    "primary": 40, "primary_link": 30,
    "secondary": 35, "secondary_link": 25,
    "tertiary": 30, "tertiary_link": 25,
}


def _first(v):
    return v[0] if isinstance(v, (list, tuple)) and v else v


def highway_class(d) -> str:
    return str(_first(d.get("highway", "unknown")))


def street_name(d) -> str:
    name = _first(d.get("name"))
    if name:
        return str(name)
    ref = _first(d.get("ref"))
    if ref:
        return str(ref)
    return f"(unnamed {highway_class(d)})"


def speed_kmh(d) -> float:
    ms = _first(d.get("maxspeed"))
    if ms is not None:
        try:
            v = float(str(ms).split()[0])
            if 5 <= v <= 120:
                return v
        except ValueError:
            pass
    return float(DEFAULT_SPEEDS.get(highway_class(d), 30))


def edge_coords(G, u, v, d):
    """[(lat, lon), ...] oriented u -> v."""
    geom = d.get("geometry")
    if geom is not None:
        return [(y, x) for x, y in geom.coords]
    return [(G.nodes[u]["y"], G.nodes[u]["x"]), (G.nodes[v]["y"], G.nodes[v]["x"])]


def build_steps(G, circuit):
    steps = []
    for i, (u, v, k, repeat) in enumerate(circuit, 1):
        d = G[u][v][k]
        steps.append({
            "step": i, "u": u, "v": v,
            "street": street_name(d), "highway": highway_class(d),
            "length_m": float(d.get("length", 0.0)),
            "speed_kmh": speed_kmh(d),
            "repeat": bool(repeat),
            "coords": edge_coords(G, u, v, d),
        })
    return steps


def group_runs(steps):
    """Merge consecutive steps on the same street with the same pass type."""
    runs = []
    for s in steps:
        if runs and runs[-1]["street"] == s["street"] and runs[-1]["repeat"] == s["repeat"]:
            r = runs[-1]
            r["length_m"] += s["length_m"]
            r["time_base_s"] += s["length_m"] / 1000 / s["speed_kmh"] * 3600
            r["coords"].extend(s["coords"][1:])
            r["last_step"] = s["step"]
            r["n_segments"] += 1
        else:
            runs.append({
                "street": s["street"], "highway": s["highway"], "repeat": s["repeat"],
                "length_m": s["length_m"],
                "time_base_s": s["length_m"] / 1000 / s["speed_kmh"] * 3600,
                "coords": list(s["coords"]),
                "first_step": s["step"], "last_step": s["step"], "n_segments": 1,
            })
    for i, r in enumerate(runs, 1):
        r["run"] = i
    return runs


def total_time_s(steps, speed_factor: float) -> float:
    """Travel time; speed_factor (<1) models slower driving while collecting."""
    return sum(s["length_m"] / 1000 / (s["speed_kmh"] * speed_factor) * 3600 for s in steps)


def runs_table(runs, speed_factor: float) -> pd.DataFrame:
    rows, cum_m, cum_s = [], 0.0, 0.0
    for r in runs:
        t = r["time_base_s"] / speed_factor
        cum_m += r["length_m"]
        cum_s += t
        rows.append({
            "Run": r["run"],
            "Street": r["street"],
            "Class": r["highway"],
            "Pass": "Repeat (deadhead)" if r["repeat"] else "Collect",
            "Segments": r["n_segments"],
            "Length (m)": round(r["length_m"]),
            "Cumulative (km)": round(cum_m / 1000, 2),
            "Elapsed (min)": round(cum_s / 60, 1),
        })
    return pd.DataFrame(rows)


def fmt_duration(seconds: float) -> str:
    m = int(round(seconds / 60))
    h, m = divmod(m, 60)
    return f"{h} h {m:02d} min" if h else f"{m} min"
