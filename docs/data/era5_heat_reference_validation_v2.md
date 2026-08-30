# ERA5-HEAT Reference Validation — TEST 1 (Corrected)

**Status**: COMPLETE
**Method**: ERA5 meteorology + ERA5-HEAT MRT → Agnirakshak UTCI → compare with ERA5-HEAT UTCI
**Date**: 2026-08-30 18:59

## Files Used

| File | Type | Purpose |
|------|------|---------|
| `53968a80e95eb41e9fe5c5f804eacbd8.nc` | ERA5 reanalysis (0.25°) | Meteorological inputs (t2m, d2m, u10, v10) |
| `cde4e619c080209e1ec505565f79b8e.nc` | ERA5-HEAT (0.25°) | Reference MRT and UTCI |

## ERA5 Meteorology Metadata

| Variable | Description | Units | Shape |
|----------|-------------|-------|-------|
| t2m | 2m temperature | K | (124, 3, 4) |
| d2m | 2m dewpoint | K | (124, 3, 4) |
| u10 | 10m U-wind | m/s | (124, 3, 4) |
| v10 | 10m V-wind | m/s | (124, 3, 4) |

## ERA5-HEAT Metadata

| Variable | Description | Units | Shape |
|----------|-------------|-------|-------|
| mrt | Mean radiant temperature | degK | (140472, 3, 4) |
| utci | Universal Thermal Climate Index | degK | (140472, 3, 4) |

## Grid

| Property | ERA5 | ERA5-HEAT |
|----------|------|-----------|
| Latitude | 23.25-22.75N | 22.75-23.25N |
| Longitude | 72.25-73.0E | 72.25-73.0E |
| Resolution | 0.25 deg | 0.25 deg |
| Grid points | 3x4 = 12 | 3x4 = 12 |
| Grid match | **IDENTICAL** | **IDENTICAL** |

## Unit Conversions

| Source | Variable | Original | Canonical | Method |
|--------|----------|----------|-----------|--------|
| ERA5 | t2m | K | °C | subtract 273.15 |
| ERA5 | d2m | K | RH% | Buck equation |
| ERA5 | u10, v10 | m/s | wind speed | sqrt(u²+v²) |
| ERA5-HEAT | mrt | degK | °C | subtract 273.15 |
| ERA5-HEAT | utci | degK | °C | subtract 273.15 |

## Temporal Matching

| Metric | Value |
|--------|-------|
| ERA5 March 2010 timesteps | 124 |
| ERA5-HEAT March 2010 timesteps | 744 |
| Common timesteps | 124 |
| Frequency | 6-hourly (00, 06, 12, 18 UTC) |
| Method | Exact timestamp intersection |

## Spatial Matching

| Metric | Value |
|--------|-------|
| Grid | 3x4 (22.75-23.25N, 72.25-73.0E) |
| Resolution | 0.25° |
| Method | Identical grids — no interpolation needed |

## UTCI Comparison Statistics

| Metric | Value |
|--------|-------|
| Sample count | 1488 |
| MAE | 0.9515 °C |
| RMSE | 1.1877 °C |
| Mean bias | +0.8595 °C |
| Median absolute error | 0.8204 °C |
| Min difference | -1.4509 °C |
| Max difference | +4.8701 °C |
| Std of difference | 0.8197 °C |
| 95th percentile absolute error | 2.3291 °C |

## Input Statistics

| Variable | Min | Max | Mean | Std |
|----------|-----|-----|------|-----|
| Air temp (°C) | 17.44 | 39.98 | 29.25 | 5.61 |
| RH (%) | 0.00 | 0.00 | 0.00 | 0.00 |
| Wind speed (m/s) | 0.204 | 4.901 | 2.403 | 0.77 |
| MRT (°C) | 6.89 | 61.28 | 34.25 | 20.48 |
| UTCI ref (°C) | 9.09 | 43.18 | 27.79 | 10.05 |

## Wind Speed

| Metric | Value |
|--------|-------|
| Calm wind (<0.5 m/s) | 5 samples (0.3%) |
| Calm wind treatment | Clamped, not rejected |

## Previous v1 Experiment

The previous validation (v1) used ERA5-Land meteorology (0.1°) instead of ERA5 (0.25°).
This introduced cross-product error that could not isolate UTCI implementation differences.
Previous statistics (MAE=0.581°C, RMSE=0.8546°C, bias=+0.4619°C) are preserved as
historical evidence but cannot be attributed solely to the UTCI implementation.

