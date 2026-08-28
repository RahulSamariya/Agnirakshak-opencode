"""Forecasts API endpoint."""
from datetime import datetime

from fastapi import APIRouter, Query

router = APIRouter()


@router.get("/")
async def list_forecasts(
    grid_cell_id: str | None = Query(None, description="Filter by grid cell ID"),  # noqa: B008
    run_id: str | None = Query(None, description="Filter by forecast run ID"),  # noqa: B008
    valid_from: datetime | None = Query(None, description="Valid time start"),  # noqa: B008
    valid_to: datetime | None = Query(None, description="Valid time end"),  # noqa: B008
    skip: int = Query(0, ge=0),  # noqa: B008
    limit: int = Query(100, ge=1, le=1000),  # noqa: B008
):
    """List weather forecasts with optional filters."""
    return {
        "message": "Not implemented yet",
        "endpoint": "GET /api/v1/forecasts",
        "filters": {
            "grid_cell_id": grid_cell_id,
            "run_id": run_id,
            "valid_from": valid_from,
            "valid_to": valid_to,
        },
    }


@router.get("/{forecast_id}")
async def get_forecast(forecast_id: str):
    """Get a specific forecast by ID."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/forecasts/{forecast_id}",
    }


@router.get("/runs/")
async def list_forecast_runs(
    model_name: str | None = Query(None, description="Filter by model name"),  # noqa: B008
    status: str | None = Query(None, description="Filter by status"),  # noqa: B008
    skip: int = Query(0, ge=0),  # noqa: B008
    limit: int = Query(100, ge=1, le=1000),  # noqa: B008
):
    """List forecast runs."""
    return {
        "message": "Not implemented yet",
        "endpoint": "GET /api/v1/forecasts/runs/",
    }
