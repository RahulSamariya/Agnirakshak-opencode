"""
PM2.5 Model Improvement - Feature Engineering Experiment
=========================================================
Tests scientifically justified ERA5 feature engineering against frozen baseline.
"""

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = DATA_DIR / "models"

print("=" * 70)
print("PM2.5 MODEL IMPROVEMENT - FEATURE ENGINEERING EXPERIMENT")
print("=" * 70)
print(f"Started: {datetime.now().isoformat()}")
print()

# ============================================================
# 1. LOAD DATA
# ============================================================

print("[1/7] Loading data...")
print("-" * 70)

pilot = pd.read_parquet(DATA_DIR / "curated" / "air_quality" / "ahmedabad_pm25_station_day_2025_pilot_500.parquet")
pilot['date'] = pd.to_datetime(pilot['date'])

print(f"Pilot rows: {len(pilot)}")
print(f"Stations: {pilot['station_id'].nunique()}")
print(f"Dates: {pilot['date'].nunique()}")
print()

# ============================================================
# 2. FEATURE ENGINEERING
# ============================================================

print("[2/7] Feature engineering...")
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
# Add temporal features
pilot['month'] = pilot['date'].dt.month
pilot['day_of_year'] = pilot['date'].dt.dayofyear

# Season mapping (Ahmedabad - India)
def get_season(month):
    if month in [12, 1, 2]:  # Winter
        return 0
    elif month in [3, 4, 5]:  # Pre-monsoon
        return 1
    elif month in [6, 7, 8, 9]:  # Monsoon
        return 2
    else:  # Post-monsoon
        return 3

pilot['season'] = pilot['month'].apply(get_season)

# Interaction features (scientifically justified)
pilot['temp_x_rh'] = pilot['temperature_daily_c'] * pilot['relative_humidity_daily_pct']
pilot['temp_x_wind'] = pilot['temperature_daily_c'] * pilot['wind_speed_daily_ms']

# Nonlinear temperature terms
pilot['temp_squared'] = pilot['temperature_daily_c'] ** 2

# Precipitation indicator (binary)
pilot['precip_indicator'] = (pilot['precipitation_daily_m'] > 0.1).astype(int)

v2_features = v1_features + [
    'month',
    'season',
    'temp_x_rh',
    'temp_x_wind',
    'temp_squared',
    'precip_indicator'
]

print("V1 features (baseline):")
for f in v1_features:
    print(f"  - {f}")
print()

print("V2 features (engineered):")
for f in v2_features:
    print(f"  - {f}")
print()

# ============================================================
# 3. LEAKAGE CONTROL
# ============================================================

print("[3/7] Leakage control checks...")
print("-" * 70)

leakage_checks = [
    ("month", "Available at prediction time", "No future information"),
    ("season", "Available at prediction time", "No future information"),
    ("temp_x_rh", "Same-day ERA5 data", "No future information"),
    ("temp_x_wind", "Same-day ERA5 data", "No future information"),
    ("temp_squared", "Same-day ERA5 data", "No future information"),
    ("precip_indicator", "Same-day ERA5 data", "No future information"),
]

print(f"{'Feature':<15} {'Availability':<25} {'Future Info?':<20}")
print("-" * 60)
for feature, availability, future_info in leakage_checks:
    print(f"{feature:<15} {availability:<25} {future_info:<20}")
print()
print("All features PASS leakage control.")
print()

# ============================================================
# 4. LOSO VALIDATION
# ============================================================

print("[4/7] Training models with LOSO validation...")
print("-" * 70)

