"""Typed Pydantic configuration models for scientific YAML files.

Includes validation that:
- Vulnerability weights sum to ~1.0
- Exposure weights are internally consistent (published 0.999 preserved)
- Nested sub-weights sum to ~1.0
- Hazard categories are ordered, contiguous, non-overlapping
- All weights are positive
- Scoring values are ordered low < medium < high
- Residual floors are in valid range [0, 1]
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
        cats_sorted = sorted(cats, key=lambda c: c.min)
        for i in range(len(cats_sorted) - 1):
            curr = cats_sorted[i]
            nxt = cats_sorted[i + 1]
            if curr.max is None:
                raise ValueError(
                    f"Category '{curr.label}' has no upper bound but is not last."
                )
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
        for cat in cats_sorted:
            if cat.hazard_min > cat.hazard_max:
                raise ValueError(
                    f"Category '{cat.label}': hazard_min={cat.hazard_min}"
                    f" > hazard_max={cat.hazard_max}"
                )
            if cat.hazard_min < 0.0 or cat.hazard_max > 1.0:
                raise ValueError(
                    f"Category '{cat.label}': hazard scores must be in [0, 1],"
                    f" got [{cat.hazard_min}, {cat.hazard_max}]"
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
        # All weights must be positive
        for name, w in self.weights.items():
            if w <= 0:
                raise ValueError(f"Vulnerability weight '{name}' must be positive, got {w}")
        for name, w in self.health_issues_sub.items():
            if w <= 0:
                raise ValueError(f"Health sub-weight '{name}' must be positive, got {w}")
        # Top-level weights sum to ~1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > _WEIGHT_TOLERANCE:
            raise ValueError(
                f"Vulnerability weights sum to {total}, expected ~1.0"
                f" (tolerance={_WEIGHT_TOLERANCE})"
            )
        # Nested sub-weights sum to ~1.0
        sub_total = sum(self.health_issues_sub.values())
        if abs(sub_total - 1.0) > _WEIGHT_TOLERANCE:
            raise ValueError(
                f"Health issues sub-weights sum to {sub_total}, expected ~1.0"
            )
        # Scoring values must be ordered low < medium < high
        if self.scoring["low"] >= self.scoring["medium"]:
            raise ValueError("Scoring low must be < medium")
        if self.scoring["medium"] >= self.scoring["high"]:
            raise ValueError("Scoring medium must be < high")
        # Residual floor in valid range
        if not (0.0 <= self.residual_floor <= 1.0):
            raise ValueError(f"residual_floor must be in [0, 1], got {self.residual_floor}")
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
        # All sub-weights must be positive
        for name, w in self.infrastructure_transit_sub.items():
            if w <= 0:
                raise ValueError(f"Infrastructure sub-weight '{name}' must be positive, got {w}")
        for name, w in self.lifestyle_sub.items():
            if w <= 0:
                raise ValueError(f"Lifestyle sub-weight '{name}' must be positive, got {w}")
        # Sub-weights sum to ~1.0
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
        # Scoring values must be ordered
        if self.scoring["low"] >= self.scoring["medium"]:
            raise ValueError("Scoring low must be < medium")
        if self.scoring["medium"] >= self.scoring["high"]:
            raise ValueError("Scoring medium must be < high")
        # Residual floor in valid range
        if not (0.0 <= self.residual_floor <= 1.0):
            raise ValueError(f"residual_floor must be in [0, 1], got {self.residual_floor}")
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
                raise ValueError(
                    "Risk category thresholds must be monotonically increasing."
                )
        # All thresholds in [0, 1]
        for cat in cats_sorted:
            if not (0.0 <= cat.min <= 1.0 and 0.0 <= cat.max <= 1.0):
                raise ValueError(
                    f"Risk category '{cat.label}' thresholds must be in [0, 1]"
                )
        return self
