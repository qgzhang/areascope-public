from ..terrain_service import classify_terrain


def test_flat_terrain():

    result = classify_terrain(
        mean_slope=1.5,
        steep_percent=3,
    )

    assert result == "Flat"


def test_gentle_terrain():

    result = classify_terrain(
        mean_slope=3.5,
        steep_percent=15,
    )

    assert result == "Gentle"


def test_hilly_terrain():

    result = classify_terrain(
        mean_slope=6,
        steep_percent=30,
    )

    assert result == "Hilly"


def test_steep_terrain():

    result = classify_terrain(
        mean_slope=10,
        steep_percent=50,
    )

    assert result == "Steep"