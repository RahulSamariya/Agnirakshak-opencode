"""
Step 2: Create pilot dataset and train models
=============================================
Joins CPCB + MAIAC + ERA5, creates Dataset A and B,
trains Ridge/RF/GBM with Leave-One-Station-Out validation.
"""

import math
import os
import warnings
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings('ignore')

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(".")
CURATED_DIR = BASE_DIR / "data" / "curated" / "air_quality"
STAGING_DIR = BASE_DIR / "data" / "staging" / "earth_engine"
MODELS_DIR = BASE_DIR / "data" / "models"
DOCS_DIR = BASE_DIR / "docs" / "models"

PM25_FILE = CURATED_DIR / "ahmedabad_pm25_station_day_2025.parquet"
MAIAC_FILE = CURATED_DIR / "ahmedabad_pm25_maiac_station_day_2025.parquet"
ERA5_FILE = STAGING_DIR / "ahmedabad_pm25_era5_pilot_500.csv"
PILOT_OUTPUT = CURATED_DIR / "ahmedabad_pm25_station_day_2025_pilot_500.parquet"

RESULTS_CSV = MODELS_DIR / "pm25_pilot_500_results.csv"
HOLDOUT_CSV = MODELS_DIR / "pm25_pilot_500_station_holdout.csv"
PREDICTIONS_PARQUET = MODELS_DIR / "pm25_pilot_500_predictions.parquet"
MODEL_DIR = MODELS_DIR / "pm25_pilot_500"
DOCS_FILE = DOCS_DIR / "pm25_pilot_500.md"

RANDOM_SEED = 42
PILOT_SIZE = 500

STATION_NAMES = {
    "site_5453": "Chandkheda",
    "site_5450": "Gyaspur",
    "site_308": "Maninagar",
    "site_5452": "Raikhad",
    "site_5451": "Rakhial",
    "site_5454": "SAC ISRO Bopal",
    "site_5455": "SAC ISRO Satellite",
    "site_5449": "SVPS Stadium",
    "site_5456": "SVPI Airport Hansol",
}

print("=" * 70)
print("STEP 2: CREATE PILOT DATASET AND TRAIN MODELS")
print("=" * 70)
print(f"Started: {datetime.now().isoformat()}")
print()

# ============================================================
# STEP 1: LOAD AND JOIN DATA
# ============================================================

print("[1/6] Loading and joining data...")

pm25 = pd.read_parquet(PM25_FILE)
pm25['date'] = pd.to_datetime(pm25['date'])
eligible = pm25[pm25['daily_qc_flag'] == 'ELIGIBLE'].copy()

maiac = pd.read_parquet(MAIAC_FILE)
maiac['date'] = pd.to_datetime(maiac['date'])

era5 = pd.read_csv(ERA5_FILE)
era5['date'] = pd.to_datetime(era5['date'])

# Select 500 pilot rows
np.random.seed(RANDOM_SEED)
stations = eligible['station_id'].unique()
spp = PILOT_SIZE // len(stations)
rem = PILOT_SIZE % len(stations)

selected = []
i = 0
for station in stations:
    sdf = eligible[eligible['station_id'] == station]
    ns = spp + (1 if i < rem else 0)
    months = sdf['date'].dt.month.unique()
    spm = math.ceil(ns / len(months))
    sels = []
    for m in months:
        mf = sdf[sdf['date'].dt.month == m]
        if len(mf) > 0:
            sels.append(mf.sample(n=min(spm, len(mf)), random_state=RANDOM_SEED))
    selected.append(pd.concat(sels).head(ns))
    i += 1

pilot = pd.concat(selected).head(PILOT_SIZE).reset_index(drop=True)

# Join MAIAC
pilot = pilot.merge(
    maiac[['station_id', 'date', 'strict_aod_550', 'strict_aod_uncertainty', 'strict_aod_available']],
    on=['station_id', 'date'], how='left'
)
pilot['strict_aod_available'] = pilot['strict_aod_available'].fillna(False).astype(bool)

