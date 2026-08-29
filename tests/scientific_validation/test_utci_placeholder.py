"""Tests for UTCI calculator model."""
import pytest
from pydantic import ValidationError

from scientific.thermal_comfort.utci import (
    UTCICalculatorModel,
    UTCIInput,
    UTCIOutput,
)


def test_utci_input_validation():
    inp = UTCIInput(
        air_temperature=35.0,
        relative_humidity=60.0,
        wind_speed=2.0,
        mean_radiant_temperature=40.0,
    )
    assert inp.air_temperature == 35.0
    assert inp.relative_humidity == 60.0


def test_utci_input_rejects_extra():
    with pytest.raises(ValidationError):
        UTCIInput(
            air_temperature=35.0,
            relative_humidity=60.0,
            wind_speed=2.0,
            mean_radiant_temperature=40.0,
            extra=1.0,
        )


def test_utci_input_rejects_invalid_humidity():
    with pytest.raises(ValidationError):
        UTCIInput(
            air_temperature=35.0,
            relative_humidity=150.0,
            wind_speed=2.0,
            mean_radiant_temperature=40.0,
        )


def test_utci_input_frozen():
    inp = UTCIInput(
        air_temperature=35.0,
        relative_humidity=60.0,
        wind_speed=2.0,
        mean_radiant_temperature=40.0,
    )
    with pytest.raises(ValidationError):
        inp.air_temperature = 40.0


def test_calculator_model_properties():
    model = UTCICalculatorModel()
    assert model.model_name == "utci-polynomial-v1"
    assert model.model_version == "1.0.0"


def test_calculator_model_produces_output():
    model = UTCICalculatorModel()
    result = model.calculate_utci(35.0, 60.0, 2.0, 40.0)
    assert isinstance(result, UTCIOutput)
    assert -50 <= result.utci_c <= 50


def test_calculator_model_get_hazard_index():
    model = UTCICalculatorModel()
    idx = model.get_hazard_index(40.0)
    assert 0.0 <= idx <= 1.0


def test_utci_reference_value():
    """Reference: tdb=25, rh=50, v=1, tmrt=25 -> UTCI ≈ 24.6."""
    model = UTCICalculatorModel()
    result = model.calculate_utci(25.0, 50.0, 1.0, 25.0)
    assert abs(result.utci_c - 24.6) < 0.2
