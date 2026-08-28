"""Wards API endpoint."""

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
async def list_wards(
    city_id: str | None = Query(None, description="Filter by city ID"),
    state_id: str | None = Query(None, description="Filter by state ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List wards with optional geographic filters."""
    return {
        "message": "Not implemented yet",
        "endpoint": "GET /api/v1/wards",
    }


@router.get("/{ward_id}")
async def get_ward(ward_id: str):
    """Get a specific ward with details."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/wards/{ward_id}",
    }


@router.get("/{ward_id}/risk")
async def get_ward_risk(ward_id: str):
    """Get current risk status for a ward."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/wards/{ward_id}/risk",
    }


@router.get("/{ward_id}/grid-cells")
async def get_ward_grid_cells(ward_id: str):
    """Get grid cells belonging to a ward."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/wards/{ward_id}/grid-cells",
    }


@router.get("/states/")
async def list_states():
    """List all states."""
    return {
        "message": "Not implemented yet",
        "endpoint": "GET /api/v1/wards/states/",
    }


@router.get("/cities/")
async def list_cities(state_id: str | None = Query(None)):
    """List cities, optionally filtered by state."""
    return {
        "message": "Not implemented yet",
        "endpoint": "GET /api/v1/wards/cities/",
    }
