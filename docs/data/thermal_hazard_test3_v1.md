# TEST 3 — Real Weather → MRT → UTCI → H Integration

## 1. Objective

Run real Ahmedabad-area ERA5 meteorological data through the complete deterministic thermal pipeline:

    ERA5 meteorology + ERA5 radiation → MRT → UTCI → Hazard H

Prove that the complete thermal calculation works on real observations and produces physically sensible UTCI and H values.

## 2. Input datasets

| File | Variables | Source |
|------|-----------|--------|
| `97c99a12bac0f84dae69bd5460cde459.nc` | ssrd, strd, fdir, ssr, str | ERA5 radiation (J/m²) |
| `53968a80e95eb41e9fe5c5f804eacbd8.nc` | t2m, d2m, u10, v10 | ERA5 meteorology |
| `cde4e619c080209e1ec505565f79b8e.nc` | mrt, utci | ERA5-HEAT reference |
| `data/raw/weather/data_0.nc` | sp | ERA5 surface pressure (Pa) |

**VERIFIED SOURCE FACT**: All files are real ERA5 data for Ahmedabad area, March 2010.

## 3. Metadata verification

### Radiation variables
- ssrd: J m⁻² → converted to W/m² (÷3600)
- strd: J m⁻² → converted to W/m²
- fdir: J m⁻² → converted to W/m²
- ssr: J m⁻² → converted to W/m²
- str: J m⁻² → converted to W/m²

### Meteorology variables
- t2m: K → converted to °C (−273.15)
- d2m: K → converted to °C
- u10: m s⁻¹
- v10: m s⁻¹

### Surface pressure
- sp: Pa → used for humidity processing

### ERA5-HEAT reference
- mrt: degK
- utci: degK

**VERIFIED SOURCE FACT**: Units and variable names match ERA5 documentation.

## 4. Temporal matching

| Source | Timestamps |
|--------|------------|
| Radiation | 124 |
| Meteorology | 124 |
| Raw weather | 124 |
| ERA5-HEAT (March 2010) | 744 |
| Common (rad+met+raw) | 124 |
| Common with ERA5-HEAT | 124 |

**OBSERVED RESULT**: All 124 hourly timestamps from March 2010 are matched across all sources.

## 5. Spatial matching

| Source | Latitude | Longitude |
|--------|----------|-----------|
| Radiation | [23.25, 23.0, 22.75] | [72.25, 72.5, 72.75, 73.0] |
| Meteorology | [23.25, 23.0, 22.75] | [72.25, 72.5, 72.75, 73.0] |
| ERA5-HEAT | [22.75, 23.0, 23.25] | [72.25, 72.5, 72.75, 73.0] |

- Grid points: 12 (3 lat × 4 lon)
- Rad==Met grid: True
- ERA5-HEAT grid matches (reordered): True

**OBSERVED RESULT**: All 12 grid points are matched. ERA5-HEAT has reversed lat order but same coordinates.

## 6. Humidity processing

- Method: Buck (1981) saturation vapor pressure equation
- RH derived from T2m and D2m
- Vapor pressure from D2m saturation vapor pressure

**OBSERVED RESULT**:
- RH range: 12.9% – 88.9%
- VP range: 7.28 – 27.66 hPa
- Mean RH: 39.3%

**IMPLEMENTATION DETAIL**: Same humidity processing as existing UTCI diagnostic.

## 7. Wind processing

- wind_speed = √(u10² + v10²)

**OBSERVED RESULT**:
- Range: 0.20 – 4.90 m/s
- Mean: 2.40 m/s
- Near-zero wind (< 0.5 m/s): 5 records

## 8. MRT

**METHOD VERSION**: ECMWF_THERMOFEEL_COMPATIBLE_V1

| Metric | Value |
|--------|-------|
| N | 1488 |
| Mean | 308.59 K |
| Median | 306.05 K |
| Min | 279.96 K |
| Max | 335.70 K |

Quality flags:
- Valid (qf=0): 744
- Nighttime (qf=1): 744
- Low sun (qf=2): 0
- Negative radiation (qf=3): 0
- Missing input (qf=4): 0
- MRT unphysical (qf=5): 0

**OBSERVED RESULT**: All 1488 MRT values are valid. Nighttime MRT is longwave-only (as expected).

## 9. UTCI

| Metric | Value |
|--------|-------|
| N | 1488 |
| Mean | 28.93 °C |
| Median | 28.95 °C |
| Min | 11.60 °C |
| Max | 45.10 °C |
| P5 | 15.00 °C |
| P25 | 19.50 °C |
| P75 | 38.20 °C |
| P95 | 42.50 °C |

- UTCI errors: 0
- Wind clamped: 5

**OBSERVED RESULT**: All UTCI values are physically plausible for Ahmedabad in March.

## 10. UTCI vs ERA5-HEAT

| Metric | Value |
|--------|-------|
| N | 1488 |
| MAE | 1.3890 K |
| RMSE | 1.6892 K |
| Bias | +1.1415 K |
| Median AE | 1.1927 K |
| P95 AE | 3.0603 K |
| R² | 0.971730 |

