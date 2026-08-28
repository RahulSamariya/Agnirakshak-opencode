"""Hazards API endpoint."""
from datetime import datetime

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
async def list_hazard_assessments(
    grid_cell_id: str | None = Query(None, description="Filter by grid cell ID"),  # noqa: B008
    valid_time: datetime | None = Query(None, description="Filter by valid time"),  # noqa: B008
    category: str | None = Query(None, description="Filter by hazard category"),  # noqa: B008
    skip: int = Query(0, ge=0),  # noqa: B008
    limit: int = Query(100, ge=1, le=1000),  # noqa: B008
):
    """List hazard assessments."""
    return {
        "message": "Not implemented yet",
        "endpoint": "GET /api/v1/hazards",
    }


@router.get("/{hazard_id}")
async def get_hazard_assessment(hazard_id: str):
    """Get a specific hazard assessment."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/hazards/{hazard_id}",
    }


@router.get("/grid/{grid_cell_id}")
async def get_hazard_by_grid_cell(
    grid_cell_id: str,
    valid_from: datetime | None = Query(None),  # noqa: B008
    valid_to: datetime | None = Query(None),  # noqa: B008
):
    """Get hazard assessments for a specific grid cell."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/hazards/grid/{grid_cell_id}",
    }
