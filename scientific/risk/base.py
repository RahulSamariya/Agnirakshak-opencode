from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class RiskCategory(Enum):
    """HSRI risk categories."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class RiskResult:
    """Result from risk calculation."""
    hsri: float
    risk_category: RiskCategory
    hazard: float
    vulnerability: float
    exposure: float
    metadata: dict[str, Any]


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
    ) -> RiskResult:
        """Calculate Human Stress Risk Index.

        Args:
            hazard: Hazard index (0.0 - 1.0).
            vulnerability: Vulnerability index (0.0 - 1.0).
            exposure: Exposure index (0.0 - 1.0).

        Returns:
            RiskResult with HSRI and risk category.
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
        return {
            "low_max": 0.33,
            "medium_max": 0.66,
            "high_max": 1.0,
        }
