"""Exposure Index calculation.

Atomic scores use the supplied 0.33 / 0.66 / 1.00 scale.
Weights and floors are loaded from configuration YAML.
Standardized naming: fluid_intake_activity, healthcare_accessibility.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from scientific.configuration.loader import load_exposure_weights
from scientific.exposure.base import ExposureModel


def _validate_discrete_score(value: float, field_name: str) -> float:
    cfg = load_exposure_weights()
    allowed = tuple(cfg.scoring.values())
    value = float(value)
    if min(abs(value - c) for c in allowed) > 1e-9:
        raise ValueError(
            f"{field_name} must be one of {allowed}; got {value}."
        )
    return value


class InfrastructureTransitScores(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    condition: float = Field(..., ge=0.33, le=1.00)
    facilities: float = Field(..., ge=0.33, le=1.00)

    @model_validator(mode="after")
    def validate_scores(self) -> InfrastructureTransitScores:
        _validate_discrete_score(self.condition, "condition")
        _validate_discrete_score(self.facilities, "facilities")
        return self


class LifestyleScores(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    alcohol: float = Field(..., ge=0.33, le=1.00)
    sleep: float = Field(..., ge=0.33, le=1.00)
    tobacco: float = Field(..., ge=0.33, le=1.00)
    caffeine: float = Field(..., ge=0.33, le=1.00)

    @model_validator(mode="after")
    def validate_scores(self) -> LifestyleScores:
        for name in ("alcohol", "sleep", "tobacco", "caffeine"):
            _validate_discrete_score(getattr(self, name), name)
        return self


class ExposureInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    infrastructure_transit: InfrastructureTransitScores
    lifestyle: LifestyleScores
    fluid_intake_activity: float = Field(..., ge=0.33, le=1.00)
    air_quality: float = Field(..., ge=0.33, le=1.00)
    healthcare_accessibility: float = Field(..., ge=0.33, le=1.00)

    @model_validator(mode="after")
    def validate_top_level_scores(self) -> ExposureInput:
        _validate_discrete_score(self.fluid_intake_activity, "fluid_intake_activity")
        _validate_discrete_score(self.air_quality, "air_quality")
        _validate_discrete_score(self.healthcare_accessibility, "healthcare_accessibility")
        return self


class ExposureContribution(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    score: float
    weight: float
    contribution: float


class ExposureOutput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    exposure_index: float = Field(..., ge=0.33, le=1.0)
    contributions: dict[str, ExposureContribution]


# ---------------------------------------------------------------------------
# Pure calculation functions (config-driven)
# ---------------------------------------------------------------------------

def calculate_infrastructure_transit(data: InfrastructureTransitScores) -> float:
    cfg = load_exposure_weights()
    sub = cfg.infrastructure_transit_sub
    return sub["condition"] * data.condition + sub["facilities"] * data.facilities


def calculate_lifestyle(data: LifestyleScores) -> float:
    cfg = load_exposure_weights()
    sub = cfg.lifestyle_sub
    return (
        sub["alcohol"] * data.alcohol
        + sub["sleep"] * data.sleep
        + sub["tobacco"] * data.tobacco
        + sub["caffeine"] * data.caffeine
    )


def calculate_exposure(data: ExposureInput) -> ExposureOutput:
    cfg = load_exposure_weights()
    infrastructure_score = calculate_infrastructure_transit(data.infrastructure_transit)
    lifestyle_score = calculate_lifestyle(data.lifestyle)

    component_scores = {
        "infrastructure_transit": infrastructure_score,
        "lifestyle": lifestyle_score,
        "fluid_intake_activity": data.fluid_intake_activity,
        "air_quality": data.air_quality,
        "healthcare_accessibility": data.healthcare_accessibility,
    }

    total = 0.0
    contributions: dict[str, ExposureContribution] = {}
    for component_name, weight in cfg.weights.items():
        score = float(component_scores[component_name])
        contribution = weight * score
        total += contribution
        contributions[component_name] = ExposureContribution(
            score=score,
            weight=weight,
            contribution=contribution,
        )
    total = float(min(1.0, max(cfg.residual_floor, round(total, 12))))
    return ExposureOutput(
        exposure_index=total,
        contributions=contributions,
    )


# ---------------------------------------------------------------------------
# Concrete Phase-1 interface implementation
# ---------------------------------------------------------------------------

class BBWMExposureModel(ExposureModel):
    """Configuration-driven BBWM exposure model."""

    @property
    def model_name(self) -> str:
        return "exposure-bbwm-v1"

    @property
    def model_version(self) -> str:
        cfg = load_exposure_weights()
        return cfg.version

    @property
    def weights(self) -> dict[str, float]:
        cfg = load_exposure_weights()
        return dict(cfg.weights)

    def score_factor(self, factor_name: str, raw_value: Any) -> float:
        """Score a raw factor value.

        Phase 2 accepts already-normalized scores from config (0.33/0.66/1.00).
        Raw-to-score classification rules are not yet implemented.
        """
        cfg = load_exposure_weights()
        allowed = tuple(cfg.scoring.values())
        value = float(raw_value)
        if min(abs(value - c) for c in allowed) > 1e-9:
            raise ValueError(
                f"{factor_name} must be one of {allowed}; got {value}."
            )
        return value

    def calculate(self, profile: dict[str, Any]) -> ExposureOutput:
        infra = InfrastructureTransitScores(**profile["infrastructure_transit"])
        lifestyle = LifestyleScores(**profile["lifestyle"])
        data = ExposureInput(
            infrastructure_transit=infra,
            lifestyle=lifestyle,
            fluid_intake_activity=profile["fluid_intake_activity"],
            air_quality=profile["air_quality"],
            healthcare_accessibility=profile["healthcare_accessibility"],
        )
        return calculate_exposure(data)
