from fastapi import APIRouter
import structlog

logger = structlog.get_logger()

router = APIRouter()


@router.get("/health")
async def health_check():
    logger.info("health_check_requested")
    return {
        "status": "healthy",
        "service": "heatwave-api",
        "version": "0.1.0",
    }


@router.get("/health/ready")
async def readiness_check():
    return {
        "status": "ready",
        "checks": {
            "api": "ok",
        },
    }
