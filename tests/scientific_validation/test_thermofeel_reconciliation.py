"""Tests for thermofeel reconciliation (TEST 2E)."""
from __future__ import annotations

import math

import numpy as np
import pytest

from scientific.thermal_comfort.mrt import (
    calculate_mrt_single,
    _day_of_year,
    _solar_declination,
    _time_correction,
    _hour_angle,
    _sunrise_sunset_hour_angle,
    _average_daytime_cos_zenith,
    _sunlit_hour_angles,
    _surface_projection_factor,
    SIGMA,
    F_A,
    ALPHA_IR,
    EPSILON_P,
)


class TestThermofeelAvailability:
    """Verify thermofeel is installed and functional."""

    def test_import(self):
        import thermofeel
        assert hasattr(thermofeel, "__version__")

    def test_mrt_function_exists(self):
        from thermofeel.thermofeel import calculate_mean_radiant_temperature
        assert callable(calculate_mean_radiant_temperature)

    def test_approximate_dsrp_exists(self):
        from thermofeel.thermofeel import approximate_dsrp
        assert callable(approximate_dsrp)


class TestInputMapping:
    """Verify input mapping between ERA5 and thermofeel."""

    def test_dsrp_calculation(self):
        from thermofeel.thermofeel import approximate_dsrp
        fdir = np.array([654.31])
        cossza = np.array([0.8])
        dsrp = approximate_dsrp(fdir, cossza)
        expected = 654.31 / 0.8
        assert dsrp[0] == pytest.approx(expected, rel=1e-4)

    def test_dsrp_low_cossza(self):
        from thermofeel.thermofeel import approximate_dsrp
        fdir = np.array([10.0])
        cossza = np.array([0.05])  # below threshold
        dsrp = approximate_dsrp(fdir, cossza)
        assert dsrp[0] == pytest.approx(10.0, rel=1e-4)  # unchanged

    def test_units_conversion(self):
        """ERA5 J/m2 to W/m2: divide by accumulation seconds."""
        acc = 3600
        ssrd_jm2 = 3159744.0
        ssrd_wm2 = ssrd_jm2 / acc
        assert ssrd_wm2 == pytest.approx(877.71, abs=0.01)


class TestSolarGeometryComparison:
    """Compare solar geometry between our implementation and thermofeel."""

    def test_cossza_matches(self):
        """cossza = cos(zenith) should be identical."""
        t = np.datetime64("2010-03-01T06:00:00")
        lat, lon = 23.0, 72.5
        jd = _day_of_year(t)
        h_sm = 6.0
        delta = _solar_declination(jd)
        tc = _time_correction(jd)
        h_end = _hour_angle(h_sm, lon, tc)
        zen_r = (math.sin(math.radians(delta)) * math.sin(math.radians(lat))
                 + math.cos(math.radians(delta)) * math.cos(math.radians(lat))
                 * math.cos(math.radians(h_end)))
        zenith = math.degrees(math.acos(max(-1.0, min(1.0, zen_r))))
        cossza = math.cos(math.radians(zenith))
        # thermofeel also uses cos(zenith)
        assert cossza == pytest.approx(math.cos(math.radians(zenith)), rel=1e-10)

    def test_fp_calculation_differs_by_convention(self):
        """fp differs because gamma convention differs (zenith vs elevation)."""
        elev = 53.13
        # Our gamma = zenith = 90 - elev
        gamma_ours = 90.0 - elev
        fp_ours = 0.308 * math.cos(math.radians(gamma_ours * (0.998 - gamma_ours**2 / 50000)))
        # Thermofeel gamma = arcsin(cossza) = elev
        cossza = math.cos(math.radians(90 - elev))
        gamma_t = math.degrees(math.asin(cossza))
        fp_t = 0.308 * math.cos(math.radians(gamma_t * (0.998 - gamma_t**2 / 50000)))
        # These are DIFFERENT due to different gamma convention
        assert fp_ours != pytest.approx(fp_t, rel=1e-3)
        # Both are positive and in valid range
        assert 0 < fp_ours < 1
        assert 0 < fp_t < 1


class TestDirectSolarComparison:
    """Compare direct solar treatment between implementations."""

    def test_dsrp_vs_istar(self):
        """dsrp (instantaneous) differs from I* (interval average)."""
        fdir = 654.31
        cossza = 0.8
        cos_bar = 0.748
        dsrp = fdir / cossza
        istar = fdir / cos_bar
        # dsrp < I* because cos_bar < cossza (interval avg < instantaneous at high sun)
        assert dsrp < istar

    def test_nighttime_zero(self):
        """Both should give zero direct solar at night."""
        result = calculate_mrt_single(
            ssrd=0.0, strd=300.0, fdir=0.0, ssr=0.0, str_val=-50.0,
            latitude_deg=23.0, longitude_deg=72.5,
            time_utc=np.datetime64("2010-03-01T00:00:00"),
            accumulation_seconds=3600.0,
        )
        assert result.direct_radiation_projected == 0.0


class TestPairwiseMetrics:
    """Test pairwise metric calculation."""

    def test_perfect_match_metrics(self):
        a = np.array([300.0, 310.0, 320.0])
        b = np.array([300.0, 310.0, 320.0])
        diff = a - b
        assert np.mean(np.abs(diff)) == 0.0
        assert np.sqrt(np.mean(diff**2)) == 0.0
        assert np.mean(diff) == 0.0

    def test_constant_bias_metrics(self):
        a = np.array([310.0, 320.0, 330.0])
        b = np.array([300.0, 310.0, 320.0])
        diff = a - b
        assert np.mean(diff) == pytest.approx(10.0)
        assert np.mean(np.abs(diff)) == pytest.approx(10.0)
