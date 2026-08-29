"""Tests for UTCI calculator model, calm-wind policy, and extended validation."""
import pytest
from pydantic import ValidationError

from scientific.thermal_comfort.utci import (
    UTCICalculatorModel,
    UTCIInput,
    UTCIOutput,
    calculate_utci,
)


class TestUTCIInputValidation:
    """Test UTCI input validation."""

    def test_utci_input_validation(self):
        inp = UTCIInput(
            air_temperature=35.0,
            relative_humidity=60.0,
            wind_speed=2.0,
            mean_radiant_temperature=40.0,
        )
        assert inp.air_temperature == 35.0
        assert inp.relative_humidity == 60.0

    def test_utci_input_rejects_extra(self):
        with pytest.raises(ValidationError):
            UTCIInput(
                air_temperature=35.0,
                relative_humidity=60.0,
                wind_speed=2.0,
                mean_radiant_temperature=40.0,
                extra=1.0,
            )

    def test_utci_input_rejects_invalid_humidity(self):
        with pytest.raises(ValidationError):
            UTCIInput(
                air_temperature=35.0,
                relative_humidity=150.0,
                wind_speed=2.0,
                mean_radiant_temperature=40.0,
            )

    def test_utci_input_frozen(self):
        inp = UTCIInput(
            air_temperature=35.0,
            relative_humidity=60.0,
            wind_speed=2.0,
            mean_radiant_temperature=40.0,
        )
        with pytest.raises(ValidationError):
            inp.air_temperature = 40.0


class TestUTCICalculatorModel:
    """Test UTCI calculator model."""

    def test_calculator_model_properties(self):
        model = UTCICalculatorModel()
        assert model.model_name == "utci-polynomial-v1"
        assert model.model_version == "1.0.0"

    def test_calculator_model_produces_output(self):
        model = UTCICalculatorModel()
        result = model.calculate_utci(35.0, 60.0, 2.0, 40.0)
        assert isinstance(result, UTCIOutput)
        assert -50 <= result.utci_c <= 50

    def test_calculator_model_get_hazard_index(self):
        model = UTCICalculatorModel()
        idx = model.get_hazard_index(40.0)
        assert 0.0 <= idx <= 1.0


class TestCalmWindPolicy:
    """Test calm-wind policy for wind speed < 0.5 m/s."""

    def test_wind_below_05_is_clamped(self):
        """Wind speed < 0.5 m/s should be clamped to 0.5 m/s."""
        result = calculate_utci(
            air_temperature=30.0,
            relative_humidity=50.0,
            wind_speed=0.0,
            mean_radiant_temperature=30.0,
        )
        assert result.wind_clamped is True
        assert result.wind_speed == 0.5
        assert result.original_wind_speed == 0.0

    def test_wind_at_05_not_clamped(self):
        """Wind speed = 0.5 m/s should not be clamped."""
        result = calculate_utci(
            air_temperature=30.0,
            relative_humidity=50.0,
            wind_speed=0.5,
            mean_radiant_temperature=30.0,
        )
        assert result.wind_clamped is False
        assert result.wind_speed == 0.5
        assert result.original_wind_speed is None

    def test_wind_above_05_not_clamped(self):
        """Wind speed > 0.5 m/s should not be clamped."""
        result = calculate_utci(
            air_temperature=30.0,
            relative_humidity=50.0,
            wind_speed=1.0,
            mean_radiant_temperature=30.0,
        )
        assert result.wind_clamped is False
        assert result.wind_speed == 1.0
        assert result.original_wind_speed is None

    def test_wind_very_low_is_clamped(self):
        """Very low wind speed (0.01 m/s) should be clamped."""
        result = calculate_utci(
            air_temperature=30.0,
            relative_humidity=50.0,
            wind_speed=0.01,
            mean_radiant_temperature=30.0,
        )
        assert result.wind_clamped is True
        assert result.wind_speed == 0.5
        assert result.original_wind_speed == 0.01

    def test_clamped_wind_produces_valid_utci(self):
        """Clamped wind should produce valid UTCI result."""
        result = calculate_utci(
            air_temperature=30.0,
            relative_humidity=50.0,
            wind_speed=0.0,
            mean_radiant_temperature=30.0,
        )
        assert isinstance(result.utci_c, float)
        assert -50 <= result.utci_c <= 50


