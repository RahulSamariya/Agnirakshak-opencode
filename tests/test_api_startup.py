"""Smoke tests for API startup and basic functionality."""
import sys
from pathlib import Path

# Add apps/api to path before importing app
API_DIR = Path(__file__).resolve().parent.parent / "apps" / "api"
if API_DIR.exists() and str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

transport = ASGITransport(app=app)


@pytest.mark.asyncio
async def test_api_root():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_endpoint():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_forecasts_endpoint():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/forecasts/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Not implemented yet"


@pytest.mark.asyncio
async def test_risk_endpoint():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/risk/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Not implemented yet"


@pytest.mark.asyncio
async def test_alerts_endpoint():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/alerts/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Not implemented yet"


@pytest.mark.asyncio
async def test_models_endpoint():
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/models/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Not implemented yet"
