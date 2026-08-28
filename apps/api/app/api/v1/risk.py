"""Risk API endpoint."""
from datetime import datetime

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
async def list_risk_assessments(
    grid_cell_id: str | None = Query(None, description="Filter by grid cell ID"),  # noqa: B008
    risk_category: str | None = Query(None, description="Filter by risk category"),  # noqa: B008
    valid_time: datetime | None = Query(None, description="Filter by valid time"),  # noqa: B008
    skip: int = Query(0, ge=0),  # noqa: B008
    limit: int = Query(100, ge=1, le=1000),  # noqa: B008
):
    """List risk assessments."""
    return {
        "message": "Not implemented yet",
        "endpoint": "GET /api/v1/risk",
    }


@router.get("/{risk_id}")
async def get_risk_assessment(risk_id: str):
    """Get a specific risk assessment with full H/V/E breakdown."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/risk/{risk_id}",
    }


@router.get("/{risk_id}/explain")
async def explain_risk_assessment(risk_id: str):
    """Get explainability details for a risk assessment."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/risk/{risk_id}/explain",
        "description": "Returns why this location has this risk level",
    }


@router.get("/runs/")
async def list_risk_runs(
    status: str | None = Query(None, description="Filter by status"),  # noqa: B008
    skip: int = Query(0, ge=0),  # noqa: B008
    limit: int = Query(100, ge=1, le=1000),  # noqa: B008
):
    """List risk calculation runs."""
    return {
        "message": "Not implemented yet",
        "endpoint": "GET /api/v1/risk/runs/",
    }


@router.get("/summary/ward/{ward_id}")
async def get_ward_risk_summary(
    ward_id: str,
    valid_time: datetime | None = Query(None),  # noqa: B008
):
    """Get aggregated risk summary for a ward."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/risk/summary/ward/{ward_id}",
    }
