# PM2.5 Pilot 2025 Baseline Model

**Status:** CANONICAL
**Version:** 1.0
**Generated:** 2026-09-09T19:34:30.136328
**Updated:** 2026-09-09T19:34:30.136334

---

## 1. Dataset

**500-row 2025 pilot**

**File:** `data/curated/air_quality/ahmedabad_pm25_station_day_2025_pilot_500.parquet`

**Rows:** 500

**Stations:** 9

**ERA5-complete:** 500

**AOD-complete:** 92

---

## 2. Target

**daily_pm25_ug_m3** (ug/m3)

**Definition:** Mean of valid hourly PM2.5 observations (minimum 18 hours)

---

## 3. Models

### Model A: ERA5-only

**Features:**
1. temperature_daily_c
2. relative_humidity_daily_pct
3. wind_speed_daily_ms
4. surface_pressure_daily_hpa
5. precipitation_daily_m

### Model B: ERA5 + strict MAIAC AOD

**Features:**
1. temperature_daily_c
2. relative_humidity_daily_pct
3. wind_speed_daily_ms
4. surface_pressure_daily_hpa
5. precipitation_daily_m
6. strict_aod_550

---

## 4. Models Trained

1. Ridge Regression
2. Random Forest
3. Gradient Boosting

---

## 5. Validation

**Method:** Leave-One-Station-Out (LOSO)

For each of 9 stations:
- Hold that station completely out
- Train on other 8 stations
- Test on held-out station

---

## 6. Leakage Audit

**Status:** PASS

- No station leakage detected
- StandardScaler fitted only on training fold
- No test-set information influences preprocessing

---

## 7. Preprocessing

**StandardScaler** fitted inside each training fold only.

No test-set information may influence preprocessing.

---

## 8. Naive Baseline

**MAE:** 19.49

**Interpretation:** Predicting training-fold mean

---

## 9. ERA5-Only Results (Dataset A1)

| Model | MAE | RMSE | R2 | Bias |
|-------|-----|------|----|------|
| Ridge | 14.56 | 18.72 | 0.335 | -0.00 |
| Random Forest | 12.17 | 15.75 | 0.500 | +0.37 |
| Gradient Boosting | 12.53 | 16.39 | 0.446 | +0.51 |

---

## 10. AOD Subset Results (92 rows)

### Model A2: ERA5-only on AOD subset

| Model | MAE | RMSE | R2 | Bias |
|-------|-----|------|----|------|
| Ridge | 15.79 | 18.72 | -0.456 | -2.82 |
| Random Forest | 17.58 | 21.27 | -0.852 | -3.97 |
| Gradient Boosting | 18.96 | 23.02 | -1.170 | -3.83 |

### Model B: ERA5 + AOD on AOD subset

| Model | MAE | RMSE | R2 | Bias |
|-------|-----|------|----|------|
| Ridge | 15.75 | 18.51 | -0.409 | -2.90 |
| Random Forest | 17.83 | 20.91 | -0.816 | -3.79 |
| Gradient Boosting | 20.89 | 24.40 | -1.609 | -3.37 |

---

## 11. AOD Added-Value Comparison

| Model | delta-MAE | delta-R2 |
|-------|-----------|----------|
| Ridge | -0.04 | +0.047 |
| Random Forest | +0.25 | +0.036 |
| Gradient Boosting | +1.93 | -0.439 |

**Interpretation:**
- Ridge: Slight improvement with AOD
- Random Forest: Slight decline with AOD
- Gradient Boosting: Overfits on small 92-row subset

---

## 12. Interpretation

- **RF is current pilot winner** (MAE=12.17, R2=0.500)
- **AOD added value is mixed**
- **AOD evidence is limited** by only 92 strict-AOD rows
- **Model is not production-ready**
- **Result is a pilot baseline**

---

## 13. What This Model Does NOT Do

- **NO** final 1-km PM2.5 surface yet
- **NO** final ward exposure yet
- **NO** health-outcome model yet
- **NO** production deployment

---

## 14. Experiment Log

**File:** `data/models/pm25_pilot_experiment_log.csv`

**Status:** Baseline frozen - do not overwrite

---

**Status:** CANONICAL - This is the authoritative description of the first model experiment.

---

## 15. Git Version History

| Commit | Stage | Description |
|--------|-------|-------------|
| 96962e2 | Stage 5 | Implement 500-row PM2.5 pilot model with ERA5 extraction and LOSO validation |
| 179a074 | Stage 6 | Freeze baseline and resolve data version discrepancy |

**Baseline frozen in commit:** 179a074
**Do not overwrite these results.**
