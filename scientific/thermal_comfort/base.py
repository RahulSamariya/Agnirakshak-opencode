from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional
from enum import Enum


class ThermalStressCategory(Enum):
    """UTCI thermal stress categories."""
    NO_STRESS = "no_stress"
    MODERATE_HEAT = "moderate_heat"
    STRONG_HEAT = "strong_heat"
    VERY_STRONG_HEAT = "very_strong_heat"
    EXTREME_HEAT = "extreme_heat"


@dataclass
class ThermalComfortResult:
    """Result from thermal comfort calculation."""
    utci: float
    category: ThermalStressCategory
    hazard_index: float
    metadata: Dict[str, Any]


class ThermalComfortModel(ABC):
    """Abstract base class for thermal comfort models.

    This interface supports pluggable thermal comfort calculations.
    Current implementation: UTCI
    Future implementations: Adaptive Thermal Comfort, etc.
    """

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Name of the thermal comfort model."""
        pass

    @property
    @abstractmethod
    def model_version(self) -> str:
        """Version of the thermal comfort model."""
        pass

    @abstractmethod
    def calculate_utci(
        self,
        air_temperature: float,
        relative_humidity: float,
        wind_speed: float,
        mean_radiant_temperature: float,
    ) -> ThermalComfortResult:
        """Calculate Universal Thermal Climate Index.

        Args:
            air_temperature: Air temperature in Celsius.
            relative_humidity: Relative humidity in percentage (0-100).
            wind_speed: Wind speed in m/s.
            mean_radiant_temperature: Mean radiant temperature in Celsius.

        Returns:
            ThermalComfortResult with UTCI value and category.
        """
        pass

    @abstractmethod
    def get_hazard_index(self, utci: float) -> float:
        """Convert UTCI to normalized hazard index.

        Args:
            utci: Universal Thermal Climate Index in Celsius.

        Returns:
            Normalized hazard index between 0.0 and 1.0.
        """
        pass
