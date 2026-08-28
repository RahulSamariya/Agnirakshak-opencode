"""UTCI thermal comfort model — interface and schema placeholders.

UTCI IMPLEMENTATION BLOCKED — AUTHORITATIVE METHODOLOGY/REFERENCE
DATA NOT PRESENT.

The actual UTCI polynomial/coefficient set/reference table is not available
in the repository. This module defines ONLY the Pydantic input/output schemas
and a placeholder model class. The calculate_utci method raises
NotImplementedError until the authoritative UTCI algorithm is provided.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from scientific.thermal_comfort.base import ThermalComfortModel


class UTCIInput(BaseModel):
    """Meteorological inputs required for UTCI calculation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    air_temperature: float = Field(
        ...,
        description="Air temperature in degrees Celsius.",
    )
    relative_humidity: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Relative humidity in percentage (0-100).",
    )
    wind_speed: float = Field(
        ...,
        ge=0.0,
        description="Wind speed in m/s at 10 m height.",
    )
    mean_radiant_temperature: float = Field(
        ...,
        description="Mean radiant temperature in degrees Celsius.",
    )


class UTCIOutput(BaseModel):
    """Result from UTCI calculation."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    utci_c: float = Field(
        ...,
        description="Universal Thermal Climate Index in degrees Celsius.",
    )
    air_temperature: float
    relative_humidity: float
    wind_speed: float
    mean_radiant_temperature: float


class PlaceholderUTCIModel(ThermalComfortModel):
    """Placeholder UTCI model — algorithm not yet implemented.

    Raises NotImplementedError for calculate_utci until the authoritative
    UTCI polynomial/coefficient set is available in the repository.
    """

    @property
    def model_name(self) -> str:
        return "utci-placeholder-v1"

    @property
    def model_version(self) -> str:
        return "0.0.0"

    def calculate_utci(
        self,
        air_temperature: float,
        relative_humidity: float,
        wind_speed: float,
        mean_radiant_temperature: float,
    ) -> UTCIOutput:
        """Calculate UTCI — NOT IMPLEMENTED.

        Raises:
            NotImplementedError: UTCI methodology/reference data not available.
        """
        raise NotImplementedError(
            "UTCI IMPLEMENTATION BLOCKED — AUTHORITATIVE METHODOLOGY/REFERENCE "
            "DATA NOT PRESENT. Provide the UTCI polynomial coefficient set and "
            "reference test cases to enable this method."
        )

    def get_hazard_index(self, utci: float) -> float:
        """Convert UTCI to normalized hazard index — NOT IMPLEMENTED."""
        raise NotImplementedError(
            "UTCI hazard index conversion requires the UTCI calculator to be "
            "implemented first."
        )
