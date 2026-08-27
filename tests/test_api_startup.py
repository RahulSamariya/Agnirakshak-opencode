"""Smoke tests for API startup and basic functionality."""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_api_root():
    """Test API root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health endpoint returns healthy."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_endpoint():
    """Test readiness endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"


@pytest.mark.asyncio
async def test_forecasts_endpoint():
    """Test forecasts endpoint returns not implemented."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/forecasts")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Not implemented yet"


@pytest.mark.asyncio
async def test_risk_endpoint():
    """Test risk endpoint returns not implemented."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/risk")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Not implemented yet"


@pytest.mark.asyncio
async def test_alerts_endpoint():
    """Test alerts endpoint returns not implemented."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/alerts")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Not implemented yet"


@pytest.mark.asyncio
async def test_models_endpoint():
    """Test models endpoint returns not implemented."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/models")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Not implemented yet"
