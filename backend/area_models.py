from typing import Any

from pydantic import BaseModel, field_validator
from shapely.geometry import shape


class AreaAnalysisRequest(BaseModel):
    geometry: dict[str, Any]

    @field_validator("geometry")
    @classmethod
    def validate_geometry(
        cls,
        value: dict[str, Any],
    ) -> dict[str, Any]:

        # Only polygons can be analysis areas.
        if value.get("type") not in {
            "Polygon",
            "MultiPolygon",
        }:
            raise ValueError(
                "Area must be a Polygon or MultiPolygon"
            )

        # Convert GeoJSON into a Shapely object.
        try:
            polygon = shape(value)
        except (ValueError, TypeError, KeyError):
            raise ValueError(
                "Malformed GeoJSON geometry"
            ) from None

        if polygon.is_empty:
            raise ValueError("Polygon is empty")

        if not polygon.is_valid:
            raise ValueError("Polygon is invalid")

        if polygon.area <= 0:
            raise ValueError("Polygon has no area")

        # GeoJSON coordinates should be
        # longitude and latitude (EPSG:4326).
        minx, miny, maxx, maxy = polygon.bounds

        if not (
            -180 <= minx <= maxx <= 180
            and -90 <= miny <= maxy <= 90
        ):
            raise ValueError(
                "Coordinates must be longitude/latitude"
            )

        return value