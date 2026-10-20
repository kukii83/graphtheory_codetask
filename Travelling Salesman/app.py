import os
import time
import folium
import geopandas as gpd
import networkx as nx
import numpy as np
import osmnx as ox
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="SPPG TSP Simulator", layout="wide")
st.title("SPPG Mealbox Delivery TSP Simulator")


# --- 1. Load Cached Data ---
@st.cache_resource
def load_data():
    G = ox.load_graphml("cache/surabaya_road.graphml")
    schools = gpd.read_file("cache/schools_surabaya.geojson")
    return G, schools


with st.spinner("Loading Surabaya road network and school locations..."):
    G_road, schools_gdf = load_data()


# --- 2. TSP Solver (Nearest Neighbor + 2-Opt) ---
def solve_tsp(dist_matrix):
    n = len(dist_matrix)
    if n <= 1:
        return [0, 0], 0.0

    # Nearest Neighbor initialization starting at depot (index 0)
    unvisited = set(range(1, n))
    curr = 0
    tour = [0]
    while unvisited:
        next_node = min(unvisited, key=lambda x: dist_matrix[curr][x])
        tour.append(next_node)
        unvisited.remove(next_node)
        curr = next_node
    tour.append(0)  # Return to SPPG

    # 2-Opt local search improvement
    def tour_cost(t):
        return sum(dist_matrix[t[i]][t[i + 1]] for i in range(len(t) - 1))

    improved = True
    best_tour = tour
    best_cost = tour_cost(best_tour)

    while improved:
        improved = False
        for i in range(1, len(best_tour) - 2):
            for j in range(i + 1, len(best_tour) - 1):
                # Reverse segment between i and j
                new_tour = (
                    best_tour[:i]
                    + best_tour[i : j + 1][::-1]
                    + best_tour[j + 1 :]
                )
                cost = tour_cost(new_tour)
                if cost < best_cost:
                    best_tour = new_tour
                    best_cost = cost
                    improved = True
                    break
            if improved:
                break

    return best_tour, best_cost


# --- 3. Sidebar Controls ---
st.sidebar.header("Delivery Configuration")
default_lat, default_lon = -7.2825, 112.7953  # Example around ITS campus

sppg_lat = st.sidebar.number_input(
    "SPPG Latitude", value=default_lat, format="%.5f"
)
sppg_lon = st.sidebar.number_input(
    "SPPG Longitude", value=default_lon, format="%.5f"
)
radius_km = st.sidebar.slider(
    "Delivery Radius x (km)",
    min_value=0.5,
    max_value=10.0,
    value=2.0,
    step=0.5,
)
avg_speed_kmh = st.sidebar.slider(
    "Assumed Vehicle Speed (km/h)",
    min_value=15,
    max_value=60,
    value=30,
    step=5,
)


# --- 4. School Filtering by Radius ---
def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(np.radians(lat1))
        * np.cos(np.radians(lat2))
        * np.sin(dlon / 2) ** 2
    )
    return 2 * R * np.arcsin(np.sqrt(a))


schools_gdf["distance_km"] = haversine_km(
    sppg_lat, sppg_lon, schools_gdf.geometry.y, schools_gdf.geometry.x
)
filtered_schools = schools_gdf[schools_gdf["distance_km"] <= radius_km].copy()

# Add temporary index for identification
filtered_schools["school_id"] = range(1, len(filtered_schools) + 1)

st.sidebar.write(f"**Schools found within {radius_km} km:** {len(filtered_schools)}")


# --- 5. Run Routing & Display ---
if len(filtered_schools) == 0:
    st.warning("No schools found within this radius. Increase the radius.")
else:
    # 5a. Map SPPG and schools to road nodes
    sppg_node = ox.distance.nearest_nodes(G_road, sppg_lon, sppg_lat)
    target_nodes = [sppg_node] + [
        ox.distance.nearest_nodes(G_road, geom.x, geom.y)
        for geom in filtered_schools.geometry
    ]

    target_labels = ["SPPG Depot"] + [
        (
            f"{row.get('name', 'School')} (#{row['school_id']})"
            if str(row.get("name")) != "nan"
            else f"School #{row['school_id']}"
        )
        for _, row in filtered_schools.iterrows()
    ]

    # 5b. Compute Pairwise Shortest Path Distance Matrix
    n_targets = len(target_nodes)
    dist_matrix = np.zeros((n_targets, n_targets))

    with st.spinner("Calculating shortest paths on road digraph..."):
        for i in range(n_targets):
            for j in range(n_targets):
                if i != j:
                    try:
                        dist_matrix[i][j] = nx.shortest_path_length(
                            G_road,
                            source=target_nodes[i],
                            target=target_nodes[j],
                            weight="length",
                        )
                    except nx.NetworkXNoPath:
                        dist_matrix[i][j] = 1e9  # Penalty if disconnected

    # 5c. Solve TSP
    t0 = time.perf_counter()
    tour_indices, total_dist_meters = solve_tsp(dist_matrix)
    solver_runtime_ms = (time.perf_counter() - t0) * 1000

    total_dist_km = total_dist_meters / 1000.0
    est_travel_hours = total_dist_km / avg_speed_kmh
    est_travel_mins = est_travel_hours * 60

    # 5d. Metrics display
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Distance", f"{total_dist_km:.2f} km")
    col2.metric("Estimated Time", f"{est_travel_mins:.1f} mins")
    col3.metric("Schools Visited", f"{len(filtered_schools)}")
    col4.metric("Solver Runtime", f"{solver_runtime_ms:.2f} ms")

    # 5e. Reconstruct full street-level path geometry
    full_path_coords = []
    for step in range(len(tour_indices) - 1):
        u = target_nodes[tour_indices[step]]
        v = target_nodes[tour_indices[step + 1]]
        try:
            node_path = nx.shortest_path(G_road, source=u, target=v, weight="length")
            coords = [(G_road.nodes[n]["y"], G_road.nodes[n]["x"]) for n in node_path]
            full_path_coords.extend(coords)
        except nx.NetworkXNoPath:
            continue

    # 5f. Render Folium Map
    m = folium.Map(location=[sppg_lat, sppg_lon], zoom_start=13)

    # Delivery radius circle
    folium.Circle(
        location=[sppg_lat, sppg_lon],
        radius=radius_km * 1000,
        color="crimson",
        fill=True,
        fill_opacity=0.08,
    ).add_to(m)

    # SPPG Depot marker
    folium.Marker(
        [sppg_lat, sppg_lon],
        popup="SPPG Depot",
        icon=folium.Icon(color="red", icon="home"),
    ).add_to(m)

    # School markers
    for idx, row in filtered_schools.iterrows():
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=5,
            color="blue",
            fill=True,
            fill_opacity=0.8,
            popup=f"{row.get('name', 'School')} (#{row['school_id']})",
        ).add_to(m)

    # TSP Route Polyline
    if full_path_coords:
        folium.PolyLine(
            locations=full_path_coords,
            color="#0066FF",
            weight=4,
            opacity=0.8,
        ).add_to(m)

    col_map, col_details = st.columns([2, 1])
    with col_map:
        st_folium(m, width=800, height=520)

    with col_details:
        st.subheader("School Visiting Order")
        order_list = [target_labels[i] for i in tour_indices]
        for step_idx, stop_name in enumerate(order_list):
            st.write(f"**{step_idx}.** {stop_name}")
