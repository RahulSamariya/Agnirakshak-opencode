"""Unified Heat Stress Risk Index (HSRI).

Core equation:
    HSRI = H * V * E

Residual-risk floor:
    V >= 0.33
    E >= 0.33
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class HSRIInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    hazard_index: float = Field(..., ge=0.0, le=1.0)
    vulnerability_index: float = Field(..., ge=0.33, le=1.0)
    exposure_index: float = Field(..., ge=0.33, le=1.0)

    @model_validator(mode="after")
    def validate_inputs(self) -> HSRIInput:
        if self.vulnerability_index < 0.33:
            raise ValueError("Vulnerability Index cannot be below 0.33.")
        if self.exposure_index < 0.33:
            raise ValueError("Exposure Index cannot be below 0.33.")
        return self


class HSRIOutput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    hazard_index: float
    vulnerability_index: float
    exposure_index: float
    hsri_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel


def classify_hsri(hsri_score: float) -> RiskLevel:
    value = float(hsri_score)
    if value <= 0.33:
        return RiskLevel.LOW
    if value <= 0.66:
        return RiskLevel.MEDIUM
    return RiskLevel.HIGH


def calculate_hsri(data: HSRIInput) -> HSRIOutput:
    """Calculate the deterministic multiplicative HSRI."""
    hsri = (
        data.hazard_index
        * data.vulnerability_index
        * data.exposure_index
    )
    hsri = float(min(1.0, max(0.0, round(hsri, 12))))
    return HSRIOutput(
        hazard_index=data.hazard_index,
        vulnerability_index=data.vulnerability_index,
        exposure_index=data.exposure_index,
        hsri_score=hsri,
        risk_level=classify_hsri(hsri),
    )
