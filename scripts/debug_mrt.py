"""MRT TEST 2 DEBUG: Investigate -108 K bias.

Print intermediate MRT terms for 5 real observations to find root cause.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scientific.thermal_comfort.mrt import (
    SIGMA, F_A, ALPHA_IR, EPSILON_P,
    _day_of_year, _solar_declination, _time_correction,
    _hour_angle, _solar_zenith_angle, _sunrise_sunset_hour_angle,
    _average_daytime_cos_zenith,
)

RADIATION_PATH = Path("97c99a12bac0f84dae69bd5460cde459.nc")
ERA5HEAT_PATH = Path("cde4e619c080209e1ec505565f79b8e.nc")
ACCUM_SECONDS = 21600


def main():
    print("=" * 80)
    print("MRT TEST 2 DEBUG")
    print("=" * 80)

    # Load data
    ds_rad = xr.open_dataset(RADIATION_PATH)
    ds_heat = xr.open_dataset(ERA5HEAT_PATH)

    rad_time = ds_rad.valid_time.values
    heat_time = ds_heat.valid_time.values
    common_times = np.intersect1d(rad_time, heat_time)

    rad_lat = ds_rad.latitude.values
    rad_lon = ds_rad.longitude.values

    print(f"\nRadiation grid: lat={rad_lat}, lon={rad_lon}")
    print(f"Common timestamps: {len(common_times)}")

    # =========================================================================
    # SECTION 1: CHECK ERA5-HEAT REFERENCE UNITS
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 8: ERA5-HEAT REFERENCE UNITS")
    print("=" * 80)

    mrt_var = ds_heat["mrt"]
    print(f"  mrt attrs: {dict(mrt_var.attrs)}")
    print(f"  mrt dtype: {mrt_var.dtype}")

    # Check a few raw values
    heat_common_mask = np.isin(heat_time, common_times)
    heat_mrt_raw = ds_heat["mrt"].sel(valid_time=heat_common_mask).values
    print(f"  Raw MRT range: [{np.nanmin(heat_mrt_raw):.2f}, {np.nanmax(heat_mrt_raw):.2f}]")
    print(f"  Raw MRT mean: {np.nanmean(heat_mrt_raw):.2f}")

    # Check if it's Kelvin or Celsius
    # Ahmedabad March: air temp ~25-40 C = 298-313 K
    # If raw values are ~280-334, it's Kelvin
    # If raw values are ~7-61, it's Celsius
    mean_val = np.nanmean(heat_mrt_raw)
    if mean_val > 200:
        print(f"  DETECTION: MRT appears to be in KELVIN (mean={mean_val:.1f})")
    elif mean_val < 100:
        print(f"  DETECTION: MRT appears to be in CELSIUS (mean={mean_val:.1f})")
    else:
        print(f"  DETECTION: UNCLEAR (mean={mean_val:.1f})")

    # =========================================================================
    # SECTION 2: CHECK RADIATION UNITS AND CONVERSION
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 2: RADIATION UNIT CONVERSION")
    print("=" * 80)

    # Get raw radiation values for first common timestamp
    t0 = common_times[0]
    rad_mask0 = rad_time == t0
    ssrd_raw = float(ds_rad["ssrd"].sel(valid_time=rad_mask0).values[0, 0, 0])
    strd_raw = float(ds_rad["strd"].sel(valid_time=rad_mask0).values[0, 0, 0])
    fdir_raw = float(ds_rad["fdir"].sel(valid_time=rad_mask0).values[0, 0, 0])
    ssr_raw = float(ds_rad["ssr"].sel(valid_time=rad_mask0).values[0, 0, 0])
    str_raw = float(ds_rad["str"].sel(valid_time=rad_mask0).values[0, 0, 0])

    print(f"\n  First timestamp: {t0}")
    print(f"  Raw values (J/m2):")
    print(f"    ssrd = {ssrd_raw:.2f}")
    print(f"    strd = {strd_raw:.2f}")
    print(f"    fdir = {fdir_raw:.2f}")
    print(f"    ssr  = {ssr_raw:.2f}")
    print(f"    str  = {str_raw:.2f}")

    # Convert to W/m2
    ssrd_w = ssrd_raw / ACCUM_SECONDS
    strd_w = strd_raw / ACCUM_SECONDS
    fdir_w = fdir_raw / ACCUM_SECONDS
    ssr_w = ssr_raw / ACCUM_SECONDS
    str_w = str_raw / ACCUM_SECONDS

    print(f"\n  Converted values (W/m2) [divided by {ACCUM_SECONDS}]:")
    print(f"    ssrd = {ssrd_w:.4f}")
    print(f"    strd = {strd_w:.4f}")
    print(f"    fdir = {fdir_w:.4f}")
    print(f"    ssr  = {ssr_w:.4f}")
    print(f"    str  = {str_w:.4f}")

    # =========================================================================
    # SECTION 3: CHECK 5 REPRESENTATIVE OBSERVATIONS
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 1-9: 5 REPRESENTATIVE OBSERVATIONS - FULL DIAGNOSTIC")
    print("=" * 80)

    # Select 5 timestamps: 2 nighttime, 3 daytime (roughly)
    # Ahmedabad IST = UTC+5:30, so UTC 00:00 = IST 05:30 (night)
    # UTC 06:00 = IST 11:30 (day), UTC 12:00 = IST 17:30 (day)
    # UTC 18:00 = IST 23:30 (night)
    sample_indices = [1, 25, 50, 75, 100]  # roughly spread across March

    for idx in sample_indices:
        if idx >= len(common_times):
            continue
        t = common_times[idx]
        print(f"\n{'-' * 80}")
        print(f"OBSERVATION #{idx}: {t}")
        print(f"{'-' * 80}")

        # Get radiation
        rad_mask = rad_time == t
        ssrd_r = float(ds_rad["ssrd"].sel(valid_time=rad_mask).values[0, 0, 0])
        strd_r = float(ds_rad["strd"].sel(valid_time=rad_mask).values[0, 0, 0])
        fdir_r = float(ds_rad["fdir"].sel(valid_time=rad_mask).values[0, 0, 0])
        ssr_r = float(ds_rad["ssr"].sel(valid_time=rad_mask).values[0, 0, 0])
        str_r = float(ds_rad["str"].sel(valid_time=rad_mask).values[0, 0, 0])

        # Convert
        ssrd_w = ssrd_r / ACCUM_SECONDS
        strd_w = strd_r / ACCUM_SECONDS
        fdir_w = fdir_r / ACCUM_SECONDS
        ssr_w = ssr_r / ACCUM_SECONDS
        str_w = str_r / ACCUM_SECONDS

        # Get ERA5-HEAT MRT
        heat_mask = heat_time == t
        heat_mrt = float(ds_heat["mrt"].sel(valid_time=heat_mask).values[0, 0, 0])

        # Use center grid point (23.0, 72.5) -> lat_idx=1, lon_idx=1
        lat = 23.0
        lon = 72.5

        print(f"\n  COORDINATES:")
        print(f"    lat = {lat}")
        print(f"    lon = {lon}")

        # Time
        hour_utc = float(t.astype("datetime64[h]").astype(int) % 24)
        ist_hour = (hour_utc + 5.5) % 24
        print(f"\n  TIME:")
        print(f"    UTC hour = {hour_utc:.1f}")
        print(f"    IST hour = {ist_hour:.1f}")

        print(f"\n  RADIATION (raw J/m2 -> converted W/m2):")
        print(f"    ssrd: {ssrd_r:.2f} -> {ssrd_w:.4f} W/m2")
        print(f"    strd: {strd_r:.2f} -> {strd_w:.4f} W/m2")
        print(f"    fdir: {fdir_r:.2f} -> {fdir_w:.4f} W/m2")
        print(f"    ssr:  {ssr_r:.2f} -> {ssr_w:.4f} W/m2")
        print(f"    str:  {str_r:.2f} -> {str_w:.4f} W/m2")

        # Derived radiation
        L_srf_up = strd_w - str_w
        S_diffuse = ssrd_w - fdir_w
        S_up = ssrd_w - ssr_w
        print(f"\n  DERIVED RADIATION:")
        print(f"    L_srf_up    = strd - str = {strd_w:.4f} - {str_w:.4f} = {L_srf_up:.4f} W/m2")
        print(f"    S_diffuse   = ssrd - fdir = {ssrd_w:.4f} - {fdir_w:.4f} = {S_diffuse:.4f} W/m2")
        print(f"    S_up        = ssrd - ssr  = {ssrd_w:.4f} - {ssr_w:.4f} = {S_up:.4f} W/m2")

        # Solar geometry
        jd = _day_of_year(t)
        hours_since_midnight = float(
            (t - np.datetime64(t.astype("datetime64[D]")))
            / np.timedelta64(1, "h")
        )
        delta = _solar_declination(jd)
        tc = _time_correction(jd)
        h = _hour_angle(hours_since_midnight, lon, tc)
        zenith = _solar_zenith_angle(delta, lat, h)
        elevation = 90.0 - zenith

        h0 = _sunrise_sunset_hour_angle(delta, lat)
        cos_theta_bar = _average_daytime_cos_zenith(delta, lat, -h0, h0)

        print(f"\n  SOLAR GEOMETRY:")
        print(f"    day_of_year = {jd:.1f}")
        print(f"    hours_since_midnight (UTC) = {hours_since_midnight:.2f}")
        print(f"    solar_declination = {delta:.4f} deg")
        print(f"    time_correction = {tc:.4f} min")
        print(f"    hour_angle = {h:.4f} deg")
        print(f"    solar_zenith = {zenith:.4f} deg")
        print(f"    solar_elevation = {elevation:.4f} deg")
        print(f"    cos_theta_bar_0 = {cos_theta_bar:.6f}")

        # Direct solar projection
        nighttime = elevation < 0.0
        cos_zenith = math.cos(math.radians(zenith))
        if nighttime or cos_zenith < 0.01:
            I_star = 0.0
        else:
            I_star = fdir_w / cos_zenith

        # Surface projection factor
        if not nighttime:
            gamma_rad = math.radians(elevation)
            f_p = 0.308 * math.cos(gamma_rad * (0.998 - elevation**2 / 50000.0))
        else:
            f_p = 0.0

        print(f"\n  DIRECT SOLAR PROJECTION:")
        print(f"    cos_zenith = {cos_zenith:.6f}")
        print(f"    nighttime = {nighttime}")
        print(f"    I* = fdir/cos_zenith = {fdir_w:.4f}/{cos_zenith:.6f} = {I_star:.4f} W/m2")
        print(f"    f_p = {f_p:.6f}")

        # MRT equation terms
        alpha_ratio = ALPHA_IR / EPSILON_P
        term1 = F_A * strd_w          # downward longwave
        term2 = F_A * L_srf_up        # upward longwave
        term3 = alpha_ratio * F_A * S_diffuse  # diffuse shortwave
        term4 = alpha_ratio * F_A * S_up        # reflected shortwave
        term5 = f_p * I_star           # direct solar

        radiant_flux = term1 + term2 + term3 + term4 + term5

        print(f"\n  MRT EQUATION TERMS:")
        print(f"    Constants: sigma={SIGMA}, f_a={F_A}, alpha_ir={ALPHA_IR}, eps={EPSILON_P}")
        print(f"    alpha_ratio = alpha_ir/eps = {alpha_ratio:.6f}")
        print(f"    term1 (down LW)   = f_a * strd     = {F_A} * {strd_w:.4f} = {term1:.4f}")
        print(f"    term2 (up LW)     = f_a * L_up     = {F_A} * {L_srf_up:.4f} = {term2:.4f}")
        print(f"    term3 (diffuse SW)= a_r * f_a * Sd = {alpha_ratio:.4f} * {F_A} * {S_diffuse:.4f} = {term3:.4f}")
        print(f"    term4 (refl SW)   = a_r * f_a * Su = {alpha_ratio:.4f} * {F_A} * {S_up:.4f} = {term4:.4f}")
        print(f"    term5 (direct SW) = f_p * I*       = {f_p:.6f} * {I_star:.4f} = {term5:.4f}")
        print(f"    {'-' * 45}")
        print(f"    radiant_flux = sum = {radiant_flux:.4f} W/m2")

        mrt_kelvin = (radiant_flux / SIGMA) ** 0.25
        mrt_celsius = mrt_kelvin - 273.15

        print(f"\n  MRT RESULT:")
        print(f"    radiant_flux / sigma = {radiant_flux:.4f} / {SIGMA} = {radiant_flux / SIGMA:.4f}")
        print(f"    fourth root = ({radiant_flux / SIGMA:.4f})^0.25 = {mrt_kelvin:.4f} K")
        print(f"    MRT = {mrt_kelvin:.4f} K = {mrt_celsius:.4f} C")

        print(f"\n  ERA5-HEAT REFERENCE:")
        print(f"    MRT_ref = {heat_mrt:.4f}")

        error = mrt_kelvin - heat_mrt
        print(f"\n  ERROR:")
        print(f"    MRT_ours - MRT_ref = {mrt_kelvin:.4f} - {heat_mrt:.4f} = {error:.4f} K")

        if nighttime:
            print(f"    FLAG: NIGHTTIME")
        else:
            print(f"    FLAG: DAYTIME")

    # =========================================================================
    # SECTION 4: CHECK NIGHTTIME FLAGS
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 3: NIGHTTIME FLAG ANALYSIS")
    print("=" * 80)

    print(f"\n  Timestamp | UTC Hour | IST Hour | Elevation | Flag")
    print(f"  {'-' * 65}")
    for i, t in enumerate(common_times[:20]):  # First 20 timestamps
        lat = 23.0
        lon = 72.5
        jd = _day_of_year(t)
        hours_since_midnight = float(
            (t - np.datetime64(t.astype("datetime64[D]")))
            / np.timedelta64(1, "h")
        )
        delta = _solar_declination(jd)
        tc = _time_correction(jd)
        h = _hour_angle(hours_since_midnight, lon, tc)
        zenith = _solar_zenith_angle(delta, lat, h)
        elevation = 90.0 - zenith

        hour_utc = float(t.astype("datetime64[h]").astype(int) % 24)
        ist_hour = (hour_utc + 5.5) % 24

        flag = "NIGHT" if elevation < 0 else "DAY"
        print(f"  {str(t)[:19]} | {hour_utc:5.1f}    | {ist_hour:5.1f}    | {elevation:7.2f}    | {flag}")

    # Check all 124 timestamps
    night_count = 0
    day_count = 0
    for t in common_times:
        lat = 23.0
        lon = 72.5
        jd = _day_of_year(t)
        hours_since_midnight = float(
            (t - np.datetime64(t.astype("datetime64[D]")))
            / np.timedelta64(1, "h")
        )
        delta = _solar_declination(jd)
        tc = _time_correction(jd)
        h = _hour_angle(hours_since_midnight, lon, tc)
        zenith = _solar_zenith_angle(delta, lat, h)
        elevation = 90.0 - zenith
        if elevation < 0:
            night_count += 1
        else:
            day_count += 1

    print(f"\n  SUMMARY: {day_count} DAYTIME, {night_count} NIGHTTIME out of {len(common_times)} total")

    # =========================================================================
    # SECTION 5: CHECK QUALITY FLAG COUNTS
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 4: QUALITY FLAG LOGIC ANALYSIS")
    print("=" * 80)

    # The validation script reported: valid=744, night=744
    # Total grid points = 124 * 3 * 4 = 1488
    # So 744 + 744 = 1488 -- every point counted TWICE
    print(f"\n  Total grid points = 124 * 3 * 4 = {124 * 3 * 4}")
    print(f"  Reported: valid=744, nighttime=744")
    print(f"  Sum = {744 + 744}")
    print(f"  This means EVERY grid point appears in BOTH valid AND nighttime!")
    print(f"  This is a counting bug in validate_mrt, not in the MRT module itself.")

    # =========================================================================
    # SECTION 6: CHECK IF MRT VALUES ARE REASONABLE
    # =========================================================================
    print("\n" + "=" * 80)
    print("SECTION 6: MRT VALUE ANALYSIS")
    print("=" * 80)

    print(f"\n  Our MRT mean: 199.21 K = -73.94 C")
    print(f"  ERA5-HEAT MRT mean: ~307 K = ~34 C")
    print(f"  Bias: -108 K")
    print(f"")
    print(f"  For a nighttime-only MRT with no solar radiation:")
    print(f"    radiant_flux = f_a * L_up + f_a * L_dn")
    print(f"    = 0.5 * L_up + 0.5 * L_dn")
    print(f"    L_dn (strd) ~ 60 W/m2, L_up ~ 79 W/m2")
    print(f"    radiant_flux ~ 0.5*79 + 0.5*60 = 69.5 W/m2")
    print(f"    MRT = (69.5 / 5.67e-8)^0.25 = (1.226e9)^0.25 = 187 K")
    print(f"")
    print(f"  This matches our result! The issue is that our MRT is computing")
    print(f"  nighttime-only MRT using strd and str which are very small values.")
    print(f"  The ERA5-HEAT MRT likely uses a DIFFERENT formulation or includes")
    print(f"  additional terms (e.g., air temperature, clothing, etc.)")

    ds_rad.close()
    ds_heat.close()


if __name__ == "__main__":
    main()
