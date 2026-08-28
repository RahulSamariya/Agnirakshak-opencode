"""Exposure Index calculation.

Atomic scores use the supplied 0.33 / 0.66 / 1.00 scale.
"""
from __future__ import annotations

from typing import Final

from pydantic import BaseModel, ConfigDict, Field, model_validator

_ALLOWED_SCORES: Final = (0.33, 0.66, 1.00)


def _validate_discrete_score(value: float, field_name: str) -> float:
    value = float(value)
    if min(abs(value - candidate) for candidate in _ALLOWED_SCORES) > 1e-9:
        raise ValueError(
            f"{field_name} must be one of 0.33, 0.66, or 1.00; got {value}."
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
    fluid_activity: float = Field(..., ge=0.33, le=1.00)
    air_quality: float = Field(..., ge=0.33, le=1.00)
    healthcare_access: float = Field(..., ge=0.33, le=1.00)

    @model_validator(mode="after")
    def validate_top_level_scores(self) -> ExposureInput:
        _validate_discrete_score(self.fluid_activity, "fluid_activity")
        _validate_discrete_score(self.air_quality, "air_quality")
        _validate_discrete_score(self.healthcare_access, "healthcare_access")
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


EXPOSURE_WEIGHTS: Final = {
    "infrastructure_transit": 0.282,
    "lifestyle": 0.184,
    "fluid_activity": 0.282,
    "air_quality": 0.126,
    "healthcare_access": 0.125,
}

INFRASTRUCTURE_WEIGHTS: Final = {
    "condition": 0.508,
    "facilities": 0.492,
}

LIFESTYLE_WEIGHTS: Final = {
    "alcohol": 0.341,
    "sleep": 0.232,
    "tobacco": 0.218,
    "caffeine": 0.208,
}


def calculate_infrastructure_transit(
    data: InfrastructureTransitScores,
) -> float:
    return (
        0.508 * data.condition
        + 0.492 * data.facilities
    )


def calculate_lifestyle(data: LifestyleScores) -> float:
    return (
        0.341 * data.alcohol
        + 0.232 * data.sleep
        + 0.218 * data.tobacco
        + 0.208 * data.caffeine
    )


def calculate_exposure(data: ExposureInput) -> ExposureOutput:
    infrastructure_score = calculate_infrastructure_transit(
        data.infrastructure_transit
    )
    lifestyle_score = calculate_lifestyle(data.lifestyle)

    component_scores = {
        "infrastructure_transit": infrastructure_score,
        "lifestyle": lifestyle_score,
        "fluid_activity": data.fluid_activity,
        "air_quality": data.air_quality,
        "healthcare_access": data.healthcare_access,
    }

    total = 0.0
    contributions: dict[str, ExposureContribution] = {}
    for component_name, weight in EXPOSURE_WEIGHTS.items():
        score = float(component_scores[component_name])
        contribution = weight * score
        total += contribution
        contributions[component_name] = ExposureContribution(
            score=score,
            weight=weight,
            contribution=contribution,
        )
    total = float(min(1.0, max(0.33, round(total, 12))))
    return ExposureOutput(
        exposure_index=total,
        contributions=contributions,
    )
