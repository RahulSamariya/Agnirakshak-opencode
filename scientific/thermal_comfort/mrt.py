"""Mean Radiant Temperature (MRT) — ECMWF thermofeel-consistent implementation.

Implements the MRT methodology consistent with ECMWF thermofeel 2.3.0:
    Di Napoli, Hogan, Pappenberger (2020)
    "Mean radiant temperature from global-scale numerical weather
     prediction models"
    DOI: 10.1007/s00484-020-01900-5

Production method: ECMWF_THERMOFEEL_COMPATIBLE_V1

Constants and equations are source-documented. Do NOT modify without
explicit scientific approval.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray

# =============================================================================
# CONSTANTS — Source: Di Napoli et al. (2020), equations 14-15
# =============================================================================

MRT_METHOD_VERSION = "ECMWF_THERMOFEEL_COMPATIBLE_V1"

SIGMA = 5.67e-8  # Stefan-Boltzmann constant [W m^-2 K^-4]
F_A = 0.5  # Angle factor for upper/lower hemispheres
ALPHA_IR = 0.7  # Solar absorption coefficient of clothed human body
EPSILON_P = 0.97  # Emissivity of clothed human body
DSRP_COSZ_THRESHOLD = 0.1  # Minimum cossza for dsrp = fdir/cossza (thermofeel convention)


class QualityFlag(Enum):
    """Quality flags for MRT calculation."""

    VALID = 0
    NIGHTTIME = 1
    LOW_SOLAR_ELEVATION = 2
    NEGATIVE_RADIATION = 3
    MISSING_INPUT = 4
    MRT_UNPHYSICAL = 5


@dataclass(frozen=True)
class MRTResult:
    """Result of MRT calculation for a single point/time."""

    mrt_kelvin: float
    mrt_celsius: float
    quality_flag: QualityFlag
    solar_zenith_deg: float
    solar_elevation_deg: float
    cossza: float
    dsrp: float  # direct solar radiation perpendicular to beam [W/m2]
    f_p: float
    direct_radiation_projected: float  # fp * dsrp in W/m2
    diffuse_shortwave: float  # S_srf_dn_diffuse in W/m2
    upward_longwave: float  # L_srf_up in W/m2
    upward_shortwave: float  # S_srf_up in W/m2


@dataclass(frozen=True)
class MRTGridResult:
    """Result of MRT calculation for a full grid."""

    mrt_kelvin: NDArray[np.float64]  # shape: (time, lat, lon)
    mrt_celsius: NDArray[np.float64]
    quality_flags: NDArray[np.int32]
    solar_zenith_deg: NDArray[np.float64]
    solar_elevation_deg: NDArray[np.float64]
    cossza: NDArray[np.float64]
    dsrp: NDArray[np.float64]
    f_p: NDArray[np.float64]
    direct_radiation_projected: NDArray[np.float64]
    diffuse_shortwave: NDArray[np.float64]
    upward_longwave: NDArray[np.float64]
    upward_shortwave: NDArray[np.float64]
    times: NDArray[np.datetime64]
    latitudes: NDArray[np.float64]
    longitudes: NDArray[np.float64]


# =============================================================================
# SOLAR GEOMETRY — Equations 6-12 from Di Napoli et al. (2020)
# =============================================================================

def _day_of_year(time_utc: np.datetime64) -> float:
    """Compute day of year (JD) from UTC timestamp.

    Source: Equation 8 from Di Napoli et al. (2020).
    """
    year = int(time_utc.astype("datetime64[Y]").astype(int) + 1970)
    jan1 = np.datetime64(f"{year}-01-01")
    delta_days = (time_utc - jan1) / np.timedelta64(1, "D")
    return float(delta_days) + 1.0  # JD: 1 = Jan 1


def _solar_declination(jd: float) -> float:
    """Compute solar declination delta from Julian day.

    Source: Equation 8 from Di Napoli et al. (2020).
    Returns declination in degrees.
    """
    g = (360.0 / 365.25) * (jd - 1.0)  # fractional year angle in degrees
    g_rad = math.radians(g)
    delta_rad = (
        0.006918
        - 0.399912 * math.cos(g_rad)
        + 0.070257 * math.sin(g_rad)
        - 0.006758 * math.cos(2 * g_rad)
        + 0.000907 * math.sin(2 * g_rad)
        - 0.002697 * math.cos(3 * g_rad)
        + 0.001480 * math.sin(3 * g_rad)
    )
    return math.degrees(delta_rad)


def _time_correction(jd: float) -> float:
    """Compute time correction TC in degrees.

    Source: Equation 10 from Di Napoli et al. (2020).
    """
    g = (360.0 / 365.25) * (jd - 1.0)
    g_rad = math.radians(g)
    tc = (
        0.004297
        + 0.107029 * math.cos(g_rad)
        - 1.837877 * math.sin(g_rad)
        - 0.837378 * math.cos(2 * g_rad)
        - 2.340475 * math.sin(2 * g_rad)
    )
    return tc


def _hour_angle(hr_utc: float, longitude_deg: float, tc: float) -> float:
    """Compute hour angle h in degrees.

    Source: Equation 9 from Di Napoli et al. (2020).
    h = (hr - 12) * 15 + longitude + TC
    """
    return (hr_utc - 12.0) * 15.0 + longitude_deg + tc


def _solar_zenith_angle(
    declination_deg: float, latitude_deg: float, hour_angle_deg: float
) -> float:
    """Compute cosine of solar zenith angle.

    Source: Equation 6 from Di Napoli et al. (2020).
    cos(theta_0) = sin(delta)*sin(phi) + cos(delta)*cos(phi)*cos(h)
    """
    delta_rad = math.radians(declination_deg)
    phi_rad = math.radians(latitude_deg)
    h_rad = math.radians(hour_angle_deg)
    cos_zenith = (
        math.sin(delta_rad) * math.sin(phi_rad)
        + math.cos(delta_rad) * math.cos(phi_rad) * math.cos(h_rad)
    )
    # Clamp to [-1, 1] for numerical safety
    cos_zenith = max(-1.0, min(1.0, cos_zenith))
    return math.degrees(math.acos(cos_zenith))


def _sunrise_sunset_hour_angle(
    declination_deg: float, latitude_deg: float
) -> float:
    """Compute sunrise/sunset hour angle h0 in degrees.

    Source: Equation 11 from Di Napoli et al. (2020).
    cos(h0) = -tan(delta) * tan(phi)
    """
    delta_rad = math.radians(declination_deg)
    phi_rad = math.radians(latitude_deg)
    cos_h0 = -math.tan(delta_rad) * math.tan(phi_rad)
    # Clamp for polar day/night
    if cos_h0 < -1.0:
        return 180.0  # polar day: sun never sets
    if cos_h0 > 1.0:
        return 0.0  # polar night: sun never rises
    return math.degrees(math.acos(cos_h0))


def _average_daytime_cos_zenith(
    declination_deg: float,
    latitude_deg: float,
    h_min_deg: float,
    h_max_deg: float,
) -> float:
    """Compute average daytime cosine of solar zenith angle.

    Source: Equation 12 from Di Napoli et al. (2020).
    cos(theta_bar_0) = sin(delta)*sin(phi)
        + [1/(h_max - h_min)] * cos(delta)*cos(phi) * [sin(h_max) - sin(h_min)]

    Parameters
    ----------
    h_min_deg : float
        Start hour angle in degrees (e.g. for sunlit interval).
    h_max_deg : float
        End hour angle in degrees (e.g. for sunlit interval).
    """
    delta_rad = math.radians(declination_deg)
    phi_rad = math.radians(latitude_deg)
    h_min_rad = math.radians(h_min_deg)
    h_max_rad = math.radians(h_max_deg)
    dh = h_max_deg - h_min_deg
    if abs(dh) < 1e-10:
        return 0.0
    cos_avg = (
        math.sin(delta_rad) * math.sin(phi_rad)
        + (1.0 / math.radians(dh))
        * math.cos(delta_rad)
        * math.cos(phi_rad)
        * (math.sin(h_max_rad) - math.sin(h_min_rad))
    )
    return max(0.0, cos_avg)


def _sunlit_hour_angles(
    h_start_deg: float,
    h_end_deg: float,
    h0_deg: float,
) -> tuple[float, float]:
    """Compute the sunlit portion of an accumulation interval.

    Parameters
    ----------
    h_start_deg : float
        Hour angle at the start of the accumulation interval.
    h_end_deg : float
        Hour angle at the end of the accumulation interval.
    h0_deg : float
        Sunrise/sunset hour angle (positive).

    Returns
    -------
    tuple[float, float]
        (h_min, h_max) for the sunlit portion.
        If no overlap: h_min > h_max (fully nighttime).
    """
    # Sunlit hour-angle range: [-h0, h0]
    h_min = max(h_start_deg, -h0_deg)
    h_max = min(h_end_deg, h0_deg)
    return h_min, h_max


# =============================================================================
# MRT CALCULATION — Equations 3-5, 13-15 from Di Napoli et al. (2020)
# =============================================================================

def _surface_projection_factor(solar_elevation_deg: float) -> float:
    """Compute surface projection factor f_p for standing person.

    Source: Equation 15 from Di Napoli et al. (2020).
    f_p = 0.308 * cos(gamma * (0.998 - gamma^2/50000))
    where gamma is solar elevation angle in degrees.
    """
    gamma = solar_elevation_deg
    gamma_rad = math.radians(gamma)
    f_p = 0.308 * math.cos(gamma_rad * (0.998 - gamma**2 / 50000.0))
    return f_p


def calculate_mrt_single(
    ssrd: float,  # S_srf_dn: downward shortwave [W/m2]
    strd: float,  # L_srf_dn: downward longwave [W/m2]
    fdir: float,  # S_srf_dn_direct: direct shortwave [W/m2]
    ssr: float,  # S_srf_net: net shortwave [W/m2]
    str_val: float,  # L_srf_net: net longwave [W/m2]
    latitude_deg: float,
    longitude_deg: float,
    time_utc: np.datetime64,
    accumulation_seconds: float,
) -> MRTResult:
    """Calculate MRT for a single point/time using thermofeel-consistent method.

    All radiation inputs must already be in W/m2 (converted from J/m2).

    Production method: ECMWF_THERMOFEEL_COMPATIBLE_V1

    Parameters
    ----------
    ssrd : float
        Surface solar radiation downwards [W/m2].
    strd : float
        Surface thermal radiation downwards [W/m2].
    fdir : float
        Direct solar radiation at surface [W/m2].
    ssr : float
        Surface net solar radiation [W/m2].
    str_val : float
        Surface net thermal radiation [W/m2].
    latitude_deg : float
        Latitude in degrees (positive north).
    longitude_deg : float
        Longitude in degrees (positive east).
    time_utc : np.datetime64
        UTC timestamp.
    accumulation_seconds : float
        Accumulation period in seconds.

    Returns
    -------
    MRTResult
        MRT in Kelvin and Celsius with quality flags.
    """
    # --- Check for missing data ---
    inputs = [ssrd, strd, fdir, ssr, str_val]
    if any(np.isnan(x) for x in inputs):
        return MRTResult(
            mrt_kelvin=float("nan"),
            mrt_celsius=float("nan"),
            quality_flag=QualityFlag.MISSING_INPUT,
            solar_zenith_deg=float("nan"),
            solar_elevation_deg=float("nan"),
            cossza=float("nan"),
            dsrp=0.0,
            f_p=0.0,
            direct_radiation_projected=0.0,
            diffuse_shortwave=0.0,
            upward_longwave=0.0,
            upward_shortwave=0.0,
        )

    # --- Derived radiation quantities (Equations 3-5) ---
    L_srf_up = strd - str_val  # Eq 3: upward longwave
    S_srf_dn_diffuse = ssrd - fdir  # Eq 4: diffuse shortwave
    S_srf_up = ssrd - ssr  # Eq 5: upward shortwave reflected

    # --- Solar geometry ---
    jd = _day_of_year(time_utc)
    hours_since_midnight = (
        (time_utc - np.datetime64(time_utc.astype("datetime64[D]")))
        / np.timedelta64(1, "h")
    )

    delta = _solar_declination(jd)
    tc = _time_correction(jd)
    h_end = _hour_angle(hours_since_midnight, longitude_deg, tc)
    zenith = _solar_zenith_angle(delta, latitude_deg, h_end)
    elevation = 90.0 - zenith

    # Cosine of solar zenith angle (thermofeel convention: instantaneous)
    cossza = math.cos(math.radians(zenith))
    cossza = max(-1.0, min(1.0, cossza))

    # --- Direct solar radiation perpendicular to beam (thermofeel convention) ---
    # dsrp = fdir / cossza where cossza > threshold, else dsrp = fdir
    dsrp = fdir / cossza if cossza > DSRP_COSZ_THRESHOLD else fdir

    nighttime = elevation < 0.0
    low_sun = elevation < 2.0  # below ~2 degrees

    # --- Surface projection factor (Equation 15, thermofeel convention) ---
    # gamma = elevation angle (thermofeel uses arcsin(cossza) = elevation)
    if nighttime:
        f_p = 0.0
    else:
        gamma = elevation  # thermofeel convention: elevation, not zenith
        f_p = 0.308 * math.cos(math.radians(gamma * (0.998 - gamma**2 / 50000.0)))

    # --- MRT equation (thermofeel-consistent, Equation 14) ---
    # rf = 0.5*strd + 0.5*L_up + (alpha_ir/epsilon_p)*(0.5*S_diff + 0.5*S_up + fp*dsrp)
    alpha_ratio = ALPHA_IR / EPSILON_P
    radiant_flux = (
        F_A * strd
        + F_A * L_srf_up
        + alpha_ratio * (F_A * S_srf_dn_diffuse + F_A * S_srf_up + f_p * dsrp)
    )

    # Quality flag
    if nighttime:
        qf = QualityFlag.NIGHTTIME
    elif low_sun:
        qf = QualityFlag.LOW_SOLAR_ELEVATION
    elif radiant_flux < 0:
        qf = QualityFlag.NEGATIVE_RADIATION
    else:
        qf = QualityFlag.VALID

    # Numerical safety: ensure non-negative before fourth root
    if radiant_flux < 0:
        mrt_kelvin = (abs(radiant_flux) / SIGMA) ** 0.25
    else:
        mrt_kelvin = (radiant_flux / SIGMA) ** 0.25

    # Sanity check: MRT should be roughly within 150-350 K
    if mrt_kelvin < 150.0 or mrt_kelvin > 400.0:
        qf = QualityFlag.MRT_UNPHYSICAL

    mrt_celsius = mrt_kelvin - 273.15

    return MRTResult(
        mrt_kelvin=mrt_kelvin,
        mrt_celsius=mrt_celsius,
        quality_flag=qf,
        solar_zenith_deg=zenith,
        solar_elevation_deg=elevation,
        cossza=cossza,
        dsrp=dsrp,
        f_p=f_p,
        direct_radiation_projected=f_p * dsrp,
        diffuse_shortwave=S_srf_dn_diffuse,
        upward_longwave=L_srf_up,
        upward_shortwave=S_srf_up,
    )


def calculate_mrt_grid(
    ssrd: NDArray[np.float64],  # (time, lat, lon) in W/m2
    strd: NDArray[np.float64],
    fdir: NDArray[np.float64],
    ssr: NDArray[np.float64],
    str_net: NDArray[np.float64],
    times: NDArray[np.datetime64],
    latitudes: NDArray[np.float64],
    longitudes: NDArray[np.float64],
    accumulation_seconds: float,
) -> MRTGridResult:
    """Calculate MRT for a full grid using thermofeel-consistent method.

    Production method: ECMWF_THERMOFEEL_COMPATIBLE_V1

    Parameters
    ----------
    ssrd, strd, fdir, ssr, str_net : NDArray
        Radiation arrays, shape (n_time, n_lat, n_lon) in W/m2.
    times : NDArray
        UTC timestamps, shape (n_time,).
    latitudes : NDArray
        Latitudes in degrees, shape (n_lat,).
    longitudes : NDArray
        Longitudes in degrees, shape (n_lon,).
    accumulation_seconds : float
        Accumulation period in seconds.

    Returns
    -------
    MRTGridResult
        Full grid MRT results.
    """
    n_time, n_lat, n_lon = ssrd.shape

    mrt_kelvin = np.full((n_time, n_lat, n_lon), np.nan)
    mrt_celsius = np.full((n_time, n_lat, n_lon), np.nan)
    quality_flags = np.full((n_time, n_lat, n_lon), -1, dtype=np.int32)
    solar_zenith = np.full((n_time, n_lat, n_lon), np.nan)
    solar_elevation = np.full((n_time, n_lat, n_lon), np.nan)
    cossza_grid = np.full((n_time, n_lat, n_lon), np.nan)
    dsrp_grid = np.full((n_time, n_lat, n_lon), np.nan)
    fp_grid = np.full((n_time, n_lat, n_lon), np.nan)
    fp_dsrp_grid = np.full((n_time, n_lat, n_lon), np.nan)
    diffuse_grid = np.full((n_time, n_lat, n_lon), np.nan)
    L_up_grid = np.full((n_time, n_lat, n_lon), np.nan)
    S_up_grid = np.full((n_time, n_lat, n_lon), np.nan)

    for ti in range(n_time):
        for la in range(n_lat):
            for lo in range(n_lon):
                result = calculate_mrt_single(
                    ssrd=ssrd[ti, la, lo],
                    strd=strd[ti, la, lo],
                    fdir=fdir[ti, la, lo],
                    ssr=ssr[ti, la, lo],
                    str_val=str_net[ti, la, lo],
                    latitude_deg=latitudes[la],
                    longitude_deg=longitudes[lo],
                    time_utc=times[ti],
                    accumulation_seconds=accumulation_seconds,
                )
                mrt_kelvin[ti, la, lo] = result.mrt_kelvin
                mrt_celsius[ti, la, lo] = result.mrt_celsius
                quality_flags[ti, la, lo] = result.quality_flag.value
                solar_zenith[ti, la, lo] = result.solar_zenith_deg
                solar_elevation[ti, la, lo] = result.solar_elevation_deg
                cossza_grid[ti, la, lo] = result.cossza
                dsrp_grid[ti, la, lo] = result.dsrp
                fp_grid[ti, la, lo] = result.f_p
                fp_dsrp_grid[ti, la, lo] = result.direct_radiation_projected
                diffuse_grid[ti, la, lo] = result.diffuse_shortwave
                L_up_grid[ti, la, lo] = result.upward_longwave
                S_up_grid[ti, la, lo] = result.upward_shortwave

    return MRTGridResult(
        mrt_kelvin=mrt_kelvin,
        mrt_celsius=mrt_celsius,
        quality_flags=quality_flags,
        solar_zenith_deg=solar_zenith,
        solar_elevation_deg=solar_elevation,
        cossza=cossza_grid,
        dsrp=dsrp_grid,
        f_p=fp_grid,
        direct_radiation_projected=fp_dsrp_grid,
        diffuse_shortwave=diffuse_grid,
        upward_longwave=L_up_grid,
        upward_shortwave=S_up_grid,
        times=times,
        latitudes=latitudes,
        longitudes=longitudes,
    )


def validate_mrt(
    mrt_ours: NDArray[np.float64],
    mrt_reference: NDArray[np.float64],
    quality_flags: NDArray[np.int32],
    solar_elevations: NDArray[np.float64] | None = None,
) -> dict:
    """Calculate validation metrics between our MRT and reference.

    Parameters
    ----------
    mrt_ours : NDArray
        Our computed MRT in Kelvin, shape (n,).
    mrt_reference : NDArray
        ERA5-HEAT MRT in Kelvin, shape (n,).
    quality_flags : NDArray
        Quality flags, shape (n,).

    Returns
    -------
    dict
        Validation metrics.
    """
    # Filter to valid (non-NaN) pairs
    valid = ~np.isnan(mrt_ours) & ~np.isnan(mrt_reference)
    o = mrt_ours[valid]
    r = mrt_reference[valid]
    n = len(o)

    if n == 0:
        return {"sample_count": 0, "status": "NO_VALID_SAMPLES"}

    error = o - r  # delta_MRT
    abs_error = np.abs(error)

    # R-squared
    ss_res = np.sum(error**2)
    ss_tot = np.sum((r - np.mean(r))**2)
    r_squared = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")

    # Correlation
    corr = np.corrcoef(o, r)[0, 1] if n > 1 else float("nan")

    metrics = {
        "sample_count": int(n),
        "mae": float(np.mean(abs_error)),
        "rmse": float(np.sqrt(np.mean(error**2))),
        "mean_bias": float(np.mean(error)),
        "median_ae": float(np.median(abs_error)),
        "std_error": float(np.std(error)),
        "min_error": float(np.min(error)),
        "max_error": float(np.max(error)),
        "p95_ae": float(np.percentile(abs_error, 95)),
        "r_squared": float(r_squared),
        "correlation": float(corr),
        "delta_mrt_mean": float(np.mean(error)),
        "delta_mrt_std": float(np.std(error)),
    }

    # Stratified by quality flag
    for qf_name, qf_val in [
        ("nighttime", QualityFlag.NIGHTTIME.value),
        ("valid", QualityFlag.VALID.value),
    ]:
        mask = quality_flags[valid] == qf_val
        if np.sum(mask) > 0:
            e = error[mask]
            ae = abs_error[mask]
            metrics[f"{qf_name}_count"] = int(np.sum(mask))
            metrics[f"{qf_name}_mae"] = float(np.mean(ae))
            metrics[f"{qf_name}_bias"] = float(np.mean(e))
            metrics[f"{qf_name}_rmse"] = float(np.sqrt(np.mean(e**2)))

    # Stratified by solar elevation
    if solar_elevations is not None:
        sel = solar_elevations[valid]
        for label, lo, hi in [("low_sun", -90, 5), ("mid_sun", 5, 45), ("high_sun", 45, 90)]:
            mask = (sel >= lo) & (sel < hi)
            if np.sum(mask) > 0:
                e = error[mask]
                ae = abs_error[mask]
                metrics[f"{label}_count"] = int(np.sum(mask))
                metrics[f"{label}_mae"] = float(np.mean(ae))
                metrics[f"{label}_bias"] = float(np.mean(e))

    return metrics
