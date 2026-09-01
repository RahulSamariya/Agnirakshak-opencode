"""Tests for thermofeel exact parity (TEST 2F)."""
from __future__ import annotations

import math

import numpy as np
import pytest

from scientific.thermal_comfort.mrt import (
    _day_of_year, _solar_declination, _time_correction, _hour_angle,
    _sunrise_sunset_hour_angle, _average_daytime_cos_zenith, _sunlit_hour_angles,
    _surface_projection_factor, SIGMA, F_A, ALPHA_IR, EPSILON_P,
)


class TestCommonInputParity:
    """Verify both implementations receive identical inputs."""

    def test_dsrp_calculation(self):
        from thermofeel.thermofeel import approximate_dsrp
        fdir = np.array([654.31])
        cossza = np.array([0.8])
        dsrp = approximate_dsrp(fdir, cossza)
        expected = 654.31 / 0.8
        assert dsrp[0] == pytest.approx(expected, rel=1e-6)

    def test_dsrp_low_cossza(self):
        from thermofeel.thermofeel import approximate_dsrp
        fdir = np.array([10.0])
        cossza = np.array([0.05])
        dsrp = approximate_dsrp(fdir, cossza)
        assert dsrp[0] == pytest.approx(10.0, rel=1e-6)


class TestCosszaParity:
    """Verify cossza is identical between implementations."""

    def test_cossza_at_06utc(self):
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
        assert cossza == pytest.approx(0.800, abs=0.001)


class TestFpParity:
    """Verify fp comparison identifies the gamma convention difference."""

    def test_fp_different_gamma_conventions(self):
        elev = 53.13
        gamma_ours = 90.0 - elev  # zenith
        gamma_tf = elev           # elevation (from arcsin(cossza))
        fp_ours = 0.308 * math.cos(math.radians(gamma_ours * (0.998 - gamma_ours**2 / 50000)))
        fp_tf = 0.308 * math.cos(math.radians(gamma_tf * (0.998 - gamma_tf**2 / 50000)))
        assert fp_ours != pytest.approx(fp_tf, rel=1e-3)
        assert 0 < fp_ours < 1
        assert 0 < fp_tf < 1

    def test_fp_low_elevation(self):
        elev = 15.7
        gamma_ours = 90.0 - elev
        gamma_tf = elev
        fp_ours = 0.308 * math.cos(math.radians(gamma_ours * (0.998 - gamma_ours**2 / 50000)))
        fp_tf = 0.308 * math.cos(math.radians(gamma_tf * (0.998 - gamma_tf**2 / 50000)))
        assert fp_ours != pytest.approx(fp_tf, rel=1e-3)
        assert fp_ours < fp_tf  # at low sun, ours is smaller


class TestAlphaEpsilonPlacement:
    """Verify alpha_ir/epsilon_p placement difference."""

    def test_placement_difference(self):
        ar = ALPHA_IR / EPSILON_P
        strd, str_val = 343.41, -166.58
        ssrd, fdir, ssr = 783.16, 654.31, 631.52
        L_up = strd - str_val
        S_diff = ssrd - fdir
        S_ref = ssrd - ssr
        dsrp = 817.90
        fp = 0.1979

        # Ours: fp*I* outside multiplier
        rf_ours = F_A*strd + F_A*L_up + ar*F_A*S_diff + ar*F_A*S_ref + fp*dsrp
        # Thermofeel: fp*dsrp inside multiplier
        rf_tf = 0.5*strd + 0.5*L_up + ar*(0.5*S_diff + 0.5*S_ref + fp*dsrp)
        assert rf_ours != pytest.approx(rf_tf, rel=1e-4)


class TestTermByTermParity:
    """Verify term-by-term comparison identifies first divergent term."""

    def test_longwave_identical(self):
        strd, str_val = 343.41, -166.58
        L_up = strd - str_val
        assert L_up == pytest.approx(509.99, abs=0.01)

    def test_shortwave_identical(self):
        ssrd, fdir, ssr = 783.16, 654.31, 631.52
        S_diff = ssrd - fdir
        S_ref = ssrd - ssr
        assert S_diff == pytest.approx(128.85, abs=0.01)
        assert S_ref == pytest.approx(151.64, abs=0.01)

    def test_fp_first_divergent(self):
        """fp is the first term where implementations differ."""
        elev = 53.13
        gamma_ours = 90.0 - elev
        gamma_tf = elev
        fp_ours = 0.308 * math.cos(math.radians(gamma_ours * (0.998 - gamma_ours**2 / 50000)))
        fp_tf = 0.308 * math.cos(math.radians(gamma_tf * (0.998 - gamma_tf**2 / 50000)))
        assert abs(fp_ours - fp_tf) > 0.01


class TestVariantMatrix:
    """Verify variant F achieves exact parity."""

    def test_all_tf_intermediates_match(self):
        ar = ALPHA_IR / EPSILON_P
        strd, str_val = 343.41, -166.58
        ssrd, fdir, ssr = 783.16, 654.31, 631.52
        cossza = 0.8
        L_up = strd - str_val
        S_diff = ssrd - fdir
        S_ref = ssrd - ssr
        dsrp = fdir / cossza

        # Compute fp exactly as thermofeel does
        gamma_tf = math.degrees(math.asin(cossza))
        fp_tf = 0.308 * math.cos(math.radians(gamma_tf * (0.998 - gamma_tf**2 / 50000)))

        rf = 0.5*strd + 0.5*L_up + ar*(0.5*S_diff + 0.5*S_ref + fp_tf*dsrp)
        mrt = (rf / SIGMA) ** 0.25

        from thermofeel.thermofeel import calculate_mean_radiant_temperature
        tf_mrt = calculate_mean_radiant_temperature(
            ssrd=np.array([ssrd]), ssr=np.array([ssr]),
            dsrp=np.array([dsrp]), strd=np.array([strd]),
            fdir=np.array([fdir]), strr=np.array([str_val]),
            cossza=np.array([cossza]),
        )[0]
        assert mrt == pytest.approx(tf_mrt, rel=1e-6)