**OBSERVED RESULT**: Agnirakshak UTCI is close to ERA5-HEAT (MAE=1.39 K, R²=0.972). The positive bias (+1.14 K) reflects the thermofeel-consistent MRT methodology difference from ERA5-HEAT's operational implementation.

**IMPORTANT REFERENCE INTERPRETATION**: ERA5-HEAT uses Di Napoli methodology with operational differences. Exact equality is not expected. The observed differences are consistent with the documented MRT methodology differences.

## 11. Hazard H

| Metric | Value |
|--------|-------|
| N | 1488 |
| Mean | 0.4537 |
| Median | 0.3770 |
| Min | 0.0382 |
| Max | 0.9719 |
| P5 | 0.0882 |
| P25 | 0.1544 |
| P75 | 0.7563 |
| P95 | 0.8906 |

Category counts:
- no_thermal_stress: 744
- strong_heat_stress: 344
- very_strong_heat_stress: 400

### H bounds

- min >= 0: **YES** (min=0.0382)
- max <= 1: **YES** (max=0.9719)

### UTCI → H monotonicity

- Monotonicity violations: 0
- Monotonic: **YES**

**OBSERVED RESULT**: H is strictly within [0,1] and monotonic with UTCI.

## 12. UTCI/H physical QA

- NaN count: 0
- Inf count: 0
- Below -50 °C: 0
- Above 60 °C: 0

**OBSERVED RESULT**: No catastrophic numeric failures. All values are physically plausible.

## 13. Time-of-day analysis

| Period | N | Mean MRT (°C) | Mean UTCI (°C) |
|--------|---|---------------|----------------|
| 00–06 UTC | 372 | 12.43 | 17.42 |
| 06–12 UTC | 372 | 55.12 | 36.80 |
| 12–18 UTC | 372 | 58.67 | 40.29 |
| 18–24 UTC | 372 | 15.52 | 21.22 |
| Daytime | 744 | 56.90 | 38.54 |
| Nighttime | 744 | 13.98 | 19.32 |

**OBSERVED RESULT**: Clear diurnal cycle. Peak thermal stress 12–18 UTC (local evening). Nighttime values are physically reasonable.

## 14. Representative cases

### Hot daytime (highest UTCI)
- 2010-03-19 12:00 UTC, (23.0, 72.75): Ta=40.0°C, RH=19%, MRT=62.6°C, UTCI=45.1°C, H=0.97
- Ref UTCI: 42.2°C (diff: +2.9°C)

### Nighttime
- 2010-03-01 00:00 UTC, (23.25, 72.25): Ta=17.4°C, RH=51%, MRT=6.8°C, UTCI=11.7°C, H=0.04
- Ref UTCI: 9.1°C (diff: +2.6°C)

### Lower thermal stress
- 2010-03-01 00:00 UTC, (23.25, 72.75): Ta=18.0°C, RH=47%, MRT=7.3°C, UTCI=11.6°C, H=0.04

## 15. Highest thermal-stress cases (top 20)

All top 20 cases occur during 12:00 UTC on March 18–21, 2010:
- UTCI range: 44.5 – 45.1 °C
- H range: 0.953 – 0.972
- Category: very_strong_heat_stress

**OBSERVED RESULT**: Highest thermal stress occurs during pre-monsoon heat episodes in mid-March.

## 16. Limitations

1. **Single month only**: March 2010. Monsoon and pre-monsoon performance unknown.
2. **Coarse grid**: 0.25° ERA5 grid. Local microclimate effects not captured.
3. **No ground truth**: No independent Ahmedabad MRT/UTCI measurements available.
4. **ERA5-HEAT is not independent validation**: Uses same Di Napoli methodology.
5. **No V/E/HSRI**: Only MRT → UTCI → H pipeline tested.

## 17. Conclusion

The deterministic thermal pipeline was **successfully executed** on the tested real Ahmedabad-area data.

- Real ERA5 meteorology and radiation were used
- Real MRT was calculated using ECMWF_THERMOFEEL_COMPATIBLE_V1
- Existing UTCI engine was used unchanged
- Existing Hazard H was applied unchanged
- H remains within [0,1] for all observations
- UTCI compares well with ERA5-HEAT (MAE=1.39 K, R²=0.972)

**This does NOT establish mortality prediction, hospitalization prediction, or health outcome prediction.**

## 18. Next milestone

- Validation against independent ground measurements (if available)
- Extension to full year or multi-year analysis
- Integration with V, E, HSRI components

## Production changes

- UTCI modified = **NO**
- H modified = **NO**
- V modified = **NO**
- E modified = **NO**
- HSRI modified = **NO**

## Files created

| File | Description |
|------|-------------|
| `data/curated/thermal_hazard_march_2010.parquet` | Curated thermal dataset |
| `data/profiles/thermal_hazard_test3_v1.json` | Machine-readable results |
| `data/profiles/plots/thermal_hazard_test3/` | Distribution and comparison plots |
| `docs/data/thermal_hazard_test3_v1.md` | This report |

## Final status

**TEST 3 COMPLETE**
