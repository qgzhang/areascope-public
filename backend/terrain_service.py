from pathlib import Path

import numpy as np
import rasterio

from rasterio.mask import mask
from rasterio.warp import transform_geom


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEM_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "elevation"
    / "brisbane_dem_7856.tif"
)

def analyse_terrain(
    geometry: dict,
) -> dict:

    if not DEM_PATH.exists():
        raise RuntimeError(
            f"DEM not found: {DEM_PATH}"
        )

    with rasterio.open(DEM_PATH) as dem:

        raster_geometry = transform_geom(
            "EPSG:4326",
            dem.crs,
            geometry,
        )
        try:
            clipped, clipped_transform = mask(
                dem,
         [raster_geometry],
                crop=True,
                filled=False,
            )
        except ValueError:
            return {
                "terrain_available": False,
            }

        elevation_band = clipped[0]
        values = elevation_band.compressed()
        if values.size == 0:
            return {
                "terrain_available": False,
            }
        min_elevation = float(
            np.min(values)
        )
        max_elevation = float(
            np.max(values)
        )
        mean_elevation = float(
            np.mean(values)
        )
        elevation_range = (
            max_elevation
            - min_elevation
        )
        elevation = (
            elevation_band
            .astype("float64")
            .filled(np.nan)
        )
        pixel_width = abs(
            clipped_transform.a
        )
        pixel_height = abs(
            clipped_transform.e
        )
        dz_dy, dz_dx = np.gradient(
            elevation,
            pixel_height,
            pixel_width,
        )
        gradient = np.sqrt(
            dz_dx ** 2
            + dz_dy ** 2
        )
        slope_radians = np.arctan(
            gradient
        )
        slope_degrees = np.degrees(
            slope_radians
        )
        valid_slopes = slope_degrees[
            np.isfinite(slope_degrees)
        ]

        if valid_slopes.size == 0:
            mean_slope = None
            p90_slope = None
            steep_percent = None
        else:
            mean_slope = float(
                np.mean(valid_slopes)
            )
            p90_slope = float(
                np.percentile(
                    valid_slopes,
                    90,
                )
            )
            steep_percent = float(
                np.mean(
                    valid_slopes >= 8.0
                )
                * 100
            )
    terrain_class = classify_terrain(
        mean_slope,
        steep_percent,
    )

    return {
        "terrain_available": True,

        "elevation_min_m": round(
            min_elevation,
            1,
        ),

        "elevation_max_m": round(
            max_elevation,
            1,
        ),

        "elevation_mean_m": round(
            mean_elevation,
            1,
        ),

        "elevation_range_m": round(
            elevation_range,
            1,
        ),

        "mean_slope_deg": (
            round(mean_slope, 1)
            if mean_slope is not None
            else None
        ),

        "p90_slope_deg": (
            round(p90_slope, 1)
            if p90_slope is not None
            else None
        ),

        "steep_area_percent": (
            round(steep_percent, 1)
            if steep_percent is not None
            else None
        ),

        "terrain_class": terrain_class,

        "terrain_source": (
            "Geoscience Australia "
            "SRTM 1-second DEM"
        ),
    }


def classify_terrain(
    mean_slope: float | None,
    steep_percent: float | None,
) -> str | None:

    if (
        mean_slope is None
        or steep_percent is None
    ):
        return None

    if (
        mean_slope < 2.5
        and steep_percent < 10
    ):
        return "Flat"

    if (
        mean_slope < 5
        and steep_percent < 25
    ):
        return "Gentle"

    if (
        mean_slope < 8
        and steep_percent < 45
    ):
        return "Hilly"

    return "Steep"