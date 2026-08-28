"""UTCI -> normalized Hazard Index conversion.

Scientific basis:
- UTCI is the thermal-stress variable.
- UTCI categories are mapped to a normalized Hazard Index H in [0, 1].
- Within each category, H is linearly interpolated.
- Values above 46 C are capped at H = 1.0.

This module intentionally does NOT calculate UTCI itself.
The raw UTCI value must be supplied by the thermal-comfort engine.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from scientific.configuration.loader import load_hazard_categories
from scientific.hazard.base import HazardModel


class HazardCategory(StrEnum):
    """WMO-style thermal stress categories used by the supplied specification."""

    NO_THERMAL_STRESS = "no_thermal_stress"
    MODERATE_HEAT_STRESS = "moderate_heat_stress"
    STRONG_HEAT_STRESS = "strong_heat_stress"
    VERY_STRONG_HEAT_STRESS = "very_strong_heat_stress"
    EXTREME_HEAT_STRESS = "extreme_heat_stress"


class HazardNormalizationInput(BaseModel):
    """Validated raw UTCI input."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    utci_c: float = Field(
        ...,
        description="Universal Thermal Climate Index in degrees Celsius.",
    )

    @field_validator("utci_c")
    @classmethod
    def validate_utci(cls, value: float) -> float:
        if not -100.0 <= value <= 100.0:
            raise ValueError(
                "UTCI must be within the supported physical range [-100, 100] C."
            )
        return float(value)


class HazardNormalizationOutput(BaseModel):
    """Normalized Hazard Index result."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    utci_c: float
    category: HazardCategory
    hazard_index: float = Field(..., ge=0.0, le=1.0)


# ---------------------------------------------------------------------------
# Pure calculation functions (config-driven)
# ---------------------------------------------------------------------------

_CATEGORY_LABEL_TO_ENUM: dict[str, HazardCategory] = {
    "no_thermal_stress": HazardCategory.NO_THERMAL_STRESS,
    "moderate_heat_stress": HazardCategory.MODERATE_HEAT_STRESS,
    "strong_heat_stress": HazardCategory.STRONG_HEAT_STRESS,
    "very_strong_heat_stress": HazardCategory.VERY_STRONG_HEAT_STRESS,
    "extreme_heat_stress": HazardCategory.EXTREME_HEAT_STRESS,
}


def _load_category_bounds() -> list[tuple[float, float, float, float, HazardCategory]]:
    cfg = load_hazard_categories()
    bounds = []
    for _key, cat in cfg.categories.items():
        enum_val = _CATEGORY_LABEL_TO_ENUM[cat.label.lower().replace(" ", "_")]
        upper = cat.max if cat.max is not None else float("inf")
        bounds.append((cat.min, upper, cat.hazard_min, cat.hazard_max, enum_val))
    return bounds


def _linear_interpolate(
    value: float,
    value_min: float,
    value_max: float,
    score_min: float,
    score_max: float,
) -> float:
    """Linearly interpolate value from [value_min, value_max] to [score_min, score_max]."""
    if value_max <= value_min:
        raise ValueError("Invalid normalization interval.")
    ratio = (value - value_min) / (value_max - value_min)
    return score_min + ratio * (score_max - score_min)


def classify_utci(utci_c: float) -> HazardCategory:
    """Return the thermal-stress category for a UTCI value."""
    bounds = _load_category_bounds()
    for utci_min, utci_max, _h_min, _h_max, category in bounds:
        if utci_min <= utci_c < utci_max:
            return category
    # Extreme heat (max is inf)
    return HazardCategory.EXTREME_HEAT_STRESS


def normalize_utci(utci_c: float) -> float:
    """Convert UTCI to normalized Hazard Index H.

    Values at/below the minimum category bound are clamped to H = 0.0.
    Values above the maximum category bound are capped at H = 1.0.
    """
    bounds = _load_category_bounds()
    first_min = bounds[0][0]
    last_max = bounds[-1][1]

    value = float(utci_c)
    if value <= first_min:
        return 0.0
    if value >= last_max:
        return 1.0
    for utci_min, utci_max, h_min, h_max, _category in bounds:
        if utci_min <= value <= utci_max:
            result = _linear_interpolate(value, utci_min, utci_max, h_min, h_max)
            return float(min(1.0, max(0.0, result)))
    raise RuntimeError(f"UTCI value {value} did not match any normalization band.")


def normalize_hazard(data: HazardNormalizationInput) -> HazardNormalizationOutput:
    """Calculate normalized Hazard Index H from a validated UTCI input."""
    hazard_index = normalize_utci(data.utci_c)
    category = classify_utci(data.utci_c)
    return HazardNormalizationOutput(
        utci_c=data.utci_c,
        category=category,
        hazard_index=hazard_index,
    )


# ---------------------------------------------------------------------------
# Concrete Phase-1 interface implementation
# ---------------------------------------------------------------------------

class UTCIHazardModel(HazardModel):
    """Configuration-driven UTCI hazard normalization model."""

    @property
    def model_name(self) -> str:
        return "utci-hazard-v1"

    @property
    def model_version(self) -> str:
        cfg = load_hazard_categories()
        return cfg.version

    def calculate_hazard(self, utci: float) -> HazardNormalizationOutput:
        return normalize_hazard(HazardNormalizationInput(utci_c=utci))

    def get_hazard_category(self, hazard_index: float) -> str:
        cfg = load_hazard_categories()
        for _key, cat in cfg.categories.items():
            if cat.min <= hazard_index <= cat.max:
                return cat.label
        return "Extreme heat stress"
