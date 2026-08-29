"""End-to-end integration pipeline.

Connects all components into one working deterministic operational pipeline:
    Synthetic Weather → UTCI → H → V → E → HSRI → Database → Ward Aggregation → Alert

This module orchestrates the existing scientific engines and database models.

SYNTHETIC DATA POLICY:
    This module is for software integration testing ONLY.
    Every record must include:
        data_source = "synthetic"
        environment = "test"
    Synthetic data MUST NOT be used for:
        scientific validation
        mortality/hospitalization model training
        model performance claims
        real-world risk reporting
        operational alerts
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict

from scientific.chain import run_thermal_hazard_chain
from scientific.risk.hsri import HSRIInput, calculate_hsri, classify_hsri
from scientific.vulnerability.scoring import BBWMVulnerabilityModel
from scientific.exposure.scoring import BBWMExposureModel


# ---------------------------------------------------------------------------
# Synthetic data policy constants
# ---------------------------------------------------------------------------
DATA_SOURCE_SYNTHETIC = "synthetic"
ENVIRONMENT_TEST = "test"


# ---------------------------------------------------------------------------
# Data models for integration
# ---------------------------------------------------------------------------

class SyntheticWeatherRecord(BaseModel):
    """Deterministic weather record for a grid cell.

    SYNTHETIC DATA POLICY:
        data_source = "synthetic"
        environment = "test"
    """
    model_config = ConfigDict(frozen=True)

    grid_cell_id: str
    valid_time: datetime
    air_temperature: float
    relative_humidity: float
    wind_speed: float
    mean_radiant_temperature: float
    data_source: str = DATA_SOURCE_SYNTHETIC
    environment: str = ENVIRONMENT_TEST


class HazardResult(BaseModel):
    """Result from UTCI → Hazard calculation.

    SYNTHETIC DATA POLICY:
        data_source = "synthetic"
        environment = "test"
    """
    model_config = ConfigDict(frozen=True)

    grid_cell_id: str
    valid_time: datetime
    utci_c: float
    hazard_index: float
    hazard_category: str
    wind_clamped: bool
    original_wind_speed: float | None
    air_temperature: float
    relative_humidity: float
    wind_speed: float
    mean_radiant_temperature: float
    data_source: str = DATA_SOURCE_SYNTHETIC
    environment: str = ENVIRONMENT_TEST


class RiskAssessmentResult(BaseModel):
    """Result from HSRI calculation for a grid cell.

    SYNTHETIC DATA POLICY:
        data_source = "synthetic"
        environment = "test"
    """
    model_config = ConfigDict(frozen=True)

    grid_cell_id: str
    valid_time: datetime
    hazard_index: float
    vulnerability_index: float
    exposure_index: float
    hsri_score: float
    risk_level: str
    data_source: str = DATA_SOURCE_SYNTHETIC
    environment: str = ENVIRONMENT_TEST


class WardRiskSummaryResult(BaseModel):
    """Aggregated risk summary for a ward.

    SYNTHETIC DATA POLICY:
        data_source = "synthetic"
        environment = "test"
    """
    model_config = ConfigDict(frozen=True)

    ward_id: str
    valid_time: datetime
    mean_hazard: float
    mean_vulnerability: float
    mean_exposure: float
    mean_hsri: float
    max_hsri: float
    min_hsri: float
    risk_level: str
    cell_count: int
    high_risk_cell_count: int
    data_source: str = DATA_SOURCE_SYNTHETIC
    environment: str = ENVIRONMENT_TEST


class AlertResult(BaseModel):
    """Generated alert for a ward.

    SYNTHETIC DATA POLICY:
        data_source = "synthetic"
        environment = "test"
    """
    model_config = ConfigDict(frozen=True)

    ward_id: str
    alert_level: str
    title: str
    message: str
    valid_from: datetime
    valid_until: datetime
    data_source: str = DATA_SOURCE_SYNTHETIC
    environment: str = ENVIRONMENT_TEST


# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------

def generate_synthetic_city(
    city_name: str = "TestCity",
    num_wards: int = 10,
    grid_cells_per_ward: int = 10,
    valid_time: datetime | None = None,
) -> dict[str, Any]:
    """Generate deterministic synthetic city data.

    Returns:
        Dictionary with cities, wards, grid_cells, and weather data.
    """
    if valid_time is None:
        valid_time = datetime(2026, 8, 29, 12, 0, 0, tzinfo=timezone.utc)

    city_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, city_name))
    wards = []
    grid_cells = []
    weather_records = []

    for ward_idx in range(num_wards):
        ward_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{city_name}_ward_{ward_idx}"))
        wards.append({
            "id": ward_id,
            "name": f"Ward {ward_idx + 1}",
            "city_id": city_id,
            "ward_code": f"W{ward_idx + 1:03d}",
            "population": 10000 + ward_idx * 1000,
        })

        for cell_idx in range(grid_cells_per_ward):
            cell_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{city_name}_ward_{ward_idx}_cell_{cell_idx}"))

            # Deterministic weather pattern: varies by ward and cell
            # Temperature: 30-42C range, higher in wards with lower index
            # This ensures some grid cells have high hazard
            base_temp = 32.0 + (ward_idx * 0.8) + (cell_idx * 0.15)
            # Humidity: 40-80% range
            base_rh = 40.0 + (ward_idx * 2.0) + (cell_idx * 0.5)
            # Wind: 0.5-5.0 m/s range
            base_wind = 0.5 + (ward_idx * 0.3) + (cell_idx * 0.05)
            # MRT: higher than air temperature to increase UTCI
            base_mrt = base_temp + 5.0 + (cell_idx * 0.3)

            grid_cells.append({
                "id": cell_id,
                "cell_code": f"GC{ward_idx + 1:02d}{cell_idx + 1:02d}",
                "ward_id": ward_id,
                "latitude": 28.6 + ward_idx * 0.01 + cell_idx * 0.001,
                "longitude": 77.2 + ward_idx * 0.01 + cell_idx * 0.001,
            })

            weather_records.append(SyntheticWeatherRecord(
                grid_cell_id=cell_id,
                valid_time=valid_time,
                air_temperature=round(base_temp, 1),
                relative_humidity=round(min(100.0, max(0.0, base_rh)), 1),
                wind_speed=round(min(17.0, max(0.5, base_wind)), 2),
                mean_radiant_temperature=round(base_mrt, 1),
            ))

    return {
        "city": {
            "id": city_id,
            "name": city_name,
            "population": 100000,
        },
        "wards": wards,
        "grid_cells": grid_cells,
        "weather": weather_records,
        "valid_time": valid_time,
    }


def generate_synthetic_vulnerability(
    ward_ids: list[str],
    valid_time: datetime | None = None,
) -> list[dict[str, Any]]:
    """Generate deterministic synthetic vulnerability profiles."""
    if valid_time is None:
        valid_time = datetime(2026, 8, 29, 12, 0, 0, tzinfo=timezone.utc)

    profiles = []
    model = BBWMVulnerabilityModel()

    for i, ward_id in enumerate(ward_ids):
        # Deterministic vulnerability factors: varies by ward
        profile_data = {
            "age": 0.33 if i % 3 == 0 else (0.66 if i % 3 == 1 else 1.0),
            "bmi": 0.33 if i % 4 == 0 else (0.66 if i % 4 == 1 else 1.0),
            "economic_status": 0.33 if i % 2 == 0 else 0.66,
            "social_isolation": 0.33 if i % 3 != 0 else 0.66,
            "education": 0.33 if i % 2 == 0 else 0.66,
            "gender": 0.66 if i % 2 == 0 else 1.0,
            "health_issues": 0.33 if i % 3 == 0 else (0.66 if i % 3 == 1 else 1.0),
            "disability": 0.33 if i % 2 == 0 else 0.66,
        }

        result = model.calculate(profile_data)
        profiles.append({
            "ward_id": ward_id,
            "vulnerability_index": result.vulnerability_index,
            "contributions": {k: v.model_dump() for k, v in result.contributions.items()},
            "valid_time": valid_time,
        })

    return profiles


def generate_synthetic_exposure(
    ward_ids: list[str],
    valid_time: datetime | None = None,
) -> list[dict[str, Any]]:
    """Generate deterministic synthetic exposure profiles."""
    if valid_time is None:
        valid_time = datetime(2026, 8, 29, 12, 0, 0, tzinfo=timezone.utc)

    profiles = []
    model = BBWMExposureModel()

    for i, ward_id in enumerate(ward_ids):
        # Deterministic exposure factors: varies by ward
        # Infrastructure/transit sub-factors
        infra_condition = 0.33 if i % 3 == 0 else (0.66 if i % 3 == 1 else 1.0)
        infra_facilities = 0.33 if i % 2 == 0 else 0.66

        # Lifestyle sub-factors
        lifestyle_alcohol = 0.33 if i % 4 == 0 else 0.66
        lifestyle_sleep = 0.33 if i % 3 == 0 else 0.66
        lifestyle_tobacco = 0.33 if i % 2 == 0 else 0.66
        lifestyle_caffeine = 0.33 if i % 3 == 0 else 0.66

        profile_data = {
            "infrastructure_transit": {
                "condition": infra_condition,
                "facilities": infra_facilities,
            },
            "fluid_intake_activity": 0.33 if i % 2 == 0 else 0.66,
            "lifestyle": {
                "alcohol": lifestyle_alcohol,
                "sleep": lifestyle_sleep,
                "tobacco": lifestyle_tobacco,
                "caffeine": lifestyle_caffeine,
            },
            "air_quality": 0.66 if i % 2 == 0 else 1.0,
            "healthcare_accessibility": 0.33 if i % 3 == 0 else 0.66,
        }

        result = model.calculate(profile_data)
        profiles.append({
            "ward_id": ward_id,
            "exposure_index": result.exposure_index,
            "contributions": {k: v.model_dump() for k, v in result.contributions.items()},
            "valid_time": valid_time,
        })

    return profiles


# ---------------------------------------------------------------------------
# Pipeline execution
# ---------------------------------------------------------------------------

def run_weather_to_hazard(
    weather_records: list[SyntheticWeatherRecord],
) -> list[HazardResult]:
    """Run UTCI → Hazard for all weather records."""
    results = []
    for record in weather_records:
        chain_result = run_thermal_hazard_chain(
            air_temperature=record.air_temperature,
            relative_humidity=record.relative_humidity,
            wind_speed=record.wind_speed,
            mean_radiant_temperature=record.mean_radiant_temperature,
        )

        if chain_result.utci_output and chain_result.hazard_output:
            results.append(HazardResult(
                grid_cell_id=record.grid_cell_id,
                valid_time=record.valid_time,
                utci_c=chain_result.utci_output.utci_c,
                hazard_index=chain_result.hazard_output.hazard_index,
                hazard_category=chain_result.hazard_output.category.value,
                wind_clamped=chain_result.utci_output.wind_clamped,
                original_wind_speed=chain_result.utci_output.original_wind_speed,
                air_temperature=record.air_temperature,
                relative_humidity=record.relative_humidity,
                wind_speed=record.wind_speed,
                mean_radiant_temperature=record.mean_radiant_temperature,
            ))

    return results


def run_risk_assessment(
    hazard_results: list[HazardResult],
    vulnerability_profiles: dict[str, float],
    exposure_profiles: dict[str, float],
    grid_cells: list[dict[str, Any]],
) -> list[RiskAssessmentResult]:
    """Run HSRI = H × V × E for all grid cells."""
    # Map grid_cell_id to ward_id
    cell_to_ward = {gc["id"]: gc["ward_id"] for gc in grid_cells}

    results = []
    for hazard in hazard_results:
        ward_id = cell_to_ward.get(hazard.grid_cell_id)
        if ward_id is None:
            continue

        v_index = vulnerability_profiles.get(ward_id, 0.33)
        e_index = exposure_profiles.get(ward_id, 0.33)

        data = HSRIInput(
            hazard_index=hazard.hazard_index,
            vulnerability_index=v_index,
            exposure_index=e_index,
        )
        hsri_result = calculate_hsri(data)

        results.append(RiskAssessmentResult(
            grid_cell_id=hazard.grid_cell_id,
            valid_time=hazard.valid_time,
            hazard_index=hsri_result.hazard_index,
            vulnerability_index=hsri_result.vulnerability_index,
            exposure_index=hsri_result.exposure_index,
            hsri_score=hsri_result.hsri_score,
            risk_level=hsri_result.risk_level.value,
        ))

    return results


def aggregate_to_wards(
    risk_assessments: list[RiskAssessmentResult],
    grid_cells: list[dict[str, Any]],
    valid_time: datetime | None = None,
) -> list[WardRiskSummaryResult]:
    """Aggregate grid-cell risk scores to ward level."""
    if valid_time is None:
        valid_time = datetime(2026, 8, 29, 12, 0, 0, tzinfo=timezone.utc)

    # Map grid_cell_id to ward_id
    cell_to_ward = {gc["id"]: gc["ward_id"] for gc in grid_cells}

    # Group assessments by ward
    ward_assessments: dict[str, list[RiskAssessmentResult]] = {}
    for assessment in risk_assessments:
        ward_id = cell_to_ward.get(assessment.grid_cell_id)
        if ward_id:
            ward_assessments.setdefault(ward_id, []).append(assessment)

    results = []
    for ward_id, assessments in ward_assessments.items():
        hsri_values = [a.hsri_score for a in assessments]
        h_values = [a.hazard_index for a in assessments]
        v_values = [a.vulnerability_index for a in assessments]
        e_values = [a.exposure_index for a in assessments]

        mean_hsri = sum(hsri_values) / len(hsri_values)
        max_hsri = max(hsri_values)
        min_hsri = min(hsri_values)
        mean_h = sum(h_values) / len(h_values)
        mean_v = sum(v_values) / len(v_values)
        mean_e = sum(e_values) / len(e_values)

        # Classify ward risk based on mean HSRI
        risk_level = classify_hsri(mean_hsri).value

        results.append(WardRiskSummaryResult(
            ward_id=ward_id,
            valid_time=valid_time,
            mean_hazard=round(mean_h, 12),
            mean_vulnerability=round(mean_v, 12),
            mean_exposure=round(mean_e, 12),
            mean_hsri=round(mean_hsri, 12),
            max_hsri=round(max_hsri, 12),
            min_hsri=round(min_hsri, 12),
            risk_level=risk_level,
            cell_count=len(assessments),
            high_risk_cell_count=sum(1 for h in hsri_values if h > 0.66),
        ))

    return results


def generate_alerts(
    ward_summaries: list[WardRiskSummaryResult],
    valid_time: datetime | None = None,
) -> list[AlertResult]:
    """Generate alerts for high-risk wards."""
    if valid_time is None:
        valid_time = datetime(2026, 8, 29, 12, 0, 0, tzinfo=timezone.utc)

    alerts = []
    for summary in ward_summaries:
        if summary.risk_level in ("medium", "high"):
            alert_level = "WARNING" if summary.risk_level == "medium" else "CRITICAL"
            alerts.append(AlertResult(
                ward_id=summary.ward_id,
                alert_level=alert_level,
                title=f"Heatwave Alert - {summary.risk_level.upper()} Risk",
                message=(
                    f"Ward {summary.ward_id[:8]}... has {summary.risk_level} heat risk. "
                    f"Mean HSRI: {summary.mean_hsri:.3f}, "
                    f"Max HSRI: {summary.max_hsri:.3f}, "
                    f"High-risk cells: {summary.high_risk_cell_count}/{summary.cell_count}"
                ),
                valid_from=valid_time,
                valid_until=valid_time,
            ))

    return alerts


# ---------------------------------------------------------------------------
# Full pipeline execution
# ---------------------------------------------------------------------------

class PipelineResult(BaseModel):
    """Complete result from the integration pipeline."""
    model_config = ConfigDict(frozen=True)

    city: dict[str, Any]
    wards: list[dict[str, Any]]
    grid_cells: list[dict[str, Any]]
    hazard_results: list[HazardResult]
    vulnerability_profiles: list[dict[str, Any]]
    exposure_profiles: list[dict[str, Any]]
    risk_assessments: list[RiskAssessmentResult]
    ward_summaries: list[WardRiskSummaryResult]
    alerts: list[AlertResult]
    valid_time: datetime


def run_full_pipeline(
    city_name: str = "TestCity",
    num_wards: int = 10,
    grid_cells_per_ward: int = 10,
    valid_time: datetime | None = None,
) -> PipelineResult:
    """Execute the complete integration pipeline.

    Flow:
        Synthetic Weather → UTCI → H → V → E → HSRI → Ward Aggregation → Alert
    """
    if valid_time is None:
        valid_time = datetime(2026, 8, 29, 12, 0, 0, tzinfo=timezone.utc)

    # 1. Generate synthetic city
    city_data = generate_synthetic_city(
        city_name=city_name,
        num_wards=num_wards,
        grid_cells_per_ward=grid_cells_per_ward,
        valid_time=valid_time,
    )

    # 2. Run weather → UTCI → Hazard
    hazard_results = run_weather_to_hazard(city_data["weather"])

    # 3. Generate vulnerability profiles
    ward_ids = [w["id"] for w in city_data["wards"]]
    vuln_profiles = generate_synthetic_vulnerability(ward_ids, valid_time)
    vuln_map = {p["ward_id"]: p["vulnerability_index"] for p in vuln_profiles}

    # 4. Generate exposure profiles
    exp_profiles = generate_synthetic_exposure(ward_ids, valid_time)
    exp_map = {p["ward_id"]: p["exposure_index"] for p in exp_profiles}

    # 5. Run risk assessment (HSRI = H × V × E)
    risk_assessments = run_risk_assessment(
        hazard_results, vuln_map, exp_map, city_data["grid_cells"]
    )

    # 6. Aggregate to ward level
    ward_summaries = aggregate_to_wards(
        risk_assessments, city_data["grid_cells"], valid_time
    )

    # 7. Generate alerts
    alerts = generate_alerts(ward_summaries, valid_time)

    return PipelineResult(
        city=city_data["city"],
        wards=city_data["wards"],
        grid_cells=city_data["grid_cells"],
        hazard_results=hazard_results,
        vulnerability_profiles=vuln_profiles,
        exposure_profiles=exp_profiles,
        risk_assessments=risk_assessments,
        ward_summaries=ward_summaries,
        alerts=alerts,
        valid_time=valid_time,
    )
