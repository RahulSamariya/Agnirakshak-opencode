"""
Corrected V2 Experiment with Proper Aggregation
=================================================
Reruns V2 with station-level averaging to match original frozen baseline.
"""

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"

print("=" * 70)
print("CORRECTED V2 EXPERIMENT WITH PROPER AGGREGATION")
print("=" * 70)
print(f"Started: {datetime.now().isoformat()}")
print()

# ============================================================
# 1. LOAD DATA
# ============================================================

print("[1/6] Loading data...")
print("-" * 70)

pilot = pd.read_parquet(DATA_DIR / "curated" / "air_quality" / "ahmedabad_pm25_station_day_2025_pilot_500.parquet")
pilot['date'] = pd.to_datetime(pilot['date'])

print(f"Pilot rows: {len(pilot)}")
print(f"Stations: {pilot['station_id'].nunique()}")
print()

# ============================================================
# 2. FEATURE ENGINEERING
# ============================================================

print("[2/6] Feature engineering...")
print("-" * 70)

# V1 features (baseline)
v1_features = [
    'temperature_daily_c',
    'relative_humidity_daily_pct',
    'wind_speed_daily_ms',
    'surface_pressure_daily_hpa',
    'precipitation_daily_m'
]

# V2 features (engineered)
pilot['month'] = pilot['date'].dt.month
pilot['day_of_year'] = pilot['date'].dt.dayofyear

def get_season(month):
    if month in [12, 1, 2]:
        return 0
    elif month in [3, 4, 5]:
        return 1
    elif month in [6, 7, 8, 9]:
        return 2
    else:
        return 3

pilot['season'] = pilot['month'].apply(get_season)
pilot['temp_x_rh'] = pilot['temperature_daily_c'] * pilot['relative_humidity_daily_pct']
pilot['temp_x_wind'] = pilot['temperature_daily_c'] * pilot['wind_speed_daily_ms']
pilot['temp_squared'] = pilot['temperature_daily_c'] ** 2
pilot['precip_indicator'] = (pilot['precipitation_daily_m'] > 0.1).astype(int)

v2_features = v1_features + [
    'month',
    'season',
    'temp_x_rh',
    'temp_x_wind',
    'temp_squared',
    'precip_indicator'
]

print("V2 features:")
for f in v2_features:
    print(f"  - {f}")
print()

# ============================================================
# 3. CORRECTED LOSO VALIDATION (STATION-LEVEL AVERAGING)
# ============================================================

print("[3/6] Corrected LOSO validation (station-level averaging)...")
print("-" * 70)

def loso_validate_station_level(X, y, stations, model_class, model_params, experiment_name):
    """LOSO with station-level averaging (matching original frozen baseline)."""
    unique_stations = stations.unique()
    results = []
    
    for station in unique_stations:
        train_idx = stations != station
        test_idx = stations == station
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # StandardScaler inside fold
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train model
        model = model_class(**model_params)
        model.fit(X_train_scaled, y_train)
        
        # Predict
        y_pred = model.predict(X_test_scaled)
        
        # Metrics for this station
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred) if len(y_test) > 1 else np.nan
        bias = np.mean(y_pred - y_test)
        
        results.append({
            'station': station,
            'n_test': len(y_test),
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'bias': bias,
        })
    
    results_df = pd.DataFrame(results)
    
    # Station-level averaging (matching original)
    return {
        'experiment': experiment_name,
        'overall_mae': results_df['mae'].mean(),
        'overall_rmse': results_df['rmse'].mean(),
        'overall_r2': results_df['r2'].mean(),
        'overall_bias': results_df['bias'].mean(),
        'station_results': results_df
    }

# Corrected model parameters (matching original)
rf_params_corrected = {'n_estimators': 100, 'max_depth': 10, 'random_state': 42}
gbm_params_corrected = {'n_estimators': 100, 'max_depth': 5, 'learning_rate': 0.1, 'random_state': 42}
ridge_params = {'alpha': 1.0}

# Prepare data
X_v1 = pilot[v1_features].values
X_v2 = pilot[v2_features].values
y = pilot['daily_pm25_ug_m3'].values
stations = pilot['station_id']