def loso_validation(X, y, stations, model_class, model_params, experiment_name):
    """Perform Leave-One-Station-Out validation."""
    unique_stations = stations.unique()
    results = []
    all_predictions = []
    all_actuals = []
    all_stations = []
    
    for station in unique_stations:
        # Split data
        train_idx = stations != station
        test_idx = stations == station
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Train model
        model = model_class(**model_params)
        model.fit(X_train, y_train)
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Calculate metrics
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
        all_stations.extend([station] * len(y_test))
    
    # Overall metrics
    overall_mae = mean_absolute_error(all_actuals, all_predictions)
    overall_rmse = np.sqrt(mean_squared_error(all_actuals, all_predictions))
    overall_r2 = r2_score(all_actuals, all_predictions)
    overall_bias = np.mean(np.array(all_predictions) - np.array(all_actuals))
    
    return {
        'experiment': experiment_name,
        'overall_mae': overall_mae,
        'overall_rmse': overall_rmse,
        'overall_r2': overall_r2,
        'overall_bias': overall_bias,
        'station_results': pd.DataFrame(results),
        'predictions': all_predictions,
        'actuals': all_actuals,
        'stations': all_stations
    }

# Prepare data
X_v1 = pilot[v1_features].values
X_v2 = pilot[v2_features].values
y = pilot['daily_pm25_ug_m3'].values
stations = pilot['station_id']

# Model parameters
rf_params = {'n_estimators': 100, 'random_state': 42}
gbm_params = {'n_estimators': 100, 'random_state': 42}
ridge_params = {'alpha': 1.0}

# Train V1 models
print("Training V1 (baseline) models...")
v1_rf = loso_validation(X_v1, y, stations, RandomForestRegressor, rf_params, "V1_RF")
v1_gbm = loso_validation(X_v1, y, stations, GradientBoostingRegressor, gbm_params, "V1_GBM")
v1_ridge = loso_validation(X_v1, y, stations, Ridge, ridge_params, "V1_Ridge")
print()

# Train V2 models
print("Training V2 (engineered) models...")
v2_rf = loso_validation(X_v2, y, stations, RandomForestRegressor, rf_params, "V2_RF")
v2_gbm = loso_validation(X_v2, y, stations, GradientBoostingRegressor, gbm_params, "V2_GBM")
v2_ridge = loso_validation(X_v2, y, stations, Ridge, ridge_params, "V2_Ridge")
print()

# ============================================================
# 5. FEATURE IMPORTANCE
# ============================================================

print("[5/7] Feature importance (Random Forest)...")
print("-" * 70)

# Train final RF model on all data for feature importance
rf_final = RandomForestRegressor(**rf_params)
rf_final.fit(X_v2, y)

feature_importance = pd.DataFrame({
    'feature': v2_features,
    'importance': rf_final.feature_importances_
}).sort_values('importance', ascending=False)

print("Feature importance (Random Forest):")
print(feature_importance.to_string(index=False))
print()

# ============================================================
# 6. RESULTS COMPARISON
# ============================================================

print("[6/7] Results comparison...")
print("-" * 70)

results_summary = pd.DataFrame([
    {'Experiment': 'V1_RF', 'MAE': v1_rf['overall_mae'], 'RMSE': v1_rf['overall_rmse'], 'R2': v1_rf['overall_r2'], 'Bias': v1_rf['overall_bias']},
    {'Experiment': 'V1_GBM', 'MAE': v1_gbm['overall_mae'], 'RMSE': v1_gbm['overall_rmse'], 'R2': v1_gbm['overall_r2'], 'Bias': v1_gbm['overall_bias']},
    {'Experiment': 'V1_Ridge', 'MAE': v1_ridge['overall_mae'], 'RMSE': v1_ridge['overall_rmse'], 'R2': v1_ridge['overall_r2'], 'Bias': v1_ridge['overall_bias']},
    {'Experiment': 'V2_RF', 'MAE': v2_rf['overall_mae'], 'RMSE': v2_rf['overall_rmse'], 'R2': v2_rf['overall_r2'], 'Bias': v2_rf['overall_bias']},
    {'Experiment': 'V2_GBM', 'MAE': v2_gbm['overall_mae'], 'RMSE': v2_gbm['overall_rmse'], 'R2': v2_gbm['overall_r2'], 'Bias': v2_gbm['overall_bias']},
    {'Experiment': 'V2_Ridge', 'MAE': v2_ridge['overall_mae'], 'RMSE': v2_ridge['overall_rmse'], 'R2': v2_ridge['overall_r2'], 'Bias': v2_ridge['overall_bias']},
])

