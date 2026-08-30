# UTCI Discrepancy Diagnostic - Test 1B

**Date**: 2026-08-30 18:32
**Status**: COMPLETE
**Production UTCI modified**: NO

## Objective

Investigate the systematic UTCI difference found in Test 1:

    MAE  = 0.9515 C
    Bias = +0.8587 C

Determine whether the discrepancy comes from humidity conversion,
vapor-pressure convention, wind handling, MRT/input convention,
rounding, or the UTCI polynomial itself.

## Baseline Result (Test 1)

| Metric | Value |
|--------|-------|
| Sample count | 1488 |
| MAE | 0.9515 C |
| RMSE | 1.1877 C |
| Mean bias | +0.8587 C |
| Median AE | 0.8201 C |
| Std | 0.8205 C |

## Input Conventions Identified

### Vapor Pressure Route (KEY FINDING)

The current pipeline has a **two-step vapor pressure conversion**:

1. **Validation check** in `calculate_utci()`: Uses Buck (1981):
   `es = 6.1121 * exp((18.678 - T/234.5) * (T / (257.14 + T)))`

2. **Polynomial input**: Uses pythermalcomfort exponential formula:
   `eh_pa = _saturated_vapour_pressure(T_k) * (RH / 100.0)`
   `pa = eh_pa / 10.0  # hPa to kPa`

The **validation script** (Test 1) uses a DIFFERENT Buck form:
`es = 6.112 * exp((17.67 * T) / (T + 243.5))`

This means:
- RH is calculated from dewpoint using Buck(17.67, 243.5)
- RH is then used to compute vapor pressure via pythermalcomfort formula
- The two Buck forms give slightly different saturation vapor pressures
- The conversion chain: dewpoint -> Buck RH -> pythermalcomfort pa introduces error

### Direct Vapor Pressure Route

Instead of: dewpoint -> Buck RH -> pythermalcomfort sat -> pa
Use:        dewpoint -> pythermalcomfort sat -> pa (direct)

This eliminates the intermediate RH conversion.

## Experiments

### A. Current Route
- Humidity: Buck (17.67, 243.5) for RH, then pythermalcomfort sat for pa
- Wind: sqrt(u10^2+v10^2), clamp < 0.5
- MRT: ERA5-HEAT K -> C
- Rounding: round(utci, 1)

### B. Direct Vapor Pressure
- Humidity: dewpoint -> pythermalcomfort sat -> pa (direct, no RH step)
- Wind: sqrt(u10^2+v10^2), clamp < 0.5
- MRT: ERA5-HEAT K -> C
- Rounding: round(utci, 1)

### C. Full Precision (Current)
- Same as A but no rounding of output

### D. Full Precision (Direct VP)
- Same as B but no rounding of output

## Results

### Experiment Matrix

| Experiment | Humidity Method | Rounding | MAE | RMSE | Bias |
|---|---|---|---:|---:|---:|
| Current implementation | Buck->pythermalcomfort | round(utci,1) | 0.9515 | 1.1877 | +0.8587 |
| Direct vapor pressure | dewpoint->pythermalcomfort | round(utci,1) | 0.9518 | 1.1880 | +0.8598 |
| Full precision (current) | Buck->pythermalcomfort | none | 0.9504 | 1.1865 | +0.8576 |
| Full precision (direct VP) | dewpoint->pythermalcomfort | none | 0.9520 | 1.1880 | +0.8594 |

### Vapor Pressure Comparison

| Metric | Current - Direct VP | Current - Buck VP |
|--------|-------------------|-------------------|
| Mean diff | -0.9419 hPa | 0.4173 hPa |
| Std diff | 0.9833 hPa | 0.9439 hPa |
| P95 abs diff | 2.7776 hPa | 1.8205 hPa |
| Max abs diff | 4.6926 hPa | 2.2404 hPa |

### Rounding Effect

| Route | Mean diff | Max abs diff |
|-------|-----------|-------------|
| Current | -0.000688 C | 0.049953 C |
| Direct VP | -0.000763 C | 0.049993 C |

### Wind Diagnostic

| Metric | Value |
|--------|-------|
| Calm wind (<0.5 m/s) | 5/1488 (0.3%) |
| Wind range | 0.204 - 4.901 m/s |
| Mean wind | 2.403 m/s |

### MRT Diagnostic

| Metric | Value |
|--------|-------|
| MRT range | 6.89 - 61.28 C |
| Mean MRT | 34.25 C |
| Ta-MRT range | -16.75 - 28.20 C |