# Join ERA5
pilot = pilot.merge(era5, on=['station_id', 'date'], how='left', suffixes=('', '_era5'))
pilot['era5_available'] = pilot['meteo_available'].fillna(False).astype(bool)
pilot['fully_matched'] = pilot['strict_aod_available'] & pilot['era5_available']

print(f"  Total pilot rows: {len(pilot)}")
print(f"  ERA5-complete: {pilot['era5_available'].sum()}")
print(f"  AOD-complete: {pilot['strict_aod_available'].sum()}")
print(f"  Fully-complete: {pilot['fully_matched'].sum()}")
print()

# Save pilot dataset
final_cols = [
    'station_id', 'station_name', 'date', 'latitude', 'longitude',
    'daily_pm25_ug_m3',
    'strict_aod_550', 'strict_aod_uncertainty', 'strict_aod_available',
    'temperature_daily_c', 'relative_humidity_daily_pct', 'wind_speed_daily_ms',
    'surface_pressure_daily_hpa', 'precipitation_daily_m',
    'era5_available', 'fully_matched',
]

CURATED_DIR.mkdir(parents=True, exist_ok=True)
pilot[final_cols].to_parquet(PILOT_OUTPUT, index=False)
print(f"  Saved pilot: {PILOT_OUTPUT}")
print()

# ============================================================
# STEP 2: DEFINE DATASETS
# ============================================================

print("[2/6] Defining modeling datasets...")

# Dataset A1: ERA5-only on all eligible pilot rows
dataset_a1 = pilot[pilot['era5_available']].copy()

# Dataset A2: ERA5-only on AOD-available subset
dataset_a2 = pilot[pilot['era5_available'] & pilot['strict_aod_available']].copy()

# Dataset B: ERA5+AOD on AOD-available subset
dataset_b = pilot[pilot['era5_available'] & pilot['strict_aod_available']].copy()

ERA5_FEATURES = ['temperature_daily_c', 'relative_humidity_daily_pct',
                 'wind_speed_daily_ms', 'surface_pressure_daily_hpa', 'precipitation_daily_m']
AOD_FEATURES = ERA5_FEATURES + ['strict_aod_550']
TARGET = 'daily_pm25_ug_m3'

print(f"  Dataset A1 (ERA5-all): {len(dataset_a1)} rows")
print(f"  Dataset A2 (ERA5-subset): {len(dataset_a2)} rows")
print(f"  Dataset B (ERA5+AOD): {len(dataset_b)} rows")
print()

# ============================================================
# STEP 3: LOSO VALIDATION FUNCTION
# ============================================================

print("[3/6] Defining LOSO validation...")

def loso_validate(X, y, stations, model_class, model_params, model_name):
    """Leave-One-Station-Out validation."""
    unique_stations = stations.unique()
    results = []

    for test_station in unique_stations:
        train_idx = stations != test_station
        test_idx = stations == test_station

        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Preprocessing inside fold
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train model
        model = model_class(**model_params)
        model.fit(X_train_scaled, y_train)

        # Predict
        y_pred = model.predict(X_test_scaled)

        # Metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred) if len(y_test) > 1 else np.nan
        bias = np.mean(y_pred - y_test)

        results.append({
            'station': test_station,
            'station_name': STATION_NAMES.get(test_station, test_station),
            'n_test': len(y_test),
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'bias': bias,
            'y_true': y_test if isinstance(y_test, np.ndarray) else y_test.values,
            'y_pred': y_pred,
        })

    return results

def aggregate_results(results):
    """Aggregate LOSO results."""
    df = pd.DataFrame(results)
    return {
        'mae_mean': df['mae'].mean(),
        'mae_std': df['mae'].std(),
        'rmse_mean': df['rmse'].mean(),
        'rmse_std': df['rmse'].std(),
        'r2_mean': df['r2'].mean(),
        'r2_std': df['r2'].std(),
        'bias_mean': df['bias'].mean(),
        'bias_std': df['bias'].std(),
        'n_test_mean': df['n_test'].mean(),
    }

