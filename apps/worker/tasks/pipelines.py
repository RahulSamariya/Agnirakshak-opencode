"""Pipeline orchestration tasks."""
import structlog

try:
    from worker.main import app
except ImportError:
    from main import app

from scientific.chain import run_thermal_hazard_chain
from scientific.risk.hsri import HSRIInput, calculate_hsri

logger = structlog.get_logger()


@app.task(name="worker.tasks.pipelines.forecast_pipeline")
def forecast_pipeline(
    source: str,
    model_name: str,
    parameters: dict | None = None,
):
    """Orchestrate the complete forecast pipeline.

    Pipeline stages:
        1. Ingest weather data
        2. Validate data
        3. Quality control
        4. Normalize data
        5. Spatialize to grid
        6. Calculate UTCI
        7. Calculate hazard indices

    This is an orchestration task that chains individual tasks.
    """
    logger.info(
        "forecast_pipeline_started",
        source=source,
        model_name=model_name,
    )

    # TODO: Implement full pipeline orchestration
    # In production, this would chain Celery tasks:
    # 1. ingest_task = ingest_weather.delay(source, parameters)
    # 2. validate_task = validate_data.delay(ingest_task.result)
    # 3. qc_task = quality_control.delay(validate_task.result)
    # 4. normalize_task = normalize_data.delay(qc_task.result)
    # 5. spatialize_task = spatialize_to_grid.delay(normalize_task.result)
    # 6. utci_task = calculate_utci.delay(spatialize_task.result)
    # 7. hazard_task = calculate_hazard.delay(utci_task.result)

    return {
        "status": "placeholder",
        "pipeline": "forecast_pipeline",
        "source": source,
        "model_name": model_name,
        "message": "Forecast pipeline orchestration ready - awaiting task chain implementation",
        "scientific_engine": "connected",
    }


@app.task(name="worker.tasks.pipelines.risk_pipeline")
def risk_pipeline(
    forecast_run_id: str,
    ward_ids: list | None = None,
):
    """Orchestrate the complete risk calculation pipeline.

    Pipeline stages:
        1. Calculate hazard from forecasts
        2. Load/calculate vulnerability profiles
        3. Load/calculate exposure profiles
        4. Calculate HSRI for each grid cell
        5. Aggregate to ward level
        6. Generate alerts

    This is an orchestration task that chains individual tasks.
    """
    logger.info(
        "risk_pipeline_started",
        forecast_run_id=forecast_run_id,
        ward_count=len(ward_ids) if ward_ids else "all",
    )

    # TODO: Implement full pipeline orchestration
    # In production, this would chain Celery tasks:
    # 1. hazard_task = calculate_hazard.delay(forecast_run_id)
    # 2. vulnerability_task = calculate_vulnerability.delay(ward_ids)
    # 3. exposure_task = calculate_exposure.delay(ward_ids)
    # 4. risk_task = calculate_risk.delay(hazard_task.result)
    # 5. aggregate_task = aggregate_wards.delay(risk_task.result)
    # 6. alert_task = generate_alerts.delay(aggregate_task.result)

    return {
        "status": "placeholder",
        "pipeline": "risk_pipeline",
        "forecast_run_id": forecast_run_id,
        "message": "Risk pipeline orchestration ready - awaiting task chain implementation",
        "scientific_engine": "connected",
    }


@app.task(name="worker.tasks.pipelines.run_single_cell")
def run_single_cell(
    air_temperature: float,
    relative_humidity: float,
    wind_speed: float,
    mean_radiant_temperature: float,
    vulnerability_index: float,
    exposure_index: float,
):
    """Run the complete pipeline for a single grid cell.

    This is a helper task for testing the full integration:
    weather -> UTCI -> H -> V -> E -> HSRI
    """
    try:
        # Step 1: Calculate UTCI and Hazard
        chain_result = run_thermal_hazard_chain(
            air_temperature=air_temperature,
            relative_humidity=relative_humidity,
            wind_speed=wind_speed,
            mean_radiant_temperature=mean_radiant_temperature,
        )

        if not chain_result.hazard_output:
            return {"status": "error", "error": "Failed to calculate hazard"}

        # Step 2: Calculate HSRI
        risk_data = HSRIInput(
            hazard_index=chain_result.hazard_output.hazard_index,
            vulnerability_index=vulnerability_index,
            exposure_index=exposure_index,
        )
        risk_result = calculate_hsri(risk_data)

        return {
            "status": "success",
            "utci_c": chain_result.utci_output.utci_c,
            "hazard_index": chain_result.hazard_output.hazard_index,
            "hazard_category": chain_result.hazard_output.hazard_category.value,
            "vulnerability_index": vulnerability_index,
            "exposure_index": exposure_index,
            "hsri_score": risk_result.hsri_score,
            "risk_level": risk_result.risk_level.value,
            "wind_clamped": chain_result.utci_output.wind_clamped,
        }
    except ValueError as e:
        return {"status": "error", "error": str(e)}