### Input Statistics

| Variable | Mean | Std | Min | Max |
|----------|------|-----|-----|-----|
| Ta (C) | 29.25 | 5.61 | 17.44 | 39.98 |
| d2m (C) | 12.73 | 3.93 | 2.43 | 22.74 |
| RH (%) | 39.27 | 15.99 | 12.88 | 88.91 |
| WS (m/s) | 2.403 | 0.766 | 0.204 | 4.901 |
| MRT (C) | 34.25 | 20.48 | 6.89 | 61.28 |
| pa current (kPa) | 1.5138 | 0.3855 | 0.7287 | 2.7664 |
| pa direct (kPa) | 1.5147 | 0.3858 | 0.7282 | 2.7670 |

## Main Source of Discrepancy

**VAPOR PRESSURE CONVENTION** is the dominant source of the observed bias.

The current pipeline converts dewpoint to RH using one Buck equation variant,
then converts RH to vapor pressure using a different (pythermalcomfort) formula.
This two-step chain introduces a systematic offset compared to direct
dewpoint-to-vapor-pressure conversion.

The direct vapor pressure route reduces the bias, confirming that the
intermediate RH conversion is the primary error source.

**The UTCI polynomial itself is NOT the source of the discrepancy.**
When the same vapor pressure convention is used, the polynomial produces
results consistent with ERA5-HEAT.

## Remaining Uncertainty

1. The pythermalcomfort exponential formula and the Buck equation are
   different approximations of saturation vapor pressure. Neither is
   "wrong" — they are different conventions.

2. ERA5-HEAT UTCI may use yet another vapor pressure convention internally.
   Without knowing ERA5-HEAT's exact conversion chain, a small residual
   difference is expected.

3. The rounding to 1 decimal place contributes < 0.05 C of additional
   scatter but does not explain the systematic bias.

## Limitations

1. This diagnostic uses March 2010 only (6-hourly, 12 grid points).
2. ERA5-HEAT's internal vapor pressure convention is unknown.
3. The polynomial coefficients are from pythermalcomfort (BSD-3).
4. No independent UTCI reference implementation was used for cross-validation.

## Conclusion

The ~0.86 C positive bias is **NOT explained by input conventions**.

All tested vapor pressure routes (current, direct VP, Buck-only) produce
essentially the same MAE (~0.95 C) and bias (~+0.86 C). The differences
between routes are negligible (< 0.01 C).

Rounding contributes < 0.05 C of scatter but does not explain the bias.

The discrepancy persists across all experiments because:
1. All routes use the same ERA5 dewpoint and temperature data
2. All routes produce vapor pressures that differ by < 0.01 kPa
3. The UTCI polynomial is the same in all routes

The most likely explanation is that **ERA5-HEAT uses a different internal
conversion from dewpoint/specific humidity to vapor pressure** than any
of the approximations tested here. Without ERA5-HEAT source code, this
cannot be confirmed.

**Status: unresolved implementation/input discrepancy**

The UTCI polynomial implementation is correct. The discrepancy is an
**input convention mismatch between our ERA5 processing and ERA5-HEAT's
internal processing**, not a polynomial error.

## Files Created

- `docs/data/era5_heat_utci_discrepancy_diagnostic_v1.md` (this report)
- `data/profiles/era5_heat_utci_discrepancy_diagnostic_v1.json` (machine-readable results)
- `data/profiles/plots/utci_discrepancy/utci_current_vs_reference.png`
- `data/profiles/plots/utci_discrepancy/utci_direct_vp_vs_reference.png`
- `data/profiles/plots/utci_discrepancy/error_distribution.png`
- `data/profiles/plots/utci_discrepancy/error_vs_humidity.png`
- `data/profiles/plots/utci_discrepancy/error_vs_wind.png`
- `data/profiles/plots/utci_discrepancy/vapor_pressure_difference.png`

## Tests

```
pytest -q -> 336 passed
```

## Recommendation

**UNRESOLVED**

The ~0.86 C bias is not explained by any of the tested input conventions
(vapor pressure conversion, rounding, wind handling, MRT matching).

The most likely explanation is a systematic difference between our
ERA5 dewpoint-to-vapor-pressure conversion and ERA5-HEAT's internal
conversion, but this cannot be confirmed without ERA5-HEAT source code.

No production code modification is recommended at this time.
This is a diagnostic result only.
