from .estimate_models import (
    EstimateAssumptions,
)

MODEL_VERSION = "0.1.0"

TERRAIN_MULTIPLIERS = {
    "Flat": 1.00,
    "Gentle": 1.05,
    "Hilly": 1.12,
    "Steep": 1.20,
}

def get_terrain_multiplier(
    terrain_class: str | None,
) -> float:
    if terrain_class is None:
        return 1.0
    return TERRAIN_MULTIPLIERS.get(
        terrain_class,
        1.0,
    )

def estimate_workload(
    analysis: dict,
    assumptions: EstimateAssumptions,
) -> dict:

    official_addresses = int(
        analysis[
            "official_address_records"
        ]
    )

    road_km = float(
        analysis[
            "road_centreline_km"
        ]
    )

    # ---------------------------------
    # Estimated eligible delivery points
    # ---------------------------------
    eligible_points = (
        official_addresses
        * assumptions.eligible_address_ratio
    )

    # ---------------------------------
    # Handling time
    # ---------------------------------
    handling_hours = (
        eligible_points
        * assumptions.seconds_per_delivery
        / 3600
    )

    # ---------------------------------
    # Service distance
    # ---------------------------------
    service_distance_km = (
        road_km
        * assumptions.service_distance_factor
    )

    # ---------------------------------
    # Movement time
    # ---------------------------------
    base_movement_hours = (
        service_distance_km
        / assumptions.walking_speed_kmh
    )

    terrain_multiplier = (
        get_terrain_multiplier(
            analysis.get(
                "terrain_class"
            )
        )
    )

    movement_hours = (
        base_movement_hours
        * terrain_multiplier
    )

    # ---------------------------------
    # Exceptions
    # ---------------------------------
    estimated_exceptions = (
        eligible_points
        * assumptions.exception_rate
    )

    exception_hours = (
        estimated_exceptions
        * assumptions.seconds_per_exception
        / 3600
    )

    # ---------------------------------
    # Fixed overhead
    # ---------------------------------
    setup_hours = (
        assumptions.fixed_setup_minutes
        / 60
    )

    # ---------------------------------
    # Total
    # ---------------------------------
    estimated_hours = (
        handling_hours
        + movement_hours
        + exception_hours
        + setup_hours
    )

    labour_cost = (
        estimated_hours
        * assumptions.labour_rate_per_hour
    )

    estimated_cost = (
        labour_cost
        + assumptions.other_costs
    )

    if estimated_cost > 0:
        suggested_quote = (
            estimated_cost / (1 - assumptions.target_margin)
        )
    else:
        suggested_quote = 0

    quote_per_point = (
        suggested_quote
        / eligible_points
        if eligible_points > 0
        else None
    )

    cost_per_point = (
        estimated_cost
        / eligible_points
        if eligible_points > 0
        else None
    )

    points_per_hour = (
        eligible_points
        / estimated_hours
        if estimated_hours > 0
        else None
    )

    return {
        "model_version": MODEL_VERSION,

        "eligible_delivery_points": round(
            eligible_points,
        ),

        "estimated_service_distance_km": round(
            service_distance_km,
            2,
        ),

        "terrain_multiplier": round(
            terrain_multiplier,
            3,
        ),

        "handling_hours": round(
            handling_hours,
            2,
        ),

        "movement_hours": round(
            movement_hours,
            2,
        ),

        "exception_hours": round(
            exception_hours,
            2,
        ),

        "setup_hours": round(
            setup_hours,
            2,
        ),

        "estimated_hours": round(
            estimated_hours,
            2,
        ),

        "estimated_exceptions": round(
            estimated_exceptions,
        ),

        "labour_cost": round(
            labour_cost,
            2,
        ),

        "other_costs": round(
            assumptions.other_costs,
            2,
        ),

        "estimated_cost": round(
            estimated_cost,
            2,
        ),

        "suggested_quote": round(
            suggested_quote,
            2,
        ),

        "cost_per_point": (
            round(cost_per_point, 3)
            if cost_per_point is not None
            else None
        ),

        "quote_per_point": (
            round(quote_per_point, 3)
            if quote_per_point is not None
            else None
        ),

        "estimated_points_per_hour": (
            round(points_per_hour, 1)
            if points_per_hour is not None
            else None
        ),

        "model_status": "provisional",

        "model_note": (
            "Estimate based on configurable "
            "AreaScope assumptions rather than "
            "observed campaign performance."
        ),
    }