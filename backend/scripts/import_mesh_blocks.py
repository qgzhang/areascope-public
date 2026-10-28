from pathlib import Path
import os

import geopandas as gpd
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import create_engine, text


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BOUNDARY_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "census"
    / "mesh_blocks"
    / "MB_2021_AUST_GDA2020.shp"
)

COUNTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "census"
    / "mesh_block_counts_2021.xlsx"
)


load_dotenv(
    PROJECT_ROOT
    / "backend"
    / ".env"
)


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured"
    )

COUNT_DTYPES = {
    "MB_CODE_2021": "string",
    "MB_CATEGORY_NAME_2021": "string",
    "AREA_ALBERS_SQKM": "float64",
    "Dwelling": "Int64",
    "Person": "Int64",
    "State": "Int64",
}


def read_count_sheet(
    sheet_name: str,
) -> pd.DataFrame:

    return pd.read_excel(
        COUNTS_PATH,
        sheet_name=sheet_name,
        header=6,
        usecols="A:F",
        skipfooter=4,
        dtype=COUNT_DTYPES,
    )


counts = pd.concat(
    [
        read_count_sheet("Table 3"),
        read_count_sheet("Table 3.1"),
    ],
    ignore_index=True,
)


print(
    "Queensland Census-count rows:",
    len(counts),
)


# Clean the counts
counts = counts.rename(
    columns={
        "MB_CODE_2021": "mb_code",
        "MB_CATEGORY_NAME_2021": "mb_category_count",
        "AREA_ALBERS_SQKM": "area_albers_count_sqkm",
        "Dwelling": "dwelling_count",
        "Person": "person_count",
        "State": "state_code_count",
    }
)


counts["mb_code"] = (
    counts["mb_code"]
    .astype("string")
    .str.strip()
)


counts = counts[
    counts["mb_code"].notna()
].copy()


counts["person_count"] = (
    counts["person_count"]
    .fillna(0)
    .astype(int)
)


counts["dwelling_count"] = (
    counts["dwelling_count"]
    .fillna(0)
    .astype(int)
)


# Read only Queensland boundaries
print(
    "Reading Queensland Mesh Block boundaries..."
)


mesh = gpd.read_file(
    BOUNDARY_PATH,
    engine="pyogrio",
    where="STE_CODE21 = '3'",
)


print(
    "Queensland boundary rows:",
    len(mesh),
)

print(
    "Boundary CRS:",
    mesh.crs,
)

# Keep useful boundary attributes
mesh = mesh[
    [
        "MB_CODE21",
        "MB_CAT21",
        "SA1_CODE21",
        "SA2_CODE21",
        "SA2_NAME21",
        "STE_CODE21",
        "STE_NAME21",
        "AREASQKM21",
        "geometry",
    ]
].copy()


mesh = mesh.rename(
    columns={
        "MB_CODE21": "mb_code",
        "MB_CAT21": "mb_category",
        "SA1_CODE21": "sa1_code",
        "SA2_CODE21": "sa2_code",
        "SA2_NAME21": "sa2_name",
        "STE_CODE21": "state_code",
        "STE_NAME21": "state_name",
        "AREASQKM21": "area_albers_sqkm",
    }
)

mesh["mb_code"] = (
    mesh["mb_code"]
    .astype("string")
    .str.strip()
)

# Join geography to statistics
mesh = mesh.merge(
    counts[
        [
            "mb_code",
            "person_count",
            "dwelling_count",
        ]
    ],
    on="mb_code",
    how="left",
    validate="one_to_one",
)

missing_counts = (
    mesh["person_count"].isna().sum()
)

print(
    "Boundaries without Census counts:",
    missing_counts,
)

mesh["person_count"] = (
    mesh["person_count"]
    .fillna(0)
    .astype(int)
)

mesh["dwelling_count"] = (
    mesh["dwelling_count"]
    .fillna(0)
    .astype(int)
)

print("\nMesh Block categories:")

print(
    mesh["mb_category"]
    .value_counts()
    .to_string()
)

mesh = mesh[
    mesh.geometry.notna()
    & ~mesh.geometry.is_empty
].copy()

mesh = mesh.to_crs(
    epsg=4326
)

mesh = mesh.rename_geometry(
    "geom"
)

print(
    "Final CRS:",
    mesh.crs,
)

engine = create_engine(
    DATABASE_URL
)


print(
    "Writing Mesh Blocks to PostGIS..."
)


with engine.begin() as connection:

    mesh.to_postgis(
        name="mesh_blocks",
        con=connection,
        if_exists="replace",
        index=False,
        chunksize=3000,
    )


    connection.execute(
        text("""
            CREATE UNIQUE INDEX
                idx_mesh_blocks_code
            ON mesh_blocks (mb_code)
        """)
    )

    connection.execute(
        text(
            "ANALYZE mesh_blocks"
        )
    )


print(
    "Mesh Block import complete."
)

