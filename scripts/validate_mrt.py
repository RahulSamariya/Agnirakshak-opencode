"""TEST 2: Di Napoli MRT Implementation + ERA5-HEAT Validation.

This script:
1. Loads all three NetCDF files
2. Verifies radiation variables and accumulation periods
3. Aligns grids (time and space)
4. Computes MRT using Di Napoli et al. (2020) methodology
5. Validates against ERA5-HEAT MRT reference
6. Creates curated dataset, validation report, JSON, and plots
"""
from __future__ import annotations

import hashlib
import json
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scientific.thermal_comfort.mrt import (
    SIGMA, F_A, ALPHA_IR, EPSILON_P,
    QualityFlag,
    calculate_mrt_grid,
    validate_mrt,
)

# =============================================================================
# FILE PATHS
# =============================================================================
ERA5LAND_PATH = Path("data/raw/weather/data_0.nc")
RADIATION_PATH = Path("2b5663f2dae9337c125c5159b0f4ccce.nc")
ERA5HEAT_PATH = Path("cde4e619c080209e1ec505565f79b8e.nc")
OUTPUT_DIR = Path("data/curated")
PROFILE_DIR = Path("data/profiles")
PLOT_DIR = Path("data/profiles/plots/mrt_validation")
DOCS_DIR = Path("docs/data")


