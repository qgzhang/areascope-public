import pytest

from pydantic import ValidationError

from ..area_models import AreaAnalysisRequest


VALID_POLYGON = {
    "type": "Polygon",
    "coordinates": [[
        [152.92, -27.50],
        [152.93, -27.50],
        [152.93, -27.51],
        [152.92, -27.50],
    ]],
}


def test_valid_polygon():
    request = AreaAnalysisRequest(
        geometry=VALID_POLYGON,
    )

    assert request.geometry["type"] == "Polygon"


def test_reject_point():
    with pytest.raises(ValidationError):
        AreaAnalysisRequest(
            geometry={
                "type": "Point",
                "coordinates": [153.0, -27.5],
            }
        )


def test_reject_empty_polygon():
    with pytest.raises(ValidationError):
        AreaAnalysisRequest(
            geometry={
                "type": "Polygon",
                "coordinates": [],
            }
        )


def test_reject_invalid_coordinates():
    with pytest.raises(ValidationError):
        AreaAnalysisRequest(
            geometry={
                "type": "Polygon",
                "coordinates": [[
                    [300, -27.50],
                    [301, -27.50],
                    [301, -27.51],
                    [300, -27.50],
                ]],
            }
        )