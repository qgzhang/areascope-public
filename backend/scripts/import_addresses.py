
from pathlib import Path
import csv
import os

import geopandas as gpd
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "addresses"
    / "property-address-locations.csv"
)


load_dotenv(PROJECT_ROOT / "backend" / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing")


# 1. Read the original CSV.

with DATA_PATH.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:
    sample = file.read(8192)

delimiter = csv.Sniffer().sniff(
    sample,
    delimiters=";,\t",
).delimiter

df = pd.read_csv(
    DATA_PATH,
    sep=delimiter,
    dtype=str,
    encoding="utf-8-sig",
    keep_default_na=False,
)

print("Source records:", len(df))


# 2. Normalise the column names.

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(r"\s+", "_", regex=True)
)

required = {
    "easting",
    "northing",
    "address_use_type",
}

missing = required - set(df.columns)

if missing:
    raise RuntimeError(
        f"Missing source columns: {missing}"
    )


# 3. Keep the relevant address attributes.

attributes = [
    "property_id",
    "unit_number",
    "house_number",
    "street_name",
    "street_type",
    "suburb",
    "postcode",
    "address_use_type",
]

for column in attributes:
    if column not in df.columns:
        df[column] = ""


# 4. Convert the coordinate columns.

df["easting"] = pd.to_numeric(
    df["easting"],
    errors="coerce",
)

df["northing"] = pd.to_numeric(
    df["northing"],
    errors="coerce",
)

before = len(df)

df = df.dropna(
    subset=["easting", "northing"]
).copy()

# Basic sanity checks for our Brisbane-focused
# import. Inspect any rejected rows separately
# if a future dataset version changes.
df = df[
    df["easting"].between(250000, 750000)
    & df["northing"].between(6750000, 7200000)
].copy()

print(
    "Rejected coordinate records:",
    before - len(df),
)

print("Usable records:", len(df))

if df.empty:
    raise RuntimeError(
        "No valid address coordinates found. "
        "Check the CSV and source CRS."
    )


# 5. Give the imported records a local ID.

df["source_row_id"] = range(
    1,
    len(df) + 1,
)


# 6. Convert the ordinary DataFrame into
# a GeoDataFrame by constructing points.

gdf = gpd.GeoDataFrame(
    df[["source_row_id", *attributes]].copy(),

    geometry=gpd.points_from_xy(
        df["easting"],
        df["northing"],
    ),

    crs="EPSG:28356",
)


# 7. Transform the coordinates for AreaScope.

gdf = gdf.to_crs(epsg=4326)

gdf = gdf.rename_geometry("geom")

print("Target CRS:", gdf.crs)
print("Geometry bounds:", gdf.total_bounds)


# 8. Import to PostgreSQL/PostGIS.

engine = create_engine(DATABASE_URL)

with engine.begin() as connection:

    gdf.to_postgis(
        name="addresses",
        con=connection,
        if_exists="replace",
        index=False,
        chunksize=5000,
    )

    connection.execute(
        text("""
            CREATE INDEX IF NOT EXISTS
                idx_addresses_geom
            ON addresses
            USING GIST (geom)
        """)
    )

    connection.execute(
        text("""
            CREATE INDEX IF NOT EXISTS
                idx_addresses_use_type
            ON addresses (address_use_type)
        """)
    )

    connection.execute(
        text("ANALYZE addresses")
    )

print("Address import completed.")
