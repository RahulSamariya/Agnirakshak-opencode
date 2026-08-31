"""TEST 2: Di Napoli MRT — BLOCKED.

No single ERA5 file contains all 5 required radiation variables
(ssrd, strd, fdir, ssr, str). The primary validation cannot proceed.

This script inspects all available NetCDF files and documents exactly
what is present and what is missing.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import xarray as xr

# =============================================================================
# FILE PATHS
# =============================================================================
ERA5LAND_PATH = Path("data/raw/weather/data_0.nc")
RADIATION_PATH = Path("2b5663f2dae9337c125c5159b0f4ccce.nc")
STREAM_PATH = Path("data_stream-mnth.nc")
ERA5HEAT_PATH = Path("cde4e619c080209e1ec505565f79b8e.nc")
PROFILE_DIR = Path("data/profiles")
DOCS_DIR = Path("docs/data")

REQUIRED_VARS = {"ssrd", "strd", "fdir", "ssr", "str"}


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def get_time_coord(ds: xr.Dataset) -> np.ndarray:
    if "valid_time" in ds.coords:
        return ds.valid_time.values
    if "time" in ds.coords:
        return ds.time.values
    raise ValueError("No time coordinate found")


def inspect_nc(path: Path) -> dict:
    """Inspect a NetCDF file and return metadata."""
    ds = xr.open_dataset(path)
    info = {
        "path": str(path),
        "hash": file_hash(path),
        "variables": sorted(ds.data_vars),
        "dims": dict(ds.sizes),
    }

    # Time
    try:
        time_vals = get_time_coord(ds)
        info["time_start"] = str(time_vals[0])
        info["time_end"] = str(time_vals[-1])
        info["n_timestamps"] = len(time_vals)

        if len(time_vals) > 1:
            import numpy as np
            dt = np.diff(time_vals.astype("datetime64[h]").astype(int))
            info["interval_hours"] = int(np.median(dt))
    except Exception:
        info["time_error"] = "No time coordinate"

    # Spatial
    for coord in ["latitude", "longitude", "lat", "lon"]:
        if coord in ds.coords:
            vals = ds[coord].values
            info[f"{coord}_values"] = vals.tolist()

    # Variable details
    var_details = {}
    for var in ds.data_vars:
        a = ds[var].attrs
        var_details[var] = {
            "units": a.get("units", "unknown"),
            "long_name": a.get("long_name", "unknown"),
            "stepType": a.get("stepType", "unknown"),
        }
    info["var_details"] = var_details

    ds.close()
    return info


def main():
    print("=" * 70)
    print("TEST 2: DI NAPOLI MRT — INSPECTION")
    print("=" * 70)

    # Inspect all files
    files_to_inspect = [
        ("ERA5-Land", ERA5LAND_PATH),
        ("ERA5 radiation", RADIATION_PATH),
        ("ERA5 stream", STREAM_PATH),
        ("ERA5-HEAT", ERA5HEAT_PATH),
    ]

    file_infos = {}
    for label, path in files_to_inspect:
        print(f"\n--- {label}: {path} ---")
        if not path.exists():
            print(f"  FILE NOT FOUND")
            file_infos[label] = {"error": "not found"}
            continue

        info = inspect_nc(path)
        file_infos[label] = info
        print(f"  Variables: {info['variables']}")
        print(f"  Dims: {info['dims']}")
        if "time_start" in info:
            print(f"  Time: {info['time_start']} to {info['time_end']} ({info['n_timestamps']} steps)")
        if "latitude_values" in info:
            print(f"  Lat: {info['latitude_values']}")
        if "longitude_values" in info:
            print(f"  Lon: {info['longitude_values']}")
        if "interval_hours" in info:
            print(f"  Interval: {info['interval_hours']} hours")

        # Check required vars
        var_set = set(info.get("variables", []))
        has = var_set & REQUIRED_VARS
        missing = REQUIRED_VARS - var_set
        print(f"  Has:     {sorted(has) if has else '(none)'}")
        print(f"  Missing: {sorted(missing) if missing else '(none)'}")

    # =========================================================================
    # DETERMINE IF SINGLE-SOURCE DATASET EXISTS
    # =========================================================================
    print("\n" + "=" * 70)
    print("SINGLE-SOURCE CHECK")
    print("=" * 70)

    single_source_found = False
    blockers = []

    # Check each file for ALL 5 variables
    for label, info in file_infos.items():
        if "error" in info:
            blockers.append(f"{label}: {info['error']}")
            continue

        var_set = set(info.get("variables", []))
        has = var_set & REQUIRED_VARS
        missing = REQUIRED_VARS - var_set

        if missing:
            blockers.append(f"{label}: has {sorted(has)}, missing {sorted(missing)}")
        else:
            # Has all 5! Check temporal coverage
            if info.get("n_timestamps", 0) < 124:
                blockers.append(f"{label}: has all 5 vars but only {info.get('n_timestamps', 0)} timestamps (need 124 for March 2010)")
            else:
                print(f"  >>> {label}: ALL 5 VARIABLES PRESENT WITH ADEQUATE COVERAGE <<<")
                single_source_found = True

    if not single_source_found:
        print("\n  NO single-source dataset found with all 5 variables.")
        print("\n  BLOCKERS:")
        for b in blockers:
            print(f"    - {b}")

    # =========================================================================
    # WRITE JSON
    # =========================================================================
    print("\n--- Writing JSON ---")
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)

    json_data = {
        "test_id": "TEST_2_DI_NAPOLI_MRT_VALIDATION",
        "status": "BLOCKED",
        "blocker": "No single ERA5 file contains all 5 required radiation variables (ssrd, strd, fdir, ssr, str)",
        "required_variables": sorted(REQUIRED_VARS),
        "files_inspected": {},
    }

    for label, info in file_infos.items():
        entry = {"variables": info.get("variables", [])}
        if "error" not in info:
            var_set = set(info.get("variables", []))
            entry["has_required"] = sorted(var_set & REQUIRED_VARS)
            entry["missing_required"] = sorted(REQUIRED_VARS - var_set)
            entry["n_timestamps"] = info.get("n_timestamps")
            entry["interval_hours"] = info.get("interval_hours")
        else:
            entry["error"] = info["error"]
        json_data["files_inspected"][label] = entry

    json_data["diagnosis"] = {
        "2b5663f2dae9337c125c5159b0f4ccce.nc": "Has fdir, ssr, str (3 of 5). Missing ssrd, strd.",
        "data_stream-mnth.nc": "Has ssrd, strd, str (3 of 5) but only 4 timestamps for March 2010. Sparse monthly product, NOT 6-hourly.",
        "data_0.nc (ERA5-Land)": "Has ssrd, strd (2 of 5). Missing fdir, ssr, str. Different ECMWF product.",
        "REQUIRED": "A single ERA5 single-level file with ALL 5 variables (ssrd, strd, fdir, ssr, str) on the Ahmedabad 0.25-deg grid for March 2010 at 6-hourly resolution.",
    }

    json_path = PROFILE_DIR / "mrt_validation_v1.json"
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"  Saved: {json_path}")

    # =========================================================================
    # WRITE REPORT
    # =========================================================================
    print("\n--- Writing report ---")
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    report = """# MRT VALIDATION REPORT -- TEST 2

