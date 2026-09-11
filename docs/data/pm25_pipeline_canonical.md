# PM2.5 Modeling Pipeline

**Status:** CANONICAL
**Version:** 1.0
**Generated:** 2026-09-12T02:05:34.129620

---

## Pipeline Conceptual Flow

```
CPCB observed PM2.5
    |
    v
daily station-day target
    |
    v
driver table
    |
    v
MAIAC satellite predictor
    +
ERA5 meteorology
    |
    v
PM2.5 model
    |
    v
future spatial PM2.5 surface
```

---

## Target vs Predictors

### TARGET

**CPCB measured PM2.5**

- Source: CPCB CAAQMS stations
- Variable: PM2.5 concentration (ug/m3)
- Aggregation: Daily mean of valid hourly observations
- Eligibility: >= 18 valid hourly observations per day
- No synthetic PM2.5
- No target imputation

### PREDICTORS

**MAIAC AOD**

- Source: MODIS/061/MCD19A2_GRANULES
- Variable: Optical_Depth_055 (scale: 0.001)
- QA: Strict filtering (cloud_mask=1, land_mask=0, AOD_QA=0, glint_mask=0)
- Coverage: ~21.8% (sparse, optional)

**ERA5 Meteorology**

- Source: ECMWF/ERA5/HOURLY
- Variables:
  - temperature_daily_c
  - relative_humidity_daily_pct
  - wind_speed_daily_ms
  - surface_pressure_daily_hpa
  - precipitation_daily_m
- Coverage: 100% for pilot rows

---

## CPCB Method

### Hourly to Daily Aggregation

```
hourly CPCB PM2.5
    |
    v
daily station/date mean
```

### Daily Eligibility Rule

- Minimum 18 valid hourly observations out of 24
- = 75% of hourly observations

### Scientific Rules

- No synthetic PM2.5
- No target imputation
- No infer PM2.5 from AQI
- No fabricate data

---

## MAIAC Method

### Dataset

- Collection: MODIS/061/MCD19A2_GRANULES
- AOD band: Optical_Depth_055
- Physical scaling: x 0.001
- Uncertainty: AOD_Uncertainty x 0.0001

### Primary Strict QA Rule

```python
cloud_mask == 1
land_mask == 0
AOD_QA == 0
glint_mask == 0
```

### Multiple Valid Observations

- Prefer lowest valid AOD uncertainty
- Do not use unmasked AOD
- Do not impute missing AOD
- Do not use neighborhood means as primary predictor
- Keep research-quality QA=11 separate from strict AOD

---

## ERA5 Method

### Daily Predictors

| Variable | ERA5 Name | Unit | Description |
|----------|-----------|------|-------------|
| temperature_daily_c | t2m | degC | Daily mean temperature |
| relative_humidity_daily_pct | d2m derived | % | Derived from T and Td |
| wind_speed_daily_ms | u10, v10 | m/s | sqrt(u^2 + v^2), daily mean |
| surface_pressure_daily_hpa | sp | hPa | Daily mean pressure |
| precipitation_daily_m | tp | mm | Daily accumulation |

---

## Model Documentation

### Pilot Experiment

- Dataset: 500-row 2025 pilot
- Models: Ridge, Random Forest, Gradient Boosting
- Validation: Leave-One-Station-Out (LOSO)
- Baseline: Naive (training-fold mean)

### Key Results

| Model | MAE | RMSE | R2 |
|-------|-----|------|----|
| Random Forest (ERA5-only) | 12.17 | 15.75 | 0.500 |
| Ridge (ERA5-only) | 14.56 | 18.72 | 0.335 |
| Gradient Boosting (ERA5-only) | 12.53 | 16.39 | 0.446 |

### AOD Comparison

- AOD added value is mixed
- Limited by only 92 strict-AOD rows
- Not conclusive yet

---

## Extraction Architecture

### MAIAC Extraction

```
CPCB eligible station/dates
    |
    v
batch selection
    |
    v
Earth Engine server-side extraction
    |
    v
table export
    |
    v
local retrieval
    |
    v
local merge
    |
    v
Parquet
```

### Problem Solved

Previous architecture caused "User memory limit exceeded" error.
Current architecture avoids large FeatureCollection.getInfo().

---

**Status:** CANONICAL - This document describes the PM2.5 modeling pipeline.
