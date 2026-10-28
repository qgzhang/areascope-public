import pytest

from ..estimate_models import (
    EstimateAssumptions,
)

from ..estimate_service import (
    estimate_workload,
    get_terrain_multiplier,
)

def test_flat_multiplier():
    assert get_terrain_multiplier("Flat") == 1.0


def test_hilly_multiplier():
    assert get_terrain_multiplier("Hilly") == 1.12


def test_unknown_terrain_defaults_to_one():
    assert get_terrain_multiplier("Unknown") == 1.0

def test_workload_estimate():

    analysis = {
        "official_address_records": 1000,
        "road_centreline_km": 10,
        "terrain_class": "Flat",
    }

    assumptions = EstimateAssumptions(
        eligible_address_ratio=1.0,
        seconds_per_delivery=10,
        service_distance_factor=1.0,
        walking_speed_kmh=5.0,
        exception_rate=0,
        seconds_per_exception=0,
        fixed_setup_minutes=0,
        labour_rate_per_hour=30,
        other_costs=0,
        target_margin=0.25,
    )

    result = estimate_workload(
        analysis,
        assumptions,
    )

    assert result[
        "eligible_delivery_points"
    ] == 1000

    assert result[
        "estimated_service_distance_km"
    ] == 10

    assert result[
        "handling_hours"
    ] == pytest.approx(
        1000 * 10 / 3600,
        abs=0.01,
    )

    assert result[
        "movement_hours"
    ] == pytest.approx(
        2.0,
        abs=0.01,
    )