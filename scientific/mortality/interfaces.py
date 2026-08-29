"""DeepTherm mortality model interfaces.

Architecture-only — no training, no Indian data, no Spanish data.

This module defines:
    - Input/output schemas for the mortality prediction model
    - Configuration structure for the Transformer and Random Forest components
    - Dataset schema for future Indian mortality/health data
    - Feature schema for model inputs
    - Model metadata structure

The actual models are NOT trained in this phase.
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AlertLevel(str, Enum):
    """Mortality excess risk alert levels."""
    NONE = "none"
    L1 = "L1"  # R > 0.15
    L2 = "L2"  # R > 0.30


class ModelType(str, Enum):
    """Supported mortality model types."""
    TRANSFORMER = "transformer"
    RANDOM_FOREST = "random_forest"
    QUASI_POISSON = "quasi_poisson"


# ---------------------------------------------------------------------------
# Feature Schema
# ---------------------------------------------------------------------------

class WeatherSequenceFeatures(BaseModel):
    """14-day weather sequence features for mortality model."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    air_temperature: list[float] = Field(
        ..., min_length=14, max_length=14,
        description="Daily mean air temperature (C) for 14 days.",
    )
    relative_humidity: list[float] = Field(
        ..., min_length=14, max_length=14,
        description="Daily mean relative humidity (%) for 14 days.",
    )
    wind_speed: list[float] = Field(
        ..., min_length=14, max_length=14,
        description="Daily mean wind speed (m/s) for 14 days.",
    )
    mean_radiant_temperature: list[float] = Field(
        ..., min_length=14, max_length=14,
        description="Daily mean radiant temperature (C) for 14 days.",
    )
    precipitation: list[float] = Field(
        ..., min_length=14, max_length=14,
        description="Daily precipitation (mm) for 14 days.",
    )


class HealthFeatures(BaseModel):
    """Population health features (for future Indian data)."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    population_density: float = Field(
        ..., ge=0.0,
        description="Population density (persons/km2).",
    )
    age_distribution_65plus: float = Field(
        ..., ge=0.0, le=1.0,
        description="Fraction of population aged 65+.",
    )
    chronic_disease_prevalence: float = Field(
        ..., ge=0.0, le=1.0,
        description="Prevalence of chronic diseases in population.",
    )
    healthcare_access_index: float = Field(
        ..., ge=0.0, le=1.0,
        description="Healthcare access index (0=worst, 1=best).",
    )


class HSRIInput(BaseModel):
    """HSRI values as input to mortality model."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    hazard_index: float = Field(..., ge=0.0, le=1.0)
    vulnerability_index: float = Field(..., ge=0.0, le=1.0)
    exposure_index: float = Field(..., ge=0.0, le=1.0)
    hsri: float = Field(..., ge=0.0, le=1.0)
    risk_level: str


# ---------------------------------------------------------------------------
# Transformer Model Configuration
# ---------------------------------------------------------------------------

class TransformerConfig(BaseModel):
    """Configuration for the DeepTherm Transformer component."""
    model_config = ConfigDict(frozen=True)

    history_length: int = Field(default=14, description="Days of input history.")
    positional_embedding_dim: int = Field(
        default=32, description="Positional embedding dimensions."
    )
    num_attention_blocks: int = Field(default=2, description="Number of attention blocks.")
    num_attention_heads: int = Field(default=2, description="Number of attention heads.")
    mlp_hidden_layers: int = Field(default=2, description="MLP head layers.")
    dropout: float = Field(default=0.1, ge=0.0, le=1.0)
    model_type: ModelType = ModelType.TRANSFORMER


# ---------------------------------------------------------------------------
# Random Forest Configuration
# ---------------------------------------------------------------------------

class RandomForestConfig(BaseModel):
    """Configuration for the baseline Random Forest component."""
    model_config = ConfigDict(frozen=True)

    n_estimators: int = Field(default=1000, description="Number of trees.")
    max_depth: int | None = Field(default=None, description="Max tree depth.")
    min_samples_split: int = Field(default=2)
    min_samples_leaf: int = Field(default=1)
    random_state: int | None = Field(default=42)
    model_type: ModelType = ModelType.RANDOM_FOREST


# ---------------------------------------------------------------------------
# Quasi-Poisson Baseline Configuration
# ---------------------------------------------------------------------------

