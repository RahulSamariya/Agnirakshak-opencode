"""Weather-related tasks."""
import structlog

try:
    from worker.main import app
except ImportError:
    from main import app

from scientific.chain import run_thermal_hazard_chain

logger = structlog.get_logger()


@app.task(name="worker.tasks.weather.ingest_weather")
def ingest_weather(source: str, parameters: dict | None = None):
    """Ingest weather data from external sources.

    This task handles:
    - Fetching forecast data from meteorological APIs
    - Fetching observation data from weather stations
    - Initial data validation
    """
    logger.info("ingest_weather_started", source=source, parameters=parameters)

    # TODO: Implement actual weather ingestion from external APIs
    # For now, return a placeholder indicating the task was received
    return {
        "status": "placeholder",
        "task": "ingest_weather",
        "source": source,
        "message": "Weather ingestion not yet connected to external APIs",
    }


@app.task(name="worker.tasks.weather.calculate_hazard")
def calculate_hazard(forecast_run_id: str, grid_cell_ids: list | None = None):
    """Calculate hazard assessments for forecast data.

    This task handles:
    - UTCI calculation for each grid cell
    - Hazard index normalization
    - Hazard category classification
    """
    logger.info(
        "calculate_hazard_started",
        forecast_run_id=forecast_run_id,
        grid_cell_count=len(grid_cell_ids) if grid_cell_ids else "all",
    )

    # TODO: Load forecast data from database
    # For now, demonstrate the scientific engine integration
    # In production, this would:
    # 1. Query WeatherForecast records for the forecast_run_id
    # 2. For each grid cell, extract Ta, RH, v, Tmrt
    # 3. Call run_thermal_hazard_chain() for each grid cell
    # 4. Store HazardAssessment records

    return {
        "status": "placeholder",
        "task": "calculate_hazard",
        "forecast_run_id": forecast_run_id,
        "message": "Hazard calculation ready - awaiting database integration",
        "scientific_engine": "connected",
    }


@app.task(name="worker.tasks.weather.calculate_utci_single")
def calculate_utci_single(
    air_temperature: float,
    relative_humidity: float,
    wind_speed: float,
    mean_radiant_temperature: float,
):
    """Calculate UTCI and hazard for a single grid cell.

    This is a helper task for testing the scientific engine integration.
    """
    try:
        result = run_thermal_hazard_chain(
            air_temperature=air_temperature,
            relative_humidity=relative_humidity,
            wind_speed=wind_speed,
            mean_radiant_temperature=mean_radiant_temperature,
        )
        return {
            "status": "success",
            "utci_c": result.utci_output.utci_c if result.utci_output else None,
            "hazard_index": result.hazard_output.hazard_index if result.hazard_output else None,
            "hazard_category": result.hazard_output.hazard_category.value if result.hazard_output else None,
            "wind_clamped": result.utci_output.wind_clamped if result.utci_output else False,
        }
    except ValueError as e:
        return {
            "status": "error",
            "error": str(e),
        }
