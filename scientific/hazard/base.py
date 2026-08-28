"""Hazard model base class."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scientific.hazard.utci.normalization import HazardNormalizationOutput


class HazardModel(ABC):
    """Abstract base class for hazard models.

    Hazard models convert UTCI (or other thermal comfort indices)
    into normalized hazard indices.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the hazard model."""

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Version of the hazard model."""

    @abstractmethod
    def calculate_hazard(self, utci: float) -> HazardNormalizationOutput:
        """Calculate hazard index from UTCI value.

        Args:
            utci: Universal Thermal Climate Index in Celsius.

        Returns:
            HazardNormalizationOutput with normalized hazard index and category.
        """

    @abstractmethod
    def get_hazard_category(self, hazard_index: float) -> str:
        """Get hazard category from normalized index.

        Args:
            hazard_index: Normalized hazard index (0.0 - 1.0).

        Returns:
            Hazard category string.
        """

    def get_residual_floor(self) -> float:
        """Return the residual risk floor for hazard.

        Default is 0.0 (hazard may reach zero).
        """
        return 0.0
