import json
from sqlalchemy import text
from .database import engine
from .terrain_service import analyse_terrain

# SAMPLE_SQL = text("""
#     SELECT
#         a.address_use_type,
#         COUNT(*) AS records
#     FROM addresses AS a
#     JOIN localities AS l
#         ON ST_Covers(l.geom, a.geom)
#     WHERE UPPER(l.locality) = 'KENMORE'
#       AND UPPER(l.lga) LIKE '%BRISBANE%'
#     GROUP BY a.address_use_type
#     ORDER BY records DESC;
# """)
#
# AREA_SQL = text("""
#     WITH selected AS (
#         SELECT
#             ST_SetSRID(
#                 ST_GeomFromGeoJSON(:geometry),
#                 4326
#             ) AS geom
#     )
#     SELECT
#         ST_Area(geom::geography)
#             / 1000000.0 AS area_km2
#     FROM selected
# """)

AREA_SQL = text("""
    WITH selected AS (
        SELECT
            ST_SetSRID(
                ST_GeomFromGeoJSON(:geometry),
                4326
            ) AS geom
    ),

    address_counts AS (
        SELECT
            COUNT(*) AS total_records,

            COUNT(*) FILTER (
                WHERE
                    LOWER(
                        COALESCE(a.address_use_type, '')
                    ) LIKE '%official location%'

                    OR LOWER(
                        COALESCE(a.address_use_type, '')
                    ) LIKE 'uprn%'
            ) AS official_records

        FROM addresses AS a
        CROSS JOIN selected AS s

        WHERE ST_Covers(s.geom, a.geom)
    ),

    road_stats AS (
    
        SELECT
    
            COALESCE(
                SUM(
                    ST_Length(
                        ST_Transform(
    
                            ST_CollectionExtract(
                                ST_Intersection(
                                    r.geom,
                                    s.geom
                                ),
                                2
                            ),
    
                            7856
                        )
                    )
                ),
                0
            ) / 1000.0
                AS road_centreline_km
    
        FROM roads AS r
    
        CROSS JOIN selected AS s
    
        WHERE ST_Intersects(
            r.geom,
            s.geom
        )
    ),
    
    mesh_parts AS (
    
        SELECT
    
            m.mb_code,
    
            m.person_count,
    
            m.dwelling_count,
    
            CASE
    
                WHEN ST_Covers(
                    s.geom,
                    m.geom
                )
                THEN 1.0
    
                ELSE
    
                    LEAST(
                        1.0,
    
                        ST_Area(
                            ST_Intersection(
                                m.geom,
                                s.geom
                            )::geography
                        )
    
                        /
    
                        NULLIF(
                            ST_Area(
                                m.geom::geography
                            ),
                            0
                        )
                    )
    
            END AS selected_fraction
    
        FROM mesh_blocks AS m
    
        CROSS JOIN selected AS s
    
        WHERE ST_Intersects(
            m.geom,
            s.geom
        )
    ),
    
    demographic_stats AS (
    
        SELECT
    
            COALESCE(
                SUM(
                    person_count
                    * selected_fraction
                ),
                0
            ) AS estimated_population,
    
            COALESCE(
                SUM(
                    dwelling_count
                    * selected_fraction
                ),
                0
            ) AS estimated_dwellings,
    
            COUNT(*)
                AS mesh_blocks_intersected,
    
            COUNT(*) FILTER (
                WHERE selected_fraction
                    < 0.999999
            )
                AS partial_mesh_blocks
    
        FROM mesh_parts
    )    
    
    SELECT
        ST_Area(s.geom::geography)
            / 1000000.0 AS area_km2,

        c.total_records,
        c.official_records,
        r.road_centreline_km,
        d.estimated_population,
        d.estimated_dwellings,
        d.mesh_blocks_intersected,
        d.partial_mesh_blocks

    FROM selected AS s
    CROSS JOIN address_counts AS c
    CROSS JOIN road_stats AS r
    CROSS JOIN demographic_stats AS d
""")


def unavailable_terrain() -> dict:
    return {
        "terrain_available": False,
        "elevation_min_m": None,
        "elevation_max_m": None,
        "elevation_mean_m": None,
        "elevation_range_m": None,
        "mean_slope_deg": None,
        "p90_slope_deg": None,
        "steep_area_percent": None,
        "terrain_class": None,
        "terrain_source": None,
    }


def analyse_area(geometry: dict) -> dict:
    # SQL receives the geometry as JSON text.
    geometry_json = json.dumps(geometry)

    with engine.connect() as connection:
        result = connection.execute(
            AREA_SQL,
            {"geometry": geometry_json},
        )

        row = result.mappings().one()

    area_km2 = float(row["area_km2"])

    total = int(row["total_records"])
    official = int(row["official_records"])
    road_km = float(
        row["road_centreline_km"]
    )

    road_density = (
        road_km / area_km2
        if area_km2 > 0
        else 0
    )

    addresses_per_road_km = (
        official / road_km
        if road_km > 0
        else None
    )

    population = float(
        row["estimated_population"]
    )

    dwellings = float(
        row["estimated_dwellings"]
    )

    population_density = (
        population / area_km2
        if area_km2 > 0
        else 0
    )

    result  = {
        "area_km2": round(area_km2, 4),

        "total_address_records": total,

        "official_address_records": official,

        "other_address_records": total - official,

        "official_density_per_km2": round(
            official / area_km2,
            2,
        ),
        "road_centreline_km": round(
            road_km,
            3,
        ),

        "road_density_km_per_km2": round(
            road_density,
            2,
        ),

        "official_addresses_per_road_km": (
            round(
                addresses_per_road_km,
                2,
            )
            if addresses_per_road_km is not None
            else None
        ),

        "estimated_population_2021": round(
            population
        ),

        "estimated_dwellings_2021": round(
            dwellings
        ),

        "population_density_per_km2": round(
            population_density,
            1,
        ),

        "mesh_blocks_intersected": int(
            row["mesh_blocks_intersected"]
        ),

        "partial_mesh_blocks": int(
            row["partial_mesh_blocks"]
        ),

        "census_year": 2021,

        "demographic_estimation_method": (
            "ABS 2021 Mesh Block counts; "
            "partial Mesh Blocks are area weighted"
        ),

        "data_coverage_note": (
            "Address data covers Brisbane City Council "
            "only. Results outside that area may be "
            "incomplete."
        ),
    }

    terrain = analyse_terrain(geometry)
    result.update(terrain)
    return result