"""Unit tests for MRT module (Di Napoli et al. 2020)."""
from __future__ import annotations

import math

import numpy as np
import pytest

from scientific.thermal_comfort.mrt import (
    SIGMA,
    F_A,
    ALPHA_IR,
    EPSILON_P,
    QualityFlag,
    _day_of_year,
    _solar_declination,
    _hour_angle,
    _solar_zenith_angle,
    _sunrise_sunset_hour_angle,
    _surface_projection_factor,
    calculate_mrt_single,
    validate_mrt,
)


class TestConstants:
    """Verify source-documented constants."""

    def test_sigma(self):
        assert SIGMA == pytest.approx(5.67e-8, rel=1e-6)

    def test_f_a(self):
        assert F_A == 0.5

    def test_alpha_ir(self):
        assert ALPHA_IR == 0.7

    def test_epsilon_p(self):
        assert EPSILON_P == 0.97


class TestSolarGeometry:
    """Test solar geometry equations (Di Napoli Eqs 6-12)."""

    def test_day_of_year_jan1(self):
        t = np.datetime64("2010-01-01T00:00:00")
        assert _day_of_year(t) == pytest.approx(1.0)

    def test_day_of_year_mar1(self):
        t = np.datetime64("2010-03-01T00:00:00")
        assert _day_of_year(t) == pytest.approx(60.0, abs=0.5)

    def test_solar_declination_equinox(self):
        jd = 80.0  # ~March 21
        delta = _solar_declination(jd)
        assert abs(delta) < 5.0  # near 0 at equinox

    def test_solar_zenith_noon_equator(self):
        # At equinox, noon at equator: zenith ~ 0
        delta = 0.0
        phi = 0.0
        h = 0.0  # noon
        zenith = _solar_zenith_angle(delta, phi, h)
        assert zenith == pytest.approx(0.0, abs=1.0)

    def test_solar_zenith_night(self):
        # At night, zenith > 90
        delta = 0.0
        phi = 45.0
        h = 180.0  # midnight
        zenith = _solar_zenith_angle(delta, phi, h)
        assert zenith > 90.0

    def test_sunrise_sunset_symmetric(self):
        delta = 10.0
        phi = 45.0
        h0 = _sunrise_sunset_hour_angle(delta, phi)
        assert h0 > 0
        assert h0 < 180


class TestSurfaceProjection:
    """Test surface projection factor (Di Napoli Eq 15)."""

    def test_noon(self):
        f_p = _surface_projection_factor(90.0)
        assert 0 < f_p < 1

    def test_horizon(self):
        f_p = _surface_projection_factor(0.0)
        assert f_p == pytest.approx(0.308, abs=0.01)

    def test_negative_elevation(self):
        f_p = _surface_projection_factor(-10.0)
        # cos(-10 deg) is positive, f_p is positive
        assert f_p != 0


class TestMRTEquation:
    """Test MRT calculation (Di Napoli Eq 14)."""

    def test_nighttime_returns_nan_or_flag(self):
        # Nighttime: all radiation zero
        result = calculate_mrt_single(
            ssrd=0.0, strd=300.0, fdir=0.0, ssr=0.0, str_val=-50.0,
            latitude_deg=23.0, longitude_deg=72.5,
            time_utc=np.datetime64("2010-03-01T00:00:00"),
            accumulation_seconds=3600.0,
        )
        # Should not crash, should have a quality flag
        assert result.quality_flag in [QualityFlag.NIGHTTIME, QualityFlag.VALID]

    def test_daytime_positive_mrt(self):
        # Daytime: reasonable radiation values
        result = calculate_mrt_single(
            ssrd=500.0, strd=300.0, fdir=200.0, ssr=100.0, str_val=-50.0,
            latitude_deg=23.0, longitude_deg=72.5,
            time_utc=np.datetime64("2010-03-01T12:00:00"),
            accumulation_seconds=3600.0,
        )
        # MRT should be positive and in reasonable range
        assert result.mrt_kelvin > 150
        assert result.mrt_kelvin < 400

    def test_mrt_in_kelvin(self):
        result = calculate_mrt_single(
            ssrd=500.0, strd=300.0, fdir=200.0, ssr=100.0, str_val=-50.0,
            latitude_deg=23.0, longitude_deg=72.5,
            time_utc=np.datetime64("2010-03-01T12:00:00"),
            accumulation_seconds=3600.0,
        )
        # MRT in Celsius = MRT in Kelvin - 273.15
        assert result.mrt_celsius == pytest.approx(
            result.mrt_kelvin - 273.15, abs=0.01
        )

    def test_missing_input_flagged(self):
        result = calculate_mrt_single(
            ssrd=float("nan"), strd=300.0, fdir=200.0, ssr=100.0, str_val=-50.0,
            latitude_deg=23.0, longitude_deg=72.5,
            time_utc=np.datetime64("2010-03-01T12:00:00"),
            accumulation_seconds=3600.0,
        )
        assert result.quality_flag == QualityFlag.MISSING_INPUT
        assert math.isnan(result.mrt_kelvin)

    def test_derived_quantities(self):
        result = calculate_mrt_single(
            ssrd=500.0, strd=300.0, fdir=200.0, ssr=100.0, str_val=-50.0,
            latitude_deg=23.0, longitude_deg=72.5,
            time_utc=np.datetime64("2010-03-01T12:00:00"),
            accumulation_seconds=3600.0,
        )
        # L_srf_up = strd - str = 300 - (-50) = 350
        assert result.upward_longwave == pytest.approx(350.0, abs=0.1)
        # S_diffuse = ssrd - fdir = 500 - 200 = 300
        assert result.diffuse_shortwave == pytest.approx(300.0, abs=0.1)
        # S_srf_up = ssrd - ssr = 500 - 100 = 400
        assert result.upward_shortwave == pytest.approx(400.0, abs=0.1)


class TestValidation:
    """Test validation metrics."""

    def test_perfect_match(self):
        ours = np.array([300.0, 310.0, 320.0])
        ref = np.array([300.0, 310.0, 320.0])
        qf = np.array([0, 0, 0])
        metrics = validate_mrt(ours, ref, qf)
        assert metrics["mae"] == pytest.approx(0.0)
        assert metrics["rmse"] == pytest.approx(0.0)
        assert metrics["mean_bias"] == pytest.approx(0.0)

    def test_constant_bias(self):
        ours = np.array([310.0, 320.0, 330.0])
        ref = np.array([300.0, 310.0, 320.0])
        qf = np.array([0, 0, 0])
        metrics = validate_mrt(ours, ref, qf)
        assert metrics["mean_bias"] == pytest.approx(10.0)
        assert metrics["mae"] == pytest.approx(10.0)

    def test_empty_arrays(self):
        ours = np.array([])
        ref = np.array([])
        qf = np.array([], dtype=np.int32)
        metrics = validate_mrt(ours, ref, qf)
        assert metrics["sample_count"] == 0