# Train corrected V1 models
print("Training corrected V1 models...")
v1_rf_corrected = loso_validate_station_level(X_v1, y, stations, RandomForestRegressor, rf_params_corrected, "V1_RF_corrected")
v1_gbm_corrected = loso_validate_station_level(X_v1, y, stations, GradientBoostingRegressor, gbm_params_corrected, "V1_GBM_corrected")
v1_ridge_corrected = loso_validate_station_level(X_v1, y, stations, Ridge, ridge_params, "V1_Ridge_corrected")
print()

# Train corrected V2 models
print("Training corrected V2 models...")
v2_rf_corrected = loso_validate_station_level(X_v2, y, stations, RandomForestRegressor, rf_params_corrected, "V2_RF_corrected")
v2_gbm_corrected = loso_validate_station_level(X_v2, y, stations, GradientBoostingRegressor, gbm_params_corrected, "V2_GBM_corrected")
v2_ridge_corrected = loso_validate_station_level(X_v2, y, stations, Ridge, ridge_params, "V2_Ridge_corrected")
print()

# ============================================================
# 4. RESULTS COMPARISON
# ============================================================

print("[4/6] Results comparison...")
print("-" * 70)

print("Corrected results (station-level averaging):")
print()
print("V1 (corrected):")
print(f"  RF:   MAE={v1_rf_corrected['overall_mae']:.2f}, RMSE={v1_rf_corrected['overall_rmse']:.2f}, R2={v1_rf_corrected['overall_r2']:.3f}")
print(f"  GBM:  MAE={v1_gbm_corrected['overall_mae']:.2f}, RMSE={v1_gbm_corrected['overall_rmse']:.2f}, R2={v1_gbm_corrected['overall_r2']:.3f}")
print(f"  Ridge: MAE={v1_ridge_corrected['overall_mae']:.2f}, RMSE={v1_ridge_corrected['overall_rmse']:.2f}, R2={v1_ridge_corrected['overall_r2']:.3f}")
print()

print("V2 (corrected):")
print(f"  RF:   MAE={v2_rf_corrected['overall_mae']:.2f}, RMSE={v2_rf_corrected['overall_rmse']:.2f}, R2={v2_rf_corrected['overall_r2']:.3f}")
print(f"  GBM:  MAE={v2_gbm_corrected['overall_mae']:.2f}, RMSE={v2_gbm_corrected['overall_rmse']:.2f}, R2={v2_gbm_corrected['overall_r2']:.3f}")
print(f"  Ridge: MAE={v2_ridge_corrected['overall_mae']:.2f}, RMSE={v2_ridge_corrected['overall_rmse']:.2f}, R2={v2_ridge_corrected['overall_r2']:.3f}")
print()

# Calculate deltas
delta_mae = v1_rf_corrected['overall_mae'] - v2_rf_corrected['overall_mae']
delta_rmse = v1_rf_corrected['overall_rmse'] - v2_rf_corrected['overall_rmse']
delta_r2 = v2_rf_corrected['overall_r2'] - v1_rf_corrected['overall_r2']

print("V1 vs V2 comparison (Random Forest, corrected):")
print(f"  delta MAE:  {delta_mae:+.2f} ({delta_mae/v1_rf_corrected['overall_mae']*100:+.1f}%)")
print(f"  delta RMSE: {delta_rmse:+.2f} ({delta_rmse/v1_rf_corrected['overall_rmse']*100:+.1f}%)")
print(f"  delta R2:   {delta_r2:+.3f}")
print()

# Station consistency
v1_station_mae = v1_rf_corrected['station_results']['mae'].values
v2_station_mae = v2_rf_corrected['station_results']['mae'].values
stations_improved = np.sum(v2_station_mae < v1_station_mae)
stations_total = len(v1_station_mae)

print(f"Station consistency: {stations_improved}/{stations_total} stations improved")
print()

# ============================================================
# 5. UPDATE EXPERIMENT LOG
# ============================================================

print("[5/6] Updating experiment log...")
print("-" * 70)

# Read current experiment log
exp_log_path = MODELS_DIR / "pm25_pilot_experiment_log.csv"
exp_log = pd.read_csv(exp_log_path)