print("  LOSO function defined")
print()

# ============================================================
# STEP 4: TRAIN MODELS
# ============================================================

print("[4/6] Training models...")

MODELS = {
    'Ridge': (Ridge, {'alpha': 1.0}),
    'RandomForest': (RandomForestRegressor, {'n_estimators': 100, 'max_depth': 10, 'random_state': RANDOM_SEED}),
    'GradientBoosting': (GradientBoostingRegressor, {'n_estimators': 100, 'max_depth': 5, 'learning_rate': 0.1, 'random_state': RANDOM_SEED}),
}

all_results = []
all_holdout = []
all_predictions = []

# Model A1: ERA5-only on all eligible rows
print("  Model A1: ERA5-only (all eligible)...")
X_a1 = dataset_a1[ERA5_FEATURES].values
y_a1 = dataset_a1[TARGET].values
stations_a1 = dataset_a1['station_id'].values

for model_name, (model_class, model_params) in MODELS.items():
    results = loso_validate(X_a1, y_a1, stations_a1, model_class, model_params, model_name)
    agg = aggregate_results(results)
    agg['model'] = model_name
    agg['dataset'] = 'A1_ERa5_all'
    all_results.append(agg)

    for r in results:
        all_holdout.append({
            'model': model_name,
            'dataset': 'A1_ERa5_all',
            'station': r['station'],
            'station_name': r['station_name'],
            'n_test': r['n_test'],
            'mae': r['mae'],
            'rmse': r['rmse'],
            'r2': r['r2'],
            'bias': r['bias'],
        })
        for i, (true, pred) in enumerate(zip(r['y_true'], r['y_pred'])):
            all_predictions.append({
                'model': model_name,
                'dataset': 'A1_ERa5_all',
                'station': r['station'],
                'y_true': true,
                'y_pred': pred,
            })

print(f"    Completed {len(MODELS)} models")
print()

# Model A2: ERA5-only on AOD-subset
print("  Model A2: ERA5-only (AOD-subset)...")
X_a2 = dataset_a2[ERA5_FEATURES].values
y_a2 = dataset_a2[TARGET].values
stations_a2 = dataset_a2['station_id'].values

for model_name, (model_class, model_params) in MODELS.items():
    results = loso_validate(X_a2, y_a2, stations_a2, model_class, model_params, model_name)
    agg = aggregate_results(results)
    agg['model'] = model_name
    agg['dataset'] = 'A2_ERa5_subset'
    all_results.append(agg)

    for r in results:
        all_holdout.append({
            'model': model_name,
            'dataset': 'A2_ERa5_subset',
            'station': r['station'],
            'station_name': r['station_name'],
            'n_test': r['n_test'],
            'mae': r['mae'],
            'rmse': r['rmse'],
            'r2': r['r2'],
            'bias': r['bias'],
        })
        for i, (true, pred) in enumerate(zip(r['y_true'], r['y_pred'])):
            all_predictions.append({
                'model': model_name,
                'dataset': 'A2_ERa5_subset',
                'station': r['station'],
                'y_true': true,
                'y_pred': pred,
            })

print(f"    Completed {len(MODELS)} models")
print()

# Model B: ERA5+AOD on AOD-subset
print("  Model B: ERA5+AOD (AOD-subset)...")
X_b = dataset_b[AOD_FEATURES].values
y_b = dataset_b[TARGET].values
stations_b = dataset_b['station_id'].values

