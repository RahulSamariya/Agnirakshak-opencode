"""Thermal comfort model base class."""
from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scientific.thermal_comfort.utci import UTCIOutput


class ThermalStressCategory(Enum):
    """UTCI thermal stress categories."""

    NO_STRESS = "no_stress"
    MODERATE_HEAT = "moderate_heat"
    STRONG_HEAT = "strong_heat"
    VERY_STRONG_HEAT = "very_strong_heat"
    EXTREME_HEAT = "extreme_heat"


class ThermalComfortModel(ABC):
    """Abstract base class for thermal comfort models.

    This interface supports pluggable thermal comfort calculations.
    Current implementation: UTCI (placeholder — algorithm not yet implemented)
    Future implementations: Adaptive Thermal Comfort, etc.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the thermal comfort model."""

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Version of the thermal comfort model."""

    @abstractmethod
    def calculate_utci(
        self,
        air_temperature: float,
        relative_humidity: float,
        wind_speed: float,
        mean_radiant_temperature: float,
    ) -> UTCIOutput:
        """Calculate Universal Thermal Climate Index.

        Args:
            air_temperature: Air temperature in Celsius.
            relative_humidity: Relative humidity in percentage (0-100).
            wind_speed: Wind speed in m/s.
            mean_radiant_temperature: Mean radiant temperature in Celsius.

        Returns:
            UTCIOutput with UTCI value and input echoes.
        """

    @abstractmethod
    def get_hazard_index(self, utci: float) -> float:
        """Convert UTCI to normalized hazard index.

        Args:
            utci: Universal Thermal Climate Index in Celsius.

        Returns:
            Normalized hazard index between 0.0 and 1.0.
        """
