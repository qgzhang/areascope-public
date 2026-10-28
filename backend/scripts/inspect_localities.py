from pathlib import Path

import geopandas as gpd
import pyogrio


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "localities"
    / "locality_boundaries_qld.gpkg"
)


print(f"Reading: {DATA_PATH}")

layers = pyogrio.list_layers(DATA_PATH)

print("\nLayers:")
print(layers)


layer_name = layers[0][0]

print(f"\nReading layer: {layer_name}")

gdf = gpd.read_file(
    DATA_PATH,
    layer=layer_name,
    engine="pyogrio",
)


print("\nNumber of rows:")
print(len(gdf))

print("\nColumns:")
print(gdf.columns.tolist())

print("\nCRS:")
print(gdf.crs)

print("\nGeometry types:")
print(gdf.geometry.geom_type.value_counts())

print("\nFirst rows:")
print(gdf.head())