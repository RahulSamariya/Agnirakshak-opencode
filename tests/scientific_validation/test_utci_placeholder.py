"""Tests for UTCI placeholder model."""
import pytest
from pydantic import ValidationError

from scientific.thermal_comfort.utci import (
    PlaceholderUTCIModel,
    UTCIInput,
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


def test_placeholder_model_properties():
    model = PlaceholderUTCIModel()
    assert model.model_name == "utci-placeholder-v1"
    assert model.model_version == "0.0.0"


def test_placeholder_model_raises_not_implemented():
    model = PlaceholderUTCIModel()
    with pytest.raises(NotImplementedError, match="AUTHORITATIVE"):
        model.calculate_utci(35.0, 60.0, 2.0, 40.0)


def test_placeholder_model_get_hazard_index_raises():
    model = PlaceholderUTCIModel()
    with pytest.raises(NotImplementedError):
        model.get_hazard_index(40.0)
