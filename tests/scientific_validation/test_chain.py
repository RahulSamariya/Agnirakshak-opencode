"""Tests for UTCI → Hazard chain."""
import pytest
from pydantic import ValidationError

from scientific.chain import ThermalHazardChainResult, run_thermal_hazard_chain


def test_chain_returns_input_when_utci_not_implemented():
    result = run_thermal_hazard_chain(
        air_temperature=35.0,
        relative_humidity=60.0,
        wind_speed=2.0,
        mean_radiant_temperature=40.0,
    )
    assert isinstance(result, ThermalHazardChainResult)
    assert result.utci_input.air_temperature == 35.0
    assert result.utci_implemented is False
    assert result.utci_output is None
    assert result.hazard_output is None


def test_chain_result_is_frozen():
    result = run_thermal_hazard_chain(35.0, 60.0, 2.0, 40.0)
    with pytest.raises(ValidationError):
        result.utci_implemented = True


def test_chain_result_rejects_extra():
    with pytest.raises(ValidationError):
        ThermalHazardChainResult(
            utci_input={"air_temperature": 35, "relative_humidity": 60,
                         "wind_speed": 2, "mean_radiant_temperature": 40},
            extra=1.0,
        )
