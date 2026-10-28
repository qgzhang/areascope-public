from pathlib import Path
import os

import geopandas as gpd
import pyogrio

from dotenv import load_dotenv
from shapely.geometry import box
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "roads"
    / "queensland_roads_tracks.gpkg"
)


load_dotenv(PROJECT_ROOT / "backend" / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

LAYER_NAME = "Queensland_roads_and_tracks"

# A deliberately generous Brisbane-region bounding box.
#
# Coordinates:
# west, south, east, north

BRISBANE_BBOX_4326 = (
    152.65,
    -27.80,
    153.35,
    -27.15,
)

info = pyogrio.read_info(
    DATA_PATH,
    layer=LAYER_NAME,
)

source_crs = info["crs"]

if not source_crs:
    raise RuntimeError(
        "Road dataset has no CRS information"
    )

print("Source CRS:", source_crs)

west, south, east, north = BRISBANE_BBOX_4326

bbox_4326 = gpd.GeoSeries(
    [
        box(
            west,
            south,
            east,
            north,
        )
    ],
    crs="EPSG:4326",
)

bbox_source = bbox_4326.to_crs(
    source_crs
)

source_bounds = tuple(
    bbox_source.total_bounds
)

print("Source-space bbox:", source_bounds)

print("Reading Brisbane-region roads...")

gdf = gpd.read_file(
    DATA_PATH,
    layer=LAYER_NAME,
    engine="pyogrio",
    bbox=source_bounds,
)

print("Records read:", len(gdf))
print("Geometry types:")
print(gdf.geometry.geom_type.value_counts())

# Normalise column names.

gdf.columns = (
    gdf.columns
    .str.strip()
    .str.lower()
    .str.replace(
        r"[^a-z0-9_]+",
        "_",
        regex=True,
    )
    .str.strip("_")
)


if gdf.columns.duplicated().any():
    duplicates = gdf.columns[
        gdf.columns.duplicated()
    ].tolist()

    raise RuntimeError(
        f"Duplicate normalised columns: {duplicates}"
    )

gdf = gdf[
    gdf.geometry.notna()
    & ~gdf.geometry.is_empty
].copy()


gdf = gdf[
    gdf.geometry.geom_type.isin(
        [
            "LineString",
            "MultiLineString",
        ]
    )
].copy()

gdf.insert(
    0,
    "areascope_road_id",
    range(1, len(gdf) + 1),
)

gdf = gdf.to_crs(
    epsg=4326
)

gdf = gdf.rename_geometry(
    "geom"
)

print("Imported CRS:", gdf.crs)
print("Road records:", len(gdf))

engine = create_engine(
    DATABASE_URL
)


print("Writing roads to PostGIS...")


with engine.begin() as connection:

    gdf.to_postgis(
        name="roads",
        con=connection,
        if_exists="replace",
        index=False,
        chunksize=5000,
    )


    connection.execute(
        text("""
            CREATE INDEX IF NOT EXISTS
                idx_roads_geom
            ON roads
            USING GIST (geom)
        """)
    )


    connection.execute(
        text(
            "ANALYZE roads"
        )
    )


print("Road import complete.")