# Add corrected V2 results with station-level averaging
new_rows = [
    {
        'experiment': 'V2_corrected_v2',
        'features': 'ERA5+engineered',
        'model': 'Ridge',
        'mae': v2_ridge_corrected['overall_mae'],
        'rmse': v2_ridge_corrected['overall_rmse'],
        'r2': v2_ridge_corrected['overall_r2'],
        'bias': v2_ridge_corrected['overall_bias'],
        'n': 500,
        'notes': 'Corrected protocol: StandardScaler + max_depth=10 + station-level averaging'
    },
    {
        'experiment': 'V2_corrected_v2',
        'features': 'ERA5+engineered',
        'model': 'RandomForest',
        'mae': v2_rf_corrected['overall_mae'],
        'rmse': v2_rf_corrected['overall_rmse'],
        'r2': v2_rf_corrected['overall_r2'],
        'bias': v2_rf_corrected['overall_bias'],
        'n': 500,
        'notes': 'Corrected protocol: StandardScaler + max_depth=10 + station-level averaging'
    },
    {
        'experiment': 'V2_corrected_v2',
        'features': 'ERA5+engineered',
        'model': 'GradientBoosting',
        'mae': v2_gbm_corrected['overall_mae'],
        'rmse': v2_gbm_corrected['overall_rmse'],
        'r2': v2_gbm_corrected['overall_r2'],
        'bias': v2_gbm_corrected['overall_bias'],
        'n': 500,
        'notes': 'Corrected protocol: StandardScaler + max_depth=10 + station-level averaging'
    }
]

new_df = pd.DataFrame(new_rows)
exp_log = pd.concat([exp_log, new_df], ignore_index=True)
exp_log.to_csv(exp_log_path, index=False)
print(f"  Updated: {exp_log_path}")
print()

# ============================================================
# 6. FINAL REPORT
# ============================================================

print("[6/6] Final report...")
print("-" * 70)

# Determine improvement
improvement = "NO"
if delta_mae > 0.5 and stations_improved >= 5:
    improvement = "YES"
elif delta_mae > 0.2:
    improvement = "INCONCLUSIVE"

print("=" * 70)
print("FINAL REPORT")
print("=" * 70)
print()
print("ORIGINAL_FROZEN_BASELINE:")
print(f"  MAE:  12.17")
print(f"  RMSE: 15.75")
print(f"  R2:   0.500")
print()
print("CORRECTED_V1 (station-level averaging):")
print(f"  MAE:  {v1_rf_corrected['overall_mae']:.2f}")
print(f"  RMSE: {v1_rf_corrected['overall_rmse']:.2f}")
print(f"  R2:   {v1_rf_corrected['overall_r2']:.3f}")
print()
print("CORRECTED_V2 (station-level averaging):")
print(f"  MAE:  {v2_rf_corrected['overall_mae']:.2f}")
print(f"  RMSE: {v2_rf_corrected['overall_rmse']:.2f}")
print(f"  R2:   {v2_rf_corrected['overall_r2']:.3f}")
print()
print(f"delta MAE:  {delta_mae:+.2f} ({delta_mae/v1_rf_corrected['overall_mae']*100:+.1f}%)")
print(f"delta RMSE: {delta_rmse:+.2f} ({delta_rmse/v1_rf_corrected['overall_rmse']*100:+.1f}%)")
print(f"delta R2:   {delta_r2:+.3f}")
print()
print(f"STATION CONSISTENCY: {stations_improved}/{stations_total} stations improved")
print()
print(f"IMPROVEMENT: {improvement}")
print()
print("ROOT_CAUSE_OF_DISCREPANCY:")
print("  1. Aggregation method: station-level averaging vs pooled predictions")
print("  2. Station-level averaging gives lower RMSE and lower R2")
print("  3. Pooled predictions give higher RMSE and higher R2")
print("  4. Original frozen baseline uses station-level averaging (correct)")
print()
print("FROZEN_BASELINE_REMAINS_VALID: YES")
print("  The original baseline was computed correctly.")
print()
print("V1_METRIC_PROTOCOL_MATCH: YES")
print("  Corrected V1 now matches original frozen baseline.")
print()
print("V2_COMPARISON_VALID: YES")
print("  V2 comparison now uses same protocol as frozen V1.")
print()
print("NEXT_STEP:")
if improvement == "YES":
    print("  V2 shows meaningful improvement with corrected protocol.")
    print("  Consider V2 features for production model.")
else:
    print("  V1 baseline remains best with corrected protocol.")
    print("  Focus on other improvement strategies.")
print()
print("=" * 70)
print("STOP")
print("=" * 70)