for model_name, (model_class, model_params) in MODELS.items():
    results = loso_validate(X_b, y_b, stations_b, model_class, model_params, model_name)
    agg = aggregate_results(results)
    agg['model'] = model_name
    agg['dataset'] = 'B_ERa5_AOD'
    all_results.append(agg)

    for r in results:
        all_holdout.append({
            'model': model_name,
            'dataset': 'B_ERa5_AOD',
            'station': r['station'],
            'station_name': r['station_name'],
            'n_test': r['n_test'],
            'mae': r['mae'],
            'rmse': r['rmse'],
            'r2': r['r2'],
            'bias': r['bias'],
        })
        for i, (true, pred) in enumerate(zip(r['y_true'], r['y_pred'])):
            all_predictions.append({
                'model': model_name,
                'dataset': 'B_ERa5_AOD',
                'station': r['station'],
                'y_true': true,
                'y_pred': pred,
            })

print(f"    Completed {len(MODELS)} models")
print()

# ============================================================
# STEP 5: SAVE RESULTS
# ============================================================

print("[5/6] Saving results...")

MODELS_DIR.mkdir(parents=True, exist_ok=True)

results_df = pd.DataFrame(all_results)
results_df.to_csv(RESULTS_CSV, index=False)
print(f"  Saved: {RESULTS_CSV}")

holdout_df = pd.DataFrame(all_holdout)
holdout_df.to_csv(HOLDOUT_CSV, index=False)
print(f"  Saved: {HOLDOUT_CSV}")

predictions_df = pd.DataFrame(all_predictions)
predictions_df.to_parquet(PREDICTIONS_PARQUET, index=False)
print(f"  Saved: {PREDICTIONS_PARQUET}")
print()

# ============================================================
# STEP 6: GENERATE REPORT
# ============================================================

print("[6/6] Generating report...")

DOCS_DIR.mkdir(parents=True, exist_ok=True)

# Summary statistics
era5_count = pilot['era5_available'].sum()
aod_count = pilot['strict_aod_available'].sum()
full_count = pilot['fully_matched'].sum()
stations_list = sorted(pilot['station_id'].unique())

# A2 vs B comparison
a2_results = results_df[results_df['dataset'] == 'A2_ERa5_subset']
b_results = results_df[results_df['dataset'] == 'B_ERa5_AOD']

comparison = []
for model_name in MODELS.keys():
    a2_row = a2_results[a2_results['model'] == model_name].iloc[0]
    b_row = b_results[b_results['model'] == model_name].iloc[0]
    comparison.append({
        'model': model_name,
        'delta_mae': b_row['mae_mean'] - a2_row['mae_mean'],
        'delta_rmse': b_row['rmse_mean'] - a2_row['rmse_mean'],
        'delta_r2': b_row['r2_mean'] - a2_row['r2_mean'],
    })

comp_df = pd.DataFrame(comparison)

# Build markdown report
report = f"""# PM2.5 Pilot Model Report (500-Row)

**Generated:** {datetime.now().isoformat()}
**Status:** PILOT MODEL (not final/production)

---

## 1. Dataset Summary

| Metric | Count |
|--------|-------|
| Total Pilot Rows | {len(pilot)} |
| ERA5-Complete Rows | {era5_count} |
| AOD-Complete Rows | {aod_count} |
| Fully Complete Rows | {full_count} |
| Stations | {len(stations_list)} |

**Stations:** {', '.join(STATION_NAMES[s] for s in stations_list)}

---

## 2. Model A — ERA5 Only

### A1: All Eligible Rows ({len(dataset_a1)} rows)

| Model | MAE | RMSE | R2 | Bias |
|-------|-----|------|----|------|
"""

for _, row in results_df[results_df['dataset'] == 'A1_ERa5_all'].iterrows():
    report += f"| {row['model']} | {row['mae_mean']:.2f} +/- {row['mae_std']:.2f} | {row['rmse_mean']:.2f} +/- {row['rmse_std']:.2f} | {row['r2_mean']:.3f} +/- {row['r2_std']:.3f} | {row['bias_mean']:.2f} +/- {row['bias_std']:.2f} |\n"