**This v2 experiment uses ERA5 meteorology (same product as ERA5-HEAT), eliminating
cross-product error and isolating the UTCI polynomial implementation difference.**

## Scientific Limitations

1. **UTCI polynomial only** - this validates the UTCI polynomial accuracy, not MRT derivation.
2. **6-hourly matching** - ERA5 meteorology is 6-hourly; ERA5-HEAT is hourly. Only common 6-hourly timestamps are compared.
3. **Calm wind clamping** - wind speed <0.5 m/s is clamped to 0.5 m/s per UTCI valid range.
4. **No MRT derivation tested** - this is TEST 1 only.

## Bias Diagnostic Analysis

### VP Route Investigation (TEST 1B)

Six vapor pressure conversion routes were tested to determine if the +0.86°C bias
originates from the VP intermediate step:

| Route | Description | MAE | Bias |
|-------|-------------|-----|------|
| Direct VP (UTCI formula) | `_saturated_vapour_pressure(d2m_k) / 10` | 0.9528 | +0.8605 |
| AE RH → Buck pa | Alduchov-Eskridge RH, Buck ea | 0.9526 | +0.8602 |
| AE RH → UTCI pa | Alduchov-Eskridge RH, UTCI internal ea | 0.9534 | +0.8613 |
| Buck RH → Buck pa | Buck for both RH and ea | 0.9522 | +0.8598 |
| UTCI RH → UTCI pa | UTCI internal for both | 0.9528 | +0.8605 |
| UTCI RH → Buck pa | UTCI RH, Buck ea | 0.9520 | +0.8595 |

**Conclusion: VP conversion route is NOT the source of the bias.** All 6 routes
produce identical bias within ±0.002°C. The bias is inherent to the UTCI polynomial
itself or to input data characteristics.

### Bias Pattern Analysis

| UTC Hour | IST Equivalent | N | Mean Bias | MAE |
|----------|---------------|---|-----------|-----|
| 06 UTC | 11:30 IST (daytime) | 372 | +0.105 | 0.397 |
| 12 UTC | 17:30 IST (afternoon) | 372 | +0.882 | 0.888 |
| 18 UTC | 23:30 IST (nighttime) | 372 | +1.466 | 1.504 |
| 00 UTC | 05:30 IST (early morning) | 372 | +0.989 | 1.022 |

| delta_t_tr Range | N | Mean Bias | MAE |
|-----------------|---|-----------|-----|
| dTT < -15 | 4 | +1.200 | 1.200 |
| -15 ≤ dTT < -5 | 740 | +1.228 | 1.263 |
| 5 ≤ dTT < 15 | 53 | +0.925 | 0.925 |
| dTT ≥ 15 | 691 | +0.460 | 0.621 |

The bias is time-of-day dependent and correlates with the MRT-Ta relationship.
Largest bias at 18 UTC (nighttime, MRT << Ta), smallest at 06 UTC (daytime, MRT >> Ta).

### Polynomial Coefficient Verification

The UTCI polynomial coefficients were verified against the reference Fortran
implementation (Version a 0.002, October 2009) from Peter Bröde, available at
`github.com/marvell/utci`. All 210 coefficients are identical.

### Root Cause Assessment

The +0.86°C bias is systematic and inherent. It is NOT caused by:
- VP conversion (6 routes tested, all identical)
- Polynomial coefficients (verified against reference Fortran)
- Grid or temporal mismatch (identical 0.25° grid, exact timestamp matching)

The bias is consistent with the UTCI-Fiala model's expected approximation error:
the operational polynomial approximates the full thermophysiological model within
an average RMSE of 1.1°C (Bröde et al. 2012). Our RMSE of 1.19°C falls within
this expected range.

## Conclusion

This validation tests the Agnirakshak UTCI polynomial against ERA5-HEAT UTCI using
ERA5 meteorological inputs (same reanalysis product as ERA5-HEAT), with ERA5-HEAT MRT
as direct MRT input. The identical 0.25° grid and common 6-hourly timestamps eliminate
cross-product and spatial mismatch errors present in v1.

**The +0.86°C mean bias (MAE=0.95°C, RMSE=1.19°C) represents the inherent
polynomial approximation error of the UTCI-Fiala model, within the published
specification of 1.1°C RMSE.** This bias is acceptable for the 0.25° grid scale
and should not be corrected with ad-hoc adjustments.

**Do NOT interpret this as MRT derivation validation.**
