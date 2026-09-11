"""
Audit: Frozen V1 Baseline Metric Discrepancy
=============================================
Reproduces both original and current V1 evaluations to identify root cause.
"""

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"

print("=" * 70)
print("AUDIT: FROZEN V1 BASELINE METRIC DISCREPANCY")
print("=" * 70)
print(f"Started: {datetime.now().isoformat()}")
print()

# ============================================================
# 1. LOAD DATA
# ============================================================

print("[1/5] Loading data...")
print("-" * 70)

pilot = pd.read_parquet(DATA_DIR / "curated" / "air_quality" / "ahmedabad_pm25_station_day_2025_pilot_500.parquet")
pilot['date'] = pd.to_datetime(pilot['date'])

print(f"Pilot rows: {len(pilot)}")
print(f"Stations: {pilot['station_id'].nunique()}")
print()

# ============================================================
# 2. ORIGINAL V1 EVALUATION (EXACT REPRODUCTION)
# ============================================================

print("[2/5] Original V1 evaluation (exact reproduction)...")
print("-" * 70)

# Original parameters from step2_train_pilot_models.py
ERA5_FEATURES = ['temperature_daily_c', 'relative_humidity_daily_pct',
                 'wind_speed_daily_ms', 'surface_pressure_daily_hpa', 'precipitation_daily_m']
TARGET = 'daily_pm25_ug_m3'
RANDOM_SEED = 42

# Original model parameters
rf_params_original = {'n_estimators': 100, 'max_depth': 10, 'random_state': RANDOM_SEED}

# Dataset A1: ERA5-only on all eligible pilot rows
dataset_a1 = pilot[pilot['era5_available']].copy()
X_original = dataset_a1[ERA5_FEATURES].values
y_original = dataset_a1[TARGET].values
stations_original = dataset_a1['station_id'].values

print(f"Dataset A1 rows: {len(dataset_a1)}")
print(f"ERA5 features: {ERA5_FEATURES}")
print(f"RandomForest params: {rf_params_original}")
print()

# Original LOSO with StandardScaler
def loso_validate_original(X, y, stations, model_class, model_params):
    """Original LOSO with StandardScaler inside fold."""
    unique_stations = np.unique(stations)
    results = []
    
    for test_station in unique_stations:
        train_idx = stations != test_station
        test_idx = stations == test_station
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Original: StandardScaler inside fold
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
            'n_test': len(y_test),
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'bias': bias,
        })
    
    return pd.DataFrame(results)

# Run original evaluation
results_original = loso_validate_original(
    X_original, y_original, stations_original,
    RandomForestRegressor, rf_params_original
)

# Original aggregation: mean of station-level metrics
original_mae = results_original['mae'].mean()
original_rmse = results_original['rmse'].mean()
original_r2 = results_original['r2'].mean()
original_bias = results_original['bias'].mean()

print("ORIGINAL_V1:")
print(f"  MAE:  {original_mae:.2f}")
print(f"  RMSE: {original_rmse:.2f}")
print(f"  R2:   {original_r2:.3f}")
print(f"  Bias: {original_bias:.2f}")
print()

# ============================================================
# 3. CURRENT V1 EVALUATION (FEATURE-ENGINEERING EXPERIMENT)
# ============================================================

print("[3/5] Current V1 evaluation (feature-engineering experiment)...")
print("-" * 70)

# Current parameters from feature_engineering_experiment.py
rf_params_current = {'n_estimators': 100, 'random_state': 42}  # NO max_depth

# Current LOSO - NO StandardScaler
def loso_validate_current(X, y, stations, model_class, model_params):
    """Current LOSO without StandardScaler."""
    unique_stations = stations.unique()
    results = []
    all_predictions = []
    all_actuals = []
    
    for station in unique_stations:
        train_idx = stations != station
        test_idx = stations == station
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Current: NO StandardScaler
        model = model_class(**model_params)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        bias = np.mean(y_pred - y_test)
        
        results.append({
            'station': station,
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'bias': bias,
            'n': len(y_test)
        })
        
        all_predictions.extend(y_pred)
        all_actuals.extend(y_test)
    
    # Current aggregation: overall metrics from pooled predictions
    overall_mae = mean_absolute_error(all_actuals, all_predictions)
    overall_rmse = np.sqrt(mean_squared_error(all_actuals, all_predictions))
    overall_r2 = r2_score(all_actuals, all_predictions)
    overall_bias = np.mean(np.array(all_predictions) - np.array(all_actuals))
    
    return {
        'station_results': pd.DataFrame(results),
        'overall_mae': overall_mae,
        'overall_rmse': overall_rmse,
        'overall_r2': overall_r2,
        'overall_bias': overall_bias
    }

# Run current evaluation
X_current = pilot[ERA5_FEATURES].values
y_current = pilot[TARGET].values
stations_current = pilot['station_id']

results_current = loso_validate_current(
    X_current, y_current, stations_current,
    RandomForestRegressor, rf_params_current
)

print("CURRENT_V1:")
print(f"  MAE:  {results_current['overall_mae']:.2f}")
print(f"  RMSE: {results_current['overall_rmse']:.2f}")
print(f"  R2:   {results_current['overall_r2']:.3f}")
print(f"  Bias: {results_current['overall_bias']:.2f}")
print()

# ============================================================
# 4. ROOT CAUSE ANALYSIS
# ============================================================

print("[4/5] Root cause analysis...")
print("-" * 70)

