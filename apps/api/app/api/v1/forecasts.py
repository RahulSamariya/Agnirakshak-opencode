"""Forecasts API endpoint."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

router = APIRouter()


@router.get("/")
async def list_forecasts(
    grid_cell_id: Optional[str] = Query(None, description="Filter by grid cell ID"),
    run_id: Optional[str] = Query(None, description="Filter by forecast run ID"),
    valid_from: Optional[datetime] = Query(None, description="Valid time start"),
    valid_to: Optional[datetime] = Query(None, description="Valid time end"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
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
    model_name: Optional[str] = Query(None, description="Filter by model name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List forecast runs."""
    return {
        "message": "Not implemented yet",
        "endpoint": "GET /api/v1/forecasts/runs/",
    }
