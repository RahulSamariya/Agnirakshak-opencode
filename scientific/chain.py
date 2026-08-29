"""UTCI → Hazard normalization chain.

Demonstrates the conceptual chain:
    meteorological inputs → UTCI → hazard normalization → H

The UTCI calculator is currently a placeholder. Once the authoritative
UTCI algorithm is implemented, the chain will produce a full result.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from scientific.hazard.utci.normalization import (
    HazardNormalizationOutput,
    UTCIHazardModel,
)
from scientific.thermal_comfort.utci import UTCICalculatorModel, UTCIInput, UTCIOutput


class ThermalHazardChainResult(BaseModel):
    """Combined result from UTCI → Hazard chain."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    utci_input: UTCIInput
    utci_output: UTCIOutput | None = None
    hazard_output: HazardNormalizationOutput | None = None
    utci_implemented: bool = False


def run_thermal_hazard_chain(
    air_temperature: float,
    relative_humidity: float,
    wind_speed: float,
    mean_radiant_temperature: float,
) -> ThermalHazardChainResult:
    """Execute the UTCI → Hazard chain.

    Returns a ThermalHazardChainResult with whatever stage succeeded.
    If UTCI is not implemented, only the input is returned.
    """
    utci_input = UTCIInput(
        air_temperature=air_temperature,
        relative_humidity=relative_humidity,
        wind_speed=wind_speed,
        mean_radiant_temperature=mean_radiant_temperature,
    )

    utci_model = UTCICalculatorModel()
    hazard_model = UTCIHazardModel()

    try:
        utci_output = utci_model.calculate_utci(
            air_temperature=utci_input.air_temperature,
            relative_humidity=utci_input.relative_humidity,
            wind_speed=utci_input.wind_speed,
            mean_radiant_temperature=utci_input.mean_radiant_temperature,
        )
    except NotImplementedError:
        return ThermalHazardChainResult(
            utci_input=utci_input,
            utci_implemented=False,
        )

    hazard_output = hazard_model.calculate_hazard(utci_output.utci_c)

    return ThermalHazardChainResult(
        utci_input=utci_input,
        utci_output=utci_output,
        hazard_output=hazard_output,
        utci_implemented=True,
    )