class QuasiPoissonConfig(BaseModel):
    """Configuration for the 2-year rolling Quasi-Poisson baseline."""
    model_config = ConfigDict(frozen=True)

    rolling_window_days: int = Field(
        default=730, description="Rolling window in days (2 years)."
    )
    degree_of_freedom: int = Field(
        default=7, description="Degrees of freedom for spline smoothing."
    )
    model_type: ModelType = ModelType.QUASI_POISSON


# ---------------------------------------------------------------------------
# Model Metadata
# ---------------------------------------------------------------------------

class MortalityModelMetadata(BaseModel):
    """Metadata for a trained mortality model (populated after training)."""
    model_config = ConfigDict(frozen=True)

    model_type: ModelType
    version: str = Field(default="0.0.0")
    training_data_source: str = Field(
        default="NOT_YET_TRAINED",
        description="Source of training data (must be Indian data).",
    )
    training_period: str | None = None
    geographic_scope: str | None = None
    feature_importances: dict[str, float] | None = None
    performance_metrics: dict[str, float] | None = None
    notes: str = ""


# ---------------------------------------------------------------------------
# Prediction Outputs
# ---------------------------------------------------------------------------

class MortalityPrediction(BaseModel):
    """Output from the mortality/hospitalization prediction model."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    predicted_excess_risk: float = Field(
        ..., ge=0.0,
        description="Predicted excess risk ratio R(t).",
    )
    alert_level: AlertLevel = Field(
        ..., description="Alert level based on R(t) thresholds."
    )
    expected_non_heat_mortality: float = Field(
        ..., ge=0.0,
        description="Expected non-heat mortality from Quasi-Poisson baseline.",
    )
    predicted_total_mortality: float = Field(
        ..., ge=0.0,
        description="Predicted all-cause mortality.",
    )
    confidence_lower: float | None = Field(
        default=None, description="Lower bound of confidence interval."
    )
    confidence_upper: float | None = Field(
        default=None, description="Upper bound of confidence interval."
    )
    model_metadata: MortalityModelMetadata


class ExcessRiskCalculation(BaseModel):
    """Excess risk calculation: R(t) = (X_all_cause - X_non_hr) / X_non_hr."""
    model_config = ConfigDict(frozen=True, extra="forbid")

    all_cause_mortality: float = Field(..., ge=0.0)
    non_heat_related_mortality: float = Field(..., ge=0.0)
    excess_risk_ratio: float = Field(..., ge=-1.0)
    alert_level: AlertLevel

    @classmethod
    def from_counts(
        cls,
        all_cause: float,
        non_heat: float,
        model_metadata: MortalityModelMetadata | None = None,
    ) -> ExcessRiskCalculation:
        """Calculate excess risk from mortality counts.

        R(t) = (X_all_cause - X_non_hr) / X_non_hr
        """
        if non_heat <= 0:
            raise ValueError("non_heat_related_mortality must be > 0")
        r = (all_cause - non_heat) / non_heat
        if r > 0.30:
            level = AlertLevel.L2
        elif r > 0.15:
            level = AlertLevel.L1
        else:
            level = AlertLevel.NONE
        return cls(
            all_cause_mortality=all_cause,
            non_heat_related_mortality=non_heat,
            excess_risk_ratio=r,
            alert_level=level,
        )


# ---------------------------------------------------------------------------
# Dataset Schema (for future Indian mortality data)
# ---------------------------------------------------------------------------

class MortalityRecord(BaseModel):
    """Schema for a single mortality/health record."""
    model_config = ConfigDict(frozen=True)

    date: str = Field(..., description="ISO date string YYYY-MM-DD.")
    region_code: str = Field(..., description="Administrative region code.")
    all_cause_deaths: int = Field(..., ge=0)
    heat_related_deaths: int | None = Field(default=None, ge=0)
    hospital_admissions: int | None = Field(default=None, ge=0)
    population: int = Field(..., gt=0)
    mean_temperature: float = Field(..., description="Mean daily temperature (C).")
    max_temperature: float = Field(..., description="Max daily temperature (C).")
    mean_humidity: float = Field(..., ge=0.0, le=100.0)


class MortalityDataset(BaseModel):
    """Schema for a mortality dataset (for future Indian data)."""
    model_config = ConfigDict(frozen=True)

    dataset_name: str
    source: str = "NOT_YET_COLLECTED"
    records: list[MortalityRecord] = Field(default_factory=list)
    geographic_scope: str = "India"
    temporal_scope: str | None = None
    notes: str = "Awaiting Indian mortality/health data collection."
