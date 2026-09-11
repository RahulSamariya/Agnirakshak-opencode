# Baseline Metric Discrepancy Audit Report

**Status:** CANONICAL
**Version:** 1.0
**Generated:** 2026-09-12

---

## Executive Summary

The metric discrepancy between the original frozen V1 baseline and the
feature-engineering experiment was caused by **different aggregation
methods**, not by different model implementations.

**Root Cause:** Station-level averaging vs pooled predictions.

---

## Original Frozen Baseline

**Source:** Commit 179a074 (feat: freeze baseline and resolve data version discrepancy)

| Metric | Value |
|--------|-------|
| MAE | 12.17 |
| RMSE | 15.75 |
| R² | 0.500 |
| Bias | 0.37 |

**Implementation Details:**
- Script: `scripts/step2_train_pilot_models.py`
- Dataset: `data/curated/air_quality/ahmedabad_pm25_station_day_2025_pilot_500.parquet`
- Features: ERA5 (temperature, RH, wind speed, surface pressure, precipitation)
- Validation: Leave-One-Station-Out (LOSO)
- Preprocessing: StandardScaler inside each fold
- Model: RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
- Aggregation: **Mean of station-level metrics**

---

## Feature-Engineering Experiment

**Source:** Commit 7d8ec5c (feat: feature engineering experiment)

| Metric | Value |
|--------|-------|
| MAE | 12.17 |
| RMSE | 16.40 |
| R² | 0.552 |
| Bias | 0.35 |

**Implementation Details:**
- Script: `scripts/feature_engineering_experiment.py`
- Dataset: Same pilot dataset
- Features: ERA5 + engineered features
- Validation: Leave-One-Station-Out (LOSO)
- Preprocessing: **No StandardScaler**
- Model: RandomForestRegressor(n_estimators=100, random_state=42) - **No max_depth**
- Aggregation: **Pooled predictions**

---

## Root Cause Analysis

### Difference 1: Aggregation Method

| Method | Description | RMSE | R² |
|--------|-------------|------|----|
| Station-level averaging | Calculate metrics per station, then average | 15.75 | 0.500 |
| Pooled predictions | Pool all predictions, then calculate metrics | 16.34 | 0.555 |

**Why this matters:**
- Station-level averaging weights each station equally
- Pooled predictions weight each observation equally
- Stations with more observations have more influence in pooled method
- This explains why RMSE increased and R² increased

### Difference 2: StandardScaler

| Method | Description |
|--------|-------------|
| Original | StandardScaler fitted inside each fold |
| Current | No StandardScaler (raw features) |

**Impact:** Minimal for tree-based models, but affects Ridge regression.

### Difference 3: max_depth

| Method | Description |
|--------|-------------|
| Original | max_depth=10 (limited tree depth) |
| Current | No max_depth (unlimited tree depth) |

**Impact:** Affects model complexity and generalization.

---

## Ablation Tests

| Test | StandardScaler | max_depth | Aggregation | RMSE | R² |
|------|----------------|-----------|-------------|------|----|
| Original | Yes | 10 | Station-level | 15.75 | 0.500 |
| Test 1 | Yes | None | Pooled | 16.40 | 0.552 |
| Test 2 | No | 10 | Pooled | 16.34 | 0.555 |
| Test 3 | Yes | 10 | Pooled | 16.34 | 0.555 |

**Conclusion:** The aggregation method is the primary cause of the discrepancy.

---

## Corrected V2 Experiment

After correcting the protocol to match the original frozen baseline:

| Metric | V1 (Corrected) | V2 (Corrected) | Delta |
|--------|----------------|----------------|-------|
| MAE | 12.17 | 12.08 | +0.10 (+0.8%) |
| RMSE | 15.75 | 15.67 | +0.08 (+0.5%) |
| R² | 0.500 | 0.506 | +0.006 |

**Station Consistency:** 5/9 stations improved

---

## Final Assessment

### FROZEN_BASELINE_REMAINS_VALID: YES

The original frozen baseline was computed correctly with:
- StandardScaler inside each fold
- max_depth=10 for RandomForest
- Station-level averaging for metrics

### V1_METRIC_PROTOCOL_MATCH: YES

The corrected V1 now matches the original frozen baseline exactly.

### V2_COMPARISON_VALID: YES

The V2 comparison now uses the same protocol as the frozen V1.

### IMPROVEMENT: NO

The V2 experiment shows a very small improvement that is not meaningful:
- MAE improved by 0.10 (0.8%)
- RMSE improved by 0.08 (0.5%)
- R² improved by 0.006
- Only 5/9 stations improved

---

## Recommendations

1. **Keep original frozen baseline as authoritative**
   - MAE = 12.17, RMSE = 15.75, R² = 0.500

2. **Use station-level averaging for all future experiments**
   - This is the correct aggregation method
   - Ensures fair comparison across stations

3. **Standardize preprocessing**
   - Always use StandardScaler inside each fold
   - Always use max_depth=10 for RandomForest

4. **Focus on other improvement strategies**
   - Feature engineering shows minimal improvement
   - Consider hyperparameter tuning
   - Consider additional data sources

---

**Status:** CANONICAL - This document resolves the baseline metric discrepancy.
