"""Smoke tests for worker application."""
import pytest


def test_import_worker_app():
    """Test worker application imports successfully."""
    from worker.main import app
    assert app is not None
    assert app.main == "heatwave_worker"


def test_import_weather_tasks():
    """Test weather task modules import."""
    from worker.tasks.weather import ingest_weather, calculate_hazard
    assert ingest_weather is not None
    assert calculate_hazard is not None


def test_import_risk_tasks():
    """Test risk task modules import."""
    from worker.tasks.risk import calculate_risk, aggregate_wards, generate_alerts
    assert calculate_risk is not None
    assert aggregate_wards is not None
    assert generate_alerts is not None


def test_import_pipeline_tasks():
    """Test pipeline task modules import."""
    from worker.tasks.pipelines import forecast_pipeline, risk_pipeline
    assert forecast_pipeline is not None
    assert risk_pipeline is not None


def test_worker_heartbeat_task():
    """Test worker heartbeat task exists and is registered."""
    from worker.main import app
    task_names = [name for name in app.tasks.keys()]
    assert "worker.heartbeat" in task_names
