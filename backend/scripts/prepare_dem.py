from pathlib import Path

import rasterio

from rasterio.enums import Resampling

from rasterio.warp import (
    calculate_default_transform,
    reproject,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SOURCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "elevation"
    / "brisbane_dem.tif"
)

TARGET_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "elevation"
)

TARGET_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

TARGET_PATH = (
    TARGET_DIR
    / "brisbane_dem_7856.tif"
)


TARGET_CRS = "EPSG:7856"


with rasterio.open(SOURCE_PATH) as source:

    print("Source CRS:", source.crs)

    transform, width, height = (
        calculate_default_transform(
            source.crs,
            TARGET_CRS,
            source.width,
            source.height,
            *source.bounds,
        )
    )

    profile = source.profile.copy()

    profile.update(
        crs=TARGET_CRS,
        transform=transform,
        width=width,
        height=height,

        # Compression significantly reduces
        # GeoTIFF storage.
        compress="deflate",
    )

    print("Output size:")
    print(width, "x", height)

    print("Output resolution:")
    print(
        abs(transform.a),
        "m x",
        abs(transform.e),
        "m",
    )

    with rasterio.open(
        TARGET_PATH,
        "w",
        **profile,
    ) as target:

        for band_index in range(
            1,
            source.count + 1,
        ):

            reproject(
                source=rasterio.band(
                    source,
                    band_index,
                ),

                destination=rasterio.band(
                    target,
                    band_index,
                ),

                src_transform=source.transform,
                src_crs=source.crs,

                dst_transform=transform,
                dst_crs=TARGET_CRS,

                resampling=Resampling.bilinear,
            )


print("Prepared DEM:")
print(TARGET_PATH)