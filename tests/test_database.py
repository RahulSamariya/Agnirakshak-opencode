"""Smoke tests for database connectivity and migration."""
import pytest
import sys
from pathlib import Path

# Add apps/api to path
API_DIR = Path(__file__).resolve().parent.parent / "apps" / "api"
if API_DIR.exists() and str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))


def test_import_database_module():
    """Test database module imports successfully."""
    from app.db.database import Base, engine, AsyncSessionLocal, get_db
    assert Base is not None
    assert engine is not None
    assert AsyncSessionLocal is not None
    assert get_db is not None


def test_import_all_models():
    """Test all domain models import successfully."""
    from app.models import (
        BaseModel,
        State,
        City,
        Ward,
        GridCell,
        GridWardIntersection,
        WeatherStation,
        WeatherObservation,
        WeatherForecastRun,
        WeatherForecast,
        ScientificModel,
        ModelRun,
        HazardAssessment,
        VulnerabilityProfile,
        VulnerabilityFactor,
        ExposureProfile,
        ExposureFactor,
        RiskRun,
        RiskAssessment,
        RiskAssessmentComponent,
        WardRiskSummary,
        Alert,
        ActionRecommendation,
    )
    models = [
        State, City, Ward, GridCell, GridWardIntersection,
        WeatherStation, WeatherObservation, WeatherForecastRun, WeatherForecast,
        ScientificModel, ModelRun, HazardAssessment,
        VulnerabilityProfile, VulnerabilityFactor,
        ExposureProfile, ExposureFactor,
        RiskRun, RiskAssessment, RiskAssessmentComponent, WardRiskSummary,
        Alert, ActionRecommendation,
    ]
    for model in models:
        assert model.__tablename__ is not None


def test_model_tablenames():
    """Test that all models have correct table names."""
    from app.models import (
        State, City, Ward, GridCell, GridWardIntersection,
        WeatherStation, WeatherObservation, WeatherForecastRun, WeatherForecast,
        ScientificModel, ModelRun, HazardAssessment,
        VulnerabilityProfile, VulnerabilityFactor,
        ExposureProfile, ExposureFactor,
        RiskRun, RiskAssessment, RiskAssessmentComponent, WardRiskSummary,
        Alert, ActionRecommendation,
    )
    expected_tables = [
        "states", "cities", "wards", "grid_cells", "grid_ward_intersections",
        "weather_stations", "weather_observations", "weather_forecast_runs", "weather_forecasts",
        "scientific_models", "model_runs", "hazard_assessments",
        "vulnerability_profiles", "vulnerability_factors",
        "exposure_profiles", "exposure_factors",
        "risk_runs", "risk_assessments", "risk_assessment_components", "ward_risk_summaries",
        "alerts", "action_recommendations",
    ]
    models = [
        State, City, Ward, GridCell, GridWardIntersection,
        WeatherStation, WeatherObservation, WeatherForecastRun, WeatherForecast,
        ScientificModel, ModelRun, HazardAssessment,
        VulnerabilityProfile, VulnerabilityFactor,
        ExposureProfile, ExposureFactor,
        RiskRun, RiskAssessment, RiskAssessmentComponent, WardRiskSummary,
        Alert, ActionRecommendation,
    ]
    for model, expected_name in zip(models, expected_tables):
        assert model.__tablename__ == expected_name, f"{model.__name__} has table {model.__tablename__}, expected {expected_name}"


def test_import_alembic_config():
    """Test Alembic configuration imports."""
    try:
        from alembic.config import Config
        from alembic.script import ScriptDirectory
        assert Config is not None
        assert ScriptDirectory is not None
    except ImportError:
        pytest.skip("alembic not installed")


def test_import_api_app():
    """Test FastAPI app imports."""
    from app.main import app
    assert app is not None
    assert app.title == "Heatwave Early Warning Platform"