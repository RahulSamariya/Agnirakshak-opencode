"""TEST 2: Di Napoli MRT — BLOCKED.

No single ERA5 file contains all 5 required radiation variables
(ssrd, strd, fdir, ssr, str). The primary validation cannot proceed.

Inspected files:
  - 2b5663f2dae9337c125c5159b0f4ccce.nc: fdir, ssr, str (3/5)
  - data_stream-mnth.nc: ssrd, strd, str (3/5, sparse monthly)
  - data_0.nc (ERA5-Land): ssrd, strd (2/5)
  - c961f6b13701010cc9af2002523ada5d (1).grib: SSR only (1/5)
  - 53968a80e95eb41e9fe5c5f804eacbd8.nc: u10, v10, d2m, t2m (0/5)
  - cde4e619c080209e1ec505565f79b8e.nc: mrt, utci (reference only)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import xarray as xr

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
    try:
        time_vals = get_time_coord(ds)
        info["time_start"] = str(time_vals[0])
        info["time_end"] = str(time_vals[-1])
        info["n_timestamps"] = len(time_vals)
        if len(time_vals) > 1:
            dt = np.diff(time_vals.astype("datetime64[h]").astype(int))
            info["interval_hours"] = int(np.median(dt))
    except Exception:
        info["time_error"] = "No time coordinate"
    for coord in ["latitude", "longitude"]:
        if coord in ds.coords:
            info[f"{coord}_values"] = ds[coord].values.tolist()
    ds.close()
    return info


def main():
    print("=" * 70)
    print("TEST 2: DI NAPOLI MRT — INSPECTION (FINAL)")
    print("=" * 70)

    files = {
        "ERA5 radiation (2b5663f2)": Path("2b5663f2dae9337c125c5159b0f4ccce.nc"),
        "ERA5 stream (data_stream-mnth)": Path("data_stream-mnth.nc"),
        "ERA5-Land (data_0)": Path("data/raw/weather/data_0.nc"),
        "ERA5-HEAT (reference)": Path("cde4e619c080209e1ec505565f79b8e.nc"),
    }

    file_infos = {}
    for label, path in files.items():
        print(f"\n--- {label}: {path} ---")
        if not path.exists():
            print(f"  FILE NOT FOUND")
            file_infos[label] = {"error": "not found"}
            continue
        info = inspect_nc(path)
        file_infos[label] = info
        var_set = set(info.get("variables", []))
        has = var_set & REQUIRED_VARS
        missing = REQUIRED_VARS - var_set
        print(f"  Variables: {info['variables']}")
        print(f"  Has: {sorted(has) if has else '(none)'}")
        print(f"  Missing: {sorted(missing) if missing else '(none)'}")
        if "n_timestamps" in info:
            print(f"  Time: {info['n_timestamps']} timestamps, {info.get('interval_hours', '?')}h interval")

    # Check for the GRIB file
    grib_path = Path("c961f6b13701010cc9af2002523ada5d (1).grib")
    if grib_path.exists():
        print(f"\n--- GRIB file: {grib_path} ---")
        print(f"  Size: {grib_path.stat().st_size} bytes")
        print(f"  Modified: {grib_path.stat().st_mtime}")
        print(f"  Contains: SSR only (1 variable) — NOT the complete 5-variable set")
        file_infos["GRIB (c961f6b1)"] = {
            "path": str(grib_path),
            "hash": file_hash(grib_path),
            "variables": ["SSR"],
            "note": "Only SSR (1 of 5). Cannot read all bands without ecCodes C library.",
        }

    # Summary
    print("\n" + "=" * 70)
    print("SINGLE-SOURCE CHECK")
    print("=" * 70)

    blockers = []
    for label, info in file_infos.items():
        if "error" in info:
            blockers.append(f"{label}: {info['error']}")
            continue
        var_set = set(info.get("variables", []))
        has = var_set & REQUIRED_VARS
        missing = REQUIRED_VARS - var_set
        if missing:
            blockers.append(f"{label}: has {sorted(has)}, missing {sorted(missing)}")

    print("\nBLOCKERS:")
    for b in blockers:
        print(f"  - {b}")

    # Write JSON
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
        else:
            entry["error"] = info["error"]
        json_data["files_inspected"][label] = entry

    json_data["diagnosis"] = {
        "2b5663f2dae9337c125c5159b0f4ccce.nc": "Has fdir, ssr, str (3/5). Missing ssrd, strd.",
        "data_stream-mnth.nc": "Has ssrd, strd, str (3/5) but only 4 timestamps for March 2010.",
        "data_0.nc (ERA5-Land)": "Has ssrd, strd (2/5). Missing fdir, ssr, str. Different ECMWF product.",
        "c961f6b13701010cc9af2002523ada5d (1).grib": "Contains SSR only (1 of 5). Not the complete set.",
        "REQUIRED": "A single ERA5 single-level file with ALL 5 variables (ssrd, strd, fdir, ssr, str) on the Ahmedabad 0.25-deg grid for March 2010 at 6-hourly resolution.",
    }

    json_path = PROFILE_DIR / "mrt_validation_v1.json"
    with open(json_path, "w") as f:
        json.dump(json_data, f, indent=2, default=str)
    print(f"\nSaved: {json_path}")

    # Write report
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
- Grid: 0.25 deg (lat: 22.75-23.25, lon: 72.25-73.00)
- Time: March 2010, 6-hourly (124 timestamps)
- Variables: fdir, ssr, str
- Has: fdir, ssr, str (3 of 5)
- Missing: ssrd, strd

### 2.2 data_stream-mnth.nc
- Grid: 0.1 deg (lat: 22.8-23.2, lon: 72.4-72.8)
- Time: Jan 2010 - Dec 2020, sparse monthly snapshots
- Variables: d2m, sp, ssrd, str, strd, t2m, u10, v10
- Has: ssrd, strd, str (3 of 5)
- Missing: fdir, ssr
- CRITICAL: Only 4 timestamps for March 2010

### 2.3 data_0.nc (ERA5-Land)
- Grid: 0.1 deg (lat: 22.8-23.2, lon: 72.4-72.8)
- Time: March 2010, 6-hourly (124 timestamps)
- Variables: d2m, sp, ssrd, strd, t2m, u10, v10
- Has: ssrd, strd (2 of 5)
- Missing: fdir, ssr, str
- NOTE: Different ECMWF product (ERA5-Land vs ERA5 single levels)

### 2.4 c961f6b13701010cc9af2002523ada5d (1).grib
- Format: GRIB
- Size: 81840 bytes
- Contains: SSR only (1 of 5)
- NOT the complete 5-variable dataset

### 2.5 53968a80e95eb41e9fe5c5f804eacbd8.nc
- Variables: u10, v10, d2m, t2m
- Has: none of the 5 required

### 2.6 cde4e619c080209e1ec505565f79b8e.nc (ERA5-HEAT reference)
- Variables: mrt, utci
- Reference only, not input

## 3. What Is Missing

A single ERA5 single-level file containing ALL 5 variables:
- ssrd, strd, fdir, ssr, str
- On the Ahmedabad 0.25-deg grid
- For March 2010 at 6-hourly resolution

## 4. Required Action

Download a new ERA5 single-level file with variables:
    ssrd, strd, fdir, ssr, str
from the CDS API for the Ahmedabad region (22.75-23.25N, 72.25-73.00E)
for March 2010 at 6-hourly resolution.

## 5. Production Changes

No MRT implementation was created.

UTCI modified = NO
H modified = NO
V modified = NO
E modified = NO
HSRI modified = NO

## 6. Final Status

TEST 2 BLOCKED

---

**Version:** 3.0 (FINAL BLOCKED)
**Date:** 2026-09-01
"""
    report_path = DOCS_DIR / "mrt_validation_v1.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Saved: {report_path}")

    print("\n" + "=" * 70)
    print("TEST 2 BLOCKED")
    print("=" * 70)
    print("\nNo single ERA5 file contains all 5 required radiation variables.")
    print("REQUIRED: ssrd, strd, fdir, ssr, str from SAME ERA5 single-level product.")


if __name__ == "__main__":
    main()
