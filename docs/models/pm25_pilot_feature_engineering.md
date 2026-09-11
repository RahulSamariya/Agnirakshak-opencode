# PM2.5 Pilot Feature Engineering Experiment

**Status:** CANONICAL
**Version:** 1.0
**Generated:** 2026-09-12

---

## Objective

Determine whether scientifically justified ERA5 feature engineering
improves the baseline under exactly the same LOSO validation protocol.

---

## Frozen Baseline (V1)

**Model:** Random Forest + ERA5

| Metric | Value |
|--------|-------|
| MAE | 12.17 |
| RMSE | 15.75 |
| R² | 0.500 |
| Bias | 0.37 |
| Naive MAE | 19.49 |
| LOSO Validation | PASS |

**Status:** EXPERIMENT BASELINE V1 - Never overwrite.

---

## Candidate Features

### Temporal Features

| Feature | Description | Scientific Justification |
|---------|-------------|-------------------------|
| month | Month of year (1-12) | Seasonal PM2.5 patterns |
| season | Season category (0-3) | Ahmedabad's distinct seasons |

### Interaction Features

| Feature | Description | Scientific Justification |
|---------|-------------|-------------------------|
| temp_x_rh | Temperature × Relative Humidity | Heat index effect on PM2.5 |
| temp_x_wind | Temperature × Wind Speed | Wind chill/heat dispersion |

### Nonlinear Features

| Feature | Description | Scientific Justification |
|---------|-------------|-------------------------|
| temp_squared | Temperature² | Nonlinear temperature effect |

### Indicator Features

| Feature | Description | Scientific Justification |
|---------|-------------|-------------------------|
| precip_indicator | Binary: rain/no rain (threshold 0.1mm) | Precipitation washout effect |

---

## Leakage Control

| Feature | Information Timestamp | Available at Prediction Time | Future Information |
|---------|----------------------|------------------------------|-------------------|
| month | Day of prediction | Yes | No |
| season | Day of prediction | Yes | No |
| temp_x_rh | Same-day ERA5 | Yes | No |
| temp_x_wind | Same-day ERA5 | Yes | No |
| temp_squared | Same-day ERA5 | Yes | No |
| precip_indicator | Same-day ERA5 | Yes | No |

**All features PASS leakage control.**

---

## Experiments

### V1 (Baseline Features)

Features:
- temperature_daily_c
- relative_humidity_daily_pct
- wind_speed_daily_ms
- surface_pressure_daily_hpa
- precipitation_daily_m

### V2 (Engineered Features)

Features:
- temperature_daily_c
- relative_humidity_daily_pct
- wind_speed_daily_ms
- surface_pressure_daily_hpa
- precipitation_daily_m
- month
- season
- temp_x_rh
- temp_x_wind
- temp_squared
- precip_indicator

---

## Results

**Note:** These results were computed using pooled predictions, which differs
from the original frozen baseline (station-level averaging). See
`docs/models/baseline_discrepancy_audit.md` for the corrected comparison.

### Overall Metrics (Pooled Predictions)

| Experiment | Model | MAE | RMSE | R² | Bias |
|------------|-------|-----|------|----|------|
| V1 | Ridge | 14.58 | 19.35 | 0.375 | -0.02 |
| V1 | RandomForest | 12.17 | 16.40 | 0.552 | 0.35 |
| V1 | GradientBoosting | 12.40 | 16.35 | 0.554 | 0.11 |
| V2 | Ridge | 13.69 | 18.37 | 0.437 | -0.04 |
| V2 | RandomForest | 12.09 | 16.26 | 0.559 | 0.35 |
| V2 | GradientBoosting | 12.41 | 16.29 | 0.557 | 0.27 |

### Corrected Comparison (Station-Level Averaging)

**This is the valid comparison matching the original frozen baseline.**

| Metric | V1 (Corrected) | V2 (Corrected) | Delta | Delta % |
|--------|----------------|----------------|-------|---------|
| MAE | 12.17 | 12.08 | +0.10 | +0.8% |
| RMSE | 15.75 | 15.67 | +0.08 | +0.5% |
| R² | 0.500 | 0.506 | +0.006 | +1.2% |

### Station-by-Station LOSO Results (Random Forest, Corrected)

| Station | V1 MAE | V2 MAE | Delta | Improved |
|---------|--------|--------|-------|----------|
| site_5453 | 8.02 | 8.08 | +0.06 | No |
| site_5450 | 18.72 | 18.01 | -0.71 | Yes |
| site_308 | 8.40 | 8.54 | +0.14 | No |
| site_5452 | 13.89 | 14.28 | +0.39 | No |
| site_5451 | 16.71 | 16.32 | -0.39 | Yes |
| site_5454 | 9.26 | 8.70 | -0.56 | Yes |
| site_5455 | 9.42 | 9.74 | +0.32 | No |
| site_5449 | 10.73 | 10.95 | +0.22 | No |
| site_5456 | 14.32 | 14.11 | -0.21 | Yes |

**Station Consistency:** 5/9 stations improved

---

## Feature Importance (Random Forest)

| Feature | Importance |
|---------|------------|
| temp_x_rh | 0.265 |
| precipitation_daily_m | 0.184 |
| relative_humidity_daily_pct | 0.182 |
| wind_speed_daily_ms | 0.143 |
| surface_pressure_daily_hpa | 0.072 |
| temp_x_wind | 0.047 |
| temp_squared | 0.038 |
| temperature_daily_c | 0.036 |
| month | 0.018 |
| season | 0.015 |
| precip_indicator | 0.001 |

**Note:** Feature importance does not imply causality.

---

## Analysis

### Improvement Assessment (Corrected)

The V2 experiment shows a **very small improvement** over V1:

- MAE improved by 0.10 (0.8%)
- RMSE improved by 0.08 (0.5%)
- R² improved by 0.006

However, **only 5 out of 9 stations improved**, which is not
consistent across held-out stations.

### Scientific Interpretation

1. **temp_x_rh** is the most important feature (26.5%), suggesting
   that the interaction between temperature and humidity has
   predictive value for PM2.5.

2. **Precipitation** features are important (18.4% for daily_m,
   0.1% for indicator), indicating washout effects.

3. **Temporal features** (month, season) have low importance,
   suggesting that the ERA5 meteorological variables already
   capture seasonal patterns.

### Conclusion

The improvement is **not meaningful or consistent** across stations.
The V1 baseline remains the best model.

---

## Success Criterion

A new experiment is considered an improvement only if it provides a
meaningful and reasonably consistent improvement across held-out
stations, not merely a better overall average caused by one station.

**Result:** V2 does not meet the success criterion.

---

## Next Steps

1. V1 baseline remains best for production use
2. Consider other improvement strategies:
   - More sophisticated feature engineering
   - Different model architectures
   - Additional data sources
   - Hyperparameter tuning
3. AOD optimization remains a separate future experiment

---

**Status:** CANONICAL - This document describes the feature engineering experiment.