report += f"""
### A2: AOD-Available Subset ({len(dataset_a2)} rows)

| Model | MAE | RMSE | R2 | Bias |
|-------|-----|------|----|------|
"""

for _, row in results_df[results_df['dataset'] == 'A2_ERa5_subset'].iterrows():
    report += f"| {row['model']} | {row['mae_mean']:.2f} +/- {row['mae_std']:.2f} | {row['rmse_mean']:.2f} +/- {row['rmse_std']:.2f} | {row['r2_mean']:.3f} +/- {row['r2_std']:.3f} | {row['bias_mean']:.2f} +/- {row['bias_std']:.2f} |\n"

report += f"""
---

## 3. Model B - ERA5 + MAIAC AOD

### B: AOD-Available Subset ({len(dataset_b)} rows)

| Model | MAE | RMSE | R2 | Bias |
|-------|-----|------|----|------|
"""

for _, row in results_df[results_df['dataset'] == 'B_ERa5_AOD'].iterrows():
    report += f"| {row['model']} | {row['mae_mean']:.2f} +/- {row['mae_std']:.2f} | {row['rmse_mean']:.2f} +/- {row['rmse_std']:.2f} | {row['r2_mean']:.3f} +/- {row['r2_std']:.3f} | {row['bias_mean']:.2f} +/- {row['bias_std']:.2f} |\n"

report += f"""
---

## 4. Matched-Subset Comparison (A2 vs B)

| Model | delta-MAE | delta-RMSE | delta-R2 |
|-------|-----------|------------|----------|
"""

for _, row in comp_df.iterrows():
    report += f"| {row['model']} | {row['delta_mae']:+.2f} | {row['delta_rmse']:+.2f} | {row['delta_r2']:+.3f} |\n"

report += """
**Interpretation:**
- Negative delta-MAE/RMSE = AOD improves prediction
- Positive delta-R2 = AOD improves variance explained

---

## 5. Per-Station LOSO Results (Best Model)

"""

# Get best model from B dataset
best_b = b_results.loc[b_results['mae_mean'].idxmin()]
best_model = best_b['model']
report += f"**Best model:** {best_model} (Dataset B)\n\n"

report += "| Station | N Test | MAE | RMSE | R2 | Bias |\n"
report += "|---------|--------|-----|------|----|------|\n"

station_holdout = holdout_df[(holdout_df['model'] == best_model) & (holdout_df['dataset'] == 'B_ERa5_AOD')]
for _, row in station_holdout.iterrows():
    report += f"| {row['station_name']} | {row['n_test']} | {row['mae']:.2f} | {row['rmse']:.2f} | {row['r2']:.3f} | {row['bias']:.2f} |\n"

report += f"""
---

## 6. Methodology

- **Validation:** Leave-One-Station-Out (LOSO)
- **Preprocessing:** StandardScaler fitted inside each training fold
- **Features (ERA5):** temperature, RH, wind speed, surface pressure, precipitation
- **Features (AOD):** ERA5 + strict_aod_550
- **Target:** daily_pm25_ug_m3 (ug/m3)
- **No station_id, lat/lon, or target-derived features used**

---

## 7. Status

This is a **PILOT MODEL** to assess whether the modeling approach is
promising before scaling to the larger 2023-2025 dataset.

Do NOT call this a final, production, or operational model.
"""

with open(DOCS_FILE, 'w') as f:
    f.write(report)
print(f"  Saved: {DOCS_FILE}")

print()
print("=" * 70)
print("ALL OUTPUTS GENERATED")
print("=" * 70)
print()
print("Files created:")
print(f"  {PILOT_OUTPUT}")
print(f"  {RESULTS_CSV}")
print(f"  {HOLDOUT_CSV}")
print(f"  {PREDICTIONS_PARQUET}")
print(f"  {DOCS_FILE}")
print()
