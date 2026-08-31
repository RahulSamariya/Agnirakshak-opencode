# MRT VALIDATION REPORT -- TEST 2

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