## Status: BLOCKED

No single ERA5 file contains all 5 required radiation variables.
The primary MRT validation cannot proceed.

## 1. Required Variables

The Di Napoli et al. (2020) method requires 5 radiation components
from the SAME ERA5 single-level product:

| Variable | Description |
|----------|-------------|
| ssrd | Surface short-wave radiation downwards |
| strd | Surface long-wave radiation downwards |
| fdir | Surface direct short-wave radiation |
| ssr | Surface net short-wave radiation |
| str | Surface net long-wave radiation |

## 2. Files Inspected

### 2.1 2b5663f2dae9337c125c5159b0f4ccce.nc

- **Source:** ERA5 single levels
- **Grid:** 0.25 deg (lat: 22.75-23.25, lon: 72.25-73.00)
- **Time:** March 2010, 6-hourly (124 timestamps)
- **Variables:** fdir, ssr, str
- **Has:** fdir, ssr, str (3 of 5)
- **Missing:** ssrd, strd

### 2.2 data_stream-mnth.nc

- **Source:** ERA5 (stream=monthly)
- **Grid:** 0.1 deg (lat: 22.8-23.2, lon: 72.4-72.8)
- **Time:** Jan 2010 - Dec 2020, sparse monthly snapshots
- **Variables:** d2m, sp, ssrd, str, strd, t2m, u10, v10
- **Has:** ssrd, strd, str (3 of 5)
- **Missing:** fdir, ssr
- **CRITICAL:** Only 4 timestamps for March 2010. This is a sparse
  monthly product with ~4 consecutive 6-hourly snapshots per month.
  NOT suitable for full-period 6-hourly MRT validation.

