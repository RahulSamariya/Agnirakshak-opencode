"""Hazard model base class."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass
class HazardResult:
    """Result from hazard calculation."""
    utci_value: float
    hazard_index: float
    hazard_category: str
    metadata: Dict[str, Any]


class HazardModel(ABC):
    """Abstract base class for hazard models.

    Hazard models convert UTCI (or other thermal comfort indices)
    into normalized hazard indices.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the hazard model."""
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Version of the hazard model."""
        pass

    @abstractmethod
    def calculate_hazard(self, utci: float) -> HazardResult:
        """Calculate hazard index from UTCI value.

        Args:
            utci: Universal Thermal Climate Index in Celsius.

        Returns:
            HazardResult with normalized hazard index and category.
        """
        pass

    @abstractmethod
    def get_hazard_category(self, hazard_index: float) -> str:
        """Get hazard category from normalized index.

        Args:
            hazard_index: Normalized hazard index (0.0 - 1.0).

        Returns:
            Hazard category string.
        """
        pass

    def get_residual_floor(self) -> float:
        """Return the residual risk floor for hazard.

        Default is 0.0 (hazard may reach zero).
        """
        return 0.0
