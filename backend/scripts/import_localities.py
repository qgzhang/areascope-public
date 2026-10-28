from pathlib import Path
import os

import geopandas as gpd
import pyogrio
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "localities"
    / "locality_boundaries_qld.gpkg"
)


load_dotenv(PROJECT_ROOT / "backend" / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")


# --------------------------------------------------
# 1. Discover the GeoPackage layer
# --------------------------------------------------

layers = pyogrio.list_layers(DATA_PATH)

layer_names = [layer[0] for layer in layers]

print("Available layers:")
for name in layer_names:
    print(f"  - {name}")


# Prefer a layer whose name contains "local"
layer_name = next(
    (
        name
        for name in layer_names
        if "local" in name.lower()
    ),
    layer_names[0],
)

print(f"\nUsing layer: {layer_name}")


# --------------------------------------------------
# 2. Read it into GeoPandas
# --------------------------------------------------

gdf = gpd.read_file(
    DATA_PATH,
    layer=layer_name,
    engine="pyogrio",
)

print(f"Read {len(gdf)} locality records")
print(f"Source CRS: {gdf.crs}")


# --------------------------------------------------
# 3. Normalise column names
# --------------------------------------------------

gdf = gdf.rename(
    columns={
        column: column.lower()
        for column in gdf.columns
    }
)


required_columns = {
    "loc_code",
    "locality",
    "lga",
    "ca_area_sqkm",
    "geometry",
}

missing = required_columns - set(gdf.columns)

if missing:
    raise RuntimeError(
        f"Expected columns not found: {missing}"
    )


# --------------------------------------------------
# 4. Keep only what AreaScope needs
# --------------------------------------------------

gdf = gdf[
    [
        "loc_code",
        "locality",
        "lga",
        "ca_area_sqkm",
        "geometry",
    ]
].copy()


# Remove missing/empty geometry
gdf = gdf[
    gdf.geometry.notna()
    & ~gdf.geometry.is_empty
].copy()


# --------------------------------------------------
# 5. Convert to longitude / latitude
# --------------------------------------------------

gdf = gdf.to_crs(epsg=4326)

gdf = gdf.rename_geometry("geom")

print(f"Target CRS: {gdf.crs}")


# --------------------------------------------------
# 6. Upload into PostGIS
# --------------------------------------------------

engine = create_engine(DATABASE_URL)

print("\nWriting localities to PostGIS...")

gdf.to_postgis(
    name="localities",
    con=engine,
    if_exists="replace",
    index=False,
)


# --------------------------------------------------
# 7. Add indexes
# --------------------------------------------------

with engine.begin() as connection:

    connection.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS
                idx_localities_geom
            ON localities
            USING GIST (geom)
            """
        )
    )

    connection.execute(
        text(
            """
            CREATE INDEX IF NOT EXISTS
                idx_localities_name
            ON localities (locality)
            """
        )
    )

    connection.execute(
        text("ANALYZE localities")
    )


print("Import complete.")