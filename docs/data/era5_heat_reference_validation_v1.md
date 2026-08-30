# ERA5-HEAT Reference Validation — March 2010

**Method**: TEST 1 — ERA5-HEAT MRT + ERA5-Land meteorological inputs → Agnirakshak UTCI → compare with ERA5-HEAT UTCI

## Files Inspected

| File | Path |
|------|------|
| ERA5-HEAT | `cde4e619c080209e1ec505565f79b8e.nc` |
| ERA5-Land | `data/raw/weather/data_0.nc` |

## ERA5-HEAT Metadata

| Property | Value |
|----------|-------|
| Variables | mrt, utci |
| Units | degK (Kelvin) |
| Grid | 3x4 (22.75-23.25N, 72.25-73.0E) |
| Resolution | ~0.25° |
| Time range | 2010-01-02 to 2026-01-10 |
| March 2010 timesteps | 744 (hourly) |

## ERA5-Land Metadata

| Property | Value |
|----------|-------|
| Variables | t2m, d2m, u10, v10, sp, ssrd, strd |
| Units | K, K, m/s, m/s, Pa, J/m², J/m² |
| Grid | 5x5 (22.8-23.2N, 72.4-72.8E) |
| Resolution | ~0.1° |
| Timesteps | 124 (6-hourly, March 2010) |

## Unit Conversions

| Source | Original | Canonical | Method |
|--------|----------|-----------|--------|
| ERA5-HEAT MRT | K | °C | subtract 273.15 |
| ERA5-HEAT UTCI | K | °C | subtract 273.15 |
| ERA5-Land t2m | K | °C | subtract 273.15 |
| ERA5-Land d2m | K | RH% | Buck equation |
| ERA5-Land u10, v10 | m/s | wind speed | sqrt(u²+v²) |

## Temporal Matching

| Metric | Value |
|--------|-------|
| ERA5-HEAT timesteps | 744 |
| ERA5-Land timesteps | 124 |
| Common timesteps | 124 |
| Method | Exact timestamp intersection |

## Spatial Matching

| Metric | Value |
|--------|-------|
| ERA5-HEAT grid | 3x4 |
| ERA5-Land grid | 5x5 |
| Method | Nearest neighbor |

Matched coordinate pairs:

| HEAT (lat, lon) | LAND (lat, lon) | Distance (km) |
|-----------------|-----------------|---------------|
| (22.75, 72.25) | (22.80, 72.40) | 17.6 |
| (22.75, 72.50) | (22.80, 72.50) | 5.5 |
| (22.75, 72.75) | (22.80, 72.80) | 7.8 |
| (22.75, 73.00) | (22.80, 72.80) | 22.9 |
| (23.00, 72.25) | (23.00, 72.40) | 16.6 |
| (23.00, 72.50) | (23.00, 72.50) | 0.0 |
| (23.00, 72.75) | (23.00, 72.80) | 5.5 |
| (23.00, 73.00) | (23.00, 72.80) | 22.2 |
| (23.25, 72.25) | (23.20, 72.40) | 17.6 |
| (23.25, 72.50) | (23.20, 72.50) | 5.5 |
| (23.25, 72.75) | (23.20, 72.80) | 7.8 |
| (23.25, 73.00) | (23.20, 72.80) | 22.9 |

## UTCI Comparison Statistics

| Metric | Value |
|--------|-------|
| Sample count | 1488 |
| MAE | 0.581 °C |
| RMSE | 0.8546 °C |
| Mean bias | 0.4619 °C |
| Median absolute error | 0.4023 °C |
| Min difference | -1.5913 °C |
| Max difference | 4.37 °C |
| Std of difference | 0.719 °C |
| Invalid calculations | 0 |
| Missing values | 0 |

## MRT Reference Statistics

| Metric | Value (°C) |
|--------|-----------|
| Min | 6.62 |
| Max | 63.64 |
| Mean | 32.75 |
| Median | 20.49 |
| Std | 19.55 |

## Plots Created

- `data/profiles/plots/utci_reference_vs_agnirakshak.png`
- `data/profiles/plots/utci_difference_distribution.png`

## Scientific Limitations

1. **ERA5-HEAT MRT is used as input** — this validates the UTCI polynomial only, not the MRT derivation method.
2. **Spatial mismatch** — ERA5-HEAT (0.25°) and ERA5-Land (0.1°) have different grids; nearest-neighbor matching introduces spatial error.
3. **Temporal mismatch** — ERA5-HEAT is hourly, ERA5-Land is 6-hourly; only 124 of 744 timesteps can be compared.
4. **Wind speed range** — UTCI requires wind >= 0.5 m/s; calm wind conditions are excluded.
5. **No MRT derivation tested** — this is TEST 1 only. TEST 2 (ERA5-Land radiation → MRT) is a separate experiment.

## Existing UTCI Engine

**Modified**: NO — the UTCI polynomial implementation is unchanged.

## Conclusion

Reference comparison completed. Results support / do not support agreement under the tested conditions. 
This validation uses ERA5-HEAT MRT as direct input to the Agnirakshak UTCI engine, 
testing only the polynomial calculation accuracy, not the full MRT derivation pipeline.

**Do NOT interpret this as MRT derivation validation.**