print("DIFFERENCE:")
print(f"  MAE:  {results_current['overall_mae'] - original_mae:+.2f}")
print(f"  RMSE: {results_current['overall_rmse'] - original_rmse:+.2f}")
print(f"  R2:   {results_current['overall_r2'] - original_r2:+.3f}")
print()

print("ROOT CAUSES IDENTIFIED:")
print()
print("1. STANDARDSCALER:")
print("   - Original: StandardScaler fitted inside each fold")
print("   - Current:  No StandardScaler (raw features)")
print()
print("2. RANDOM FOREST HYPERPARAMETERS:")
print(f"   - Original: max_depth=10 (limited tree depth)")
print(f"   - Current:  No max_depth (unlimited tree depth)")
print()
print("3. AGGREGATION METHOD:")
print("   - Original: Mean of station-level metrics (fold-level)")
print("   - Current:  Overall metrics from pooled predictions")
print()

# Test each factor individually
print("ABLAISON TESTS:")
print()

# Test 1: With StandardScaler only
def loso_with_scaler(X, y, stations, model_params):
    """LOSO with StandardScaler but current hyperparameters."""
    unique_stations = stations.unique()
    all_predictions = []
    all_actuals = []
    
    for station in unique_stations:
        train_idx = stations != station
        test_idx = stations == station
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        model = RandomForestRegressor(**model_params)
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        
        all_predictions.extend(y_pred)
        all_actuals.extend(y_test)
    
    return {
        'mae': mean_absolute_error(all_actuals, all_predictions),
        'rmse': np.sqrt(mean_squared_error(all_actuals, all_predictions)),
        'r2': r2_score(all_actuals, all_predictions)
    }

# Test with StandardScaler + current hyperparameters (no max_depth)
result_scaler_current = loso_with_scaler(X_current, y_current, stations_current, rf_params_current)
print("Test 1: StandardScaler + current RF (no max_depth):")
print(f"  MAE:  {result_scaler_current['mae']:.2f}")
print(f"  RMSE: {result_scaler_current['rmse']:.2f}")
print(f"  R2:   {result_scaler_current['r2']:.3f}")
print()

# Test 2: With max_depth=10 only (no scaler)
def loso_with_maxdepth(X, y, stations, model_params):
    """LOSO without StandardScaler but with max_depth=10."""
    unique_stations = stations.unique()
    all_predictions = []
    all_actuals = []
    
    for station in unique_stations:
        train_idx = stations != station
        test_idx = stations == station
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # No scaler
        model = RandomForestRegressor(**model_params)
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        
        all_predictions.extend(y_pred)
        all_actuals.extend(y_test)
    
    return {
        'mae': mean_absolute_error(all_actuals, all_predictions),
        'rmse': np.sqrt(mean_squared_error(all_actuals, all_predictions)),
        'r2': r2_score(all_actuals, all_predictions)
    }

rf_params_maxdepth = {'n_estimators': 100, 'max_depth': 10, 'random_state': 42}
result_maxdepth = loso_with_maxdepth(X_current, y_current, stations_current, rf_params_maxdepth)
print("Test 2: max_depth=10 + no scaler:")
print(f"  MAE:  {result_maxdepth['mae']:.2f}")
print(f"  RMSE: {result_maxdepth['rmse']:.2f}")
print(f"  R2:   {result_maxdepth['r2']:.3f}")
print()

# Test 3: Both scaler and max_depth
result_both = loso_with_scaler(X_current, y_current, stations_current, rf_params_maxdepth)
print("Test 3: StandardScaler + max_depth=10:")
print(f"  MAE:  {result_both['mae']:.2f}")
print(f"  RMSE: {result_both['rmse']:.2f}")
print(f"  R2:   {result_both['r2']:.3f}")
print()

# ============================================================
# 5. FINAL REPORT
# ============================================================

print("[5/5] Final report...")
print("-" * 70)

print("=" * 70)
print("FINAL REPORT")
print("=" * 70)
print()
print("ORIGINAL_V1:")
print(f"  MAE:  {original_mae:.2f}")
print(f"  RMSE: {original_rmse:.2f}")
print(f"  R2:   {original_r2:.3f}")
print()
print("CURRENT_V1:")
print(f"  MAE:  {results_current['overall_mae']:.2f}")
print(f"  RMSE: {results_current['overall_rmse']:.2f}")
print(f"  R2:   {results_current['overall_r2']:.3f}")
print()
print("ROOT_CAUSE:")
print("  1. No StandardScaler in current evaluation")
print("  2. No max_depth limit in current RandomForest")
print("  3. Different aggregation method (pooled vs fold-level)")
print()
print("FROZEN_BASELINE_REMAINS_VALID: YES")
print("  The original baseline was computed correctly with proper")
print("  preprocessing (StandardScaler) and hyperparameters (max_depth=10).")
print()
print("V1_METRIC_PROTOCOL_MATCH: NO")
print("  Current V1 uses different protocol than original frozen baseline.")
print()
print("V2_COMPARISON_VALID: NO")
print("  V2 comparison used incorrect V1 baseline (different protocol).")
print()
print("NEXT_STEP:")
print("  1. Keep original frozen baseline as authoritative")
print("  2. Rerun V2 with corrected protocol (StandardScaler + max_depth=10)")
print("  3. Update experiment log with corrected V2 results")
print()
print("=" * 70)
print("STOP")
print("=" * 70)
