"""Risk API endpoint."""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime

router = APIRouter()


@router.get("/")
async def list_risk_assessments(
    grid_cell_id: Optional[str] = Query(None, description="Filter by grid cell ID"),
    risk_category: Optional[str] = Query(None, description="Filter by risk category"),
    valid_time: Optional[datetime] = Query(None, description="Filter by valid time"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
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
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List risk calculation runs."""
    return {
        "message": "Not implemented yet",
        "endpoint": "GET /api/v1/risk/runs/",
    }


@router.get("/summary/ward/{ward_id}")
async def get_ward_risk_summary(
    ward_id: str,
    valid_time: Optional[datetime] = Query(None),
):
    """Get aggregated risk summary for a ward."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/risk/summary/ward/{ward_id}",
    }
