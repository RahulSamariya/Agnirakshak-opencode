# MRT VALIDATION REPORT -- TEST 2

## 1. Objective

Implement the Di Napoli et al. (2020) MRT methodology using single-source
ERA5 radiation data, then validate against ERA5-HEAT MRT reference.

## 2. Source Dataset

**ERA5 single-level radiation** (single source for ALL 5 variables):

| Variable | Long Name | Units |
|----------|-----------|-------|
| ssrd | Surface short-wave radiation downwards | J/m2 |
| strd | Surface long-wave radiation downwards | J/m2 |
| fdir | Surface direct short-wave radiation | J/m2 |
| ssr | Surface net short-wave radiation | J/m2 |
| str | Surface net long-wave radiation | J/m2 |

File: `97c99a12bac0f84dae69bd5460cde459.nc`
Hash: `ff22fd17747061c8...`
Grid: 0.25 deg (lat: [23.25 23.   22.75], lon: [72.25 72.5  72.75 73.  ])
Time: 2010-03-01T00:00:00.000000000 to 2010-03-31T18:00:00.000000000
Timestamps: 124
    Interval: 1 hour (3600 s)
    Accumulation: J/m2 -> W/m2 via flux = accumulation / 3600

## 3. Reference

ERA5-HEAT MRT (same 0.25 deg grid)
File: `cde4e619c080209e1ec505565f79b8e.nc`

## 4. Time Matching

Common timestamps: 124
All from March 2010 at 6-hourly resolution.

## 5. Spatial Matching

Radiation and ERA5-HEAT share the exact same 0.25 deg grid.
No interpolation required.

## 6. Solar Geometry

Implemented from Di Napoli et al. (2020) equations 6-12.

## 7. Di Napoli MRT Equations

- L_srf_up = strd - str
- S_diffuse = ssrd - fdir
- S_srf_up = ssrd - ssr
- I* = fdir / cos(zenith)
- f_p = 0.308 * cos(gamma * (0.998 - gamma^2/50000))
- MRT* = [1/sigma * (f_a*L_dn + f_a*L_up + (a/eps)*f_a*S_diff + (a/eps)*f_a*S_up + f_p*I*)]^0.25

## 8. Constants (SOURCE-DERIVED)

- sigma = 5.67e-8 W/m2K4
- f_a = 0.5
- alpha_ir = 0.7
- epsilon_p = 0.97

## 9. MRT Results

| Metric | Value |
|--------|-------|
| N | 1488 |
| MAE | 2.1823 K |
| RMSE | 3.4467 K |
| Mean bias | -1.5651 K |
| Median AE | 0.8655 K |
| P95 AE | 7.4981 K |
| R-squared | 0.971676 |
| Correlation | 0.989749 |

## 10. Stratified Results

| Bin | N | MAE | Bias |
|-----|---|-----|------|
| (-90, 0] deg | 744 | 0.57 | -0.02 |
| (10, 20] deg | 372 | 6.60 | -6.60 |
| (30, 90] deg | 372 | 0.98 | 0.39 |


## 11. Component Diagnostics

| Component | Mean | Std | Min | Max |
|-----------|------|-----|-----|-----|
| ssrd | 291.32 | 337.77 | 0.00 | 877.71 |
| ssr | 233.64 | 271.30 | 0.00 | 713.87 |
| fdir | 232.43 | 280.93 | 0.00 | 737.08 |
| strd | 362.20 | 21.56 | 312.44 | 417.38 |
| str | -110.24 | 38.36 | -186.98 | -42.68 |
| S_diffuse | 58.89 | 61.60 | 0.00 | 236.59 |
| S_up | 57.68 | 66.62 | -0.00 | 183.20 |
| L_up | 472.45 | 51.36 | 383.58 | 565.60 |
| I* | 232.43 | 280.93 | 0.00 | 737.08 |
| MRT | 305.84 | 19.33 | 279.96 | 334.34 |


## 12. Production Changes

- `scientific/thermal_comfort/mrt.py` -- Di Napoli MRT module
- `scripts/validate_mrt.py` -- Validation script
- `tests/scientific_validation/test_mrt.py` -- 21 unit tests

UTCI modified = NO
H modified = NO
V modified = NO
E modified = NO
HSRI modified = NO

## 13. Final Status

TEST 2 COMPLETE

---

**Version:** 3.0 (FINAL)
**Date:** 2026-09-01
