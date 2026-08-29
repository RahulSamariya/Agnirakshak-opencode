"""Risk pipeline - run module.

This module orchestrates risk calculations by calling the scientific engine.
The scientific engine (scientific.risk.hsri) is the authoritative source for
HSRI calculation and risk classification.
"""
from __future__ import annotations

from scientific.risk.hsri import (
    HSRIInput,
    HSRIOutput,
    RiskLevel,
    calculate_hsri,
    classify_hsri,
)


class RiskRunner:
    """Handles execution of risk calculations using the scientific engine."""

    def __init__(self, model_config: dict | None = None):
        self.model_config = model_config or {}

    def run_hsri_calculation(
        self,
        hazard: float,
        vulnerability: float,
        exposure: float,
    ) -> HSRIOutput:
        """Run HSRI = H x V x E calculation.

        Delegates to the scientific engine (scientific.risk.hsri.calculate_hsri).

        Args:
            hazard: Hazard index (0-1).
            vulnerability: Vulnerability index (0.33-1.0).
            exposure: Exposure index (0.33-1.0).

        Returns:
            HSRIOutput with HSRI score and risk level.
        """
        data = HSRIInput(
            hazard_index=hazard,
            vulnerability_index=vulnerability,
            exposure_index=exposure,
        )
        return calculate_hsri(data)

    def classify_risk(self, hsri: float) -> RiskLevel:
        """Classify HSRI into risk category.

        Delegates to the scientific engine (scientific.risk.hsri.classify_hsri).

        Args:
            hsri: Human Stress Risk Index (0-1).

        Returns:
            RiskLevel enum (low, medium, high).
        """
        return classify_hsri(hsri)
