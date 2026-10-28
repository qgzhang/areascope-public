from pathlib import Path

import geopandas as gpd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "census"
    / "mesh_blocks"
    / "MB_2021_AUST_GDA2020.shp"
)


gdf = gpd.read_file(
    DATA_PATH,
    engine="pyogrio",
    rows=10,
)


print("CRS:")
print(gdf.crs)

print("\nColumns:")
print(gdf.columns.tolist())

print("\nGeometry types:")
print(gdf.geometry.geom_type.value_counts())

print("\nSample:")
print(gdf.head().to_string())