from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .database import check_database
from .locality_service import get_locality_at
from .area_models import AreaAnalysisRequest
from .area_service import analyse_area
from .estimate_models import (
    WorkEstimateRequest,
)

from .estimate_service import (
    estimate_workload,
)

app = FastAPI(
    title="AreaScope API",
    description="Backend API for AreaScope spatial analysis",
    version="0.1.0",
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "name": "AreaScope API",
        "status": "ok",
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
    }

@app.get("/health/database")
def database_health():
    try:
        database = check_database()

        return {
            "status": "healthy",
            **database,
        }

    except Exception:
        return {
            "status": "unhealthy",
            "database": "unavailable",
        }

@app.get("/api/localities/at")
def locality_at(
    lng: float = Query(
        ...,
        ge=-180,
        le=180,
    ),
    lat: float = Query(
        ...,
        ge=-90,
        le=90,
    ),
):
    feature = get_locality_at(
        lng=lng,
        lat=lat,
    )

    if feature is None:
        raise HTTPException(
            status_code=404,
            detail="No locality found at this location",
        )

    return feature

@app.post("/api/analysis")
def analyze_area(request: AreaAnalysisRequest):
    return analyse_area(request.geometry)


@app.post("/api/estimate")
def estimate_area(
    request: WorkEstimateRequest,
):

    analysis = analyse_area(
        request.geometry
    )

    estimate = estimate_workload(
        analysis,
        request.assumptions,
    )

    return {
        "analysis": analysis,
        "assumptions": (
            request.assumptions.model_dump()
        ),
        "estimate": estimate,
    }