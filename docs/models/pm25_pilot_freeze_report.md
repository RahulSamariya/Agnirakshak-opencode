# PM2.5 Pilot Baseline Freeze and Improvement Phase

**Generated:** 2026-09-09T19:09:44.041364
**Status:** BASELINE FROZEN - READY FOR FEATURE ENGINEERING

---

## 1. Canonical 2025 Row Count

| Metric | Count |
|--------|-------|
| Total station-days | 3285 |
| Eligible station-days | 2780 |
| Stations | 9 |
| Date range | 2025-01-01 to 2025-12-31 |

**Note:** Previous driver CSV had 2737 rows (43 fewer Maninagar station-days).
Canonical source is now the parquet file. Old driver preserved for provenance.

---

## 2. Baseline Random Forest (FROZEN)

| Metric | Value |
|--------|-------|
| MAE | 12.17 |
| RMSE | 15.75 |
| R2 | 0.500 |
| Bias | +0.37 |
| Features | ERA5 (5 predictors) |
| Validation | Leave-One-Station-Out |
| Training rows | 444-445 per fold |
| Test rows | 55-56 per fold |

**Status:** FROZEN - Do not overwrite

---

## 3. Feature Engineering: READY

### Candidate Features (Controlled Experiment)

| # | Feature | Description | Leakage Risk |
|---|---------|-------------|--------------|
| 1 | month | Calendar month (1-12) | None |
| 2 | season | Season category | None |
| 3 | temp_x_humidity | Temperature x Humidity interaction | None |
| 4 | wind_x_temp | Wind speed x Temperature interaction | None |
| 5 | precip_indicator | Binary precipitation indicator | None |
| 6 | temp_lag1d | Temperature lagged 1 day | LOW - requires same-station data |
| 7 | humidity_lag1d | Humidity lagged 1 day | LOW - requires same-station data |

### Experiment Design

1. **Experiment 1:** Add month/season features
2. **Experiment 2:** Add interaction terms (temp_x_humidity, wind_x_temp)
3. **Experiment 3:** Add precipitation indicator
4. **Experiment 4:** All features combined
5. **Experiment 5:** Lagged features (if validated safe)

### Leakage Prevention

- All features use only information available at or before prediction date
- Preprocessing fitted inside each training fold only
- StandardScaler applied per-fold

---

## 4. Data Version

| Item | Status |
|------|--------|
| Canonical source | `data/curated/air_quality/ahmedabad_pm25_station_day_2025.parquet` |
| Canonical count | 2780 eligible station-days |
| Old driver | `data/staging/earth_engine/ahmedabad_pm25_station_days_2025_old.csv` |
| Updated driver | `data/staging/earth_engine/ahmedabad_pm25_station_days_2025.csv` |
| Documentation | `data/metadata/canonical_2025_target_version.md` |

---

## 5. Experiment Log

| Experiment | Features | Model | MAE | RMSE | R2 | Notes |
|------------|----------|-------|-----|------|----|-------|
| baseline | ERA5 | Ridge | 14.56 | 18.72 | 0.335 | Frozen baseline |
| baseline | ERA5 | RandomForest | 12.17 | 15.75 | 0.5 | Frozen baseline |
| baseline | ERA5 | GradientBoosting | 12.53 | 16.39 | 0.446 | Frozen baseline |
| baseline | ERA5-subset | Ridge | 15.79 | 18.72 | -0.456 | Frozen baseline |
| baseline | ERA5-subset | RandomForest | 17.58 | 21.27 | -0.852 | Frozen baseline |
| baseline | ERA5-subset | GradientBoosting | 18.96 | 23.02 | -1.17 | Frozen baseline |
| baseline | ERA5+AOD | Ridge | 15.75 | 18.51 | -0.409 | Frozen baseline |
| baseline | ERA5+AOD | RandomForest | 17.83 | 20.91 | -0.816 | Frozen baseline |
| baseline | ERA5+AOD | GradientBoosting | 20.89 | 24.4 | -1.609 | Frozen baseline |

---

## 6. Next Experiment

**Recommended:** Experiment 1 - Add month/season features

**Rationale:**
- PM2.5 has strong seasonal patterns
- Month/season captures monsoon, winter pollution, etc.
- No temporal leakage risk
- Easy to implement and interpret

**Features to add:**
- month (1-12)
- season (winter/summer/monsoon/post-monsoon)

**Models to test:**
- Random Forest (primary)
- Ridge (comparison)

**Validation:** Leave-One-Station-Out (same as baseline)

---

## 7. Files Created

| File | Description |
|------|-------------|
| `data/models/pm25_pilot_experiment_log.csv` | Experiment tracking |
| `data/metadata/canonical_2025_target_version.md` | Data version docs |
| `data/staging/earth_engine/ahmedabad_pm25_station_days_2025_old.csv` | Old driver (provenance) |
| `docs/models/pm25_pilot_freeze_report.md` | This report |

---

## 8. Summary

| Item | Status |
|------|--------|
| Baseline frozen | YES |
| Data version resolved | YES |
| Feature engineering designed | YES |
| Experiment tracking created | YES |
| Ready for next experiment | YES |

**DO NOT:**
- Generate 1-km PM2.5 surface
- Integrate with HSRI
- Start health-outcome ML

**NEXT:** Run Experiment 1 (month/season features)

---

**Status:** BASELINE FROZEN - READY FOR FEATURE ENGINEERING
