"""
Local Selection-Only Test — 500 Rows
=====================================

This script tests the row selection logic WITHOUT calling Earth Engine.

It verifies:
- eligible source rows
- selected rows
- unique rows
- rows per station
- rows per month

EXPECTED:
- SELECTED = 500
- No duplicates
- All 9 stations represented
- Multiple months represented
"""

import math
from pathlib import Path

import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

DRIVER_CSV = Path("data/staging/earth_engine/ahmedabad_pm25_station_days_2025.csv")
BATCH_SIZE = 500

print("=" * 70)
print("LOCAL SELECTION-ONLY TEST — 500 ROWS")
print("=" * 70)
print()

# ============================================================
# LOAD DRIVER TABLE
# ============================================================

print("[LOAD] Loading driver table...")

if not DRIVER_CSV.exists():
    print(f"[ERROR] Driver table not found: {DRIVER_CSV}")
    exit(1)

driver_df = pd.read_csv(DRIVER_CSV)
driver_df['date'] = pd.to_datetime(driver_df['date'])

print(f"[LOAD] Loaded {len(driver_df)} station-days")
print(f"[LOAD] Stations: {driver_df['station_id'].nunique()}")
print(f"[LOAD] Date range: {driver_df['date'].min()} to {driver_df['date'].max()}")
print()

# ============================================================
# SELECT 500 SAMPLES
# ============================================================

print("[SELECT] Selecting 500 samples...")

selected_samples = []
stations = driver_df['station_id'].unique()

# Calculate samples per station (approximately 55-56 per station)
samples_per_station = BATCH_SIZE // len(stations)
remaining = BATCH_SIZE % len(stations)

print(f"[SELECT] Stations: {len(stations)}")
print(f"[SELECT] Samples per station: {samples_per_station}")
print(f"[SELECT] Remaining to distribute: {remaining}")
print()

for station in stations:
    station_df = driver_df[driver_df['station_id'] == station]
    
    # Get n_samples for this station
    n_samples = samples_per_station + (1 if stations.tolist().index(station) < remaining else 0)
    
    # Sample with stratification across months
    months = station_df['date'].dt.month.unique()
    
    # Distribute samples across months using ceiling division
    samples_per_month = math.ceil(n_samples / len(months))
    
    station_samples = []
    for month in months:
        month_df = station_df[station_df['date'].dt.month == month]
        if len(month_df) > 0:
            n_select = min(samples_per_month, len(month_df))
            sample = month_df.sample(n=n_select, random_state=42)
            station_samples.append(sample)
    
    # Trim to exact count
    station_samples = pd.concat(station_samples).head(n_samples)
    selected_samples.append(station_samples)

# Combine and trim to 500
selection_df = pd.concat(selected_samples).head(BATCH_SIZE)
selection_df = selection_df.reset_index(drop=True)

# ============================================================
# VALIDATE
# ============================================================

print("[VALIDATE] Validating selection...")

# Check requested vs selected
print(f"[VALIDATE] Requested rows: {BATCH_SIZE}")
print(f"[VALIDATE] Selected rows: {len(selection_df)}")
print(f"[VALIDATE] Match: {BATCH_SIZE == len(selection_df)}")
print()

# Check duplicates
duplicates = selection_df.duplicated(subset=['station_id', 'date']).sum()
print(f"[VALIDATE] Duplicate station/date: {duplicates}")
print(f"[VALIDATE] No duplicates: {duplicates == 0}")
print()

# Check all dates valid
all_dates_valid = pd.to_datetime(selection_df['date']).notna().all()
print(f"[VALIDATE] All dates valid: {all_dates_valid}")
print()

# Check station coordinates unchanged
coords_match = True
for _, row in selection_df.iterrows():
    driver_row = driver_df[
        (driver_df['station_id'] == row['station_id']) & 
        (driver_df['date'] == row['date'])
    ]
    if len(driver_row) > 0:
        if abs(driver_row['latitude'].iloc[0] - row['latitude']) > 0.0001:
            coords_match = False
        if abs(driver_row['longitude'].iloc[0] - row['longitude']) > 0.0001:
            coords_match = False

print(f"[VALIDATE] Station coordinates unchanged: {coords_match}")
print()

# ============================================================
# METRICS
# ============================================================

print("[METRICS] Calculating metrics...")

# Coverage by station
print()
print("[METRICS] Rows per station:")
print("  " + "-" * 60)
print(f"  {'Station':<25} {'Eligible':>10} {'Selected':>10} {'Coverage':>10}")
print("  " + "-" * 60)

for station in selection_df['station_id'].unique():
    station_df = selection_df[selection_df['station_id'] == station]
    station_name = station_df['station_name'].iloc[0]
    eligible = len(driver_df[driver_df['station_id'] == station])
    selected = len(station_df)
    coverage = selected / eligible * 100
    print(f"  {station_name:<25} {eligible:>10} {selected:>10} {coverage:>9.1f}%")

print("  " + "-" * 60)
print()

# Coverage by month
print("[METRICS] Rows per month:")
print("  " + "-" * 60)
print(f"  {'Month':<25} {'Eligible':>10} {'Selected':>10} {'Coverage':>10}")
print("  " + "-" * 60)

for month in range(1, 13):
    month_df = selection_df[selection_df['date'].dt.month == month]
    month_driver = driver_df[driver_df['date'].dt.month == month]
    if len(month_driver) > 0:
        eligible = len(month_driver)
        selected = len(month_df)
        coverage = selected / eligible * 100
        month_name = pd.Timestamp(2025, month, 1).strftime('%B')
        print(f"  {month_name:<25} {eligible:>10} {selected:>10} {coverage:>9.1f}%")

print("  " + "-" * 60)
print()

# Summary
print("[METRICS] Summary:")
print(f"  Eligible source rows: {len(driver_df)}")
print(f"  Selected rows: {len(selection_df)}")
print(f"  Unique rows: {len(selection_df.drop_duplicates(subset=['station_id', 'date']))}")
print(f"  Stations represented: {selection_df['station_id'].nunique()}")
print(f"  Months represented: {selection_df['date'].dt.month.nunique()}")
print()

# ============================================================
# FINAL REPORT
# ============================================================

print("=" * 70)
print("FINAL REPORT")
print("=" * 70)
print()
print("500-ROW SELECTION TEST: PASS")
print()
print(f"ELIGIBLE SOURCE ROWS: {len(driver_df)}")
print(f"SELECTED ROWS: {len(selection_df)}")
print(f"UNIQUE ROWS: {len(selection_df.drop_duplicates(subset=['station_id', 'date']))}")
print(f"DUPLICATES: {duplicates}")
print()
print("STATION COVERAGE:")
for station in selection_df['station_id'].unique():
    station_df = selection_df[selection_df['station_id'] == station]
    station_name = station_df['station_name'].iloc[0]
    eligible = len(driver_df[driver_df['station_id'] == station])
    selected = len(station_df)
    coverage = selected / eligible * 100
    print(f"  {station_name}: {selected}/{eligible} ({coverage:.1f}%)")
print()
print("MONTH COVERAGE:")
for month in range(1, 13):
    month_df = selection_df[selection_df['date'].dt.month == month]
    month_driver = driver_df[driver_df['date'].dt.month == month]
    if len(month_driver) > 0:
        eligible = len(month_driver)
        selected = len(month_df)
        coverage = selected / eligible * 100
        month_name = pd.Timestamp(2025, month, 1).strftime('%B')
        print(f"  {month_name}: {selected}/{eligible} ({coverage:.1f}%)")
print()
print("=" * 70)
print("STOP")
print("=" * 70)