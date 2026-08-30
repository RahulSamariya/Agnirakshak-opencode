"""Canonical staging schemas for Ahmedabad pilot data.

Pydantic models that define the expected format for real data ingestion.
These align with existing scientific models and serve as contracts
for data loading, validation, and normalization.

No synthetic data policy markers — these are for REAL data ingestion.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Weather staging schemas
# ---------------------------------------------------------------------------

class WeatherRecord(BaseModel):
    """Single weather observation from ERA5-Land or IMDAA.

    Maps directly to UTCIInput fields for pipeline consumption.
    """
    model_config = ConfigDict(frozen=True)

    station_id: str = Field(..., description="Grid cell or station identifier")
    valid_time: datetime = Field(..., description="Observation timestamp (UTC)")
    air_temperature: float = Field(
        ..., description="2m air temperature in degrees Celsius"
    )
    relative_humidity: float = Field(
        ..., ge=0.0, le=100.0, description="Relative humidity in percent"
    )
    wind_speed: float = Field(
        ..., ge=0.0, description="10m wind speed in m/s"
    )
    mean_radiant_temperature: float = Field(
        ..., description="Mean radiant temperature in degrees Celsius"
    )
    surface_pressure: float | None = Field(
        None, description="Surface pressure in Pa (ERA5 sp)"
    )
    solar_radiation: float | None = Field(
        None, description="Surface solar radiation in J/m2 (ERA5 ssrd)"
    )
    thermal_radiation: float | None = Field(
        None, description="Surface thermal radiation in J/m2 (ERA5 strd)"
    )
    data_source: str = Field(
        "era5land", description="Source dataset identifier"
    )

    def to_utci_input(self) -> dict[str, Any]:
        """Convert to UTCI calculation input format."""
        return {
            "air_temperature": self.air_temperature,
            "relative_humidity": self.relative_humidity,
            "wind_speed": self.wind_speed,
            "mean_radiant_temperature": self.mean_radiant_temperature,
        }


class WeatherGrid(BaseModel):
    """Grid of weather records for a single timestep."""
    model_config = ConfigDict(frozen=True)

    valid_time: datetime
    records: list[WeatherRecord]
    data_source: str = "era5land"


# ---------------------------------------------------------------------------
# GIS staging schemas
# ---------------------------------------------------------------------------

class WardBoundary(BaseModel):
    """Single ward boundary from normalized GeoJSON."""
    model_config = ConfigDict(frozen=True)

    ward_id: str = Field(..., description="Unique ward identifier")
    ward_name: str = Field(..., description="Human-readable ward name")
    ward_code: str = Field(..., description="Administrative ward code")
    lgd_code: str | None = Field(None, description="LGD ward code")
    geometry: dict[str, Any] = Field(
        ..., description="GeoJSON geometry (Polygon)"
    )
    centroid_lat: float = Field(..., description="Ward centroid latitude")
    centroid_lon: float = Field(..., description="Ward centroid longitude")
    area_sq_km: float | None = Field(None, description="Ward area in km²")
    crs: str = Field("EPSG:4326", description="Coordinate reference system")


class WardCensus(BaseModel):
    """Census demographic data for a ward."""
    model_config = ConfigDict(frozen=True)

    ward_id: str = Field(..., description="Ward identifier (must match WardBoundary)")
    ward_name: str
    population_total: int = Field(..., ge=0)
    population_male: int | None = Field(None, ge=0)
    population_female: int | None = Field(None, ge=0)
    population_0_14: int | None = Field(None, ge=0, description="Age 0-14")
    population_15_29: int | None = Field(None, ge=0, description="Age 15-29")
    population_30_44: int | None = Field(None, ge=0, description="Age 30-44")
    population_45_59: int | None = Field(None, ge=0, description="Age 45-59")
    population_60_plus: int | None = Field(None, ge=0, description="Age 60+")
    households: int | None = Field(None, ge=0)
    workers_total: int | None = Field(None, ge=0)
    workers_main_worker: int | None = Field(None, ge=0)
    workers_marginal_worker: int | None = Field(None, ge=0)
    source: str = Field("census_2011", description="Data source")
    census_year: int = Field(2011)


# ---------------------------------------------------------------------------
# AQI staging schemas
# ---------------------------------------------------------------------------

class AQIRecord(BaseModel):
    """Single hourly AQI observation."""
    model_config = ConfigDict(frozen=True)

    city: str = Field("Ahmedabad")
    valid_time: datetime = Field(..., description="Observation timestamp (IST)")
    aqi_value: float = Field(..., ge=0, description="AQI value (CPCB scale)")
    pollutant: str = Field("composite", description="Pollutant name or 'composite'")
    data_source: str = Field("cpcb", description="Source agency")
    quality_flag: str | None = Field(
        None, description="QC flag if available"
    )


class AQIDaily(BaseModel):
    """Daily AQI summary."""
    model_config = ConfigDict(frozen=True)

    city: str = "Ahmedabad"
    date: datetime
    aqi_mean: float = Field(..., ge=0)
    aqi_min: float = Field(..., ge=0)
    aqi_max: float = Field(..., ge=0)
    aqi_missing_hours: int = Field(0, ge=0)
    data_source: str = "cpcb"


# ---------------------------------------------------------------------------
# Vulnerability staging schemas
# ---------------------------------------------------------------------------

class VulnerabilityWardInput(BaseModel):
    """Vulnerability factor scores for a single ward.

    Uses the 0.33 / 0.66 / 1.00 discrete scale from BBWM model.
    """
    model_config = ConfigDict(frozen=True)

    ward_id: str = Field(..., description="Ward identifier")
    valid_time: datetime = Field(..., description="Assessment timestamp")

    age: float = Field(..., ge=0.33, le=1.0)
    bmi: float = Field(..., ge=0.33, le=1.0)
    economic_status: float = Field(..., ge=0.33, le=1.0)
    social_isolation: float = Field(..., ge=0.33, le=1.0)
    education: float = Field(..., ge=0.33, le=1.0)
    gender: float = Field(..., ge=0.33, le=1.0)
    health_issues: float = Field(..., ge=0.33, le=1.0)
    disability: float = Field(..., ge=0.33, le=1.0)

    data_source: str = Field("survey", description="Data source")


# ---------------------------------------------------------------------------
# Exposure staging schemas
# ---------------------------------------------------------------------------

class ExposureWardInput(BaseModel):
    """Exposure factor scores for a single ward.

    Uses the 0.33 / 0.66 / 1.00 discrete scale from BBWM model.
    """
    model_config = ConfigDict(frozen=True)

    ward_id: str = Field(..., description="Ward identifier")
    valid_time: datetime = Field(..., description="Assessment timestamp")

    infrastructure_transit_condition: float = Field(..., ge=0.33, le=1.0)
    infrastructure_transit_facilities: float = Field(..., ge=0.33, le=1.0)
    fluid_intake_activity: float = Field(..., ge=0.33, le=1.0)
    lifestyle_alcohol: float = Field(..., ge=0.33, le=1.0)
    lifestyle_sleep: float = Field(..., ge=0.33, le=1.0)
    lifestyle_tobacco: float = Field(..., ge=0.33, le=1.0)
    lifestyle_caffeine: float = Field(..., ge=0.33, le=1.0)
    air_quality: float = Field(..., ge=0.33, le=1.0)
    healthcare_accessibility: float = Field(..., ge=0.33, le=1.0)

    data_source: str = Field("survey", description="Data source")

    def to_model_input(self) -> dict[str, Any]:
        """Convert to BBWMExposureModel input format."""
        return {
            "infrastructure_transit": {
                "condition": self.infrastructure_transit_condition,
                "facilities": self.infrastructure_transit_facilities,
            },
            "fluid_intake_activity": self.fluid_intake_activity,
            "lifestyle": {
                "alcohol": self.lifestyle_alcohol,
                "sleep": self.lifestyle_sleep,
                "tobacco": self.lifestyle_tobacco,
                "caffeine": self.lifestyle_caffeine,
            },
            "air_quality": self.air_quality,
            "healthcare_accessibility": self.healthcare_accessibility,
        }


# ---------------------------------------------------------------------------
# Risk output staging schemas
# ---------------------------------------------------------------------------

class RiskAssessment(BaseModel):
    """Risk assessment result for a grid cell or ward."""
    model_config = ConfigDict(frozen=True)

    location_id: str = Field(..., description="Grid cell or ward ID")
    valid_time: datetime
    hazard_index: float = Field(..., ge=0.0, le=1.0)
    vulnerability_index: float = Field(..., ge=0.33, le=1.0)
    exposure_index: float = Field(..., ge=0.33, le=1.0)
    hsri_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., description="low / medium / high")
    data_source: str = Field("pipeline", description="Processing source")


class WardRiskSummary(BaseModel):
    """Aggregated ward-level risk summary."""
    model_config = ConfigDict(frozen=True)

    ward_id: str
    valid_time: datetime
    mean_hazard: float = Field(..., ge=0.0, le=1.0)
    mean_vulnerability: float = Field(..., ge=0.33, le=1.0)
    mean_exposure: float = Field(..., ge=0.33, le=1.0)
    mean_hsri: float = Field(..., ge=0.0, le=1.0)
    max_hsri: float = Field(..., ge=0.0, le=1.0)
    min_hsri: float = Field(..., ge=0.0, le=1.0)
    risk_level: str
    cell_count: int = Field(..., ge=0)
    high_risk_cell_count: int = Field(..., ge=0)
    data_source: str = "pipeline"


# ---------------------------------------------------------------------------
# Health data staging schemas (when available)
# ---------------------------------------------------------------------------

class HealthRecord(BaseModel):
    """Mortality or hospitalization record."""
    model_config = ConfigDict(frozen=True)

    ward_id: str
    valid_time: datetime
    record_type: str = Field(..., description="mortality or hospitalization")
    count: int = Field(..., ge=0)
    cause: str | None = Field(None, description="Cause category if available")
    age_group: str | None = Field(None)
    gender: str | None = Field(None)
    data_source: str = Field("health_dept", description="Source agency")


# ---------------------------------------------------------------------------
# Provenance tracking
# ---------------------------------------------------------------------------

class ProvenanceRecord(BaseModel):
    """Data provenance metadata for a processed record."""
    model_config = ConfigDict(frozen=True)

    source_id: str = Field(..., description="Source dataset identifier")
    source_file: str = Field(..., description="Original file path")
    source_hash: str = Field(..., description="SHA-256 hash of source file (canonical project checksum)")
    retrieved_at: datetime = Field(..., description="When data was retrieved")
    transformation_version: str = Field(
        "v1.0.0", description="Processing script version"
    )
    quality_flag: str = Field(
        "PASS", description="PASS / PARTIAL / BLOCKED"
    )
    schema_version: str = Field(
        "v1.0.0", description="Schema version"
    )
    notes: str | None = Field(None, description="Additional notes")
