# ERA5-HEAT Reference Validation — TEST 1 (Corrected)

**Status**: COMPLETE
**Method**: ERA5 meteorology + ERA5-HEAT MRT → Agnirakshak UTCI → compare with ERA5-HEAT UTCI
**Date**: 2026-08-30 18:14

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
| Latitude | 23.25–22.75°N | 22.75–23.25°N |
| Longitude | 72.25–73.0°E | 72.25–73.0°E |
| Resolution | 0.25° | 0.25° |
| Grid points | 3×4 = 12 | 3×4 = 12 |
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
| Grid | 3×4 (22.75–23.25°N, 72.25–73.0°E) |
| Resolution | 0.25° |
| Method | Identical grids — no interpolation needed |

## UTCI Comparison Statistics

| Metric | Value |
|--------|-------|
| Sample count | 1488 |
| MAE | 0.9515 °C |
| RMSE | 1.1877 °C |
| Mean bias | +0.8587 °C |
| Median absolute error | 0.8201 °C |
| Min difference | -1.4509 °C |
| Max difference | +4.8701 °C |
| Std of difference | 0.8205 °C |
| 95th percentile absolute error | 2.3291 °C |

## Input Statistics

| Variable | Min | Max | Mean | Std |
|----------|-----|-----|------|-----|
| Air temp (°C) | 17.44 | 39.98 | 29.25 | 5.61 |
| RH (%) | 12.88 | 88.91 | 39.27 | 15.99 |
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

1. **UTCI polynomial only** — this validates the UTCI polynomial accuracy, not MRT derivation.
2. **6-hourly matching** — ERA5 meteorology is 6-hourly; ERA5-HEAT is hourly. Only common 6-hourly timestamps are compared.
3. **Calm wind clamping** — wind speed <0.5 m/s is clamped to 0.5 m/s per UTCI valid range.
4. **No MRT derivation tested** — this is TEST 1 only.

## Conclusion

This validation tests the Agnirakshak UTCI polynomial against ERA5-HEAT UTCI using
ERA5 meteorological inputs (same reanalysis product as ERA5-HEAT), with ERA5-HEAT MRT
as direct MRT input. The identical 0.25° grid and common 6-hourly timestamps eliminate
cross-product and spatial mismatch errors present in v1.

**Do NOT interpret this as MRT derivation validation.**
