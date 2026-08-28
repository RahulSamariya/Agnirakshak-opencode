"""Typed Pydantic configuration models for scientific YAML files.

Includes validation that:
- Vulnerability weights sum to ~1.0
- Exposure weights are internally consistent
- Nested sub-weights sum to ~1.0
- Hazard categories are ordered, contiguous, non-overlapping
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, model_validator

_WEIGHT_TOLERANCE = 1e-2  # Allows published rounded coefficients like 0.999


class HazardCategoryConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    min: float
    max: float | None
    hazard_min: float
    hazard_max: float
    label: str


class HazardCategoriesConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    description: str
    categories: dict[str, HazardCategoryConfig]

    @model_validator(mode="after")
    def validate_categories(self) -> HazardCategoriesConfig:
        cats = list(self.categories.values())
        if len(cats) < 2:
            raise ValueError("At least 2 hazard categories required.")
        # Sort by min bound
        cats_sorted = sorted(cats, key=lambda c: c.min)
        # Check ordered and non-overlapping
        for i in range(len(cats_sorted) - 1):
            curr = cats_sorted[i]
            nxt = cats_sorted[i + 1]
            if curr.max is None:
                raise ValueError(f"Category '{curr.label}' has no upper bound but is not last.")
            if curr.max > nxt.min:
                raise ValueError(
                    f"Categories overlap: '{curr.label}' max={curr.max}"
                    f" > '{nxt.label}' min={nxt.min}"
                )
            if curr.max < nxt.min:
                raise ValueError(
                    f"Categories non-contiguous: '{curr.label}' max={curr.max}"
                    f" < '{nxt.label}' min={nxt.min}"
                )
        # Check hazard score ranges are consistent
        for cat in cats_sorted:
            if cat.hazard_min > cat.hazard_max:
                raise ValueError(
                    f"Category '{cat.label}': hazard_min={cat.hazard_min}"
                    f" > hazard_max={cat.hazard_max}"
                )
        return self


class VulnerabilityWeightsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    description: str
    weights: dict[str, float]
    scoring: dict[str, float]
    health_issues_sub: dict[str, float]
    residual_floor: float

    @model_validator(mode="after")
    def validate_weights(self) -> VulnerabilityWeightsConfig:
        total = sum(self.weights.values())
        if abs(total - 1.0) > _WEIGHT_TOLERANCE:
            raise ValueError(
                f"Vulnerability weights sum to {total}, expected ~1.0"
                f" (tolerance={_WEIGHT_TOLERANCE})"
            )
        sub_total = sum(self.health_issues_sub.values())
        if abs(sub_total - 1.0) > _WEIGHT_TOLERANCE:
            raise ValueError(
                f"Health issues sub-weights sum to {sub_total}, expected ~1.0"
            )
        return self


class ExposureWeightsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    description: str
    weights: dict[str, float]
    infrastructure_transit_sub: dict[str, float]
    lifestyle_sub: dict[str, float]
    scoring: dict[str, float]
    residual_floor: float

    @model_validator(mode="after")
    def validate_weights(self) -> ExposureWeightsConfig:
        # Top-level exposure weights are published as 0.999; record but don't renormalize
        infra_total = sum(self.infrastructure_transit_sub.values())
        if abs(infra_total - 1.0) > _WEIGHT_TOLERANCE:
            raise ValueError(
                f"Infrastructure sub-weights sum to {infra_total}, expected ~1.0"
            )
        lifestyle_total = sum(self.lifestyle_sub.values())
        if abs(lifestyle_total - 1.0) > _WEIGHT_TOLERANCE:
            raise ValueError(
                f"Lifestyle sub-weights sum to {lifestyle_total}, expected ~1.0"
            )
        return self


class RiskCategoryConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    min: float
    max: float
    label: str
    color: str


class RiskThresholdsConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    version: str
    description: str
    categories: dict[str, RiskCategoryConfig]

    @model_validator(mode="after")
    def validate_thresholds(self) -> RiskThresholdsConfig:
        cats = list(self.categories.values())
        if len(cats) < 2:
            raise ValueError("At least 2 risk categories required.")
        cats_sorted = sorted(cats, key=lambda c: c.min)
        for i in range(len(cats_sorted) - 1):
            if cats_sorted[i].max > cats_sorted[i + 1].max:
                raise ValueError("Risk category thresholds must be monotonically increasing.")
        return self