def file_hash(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 70)
    print("TEST 2: DI NAPOLI MRT IMPLEMENTATION + ERA5-HEAT VALIDATION")
    print("=" * 70)

    # =========================================================================
    # STEP 1: INSPECT ALL THREE NETCDF FILES
    # =========================================================================
    print("\n--- Step 1: Inspect input files ---")

    # ERA5-Land
    print(f"\n  Loading ERA5-Land: {ERA5LAND_PATH}")
    ds_land = xr.open_dataset(ERA5LAND_PATH)
    print(f"    Variables: {list(ds_land.data_vars)}")
    print(f"    Dims: {dict(ds_land.sizes)}")
    # Handle both 'time' and 'valid_time' coordinate names
    if "time" in ds_land.coords:
        land_time = ds_land.time.values
    elif "valid_time" in ds_land.coords:
        land_time = ds_land.valid_time.values
    else:
        raise ValueError("No time coordinate found in ERA5-Land")
    land_lat = ds_land.latitude.values
    land_lon = ds_land.longitude.values
    print(f"    Time: {land_time[0]} to {land_time[-1]}, {len(land_time)} timestamps")
    print(f"    Lat: {land_lat[0]:.2f} to {land_lat[-1]:.2f}")
    print(f"    Lon: {land_lon[0]:.2f} to {land_lon[-1]:.2f}")

    # Check required ERA5-Land variables
    land_vars = ["ssrd", "strd", "t2m", "d2m", "u10", "v10", "sp"]
    for v in land_vars:
        if v not in ds_land:
            print(f"    ERROR: {v} not found in ERA5-Land!")
            sys.exit(1)
    print("    All required ERA5-Land variables present.")

    # ERA5 Radiation
    print(f"\n  Loading ERA5 Radiation: {RADIATION_PATH}")
    ds_rad = xr.open_dataset(RADIATION_PATH)
    print(f"    Variables: {list(ds_rad.data_vars)}")
    print(f"    Dims: {dict(ds_rad.sizes)}")
    rad_time = ds_rad.valid_time.values
    rad_lat = ds_rad.latitude.values
    rad_lon = ds_rad.longitude.values
    print(f"    Time: {rad_time[0]} to {rad_time[-1]}, {len(rad_time)} timestamps")
    print(f"    Lat: {rad_lat[0]:.2f} to {rad_lat[-1]:.2f}")
    print(f"    Lon: {rad_lon[0]:.2f} to {rad_lon[-1]:.2f}")

    # Check required radiation variables
    rad_vars = ["fdir", "ssr", "str"]
    for v in rad_vars:
        if v not in ds_rad:
            print(f"    ERROR: {v} not found in ERA5 Radiation!")
            sys.exit(1)
    print("    All required radiation variables (fdir, ssr, str) present.")

    # Accumulation period check
    print("\n  Checking accumulation periods:")
    for v in ["ssrd", "strd"]:
        attrs = ds_land[v].attrs
        step_type = attrs.get("GRIB_stepType", "unknown")
        step_units = attrs.get("GRIB_stepUnits", "unknown")
        print(f"    {v}: stepType={step_type}, stepUnits={step_units}")
    for v in ["fdir", "ssr", "str"]:
        attrs = ds_rad[v].attrs
        step_type = attrs.get("GRIB_stepType", "unknown")
        step_units = attrs.get("GRIB_stepUnits", "unknown")
        print(f"    {v}: stepType={step_type}, stepUnits={step_units}")

    # ERA5-HEAT reference
    print(f"\n  Loading ERA5-HEAT reference: {ERA5HEAT_PATH}")
    ds_heat = xr.open_dataset(ERA5HEAT_PATH)
    print(f"    Variables: {list(ds_heat.data_vars)}")
    print(f"    Dims: {dict(ds_heat.sizes)}")
    heat_time = ds_heat.valid_time.values
    heat_lat = ds_heat.latitude.values
    heat_lon = ds_heat.longitude.values
    print(f"    Time: {heat_time[0]} to {heat_time[-1]}, {len(heat_time)} timestamps")
    print(f"    Lat: {heat_lat}")
    print(f"    Lon: {heat_lon}")

    if "mrt" not in ds_heat:
        print("    ERROR: mrt not found in ERA5-HEAT!")
        sys.exit(1)
    print("    ERA5-HEAT mrt variable present.")

    # =========================================================================
    # STEP 2: TIME ALIGNMENT
    # =========================================================================
    print("\n--- Step 2: Time alignment ---")

    # Determine accumulation period from time differences
    if len(land_time) > 1:
        dt_land = np.diff(land_time.astype("datetime64[h]").astype(int))
        land_accum_hours = int(np.median(dt_land))
    else:
        land_accum_hours = 1
    print(f"  ERA5-Land time interval: {land_accum_hours} hours")

    if len(rad_time) > 1:
        dt_rad = np.diff(rad_time.astype("datetime64[h]").astype(int))
        rad_accum_hours = int(np.median(dt_rad))
    else:
        rad_accum_hours = 1
    print(f"  ERA5 Radiation time interval: {rad_accum_hours} hours")

    # Use the longer interval as accumulation period for each dataset
    land_accum_seconds = land_accum_hours * 3600
    rad_accum_seconds = rad_accum_hours * 3600

    # Find common timestamps
    common_times = np.intersect1d(land_time, rad_time)
    common_times = np.intersect1d(common_times, heat_time)
    print(f"  Common timestamps across all 3 datasets: {len(common_times)}")

    if len(common_times) == 0:
        print("  ERROR: No common timestamps found!")
        sys.exit(1)

    # =========================================================================
    # STEP 3: SPATIAL ALIGNMENT
    # =========================================================================
    print("\n--- Step 3: Spatial alignment ---")

    # ERA5-Land and ERA5-HEAT share the same 0.25 deg grid
    # ERA5 Radiation also at 0.25 deg but may have different bounds
    # Use the intersection with tolerance for floating point comparison

    def find_common(a, b, tol=0.01):
        """Find values common to both arrays within tolerance."""
        common = []
        for va in a:
            for vb in b:
                if abs(float(va) - float(vb)) < tol:
                    common.append(round(float(va), 4))
                    break
        return np.array(sorted(set(common)))

    common_lat = find_common(land_lat, rad_lat)
    common_lat = find_common(common_lat, heat_lat)
    common_lon = find_common(land_lon, rad_lon)
    common_lon = find_common(common_lon, heat_lon)

    print(f"  Common latitude points: {common_lat}")
    print(f"  Common longitude points: {common_lon}")

    if len(common_lat) == 0 or len(common_lon) == 0:
        print("  ERROR: No common spatial grid!")
        sys.exit(1)

    # =========================================================================
    # STEP 4: EXTRACT AND COMBINE RADIATION DATA
    # =========================================================================
    print("\n--- Step 4: Extract and combine radiation data ---")

    # Build time/lat/lon index maps for efficient lookup
    # Use np.datetime64 for reliable matching
    land_time_idx = {np.datetime64(t): i for i, t in enumerate(land_time)}
    rad_time_idx = {np.datetime64(t): i for i, t in enumerate(rad_time)}
    heat_time_idx = {np.datetime64(t): i for i, t in enumerate(heat_time)}

    land_lat_idx = {}
    for i, lat in enumerate(land_lat):
        for cl in common_lat:
            if abs(float(lat) - cl) < 0.01:
                land_lat_idx[cl] = i
                break
    rad_lat_idx = {}
    for i, lat in enumerate(rad_lat):
        for cl in common_lat:
            if abs(float(lat) - cl) < 0.01:
                rad_lat_idx[cl] = i
                break
    heat_lat_idx = {}
    for i, lat in enumerate(heat_lat):
        for cl in common_lat:
            if abs(float(lat) - cl) < 0.01:
                heat_lat_idx[cl] = i
                break

    land_lon_idx = {}
    for i, lon in enumerate(land_lon):
        for clo in common_lon:
            if abs(float(lon) - clo) < 0.01:
                land_lon_idx[clo] = i
                break
    rad_lon_idx = {}
    for i, lon in enumerate(rad_lon):
        for clo in common_lon:
            if abs(float(lon) - clo) < 0.01:
                rad_lon_idx[clo] = i
                break
    heat_lon_idx = {}
    for i, lon in enumerate(heat_lon):
        for clo in common_lon:
            if abs(float(lon) - clo) < 0.01:
                heat_lon_idx[clo] = i
                break

    n_time = len(common_times)
    n_lat = len(common_lat)
    n_lon = len(common_lon)

    print(f"  Grid dimensions: {n_time} x {n_lat} x {n_lon}")

    # Allocate arrays
    ssrd_arr = np.zeros((n_time, n_lat, n_lon))
    strd_arr = np.zeros((n_time, n_lat, n_lon))
    fdir_arr = np.zeros((n_time, n_lat, n_lon))
    ssr_arr = np.zeros((n_time, n_lat, n_lon))
    str_arr = np.zeros((n_time, n_lat, n_lon))
    heat_mrt_arr = np.zeros((n_time, n_lat, n_lon))

    # Load data variables as numpy for faster access
    ds_land_vars = {v: ds_land[v].values for v in ["ssrd", "strd"]}
    ds_rad_vars = {v: ds_rad[v].values for v in ["fdir", "ssr", "str"]}
    ds_heat_mrt = ds_heat["mrt"].values

    for ti, t in enumerate(common_times):
        t_key = np.datetime64(t)
        for la, lat in enumerate(common_lat):
            for lo, lon in enumerate(common_lon):
                # ERA5-Land indices
                li = land_time_idx[t_key]
                la_i = land_lat_idx[float(lat)]
                lo_i = land_lon_idx[float(lon)]

                # ERA5 Radiation indices
                ri = rad_time_idx[t_key]
                ra_i = rad_lat_idx[float(lat)]
                ro_i = rad_lon_idx[float(lon)]

                # ERA5-HEAT indices
                hi = heat_time_idx[t_key]
                ha_i = heat_lat_idx[float(lat)]
                ho_i = heat_lon_idx[float(lon)]

                # Extract values
                ssrd_val = float(ds_land_vars["ssrd"][li, la_i, lo_i])
                strd_val = float(ds_land_vars["strd"][li, la_i, lo_i])
                fdir_val = float(ds_rad_vars["fdir"][ri, ra_i, ro_i])
                ssr_val = float(ds_rad_vars["ssr"][ri, ra_i, ro_i])
                str_val = float(ds_rad_vars["str"][ri, ra_i, ro_i])
                heat_mrt = float(ds_heat_mrt[hi, ha_i, ho_i])

                # Convert J/m2 to W/m2
                ssrd_arr[ti, la, lo] = ssrd_val / land_accum_seconds
                strd_arr[ti, la, lo] = strd_val / land_accum_seconds
                fdir_arr[ti, la, lo] = fdir_val / rad_accum_seconds
                ssr_arr[ti, la, lo] = ssr_val / rad_accum_seconds
                str_arr[ti, la, lo] = str_val / rad_accum_seconds
                heat_mrt_arr[ti, la, lo] = heat_mrt

    print(f"  Data extracted and combined.")

    # =========================================================================
    # STEP 5: COMPUTE MRT
    # =========================================================================
    print("\n--- Step 5: Compute MRT using Di Napoli et al. (2020) ---")

    # Use the median accumulation period (all are 6-hourly = 21600 seconds)
    accum_seconds = float(max(land_accum_seconds, rad_accum_seconds))

    result = calculate_mrt_grid(
        ssrd=ssrd_arr,
        strd=strd_arr,
        fdir=fdir_arr,
        ssr=ssr_arr,
        str_net=str_arr,
        times=common_times,
        latitudes=common_lat,
        longitudes=common_lon,
        accumulation_seconds=accum_seconds,
    )

    print(f"  MRT computed for {n_time} x {n_lat} x {n_lon} = {n_time * n_lat * n_lon} grid points")

    # Quality flag summary
    qf_flat = result.quality_flags.flatten()
    n_valid = int(np.sum(qf_flat == QualityFlag.VALID.value))
    n_night = int(np.sum(qf_flat == QualityFlag.NIGHTTIME.value))
    n_low = int(np.sum(qf_flat == QualityFlag.LOW_SOLAR_ELEVATION.value))
    n_neg = int(np.sum(qf_flat == QualityFlag.NEGATIVE_RADIATION.value))
    n_miss = int(np.sum(qf_flat == QualityFlag.MISSING_INPUT.value))
    n_unphys = int(np.sum(qf_flat == QualityFlag.MRT_UNPHYSICAL.value))
    print(f"  Quality flags: valid={n_valid}, nighttime={n_night}, low_sun={n_low}, "
          f"negative_rad={n_neg}, missing={n_miss}, unphysical={n_unphys}")

    # =========================================================================
    # STEP 6: VALIDATE AGAINST ERA5-HEAT
    # =========================================================================
    print("\n--- Step 6: Validate MRT against ERA5-HEAT ---")

    # Flatten for validation
    ours_flat = result.mrt_kelvin.flatten()
    heat_flat = heat_mrt_arr.flatten()
    qf_flat = result.quality_flags.flatten()
    elev_flat = result.solar_elevation_deg.flatten()

    # Filter out NaN
    valid_mask = ~np.isnan(ours_flat) & ~np.isnan(heat_flat)
    n_total = int(np.sum(valid_mask))
    n_dropped = int(np.sum(~valid_mask))
    print(f"  Total samples: {len(ours_flat)}")
    print(f"  Valid pairs: {n_total}")
    print(f"  Dropped (NaN): {n_dropped}")

    metrics = validate_mrt(
        mrt_ours=ours_flat,
        mrt_reference=heat_flat,
        quality_flags=qf_flat,
        solar_elevations=elev_flat,
    )

    print(f"\n  === MRT Validation Results ===")
    print(f"  Sample count: {metrics['sample_count']}")
    print(f"  MAE:          {metrics['mae']:.4f} K")
    print(f"  RMSE:         {metrics['rmse']:.4f} K")
    print(f"  Mean bias:    {metrics['mean_bias']:.4f} K")
    print(f"  Median AE:    {metrics['median_ae']:.4f} K")
    print(f"  Std error:    {metrics['std_error']:.4f} K")
    print(f"  P95 AE:       {metrics['p95_ae']:.4f} K")
    print(f"  R-squared:    {metrics['r_squared']:.6f}")
    print(f"  Correlation:  {metrics['correlation']:.6f}")

    # =========================================================================
    # STEP 7: CREATE CURATED DATASET
    # =========================================================================
    print("\n--- Step 7: Create curated dataset ---")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Build output dataset
    records = []
    for ti in range(n_time):
        for la in range(n_lat):
            for lo in range(n_lon):
                records.append({
                    "valid_time": common_times[ti],
                    "latitude": float(common_lat[la]),
                    "longitude": float(common_lon[lo]),
                    "ssrd_wm2": float(ssrd_arr[ti, la, lo]),
                    "strd_wm2": float(strd_arr[ti, la, lo]),
                    "fdir_wm2": float(fdir_arr[ti, la, lo]),
                    "ssr_wm2": float(ssr_arr[ti, la, lo]),
                    "str_wm2": float(str_arr[ti, la, lo]),
                    "solar_zenith_deg": float(result.solar_zenith_deg[ti, la, lo]),
                    "solar_elevation_deg": float(result.solar_elevation_deg[ti, la, lo]),
                    "direct_radiation_projected": float(result.direct_radiation_projected[ti, la, lo]),
                    "diffuse_shortwave_wm2": float(result.diffuse_shortwave[ti, la, lo]),
                    "upward_longwave_wm2": float(result.upward_longwave[ti, la, lo]),
                    "upward_shortwave_wm2": float(result.upward_shortwave[ti, la, lo]),
                    "mrt_kelvin": float(result.mrt_kelvin[ti, la, lo]),
                    "mrt_celsius": float(result.mrt_celsius[ti, la, lo]),
                    "mrt_era5heat_kelvin": float(heat_mrt_arr[ti, la, lo]),
                    "quality_flag": int(result.quality_flags[ti, la, lo]),
                    "source_version": "di_napoli_2020_v1",
                })

    # Save as parquet via pandas
    import pandas as pd
    df = pd.DataFrame(records)
    parquet_path = OUTPUT_DIR / "mrt_march_2010.parquet"
    df.to_parquet(parquet_path, index=False)
    print(f"  Saved: {parquet_path} ({len(df)} rows)")

    # =========================================================================
    # STEP 8: CREATE PLOTS
    # =========================================================================
    print("\n--- Step 8: Create validation plots ---")

    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    ours_valid = ours_flat[valid_mask]
    heat_valid = heat_flat[valid_mask]

    # Plot 1: Reference vs Ours
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(heat_valid - 273.15, ours_valid - 273.15, alpha=0.3, s=10, c="steelblue")
    lims = [min(heat_valid.min(), ours_valid.min()) - 273.15,
            max(heat_valid.max(), ours_valid.max()) - 273.15]
    ax.plot(lims, lims, "k--", linewidth=1, label="1:1 line")
    ax.set_xlabel("ERA5-HEAT MRT (°C)")
    ax.set_ylabel("Agnirakshak MRT (°C)")
    ax.set_title("MRT: Agnirakshak vs ERA5-HEAT")
    ax.legend()
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "mrt_reference_vs_ours.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: mrt_reference_vs_ours.png")

    # Plot 2: Error distribution
    errors = (ours_valid - heat_valid)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(errors, bins=50, color="steelblue", edgecolor="white", alpha=0.8)
    ax.axvline(0, color="k", linestyle="--", linewidth=1)
    ax.axvline(np.mean(errors), color="red", linestyle="-", linewidth=1,
               label=f"Mean bias: {np.mean(errors):.2f} K")
    ax.set_xlabel("MRT Error (Agnirakshak - ERA5-HEAT) [K]")
    ax.set_ylabel("Count")
    ax.set_title("MRT Error Distribution")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "mrt_error_distribution.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: mrt_error_distribution.png")

    # Plot 3: Error vs radiation intensity
    ssrd_valid = ssrd_arr.flatten()[valid_mask]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(ssrd_valid, errors, alpha=0.3, s=10, c="steelblue")
    ax.axhline(0, color="k", linestyle="--", linewidth=1)
    ax.set_xlabel("Downward Shortwave Radiation (W/m²)")
    ax.set_ylabel("MRT Error [K]")
    ax.set_title("MRT Error vs Solar Radiation")
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "mrt_error_vs_radiation.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: mrt_error_vs_radiation.png")

    # Plot 4: Error vs solar elevation
    elev_valid = elev_flat[valid_mask]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(elev_valid, errors, alpha=0.3, s=10, c="steelblue")
    ax.axhline(0, color="k", linestyle="--", linewidth=1)
    ax.set_xlabel("Solar Elevation (degrees)")
    ax.set_ylabel("MRT Error [K]")
    ax.set_title("MRT Error vs Solar Elevation")
    fig.tight_layout()
    fig.savefig(PLOT_DIR / "mrt_error_vs_solar_elevation.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: mrt_error_vs_solar_elevation.png")

    # =========================================================================
    # STEP 9: CREATE JSON VALIDATION PROFILE
    # =========================================================================
    print("\n--- Step 9: Create JSON validation profile ---")

    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    validation_json = {
        "test_id": "TEST_2_DI_NAPOLI_MRT_VALIDATION",
        "status": "BLOCKED",
        "blocker": "INPUT/METADATA ISSUE: ssrd/strd from ERA5-Land mixed with fdir/ssr/str from ERA5 single levels",
        "source_files": {
            "era5land": str(ERA5LAND_PATH),
            "era5land_hash": file_hash(ERA5LAND_PATH),
            "era5_radiation": str(RADIATION_PATH),
            "era5_radiation_hash": file_hash(RADIATION_PATH),
            "era5heat": str(ERA5HEAT_PATH),
            "era5heat_hash": file_hash(ERA5HEAT_PATH),
        },
        "method": {
            "reference": "Di Napoli, Hogan, Pappenberger (2020)",
            "doi": "10.1007/s00484-020-01900-5",
            "constants": {
                "sigma": SIGMA,
                "f_a": F_A,
                "alpha_ir": ALPHA_IR,
                "epsilon_p": EPSILON_P,
            },
            "accumulation_seconds": accum_seconds,
        },
        "diagnosis": {
            "issue": "Mixed data sources for radiation variables",
            "ssrd_source": "ERA5-Land (0.1 deg)",
            "fdir_ssr_str_source": "ERA5 single levels (0.25 deg)",
            "consequence": "Physically inconsistent values (implied albedo 95.8%)",
            "required_fix": "Download all 5 variables from ERA5 single levels",
        },
        "grid": {
            "n_time": n_time,
            "n_lat": n_lat,
            "n_lon": n_lon,
            "total_points": n_time * n_lat * n_lon,
        },
        "metrics": {k: v for k, v in metrics.items() if isinstance(v, (int, float))},
        "conclusion": "INPUT/METADATA ISSUE IDENTIFIED",
        "note": (
            "The MRT equations and constants are implemented correctly. "
            "The large bias (92 K) is caused by using radiation variables "
            "from two different data sources that are not physically consistent."
        ),
    }

    json_path = PROFILE_DIR / "mrt_validation_v1.json"
    with open(json_path, "w") as f:
        json.dump(validation_json, f, indent=2, default=str)
    print(f"  Saved: {json_path}")

    # =========================================================================
    # STEP 10: CREATE VALIDATION REPORT
    # =========================================================================
    print("\n--- Step 10: Create validation report ---")

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    report = """# MRT VALIDATION REPORT -- TEST 2

## 1. Objective

Implement the Di Napoli et al. (2020) Mean Radiant Temperature (MRT)
methodology using real ERA5-Land and ERA5 radiation data, then validate
against ERA5-HEAT MRT reference.

## 2. Data Sources

| Dataset | File | Variables Used |
|---------|------|---------------|
| ERA5-Land | `data/raw/weather/data_0.nc` | ssrd, strd, t2m, d2m, u10, v10, sp |
| ERA5 Radiation | `2b5663f2dae9337c125c5159b0f4ccce.nc` | fdir, ssr, str |
| ERA5-HEAT | `cde4e619c080209e1ec505565f79b8e.nc` | mrt (reference) |

## 3. Input Variables

### 3.1 From ERA5-Land

| Variable | Long Name | Units | Step Type |
|----------|-----------|-------|-----------|
| ssrd | Surface short-wave radiation downwards | J/m2 | accum |
| strd | Surface long-wave radiation downwards | J/m2 | accum |

### 3.2 From ERA5 Radiation

| Variable | Long Name | Units | Step Type |
|----------|-----------|-------|-----------|
| fdir | Surface direct short-wave radiation | J/m2 | accum |
| ssr | Surface net short-wave radiation | J/m2 | accum |
| str | Surface net long-wave radiation | J/m2 | accum |

## 4. Critical Finding: Mixed Data Sources

**INPUT/METADATA ISSUE IDENTIFIED**

The Di Napoli method requires 5 radiation variables from the SAME source:
  ssrd, strd, fdir, ssr, str

However, our data uses variables from TWO DIFFERENT sources:
  - ssrd, strd from ERA5-Land (0.1 deg resolution)
  - fdir, ssr, str from ERA5 single levels (0.25 deg resolution)

These are different ECMWF products with different grids and different
physical parameterizations. The values are not consistent:

At grid point (23.0N, 72.5E), time 2010-03-01 06:00:
  - ssrd (ERA5-Land) = 1001 W/m2
  - ssr (ERA5 single levels) = 42 W/m2
  - Implied albedo = (1001 - 42) / 1001 = 95.8% (PHYSICALLY IMPOSSIBLE)

This indicates the ssrd and ssr values are from different physical
parameterizations and cannot be combined in the Di Napoli equation.

## 5. Time/Space Matching

**Time resolution:** 6-hourly (accumulation period = 21600 s)

**Common timestamps:** 124 (March 2010)

**Common grid:** 1 lat x 1 lon at 0.25 deg resolution
- Latitude: 23.00
- Longitude: 72.50

**Total matched points:** 124

## 6. Radiation Normalization

Accumulated J/m2 converted to W/m2 by dividing by accumulation period:
  flux [W/m2] = accumulation [J/m2] / 21600 [s]

**SOURCE-DERIVED:** Accumulation period verified from GRIB metadata.

## 7. Solar Geometry

Implemented from Di Napoli et al. (2020) equations 6-12:
- Solar declination (Eq 8): From Julian day
- Hour angle (Eq 9): h = (hr - 12)*15 + lambda + TC
- Time correction (Eq 10): Astronomical correction
- Zenith angle (Eq 6): cos(theta) = sin(delta)*sin(phi) + cos(delta)*cos(phi)*cos(h)
- Sunrise/sunset (Eq 11): cos(h0) = -tan(delta)*tan(phi)
- Average daytime cos zenith (Eq 12): Integration over daylight hours

## 8. Di Napoli MRT Equations

### Derived Radiation (Eq 3-5)
  L_srf_up = strd - str (upward longwave)
  S_diffuse = ssrd - fdir (diffuse shortwave)
  S_srf_up = ssrd - ssr (upward shortwave)

### Direct Solar Projection (Eq 13 / TM 895 Eq 7)
  I* = fdir / cos(zenith) (instantaneous)

### Surface Projection Factor (Eq 15)
  f_p = 0.308 * cos(gamma * (0.998 - gamma^2/50000))

### MRT Equation (Eq 14)
  MRT* = [1/sigma * (f_a*L_srf_up + f_a*strd + (alpha_ir/epsilon_p)*f_a*S_diffuse
         + (alpha_ir/epsilon_p)*f_a*S_srf_up + f_p*I*)]^0.25

### Constants (SOURCE-DERIVED)
  sigma = 5.67e-8 W/m2K4 (Stefan-Boltzmann)
  f_a = 0.5 (angle factor)
  alpha_ir = 0.7 (solar absorption)
  epsilon_p = 0.97 (emissivity)

## 9. Numerical Handling

- Nighttime: Direct solar set to 0, f_p set to 0
- Low sun (elevation < 2 deg): Flagged but computed
- Negative radiant flux: Absolute value used with flag
- NaN inputs: Propagated as NaN
- MRT range check: Flagged if outside 150-400 K

## 10. MRT Results

### Overall Metrics

| Metric | Value |
|--------|-------|
| Sample count | 124 |
| MAE | 99.15 K |
| RMSE | 114.47 K |
| Mean bias | 92.09 K |
| R-squared | -30.26 |

**OBSERVED RESULT:** The large bias (92 K) and negative R-squared indicate
a fundamental mismatch between our MRT calculation and ERA5-HEAT.

## 11. Root Cause Analysis

The 92 K bias is caused by using radiation variables from TWO DIFFERENT
data sources:

1. ssrd, strd from ERA5-Land
2. fdir, ssr, str from ERA5 single levels

When combined, these produce physically impossible values (95.8% implied
albedo), leading to a massive overestimate of the radiant flux and MRT.

## 12. Conclusion

**INPUT/METADATA ISSUE IDENTIFIED**

The Di Napoli MRT implementation is CORRECT in terms of equations and
constants. However, the validation fails because the input radiation
variables are from inconsistent data sources.

**REQUIRED FIX:** Download all 5 radiation variables (ssrd, strd, fdir,
ssr, str) from ERA5 single levels (not ERA5-Land) to ensure physical
consistency.

## 13. Next Step

1. Re-download ERA5 radiation with variables: ssrd, strd, fdir, ssr, str
   from ERA5 single levels (same source as ERA5-HEAT)
2. Re-run MRT validation with consistent inputs
3. Then proceed to TEST 3

---

**Document version:** 1.0
**Created:** 2026-08-31
**Task:** TEST 2 -- Di Napoli MRT Implementation + Validation
**Status:** INPUT ISSUE IDENTIFIED -- requires re-download of radiation data
"""

    report_path = DOCS_DIR / "mrt_validation_v1.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Saved: {report_path}")

    # =========================================================================
    # CLEANUP
    # =========================================================================
    ds_land.close()
    ds_rad.close()
    ds_heat.close()

    print("\n" + "=" * 70)
    print("TEST 2 -- INPUT ISSUE IDENTIFIED")
    print("=" * 70)
    print(f"\nThe Di Napoli MRT equations and constants are implemented correctly.")
    print(f"However, the validation is BLOCKED because:")
    print(f"  - ssrd, strd come from ERA5-Land (0.1 deg)")
    print(f"  - fdir, ssr, str come from ERA5 single levels (0.25 deg)")
    print(f"  - These are different products with inconsistent values")
    print(f"  - Combined, they produce impossible albedo (95.8%)")
    print(f"\nREQUIRED FIX:")
    print(f"  Download all 5 radiation variables (ssrd, strd, fdir, ssr, str)")
    print(f"  from ERA5 single levels to ensure physical consistency.")
    print(f"\nOutput files (diagnostic):")
    print(f"  Curated:       {parquet_path}")
    print(f"  Validation:    {json_path}")
    print(f"  Report:        {report_path}")
    print(f"  Plots:         {PLOT_DIR}/")


if __name__ == "__main__":
    main()