class TestUTCIReferenceCases:
    """Extended UTCI reference validation cases."""

    def test_hot_humid(self):
        """Hot/humid: 35C, 80% RH, 1 m/s, MRT 35C."""
        result = calculate_utci(35.0, 80.0, 1.0, 35.0)
        # UTCI should be in reasonable range for hot/humid conditions
        assert 30 <= result.utci_c <= 45

    def test_hot_dry(self):
        """Hot/dry: 42C, 20% RH, 1 m/s, MRT 42C."""
        result = calculate_utci(42.0, 20.0, 1.0, 42.0)
        # UTCI should be in reasonable range for hot/dry conditions
        assert 35 <= result.utci_c <= 50

    def test_high_radiation(self):
        """High radiation: 38C, 50% RH, 1 m/s, MRT 55C."""
        result = calculate_utci(38.0, 50.0, 1.0, 55.0)
        # UTCI should be elevated due to high MRT
        assert 40 <= result.utci_c <= 60

    def test_windy(self):
        """Windy: 40C, 50% RH, 5 m/s, MRT 40C."""
        result = calculate_utci(40.0, 50.0, 5.0, 40.0)
        # UTCI should be lower due to wind cooling
        assert 30 <= result.utci_c <= 45

    def test_cold(self):
        """Cold: -5C, 50% RH, 2 m/s, MRT -5C."""
        result = calculate_utci(-5.0, 50.0, 2.0, -5.0)
        # UTCI should be below air temperature
        assert -15 <= result.utci_c <= 0

    def test_extreme_cold(self):
        """Extreme cold: -20C, 50% RH, 3 m/s, MRT -20C."""
        result = calculate_utci(-20.0, 50.0, 3.0, -20.0)
        # UTCI should be well below air temperature
        assert -35 <= result.utci_c <= -15


class TestUTCIValidityBoundaries:
    """Test UTCI validity boundary conditions."""

    def test_ta_minus_50(self):
        """Test Ta = -50C (lower boundary)."""
        result = calculate_utci(-50.0, 50.0, 1.0, -50.0)
        assert isinstance(result.utci_c, float)

    def test_ta_plus_50(self):
        """Test Ta = +50C (upper boundary)."""
        # At Ta=50C, RH must be low enough to keep VP <= 50 hPa
        result = calculate_utci(50.0, 30.0, 1.0, 50.0)
        assert isinstance(result.utci_c, float)

    def test_wind_05(self):
        """Test wind = 0.5 m/s (lower boundary)."""
        result = calculate_utci(25.0, 50.0, 0.5, 25.0)
        assert isinstance(result.utci_c, float)
        assert result.wind_clamped is False

    def test_wind_17(self):
        """Test wind = 17 m/s (upper boundary)."""
        result = calculate_utci(25.0, 50.0, 17.0, 25.0)
        assert isinstance(result.utci_c, float)

    def test_vapor_pressure_50(self):
        """Test vapor pressure near 50 hPa (upper boundary)."""
        # At Ta=40C, RH=100%, VP ~ 73 hPa (too high)
        # At Ta=35C, RH=100%, VP ~ 56 hPa (too high)
        # At Ta=30C, RH=100%, VP ~ 42 hPa (valid)
        result = calculate_utci(30.0, 100.0, 1.0, 30.0)
        assert isinstance(result.utci_c, float)

    def test_mrt_minus_30(self):
        """Test MRT = Ta - 30C (lower boundary)."""
        result = calculate_utci(25.0, 50.0, 1.0, -5.0)
        assert isinstance(result.utci_c, float)

    def test_mrt_plus_70(self):
        """Test MRT = Ta + 70C (upper boundary)."""
        result = calculate_utci(25.0, 50.0, 1.0, 95.0)
        assert isinstance(result.utci_c, float)


def test_utci_reference_value():
    """Reference: tdb=25, rh=50, v=1, tmrt=25 -> UTCI ≈ 24.6."""
    model = UTCICalculatorModel()
    result = model.calculate_utci(25.0, 50.0, 1.0, 25.0)
    assert abs(result.utci_c - 24.6) < 0.2
