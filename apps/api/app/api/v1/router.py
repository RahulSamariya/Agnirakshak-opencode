"""API v1 router."""
from fastapi import APIRouter

from app.api.v1.alerts import router as alerts_router
from app.api.v1.exposure import router as exposure_router
from app.api.v1.forecasts import router as forecasts_router
from app.api.v1.hazards import router as hazards_router
from app.api.v1.health import router as health_router
from app.api.v1.models import router as models_router
from app.api.v1.risk import router as risk_router
from app.api.v1.vulnerability import router as vulnerability_router
from app.api.v1.wards import router as wards_router

api_router = APIRouter()

api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(forecasts_router, prefix="/forecasts", tags=["forecasts"])
api_router.include_router(hazards_router, prefix="/hazards", tags=["hazards"])
api_router.include_router(
    vulnerability_router, prefix="/vulnerability", tags=["vulnerability"]
)
api_router.include_router(exposure_router, prefix="/exposure", tags=["exposure"])
api_router.include_router(risk_router, prefix="/risk", tags=["risk"])
api_router.include_router(wards_router, prefix="/wards", tags=["wards"])
api_router.include_router(alerts_router, prefix="/alerts", tags=["alerts"])
api_router.include_router(models_router, prefix="/models", tags=["models"])
