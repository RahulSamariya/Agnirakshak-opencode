"""Tests for UTCI → Hazard chain."""
import pytest
from pydantic import ValidationError

from scientific.chain import ThermalHazardChainResult, run_thermal_hazard_chain


def test_chain_produces_full_result():
    result = run_thermal_hazard_chain(
        air_temperature=35.0,
        relative_humidity=60.0,
        wind_speed=2.0,
        mean_radiant_temperature=40.0,
    )
    assert isinstance(result, ThermalHazardChainResult)
    assert result.utci_input.air_temperature == 35.0
    assert result.utci_implemented is True
    assert result.utci_output is not None
    assert result.hazard_output is not None


def test_chain_utci_value_in_range():
    result = run_thermal_hazard_chain(25.0, 50.0, 1.0, 25.0)
    assert result.utci_output is not None
    assert -50 <= result.utci_output.utci_c <= 50


def test_chain_hazard_index_in_range():
    result = run_thermal_hazard_chain(25.0, 50.0, 1.0, 25.0)
    assert result.hazard_output is not None
    assert 0.0 <= result.hazard_output.hazard_index <= 1.0


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