### 2.3 data_0.nc (ERA5-Land)

- **Source:** ERA5-Land
- **Grid:** 0.1 deg (lat: 22.8-23.2, lon: 72.4-72.8)
- **Time:** March 2010, 6-hourly (124 timestamps)
- **Variables:** d2m, sp, ssrd, strd, t2m, u10, v10
- **Has:** ssrd, strd (2 of 5)
- **Missing:** fdir, ssr, str
- **NOTE:** Different ECMWF product (ERA5-Land vs ERA5 single levels).
  Mixing with ERA5 radiation produces physically inconsistent values.

## 3. What Is Missing

**A single ERA5 single-level file containing ALL 5 variables:**
- ssrd, strd, fdir, ssr, str
- On the Ahmedabad 0.25-deg grid
- For March 2010 at 6-hourly resolution

## 4. Why This Matters

The Di Napoli method computes MRT from 5 radiation components that
must be physically consistent. Using variables from different ECMWF
products (e.g., ERA5-Land + ERA5 single levels) produces impossible
values (e.g., 95.8% implied albedo).

## 5. Required Action

Download a new ERA5 single-level file with variables:
    ssrd, strd, fdir, ssr, str
from the CDS API for the Ahmedabad region (22.75-23.25N, 72.25-73.00E)
for March 2010 at 6-hourly resolution.

## 6. Production Changes

No MRT implementation was created.

UTCI modified = NO
H modified = NO
V modified = NO
E modified = NO
HSRI modified = NO

## 7. Final Status

TEST 2 BLOCKED

---

**Version:** 2.0 (BLOCKED)
**Date:** 2026-09-01
"""

    report_path = DOCS_DIR / "mrt_validation_v1.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Saved: {report_path}")

    # =========================================================================
    # SUMMARY
    # =========================================================================
    print("\n" + "=" * 70)
    print("TEST 2 BLOCKED")
    print("=" * 70)
    print("\nNo single ERA5 file contains all 5 required radiation variables.")
    print("Required: ssrd, strd, fdir, ssr, str from SAME ERA5 single-level product.")
    print("\nAvailable:")
    print("  2b5663f2dae9337c125c5159b0f4ccce.nc: fdir, ssr, str (3/5) — missing ssrd, strd")
    print("  data_stream-mnth.nc:                 ssrd, strd, str (3/5) — missing fdir, ssr, only 4 timestamps")
    print("  data_0.nc (ERA5-Land):               ssrd, strd (2/5) — missing fdir, ssr, str")
    print("\nREQUIRED: A new ERA5 single-level download with all 5 variables.")


if __name__ == "__main__":
    main()
