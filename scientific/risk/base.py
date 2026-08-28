"""Risk model base class."""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scientific.risk.hsri import HSRIOutput


class RiskCategory(Enum):
    """HSRI risk categories."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RiskModel(ABC):
    """Abstract base class for risk calculation models.

    Core formula: HSRI = H x V x E
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the risk model."""

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Version of the risk model."""

    @abstractmethod
    def calculate(
        self,
        hazard: float,
        vulnerability: float,
        exposure: float,
    ) -> HSRIOutput:
        """Calculate Human Stress Risk Index.

        Args:
            hazard: Hazard index (0.0 - 1.0).
            vulnerability: Vulnerability index (0.33 - 1.0).
            exposure: Exposure index (0.33 - 1.0).

        Returns:
            HSRIOutput with HSRI score and risk level.
        """

    @abstractmethod
    def classify_risk(self, hsri: float) -> RiskCategory:
        """Classify HSRI into risk category.

        Args:
            hsri: Human Stress Risk Index (0.0 - 1.0).

        Returns:
            RiskCategory enum value.
        """

    def get_risk_thresholds(self) -> dict[str, float]:
        """Return current risk category thresholds.

        Returns:
            Dictionary with threshold boundaries.
        """
        from scientific.configuration.loader import load_risk_thresholds
        cfg = load_risk_thresholds()
        return {k: v.max for k, v in cfg.categories.items()}
