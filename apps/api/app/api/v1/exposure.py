"""Exposure API endpoint."""
from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()


@router.get("/")
async def list_exposure_profiles(
    ward_id: Optional[str] = Query(None, description="Filter by ward ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List exposure profiles."""
    return {
        "message": "Not implemented yet",
        "endpoint": "GET /api/v1/exposure",
    }


@router.get("/{profile_id}")
async def get_exposure_profile(profile_id: str):
    """Get a specific exposure profile."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/exposure/{profile_id}",
    }


@router.get("/ward/{ward_id}")
async def get_exposure_by_ward(ward_id: str):
    """Get exposure profile for a specific ward."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/exposure/ward/{ward_id}",
    }


@router.get("/{profile_id}/factors")
async def get_exposure_factors(profile_id: str):
    """Get detailed factor breakdown for an exposure profile."""
    return {
        "message": "Not implemented yet",
        "endpoint": f"GET /api/v1/exposure/{profile_id}/factors",
    }
