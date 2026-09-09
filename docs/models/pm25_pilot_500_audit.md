# PM2.5 Pilot Model Audit Report

**Generated:** 2026-09-09T18:58:21.070929
**Status:** AUDIT COMPLETE

---

## 1. Data Count Reconciliation

| Metric | Value |
|--------|-------|
| OLD COUNT (driver CSV) | 2737 |
| CURRENT COUNT (parquet eligible) | 2780 |
| DIFFERENCE | 43 |

**REASON:** Driver CSV created from earlier CPCB data version. Maninagar (site_308) has 43 additional eligible station-days in current parquet not present in driver CSV.

---

## 2. Pilot Integrity: PASS

| Check | Result |
|-------|--------|
| rows | 500 |
| unique station/date | 500 |
| duplicates | 0 |
| stations | 9 |
| target from canonical CPCB | YES |

---

## 3. LOSO Implementation: PASS

- All 9 stations used as test sets
- 8 training stations, 1 test station per fold
- No overlap between train and test
- Station leakage = 0

---

## 4. Preprocessing Leakage: PASS

- StandardScaler fitted only on training fold
- No test-set information influences preprocessing

---

## 5. Feature Set: PASS

**ERA5 Features:** temperature_daily_c, relative_humidity_daily_pct, wind_speed_daily_ms, surface_pressure_daily_hpa, precipitation_daily_m

**AOD Features:** ERA5 + strict_aod_550

No station_id, target-derived, future, or duplicate features used.

---

## 6. Model B Full Results (92 rows)

| Model | MAE | RMSE | R2 | Bias |
|-------|-----|------|----|------|
| Ridge | 15.75 | 18.51 | -0.409 | -2.90 |
| RandomForest | 17.83 | 20.91 | -0.816 | -3.79 |
| GradientBoosting | 20.89 | 24.40 | -1.609 | -3.37 |

---

## 7. Fair AOD Comparison

| Model | A1-MAE | A2-MAE | B-MAE | delta-MAE | A1-R2 | A2-R2 | B-R2 | delta-R2 |
|-------|--------|--------|-------|-----------|-------|-------|------|----------|
| Ridge | 14.56 | 15.79 | 15.75 | -0.04 | 0.335 | -0.456 | -0.409 | +0.047 |
| RandomForest | 12.17 | 17.58 | 17.83 | +0.25 | 0.500 | -0.852 | -0.816 | +0.036 |
| GradientBoosting | 12.53 | 18.96 | 20.89 | +1.93 | 0.446 | -1.170 | -1.609 | -0.439 |

---

## 8. AOD Sample Distribution

- Stations represented: 9
- Months represented: 7
- AOD missingness is strongly seasonal

---

## 9. Naive Baseline

| Metric | Naive | Random Forest |
|--------|-------|---------------|
| MAE | 21.45 | 12.17 |
| R2 | -0.375 | 0.500 |

RF substantially outperforms naive baseline.

---

## 10. Feature Importance

**Random Forest:** wind_speed_daily_ms most important, followed by temperature and humidity.

**Ridge:** wind_speed_daily_ms has largest standardized coefficient.

---

## 11. Pilot Conclusion: PROMISING

**Justification:**
- Station-held-out performance: RF R2=0.50 (meaningful skill)
- Comparison to naive baseline: RF substantially outperforms
- Consistency across stations: Most stations show positive R2
- AOD added value: Mixed (limited by 18.4% coverage)

**Recommendations:**
1. Scale to full 2023-2025 dataset
2. Consider ERA5-only as primary model
3. Investigate station-specific patterns

---

**PILOT STATUS: PROMISING - Ready for scaling investigation**
