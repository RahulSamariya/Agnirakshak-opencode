"""Scientific models API endpoint."""
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()


@router.get("/")
async def list_models(
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    status: Optional[str] = Query(None, description="Filter by status"),
):
    """List registered scientific models."""
    return {
        "message": "Not implemented yet",
        "endpoint": "GET /api/v1/models",
    }


@router.get("/{model_id}")
async def get_model(model_id: str):
    """Get details of a specific scientific model."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/models/{model_id}",
    }


@router.get("/{model_id}/runs")
async def get_model_runs(
    model_id: str,
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get run history for a specific model."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/models/{model_id}/runs",
    }


@router.get("/runs/{run_id}")
async def get_model_run(run_id: str):
    """Get details of a specific model run."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/models/runs/{run_id}",
    }


@router.get("/configuration/{model_type}")
async def get_model_configuration(model_type: str):
    """Get YAML configuration for a model type."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/models/configuration/{model_type}",
    }
