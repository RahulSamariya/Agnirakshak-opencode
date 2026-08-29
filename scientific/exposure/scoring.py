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

# ---------------------------------------------------------------------------
# Raw-to-score classification functions
# ---------------------------------------------------------------------------

def score_infrastructure_condition(condition: str) -> float:
    """Classify housing/infrastructure condition.

    Convention:
        'permanent' / 'masonry' / 'pucca' -> LOW (0.33)
        'kutcha' / 'homeless' / 'temporary' -> HIGH (1.00)
    """
    normalized = condition.strip().lower()
    mapping = {
        "permanent": 0.33,
        "masonry": 0.33,
        "pucca": 0.33,
        "kutcha": 1.00,
        "homeless": 1.00,
        "temporary": 1.00,
        "semi_pucca": 0.66,
        "semi-pucca": 0.66,
    }
    if normalized not in mapping:
        raise ValueError(
            f"Invalid infrastructure condition: {condition!r}. "
            f"Expected one of: {list(mapping.keys())}"
        )
    return mapping[normalized]


def score_facilities_commuting(commuting: str) -> float:
    """Classify facilities and commuting type.

    Convention:
        'ac' / 'ac_workspace' / 'ac_commute'  -> LOW (0.33)
        'shade' / 'motorized' / 'non_ac'       -> MEDIUM (0.66)
        'no_cooling' / 'walking' / 'cycling' / 'non_motorized' -> HIGH (1.00)
    """
    normalized = commuting.strip().lower()
    mapping = {
        "ac": 0.33,
        "ac_workspace": 0.33,
        "ac_commute": 0.33,
        "air_conditioned": 0.33,
        "shade": 0.66,
        "motorized": 0.66,
        "non_ac": 0.66,
        "basic_shade": 0.66,
        "no_cooling": 1.00,
        "walking": 1.00,
        "cycling": 1.00,
        "non_motorized": 1.00,
        "no_shade": 1.00,
    }
    if normalized not in mapping:
        raise ValueError(
            f"Invalid commuting/facilities: {commuting!r}. "
            f"Expected one of: {list(mapping.keys())}"
        )
    return mapping[normalized]


def score_lifestyle_factor(
    factor: str, is_high_risk: bool
) -> float:
    """Score a binary lifestyle sub-factor.

    Convention:
        absent (is_high_risk=False) -> LOW (0.33)
        present (is_high_risk=True) -> HIGH (1.00)

    Factors: alcohol, sleep, tobacco, caffeine
    """
    return 1.00 if is_high_risk else 0.33


def score_fluid_intake(fluid_deficit_pct: float) -> float:
    """Classify fluid intake/activity status.

    Convention:
        fluid_deficit <= 4%  -> LOW (0.33)  (meets requirement)
        fluid_deficit > 4%   -> HIGH (1.00) (dehydration risk)
    """
    if fluid_deficit_pct > 4.0:
        return 1.00
    return 0.33


def score_air_quality(aqi_category: str) -> float:
    """Classify air quality into exposure score.

    Convention:
        'good' / 'satisfactory' / 'moderate' -> LOW (0.33)
        'poor' / 'very_poor' / 'severe'       -> HIGH (1.00)

    Note: 'poor' intermediate is NOT YET SPECIFIED in source; conservatively
    mapped to MEDIUM (0.66) as an intermediate default.
    """
    normalized = aqi_category.strip().lower()
    mapping = {
        "good": 0.33,
        "satisfactory": 0.33,
        "moderate": 0.33,
        "poor": 0.66,
        "very_poor": 1.00,
        "severe": 1.00,
    }
    if normalized not in mapping:
        raise ValueError(
            f"Invalid AQI category: {aqi_category!r}. "
            f"Expected one of: {list(mapping.keys())}"
        )
    return mapping[normalized]


def score_healthcare_access(travel_time_minutes: float) -> float:
    """Classify healthcare access by travel time.

    Convention:
        < 30 min   -> LOW (0.33)
        30-60 min  -> MEDIUM (0.66)  [intermediate NOT YET SPECIFIED]
        > 60 min   -> HIGH (1.00)
    """
    if travel_time_minutes < 30.0:
        return 0.33
    if travel_time_minutes <= 60.0:
        return 0.66
    return 1.00


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
        """Score a raw factor value using classification rules.

        Supports:
            infrastructure_condition: string label
            facilities_commuting: string label
            fluid_intake: numeric deficit percentage
            air_quality: string AQI category
            healthcare_access: numeric travel time (minutes)
            lifestyle: dict with boolean flags per sub-factor
        """
        classifiers = {
            "infrastructure_condition": lambda v: score_infrastructure_condition(str(v)),
            "facilities_commuting": lambda v: score_facilities_commuting(str(v)),
            "fluid_intake": lambda v: score_fluid_intake(float(v)),
            "air_quality": lambda v: score_air_quality(str(v)),
            "healthcare_access": lambda v: score_healthcare_access(float(v)),
        }
        if factor_name == "lifestyle" and isinstance(raw_value, dict):
            sub_scores = []
            for sub_name in ("alcohol", "sleep", "tobacco", "caffeine"):
                if sub_name in raw_value:
                    sub_scores.append(score_lifestyle_factor(
                        sub_name, bool(raw_value[sub_name])
                    ))
            if not sub_scores:
                raise ValueError("lifestyle dict must contain at least one sub-factor")
            return sum(sub_scores) / len(sub_scores)
        if factor_name in classifiers:
            return classifiers[factor_name](raw_value)
        raise ValueError(f"No classifier for factor: {factor_name!r}")

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
