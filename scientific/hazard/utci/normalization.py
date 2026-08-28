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
from typing import Final

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


# Lower/upper UTCI boundaries supplied by the specification.
_CATEGORY_BOUNDS: Final = (
    (9.0, 26.0, 0.0, 0.25, HazardCategory.NO_THERMAL_STRESS),
    (26.0, 32.0, 0.25, 0.50, HazardCategory.MODERATE_HEAT_STRESS),
    (32.0, 38.0, 0.50, 0.75, HazardCategory.STRONG_HEAT_STRESS),
    (38.0, 46.0, 0.75, 1.00, HazardCategory.VERY_STRONG_HEAT_STRESS),
)

_MIN_UTCI_FOR_SCALE: Final = 9.0
_MAX_UTCI_FOR_SCALE: Final = 46.0


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
    if 9.0 <= utci_c < 26.0:
        return HazardCategory.NO_THERMAL_STRESS
    if utci_c < 32.0:
        return HazardCategory.MODERATE_HEAT_STRESS
    if utci_c < 38.0:
        return HazardCategory.STRONG_HEAT_STRESS
    if utci_c <= 46.0:
        return HazardCategory.VERY_STRONG_HEAT_STRESS
    return HazardCategory.EXTREME_HEAT_STRESS


def normalize_utci(utci_c: float) -> float:
    """Convert UTCI to normalized Hazard Index H.

    Values at/below 9 C are clamped to H = 0.0 because the supplied
    material does not define a separate cold-stress normalization regime.
    Values above 46 C are capped at H = 1.0.
    """
    value = float(utci_c)
    if value <= _MIN_UTCI_FOR_SCALE:
        return 0.0
    if value > _MAX_UTCI_FOR_SCALE:
        return 1.0
    for utci_min, utci_max, h_min, h_max, _category in _CATEGORY_BOUNDS:
        if utci_min <= value <= utci_max:
            result = _linear_interpolate(
                value,
                utci_min,
                utci_max,
                h_min,
                h_max,
            )
            return float(min(1.0, max(0.0, result)))
    raise RuntimeError(f"UTCI value {value} did not match any normalization band.")


def normalize_hazard(
    data: HazardNormalizationInput,
) -> HazardNormalizationOutput:
    """Calculate normalized Hazard Index H from a validated UTCI input."""
    hazard_index = normalize_utci(data.utci_c)
    category = classify_utci(data.utci_c)
    return HazardNormalizationOutput(
        utci_c=data.utci_c,
        category=category,
        hazard_index=hazard_index,
    )
