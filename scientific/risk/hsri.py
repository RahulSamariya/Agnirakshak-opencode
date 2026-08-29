"""Unified Heat Stress Risk Index (HSRI).

Core equation:
    HSRI = H * V * E

Risk thresholds and floors are loaded from configuration YAML.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

from scientific.configuration.loader import load_risk_thresholds
from scientific.risk.base import RiskCategory, RiskModel


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HSRIInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    hazard_index: float = Field(..., ge=0.0, le=1.0)
    vulnerability_index: float = Field(..., ge=0.33, le=1.0)
    exposure_index: float = Field(..., ge=0.33, le=1.0)


class HSRIOutput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    hazard_index: float
    vulnerability_index: float
    exposure_index: float
    hsri_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel


# ---------------------------------------------------------------------------
# Pure calculation functions (config-driven)
# ---------------------------------------------------------------------------

def classify_hsri(hsri_score: float) -> RiskLevel:
    """Classify HSRI score into risk level.

    Boundary convention (non-overlapping):
        0.0 < HSRI <= 0.33 -> LOW
        0.33 < HSRI <= 0.66 -> MEDIUM
        0.66 < HSRI <= 1.00 -> HIGH
        HSRI == 0 -> LOW (no hazard)
    """
    cfg = load_risk_thresholds()
    value = float(hsri_score)
    if value <= 0.0:
        return RiskLevel.LOW
    for _key, cat in cfg.categories.items():
        if cat.min < value <= cat.max:
            return RiskLevel(cat.label.lower())
    return RiskLevel.HIGH


def calculate_hsri(data: HSRIInput) -> HSRIOutput:
    """Calculate the deterministic multiplicative HSRI."""
    hsri = data.hazard_index * data.vulnerability_index * data.exposure_index
    hsri = float(min(1.0, max(0.0, round(hsri, 12))))
    return HSRIOutput(
        hazard_index=data.hazard_index,
        vulnerability_index=data.vulnerability_index,
        exposure_index=data.exposure_index,
        hsri_score=hsri,
        risk_level=classify_hsri(hsri),
    )


# ---------------------------------------------------------------------------
# Concrete Phase-1 interface implementation
# ---------------------------------------------------------------------------

class MultiplicativeHSRIModel(RiskModel):
    """Configuration-driven multiplicative HSRI risk model."""

    @property
    def model_name(self) -> str:
        return "hsri-multiplicative-v1"

    @property
    def model_version(self) -> str:
        cfg = load_risk_thresholds()
        return cfg.version

    def calculate(
        self,
        hazard: float,
        vulnerability: float,
        exposure: float,
    ) -> HSRIOutput:
        data = HSRIInput(
            hazard_index=hazard,
            vulnerability_index=vulnerability,
            exposure_index=exposure,
        )
        return calculate_hsri(data)

    def classify_risk(self, hsri: float) -> RiskCategory:
        level = classify_hsri(hsri)
        return RiskCategory(level.value)

    def get_risk_thresholds(self) -> dict[str, float]:
        cfg = load_risk_thresholds()
        return {k: v.max for k, v in cfg.categories.items()}