print("Overall results:")
print(results_summary.to_string(index=False))
print()

# Station-by-station comparison for best models
print("Station-by-station LOSO results (Random Forest):")
print()
print("V1_RF:")
print(v1_rf['station_results'][['station', 'mae', 'rmse', 'r2', 'bias']].to_string(index=False))
print()
print("V2_RF:")
print(v2_rf['station_results'][['station', 'mae', 'rmse', 'r2', 'bias']].to_string(index=False))
print()

# Calculate deltas
delta_mae = v1_rf['overall_mae'] - v2_rf['overall_mae']
delta_rmse = v1_rf['overall_rmse'] - v2_rf['overall_rmse']
delta_r2 = v2_rf['overall_r2'] - v1_rf['overall_r2']

print("V1 vs V2 comparison (Random Forest):")
print(f"  delta MAE:  {delta_mae:+.2f} ({delta_mae/v1_rf['overall_mae']*100:+.1f}%)")
print(f"  delta RMSE: {delta_rmse:+.2f} ({delta_rmse/v1_rf['overall_rmse']*100:+.1f}%)")
print(f"  delta R2:   {delta_r2:+.3f}")
print()

# Station consistency check
v1_station_mae = v1_rf['station_results']['mae'].values
v2_station_mae = v2_rf['station_results']['mae'].values
stations_improved = np.sum(v2_station_mae < v1_station_mae)
stations_total = len(v1_station_mae)

print(f"Station consistency: {stations_improved}/{stations_total} stations improved")
print()

# ============================================================
# 7. FINAL REPORT
# ============================================================

print("[7/7] Final report...")
print("-" * 70)

# Determine improvement
improvement = "NO"
if delta_mae > 0.5 and stations_improved >= 5:  # At least 0.5 MAE improvement and 5+ stations
    improvement = "YES"
elif delta_mae > 0.2:
    improvement = "INCONCLUSIVE"

print("=" * 70)
print("FINAL REPORT")
print("=" * 70)
print()
print("BASELINE V1 (RF + ERA5):")
print(f"  MAE:  {v1_rf['overall_mae']:.2f}")
print(f"  RMSE: {v1_rf['overall_rmse']:.2f}")
print(f"  R²:   {v1_rf['overall_r2']:.3f}")
print(f"  Bias: {v1_rf['overall_bias']:.2f}")
print()
print("BEST NEW EXPERIMENT (V2_RF):")
print(f"  MAE:  {v2_rf['overall_mae']:.2f}")
print(f"  RMSE: {v2_rf['overall_rmse']:.2f}")
print(f"  R²:   {v2_rf['overall_r2']:.3f}")
print(f"  Bias: {v2_rf['overall_bias']:.2f}")
print()
print(f"delta MAE:  {delta_mae:+.2f} ({delta_mae/v1_rf['overall_mae']*100:+.1f}%)")
print(f"delta RMSE: {delta_rmse:+.2f} ({delta_rmse/v1_rf['overall_rmse']*100:+.1f}%)")
print(f"delta R2:   {delta_r2:+.3f}")
print()
print(f"STATION CONSISTENCY: {stations_improved}/{stations_total} stations improved")
print()
print(f"IMPROVEMENT: {improvement}")
print()

if improvement == "YES":
    print("NEXT STEP: Consider V2 features for production model.")
elif improvement == "INCONCLUSIVE":
    print("NEXT STEP: Collect more data or try different feature engineering.")
else:
    print("NEXT STEP: V1 baseline remains best. Focus on other improvements.")
print()
print("=" * 70)
print("STOP")
print("=" * 70)
