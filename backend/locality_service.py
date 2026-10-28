import json

from sqlalchemy import text

from .database import engine


LOCALITY_AT_POINT_SQL = text(
    """
    SELECT
        loc_code,
        locality,
        lga,
        ca_area_sqkm,
        ST_AsGeoJSON(geom, 6) AS geometry_geojson

    FROM localities

    WHERE ST_Covers(
        geom,
        ST_SetSRID(
            ST_MakePoint(:lng, :lat),
            4326
        )
    )

    ORDER BY ca_area_sqkm ASC NULLS LAST

    LIMIT 1
    """
)


def get_locality_at(
    lng: float,
    lat: float,
) -> dict | None:

    with engine.connect() as connection:

        row = connection.execute(
            LOCALITY_AT_POINT_SQL,
            {
                "lng": lng,
                "lat": lat,
            },
        ).mappings().first()

    if row is None:
        return None

    return {
        "type": "Feature",

        "geometry": json.loads(
            row["geometry_geojson"]
        ),

        "properties": {
            "loc_code": row["loc_code"],
            "locality": row["locality"],
            "lga": row["lga"],
            "area_sqkm": row["ca_area_sqkm"],
        },
    }


if __name__ == "__main__":
    geo_json = get_locality_at(
        lng= 153.0251,
        lat= -27.4698,
    )
    print(geo_json)