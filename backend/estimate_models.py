from pydantic import (
    BaseModel,
    Field,
)
from typing import Any
from .area_models import AreaAnalysisRequest


class EstimateAssumptions(BaseModel):

    eligible_address_ratio: float = Field(
        default=0.90,
        ge=0,
        le=1,
    )

    seconds_per_delivery: float = Field(
        default=10,
        gt=0,
        le=300,
    )

    service_distance_factor: float = Field(
        default=1.45,
        ge=1,
        le=5,
    )

    walking_speed_kmh: float = Field(
        default=4.0,
        gt=0,
        le=10,
    )

    exception_rate: float = Field(
        default=0.05,
        ge=0,
        le=1,
    )

    seconds_per_exception: float = Field(
        default=20,
        ge=0,
        le=600,
    )

    fixed_setup_minutes: float = Field(
        default=20,
        ge=0,
        le=240,
    )

    labour_rate_per_hour: float = Field(
        default=30,
        ge=0,
        le=500,
    )

    other_costs: float = Field(
        default=0,
        ge=0,
    )

    target_margin: float = Field(
        default=0.30,
        ge=0,
        lt=1,
    )

class WorkEstimateRequest(
    AreaAnalysisRequest
):
    assumptions: EstimateAssumptions = (
        EstimateAssumptions()
    )