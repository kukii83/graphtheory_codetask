"""DLH Surabaya garbage-truck route simulator (Directed Chinese Postman Problem).

Run:  streamlit run app.py
"""
from __future__ import annotations

import colorsys
import math
import time

import folium
import streamlit as st
from folium import plugins
from streamlit_folium import st_folium

import network
import route
from cpp_solver import solve_directed_cpp

SURABAYA_CENTER = (-7.2575, 112.7521)

st.set_page_config(page_title="DLH CPP Simulator – Surabaya", layout="wide")


@st.cache_resource(show_spinner="Loading road network (first run downloads Surabaya from OpenStreetMap – can take a few minutes)…")
def get_graph(demo: bool):
    return network.make_demo_graph() if demo else network.load_surabaya()


def progress_color(p: float) -> str:
    """blue (start) -> red (end)."""
    r, g, b = colorsys.hsv_to_rgb((1 - p) * 0.66, 0.9, 0.9)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def make_map(base, radius_km, result, arrows):
    m = folium.Map(location=base, zoom_start=13, tiles="OpenStreetMap", control_scale=True)
    dlat = radius_km / 111.32
    dlon = radius_km / (111.32 * math.cos(math.radians(base[0])))
    m.fit_bounds([[base[0] - dlat, base[1] - dlon], [base[0] + dlat, base[1] + dlon]])

    folium.Circle(base, radius=radius_km * 1000, color="#2563eb", weight=2,
                  fill=True, fill_opacity=0.04, tooltip=f"Service radius {radius_km:g} km").add_to(m)

    if result:
        runs = result["runs"]
        n = max(len(runs) - 1, 1)
        for r in runs:
            col = progress_color((r["run"] - 1) / n)
            kind = "repeat" if r["repeat"] else "collect"
            line = folium.PolyLine(
                r["coords"], color=col, weight=3 if r["repeat"] else 5, opacity=0.9,
                dash_array="6 6" if r["repeat"] else None,
                tooltip=f"#{r['run']} {r['street']} · {r['length_m']:.0f} m · {kind}",
            ).add_to(m)
            if arrows:
                plugins.PolyLineTextPath(
                    line, "   ►   ", repeat=True, offset=5,
                    attributes={"fill": col, "font-size": "13", "font-weight": "bold"},
                ).add_to(m)

    folium.Marker(base, tooltip="Dump truck base (start & end)",
                  icon=folium.Icon(color="green", icon="trash", prefix="fa")).add_to(m)
    return m


# ───────────────────────── sidebar ─────────────────────────
st.sidebar.header("Settings")
demo = st.sidebar.checkbox("Offline demo grid (no OSM download)", value=False)
if "base" not in st.session_state:
    st.session_state.base = SURABAYA_CENTER
    st.session_state.last_click = None
    st.session_state.result = None

radius_km = st.sidebar.slider("Service radius x (km)", 0.5, 15.0, 3.0, 0.5)
speed_factor = st.sidebar.slider(
    "Speed factor", 0.2, 1.0, 0.6, 0.05,
    help="Multiplies typical road-class speeds (or OSM maxspeed) to model a slow, "
         "stop-and-go collection truck. 1.0 = free-flow.")
show_arrows = st.sidebar.checkbox("Direction arrows on route", value=False)

st.sidebar.subheader("Base location")
lat_in = st.sidebar.number_input("Latitude", value=float(st.session_state.base[0]), format="%.6f")
lon_in = st.sidebar.number_input("Longitude", value=float(st.session_state.base[1]), format="%.6f")
if (lat_in, lon_in) != tuple(st.session_state.base):
    st.session_state.base = (lat_in, lon_in)
    st.session_state.result = None
st.sidebar.caption("…or just click anywhere on the map.")

# ───────────────────────── main ─────────────────────────
st.title("🚛 DLH Garbage Truck – Chinese Postman Route Simulator")
st.write("Click the map to place the dump-truck base, set the radius, then **Compute route**. "
         "The truck covers every trunk / primary / secondary / tertiary road segment inside the "
         "radius (respecting one-way streets), starting and ending at the base.")

G = get_graph(demo)
base = tuple(st.session_state.base)
res = st.session_state.result
if res and (res["params"] != (base, radius_km, demo)):
    res = None  # stale -> hide route
    st.info("Base or radius changed – press **Compute route** to update.")

if st.button("▶ Compute route", type="primary"):
    with st.spinner("Building service graph and solving CPP…"):
        t0 = time.perf_counter()
        sub, base_node, info = network.build_service_graph(G, base[0], base[1], radius_km)
        prep_time = time.perf_counter() - t0
        if sub.number_of_edges() == 0:
            st.error("No road segments reachable inside this radius. Increase the radius or move the base.")
            st.stop()
        cpp = solve_directed_cpp(sub, base_node)
        steps = route.build_steps(sub, cpp.circuit)
        runs = route.group_runs(steps)
    st.session_state.result = res = {
        "params": (base, radius_km, demo), "cpp": cpp, "info": info,
        "steps": steps, "runs": runs, "prep_time": prep_time,
    }

m = make_map(base, radius_km, res, show_arrows)
out = st_folium(m, height=620, use_container_width=True, returned_objects=["last_clicked"], key="map")
click = out.get("last_clicked") if out else None
if click:
    pt = (round(click["lat"], 6), round(click["lng"], 6))
    if pt != st.session_state.last_click:
        st.session_state.last_click = pt
        st.session_state.base = pt
        st.session_state.result = None
        st.rerun()

if res:
    cpp, info = res["cpp"], res["info"]
    secs = route.total_time_s(res["steps"], speed_factor)
    overhead = (cpp.total_length / cpp.required_length - 1) * 100 if cpp.required_length else 0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total distance", f"{cpp.total_length / 1000:.2f} km")
    c2.metric("Est. travel time", route.fmt_duration(secs))
    c3.metric("CPP solver time", f"{cpp.solve_time * 1000:.1f} ms")
    c4.metric("Repeated distance", f"{(cpp.total_length - cpp.required_length) / 1000:.2f} km",
              f"+{overhead:.1f}% over collect-only", delta_color="off")
    st.caption(
        f"Road length to collect: {cpp.required_length / 1000:.2f} km · "
        f"{info['edges']} directed segments in the route graph · {cpp.added_edges} segment repeats · "
        f"{cpp.unbalanced_nodes} unbalanced junctions · {info['edges_dropped']} segments ignored "
        f"(not strongly connected to the base) · graph preparation {res['prep_time'] * 1000:.0f} ms · "
        f"base snapped to nearest junction ({info['snap_distance_m']:.0f} m away). "
        "Colour goes blue → red along the route; dashed = repeated (deadhead) segment."
    )
    if info["snap_distance_m"] > 500:
        st.warning("The base is more than 500 m from the nearest mapped road.")

    st.subheader("Street traversal order")
    df = route.runs_table(res["runs"], speed_factor)
    st.dataframe(df, use_container_width=True, hide_index=True, height=380)
    d1, d2 = st.columns(2)
    d1.download_button("⬇ Traversal order (CSV)", df.to_csv(index=False).encode(),
                       "traversal_order.csv", "text/csv")
    d2.download_button("⬇ Route map (HTML)", m.get_root().render().encode(),
                       "cpp_route.html", "text/html")
