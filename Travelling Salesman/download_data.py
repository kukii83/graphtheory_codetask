import os
import geopandas as gpd
import osmnx as ox

# Configure OSMnx settings
ox.settings.overpass_endpoint = "https://overpass.kumi.systems/api"
ox.settings.timeout = 180
ox.settings.use_cache = True

os.makedirs("cache", exist_ok=True)

# 1. Download or load road network
road_file = "cache/surabaya_road.graphml"
if os.path.exists(road_file):
    print(f"1. Road network already found at {road_file}. Skipping download.")
else:
    print("1. Downloading road network for Surabaya (drive network)...")
    G_road = ox.graph_from_place(
        "Surabaya, East Java, Indonesia", network_type="drive"
    )
    ox.save_graphml(G_road, road_file)
    print(
        f"   Saved road network ({len(G_road.nodes)} nodes, {len(G_road.edges)} edges) to {road_file}."
    )

# 2. Download school locations
schools_file = "cache/schools_surabaya.geojson"
if os.path.exists(schools_file):
    print(f"2. Schools data already found at {schools_file}. Skipping download.")
else:
    print("2. Downloading school locations from OpenStreetMap...")
    tags = {"amenity": "school"}
    schools_gdf = ox.features_from_place(
        "Surabaya, East Java, Indonesia", tags=tags
    )

    # Convert area polygons to center coordinate points
    schools_points = schools_gdf.copy()
    schools_points["geometry"] = schools_points["geometry"].centroid

    # Retain name and valid coordinates
    keep_cols = (
        ["name", "geometry"]
        if "name" in schools_points.columns
        else ["geometry"]
    )
    schools_points = schools_points[keep_cols].dropna(subset=["geometry"])

    schools_points.to_file(schools_file, driver="GeoJSON")
    print(f"   Saved {len(schools_points)} schools to {schools_file}.")

print("\nData preparation complete!")
