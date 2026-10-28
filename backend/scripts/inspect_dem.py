from pathlib import Path

import rasterio
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEM_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "elevation"
    / "brisbane_dem.tif"
)

DEM_PATH_PROCESSED = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "elevation"
    / "brisbane_dem_7856.tif"
)

# with rasterio.open(DEM_PATH) as src:
with rasterio.open(DEM_PATH_PROCESSED) as src:

    print("CRS:")
    print(src.crs)

    print("\nDimensions:")
    print("Width:", src.width)
    print("Height:", src.height)

    print("\nNumber of bands:")
    print(src.count)

    print("\nData type:")
    print(src.dtypes)

    print("\nNoData:")
    print(src.nodata)

    print("\nPixel resolution:")
    print(src.res)

    print("\nBounds:")
    print(src.bounds)

    print("\nTransform:")
    print(src.transform)

with rasterio.open(DEM_PATH) as src:

    elevation = src.read(
        1,
        masked=True,
    )

    values = elevation.compressed()

    print("\nValid pixels:")
    print(values.size)

    print("\nElevation min:")
    print(float(np.min(values)))

    print("\nElevation max:")
    print(float(np.max(values)))

    print("\nElevation mean:")
    print(float(np.mean(values)))

    print("\nMasked / NoData pixels:")
    print(
        elevation.size
        - values.size
    )