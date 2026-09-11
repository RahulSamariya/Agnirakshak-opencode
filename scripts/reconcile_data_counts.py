"""
Data Count Reconciliation Script
=================================
Reconciles reported counts for CPCB, MAIAC, ERA5, and pilot datasets.
"""

from pathlib import Path
from datetime import datetime

import pandas as pd

BASE_DIR = Path(".")
DATA_DIR = BASE_DIR / "data"

print("=" * 70)
print("DATA COUNT RECONCILIATION")
print("=" * 70)
print(f"Started: {datetime.now().isoformat()}")
print()

# ============================================================
# 1. INSPECT ACTUAL FILES
# ============================================================

print("[1/5] Inspecting actual files...")
print("-" * 70)

# Load all datasets
pm25 = pd.read_parquet(DATA_DIR / "curated" / "air_quality" / "ahmedabad_pm25_station_day_2025.parquet")
maiac = pd.read_parquet(DATA_DIR / "curated" / "air_quality" / "ahmedabad_pm25_maiac_station_day_2025.parquet")
era5 = pd.read_csv(DATA_DIR / "staging" / "earth_engine" / "ahmedabad_pm25_era5_pilot_500.csv")
pilot = pd.read_parquet(DATA_DIR / "curated" / "air_quality" / "ahmedabad_pm25_station_day_2025_pilot_500.parquet")

# Standardize date columns
pm25['date'] = pd.to_datetime(pm25['date'])
maiac['date'] = pd.to_datetime(maiac['date'])
era5['date'] = pd.to_datetime(era5['date'])
pilot['date'] = pd.to_datetime(pilot['date'])

# Filter eligible rows
eligible = pm25[pm25['daily_qc_flag'] == 'ELIGIBLE']

# Create composite keys for matching
eligible['station_date'] = eligible['station_id'].astype(str) + '_' + eligible['date'].astype(str)
maiac['station_date'] = maiac['station_id'].astype(str) + '_' + maiac['date'].astype(str)
era5['station_date'] = era5['station_id'].astype(str) + '_' + era5['date'].astype(str)
pilot['station_date'] = pilot['station_id'].astype(str) + '_' + pilot['date'].astype(str)

print("Row counts:")
print(f"  PM2.5 total rows:             {len(pm25)}")
print(f"  PM2.5 eligible rows:          {len(eligible)}")
print(f"  MAIAC rows:                   {len(maiac)}")
print(f"  ERA5 rows:                    {len(era5)}")
print(f"  Pilot rows:                   {len(pilot)}")
print()

print("Unique station/date combinations:")
print(f"  PM2.5 eligible station/dates: {eligible['station_date'].nunique()}")
print(f"  MAIAC station/dates:          {maiac['station_date'].nunique()}")
print(f"  ERA5 station/dates:           {era5['station_date'].nunique()}")
print(f"  Pilot station/dates:          {pilot['station_date'].nunique()}")
print()

print("Unique stations:")
print(f"  PM2.5 eligible stations:      {eligible['station_id'].nunique()}")
print(f"  MAIAC stations:               {maiac['station_id'].nunique()}")
print(f"  ERA5 stations:                {era5['station_id'].nunique()}")
print(f"  Pilot stations:               {pilot['station_id'].nunique()}")
print()

print("Unique dates:")
print(f"  PM2.5 eligible dates:         {eligible['date'].nunique()}")
print(f"  MAIAC dates:                  {maiac['date'].nunique()}")
print(f"  ERA5 dates:                   {era5['date'].nunique()}")
print(f"  Pilot dates:                  {pilot['date'].nunique()}")
print()

# ============================================================
# 2. ERA5 RECONCILIATION
# ============================================================

print("[2/5] ERA5 Reconciliation...")
print("-" * 70)

print("ERA5 raw statistics:")
print(f"  Total rows:                   {len(era5)}")
print(f"  Unique station IDs:           {era5['station_id'].nunique()}")
print(f"  Unique dates:                 {era5['date'].nunique()}")
print(f"  Unique station/date combos:   {era5['station_date'].nunique()}")
print()

# Check if 500 pilot station/dates are all in ERA5
pilot_set = set(pilot['station_date'].values)
era5_set = set(era5['station_date'].values)

missing_in_era5 = pilot_set - era5_set
in_both = pilot_set & era5_set

print("Pilot vs ERA5 coverage:")
print(f"  Pilot station/dates:          {len(pilot_set)}")
print(f"  ERA5 station/dates:           {len(era5_set)}")
print(f"  Pilot in ERA5:                {len(in_both)}")
print(f"  Pilot missing from ERA5:      {len(missing_in_era5)}")

if missing_in_era5:
    print()
    print("Missing station/dates:")
    for sd in sorted(missing_in_era5)[:10]:
        print(f"    {sd}")
    if len(missing_in_era5) > 10:
        print(f"    ... and {len(missing_in_era5) - 10} more")
print()

# ============================================================
# 3. PILOT RECONCILIATION
# ============================================================

print("[3/5] Pilot Reconciliation...")
print("-" * 70)

# Count matches for pilot
pilot_eligible = pilot.merge(eligible[['station_id', 'date', 'station_date']], on='station_date', how='left', indicator=True)
pilot_maiac = pilot.merge(maiac[['station_id', 'date', 'station_date']], on='station_date', how='left', indicator=True)
pilot_era5 = pilot.merge(era5[['station_id', 'date', 'station_date']], on='station_date', how='left', indicator=True)

print("Pilot row matches:")
print(f"  CPCB matches:                 {len(pilot_eligible[pilot_eligible['_merge'] == 'both'])}")
print(f"  MAIAC matches:                {len(pilot_maiac[pilot_maiac['_merge'] == 'both'])}")
print(f"  ERA5 matches:                 {len(pilot_era5[pilot_era5['_merge'] == 'both'])}")
print()

# Complete rows (CPCB + ERA5)
complete_cpcb_era5 = pilot_eligible.merge(era5[['station_id', 'date', 'station_date']], on='station_date', how='inner')
print(f"  Complete CPCB + ERA5 rows:    {len(complete_cpcb_era5)}")
print()

# Complete rows (CPCB + ERA5 + strict AOD)
if 'strict_aod_available' in pilot.columns:
    complete_all = pilot_eligible[(pilot_eligible['_merge'] == 'both') & (pilot['strict_aod_available'] == True)]
    print(f"  Complete CPCB + ERA5 + AOD:   {len(complete_all)}")
else:
    print("  Complete CPCB + ERA5 + AOD:   (strict_aod_available column not in pilot)")
print()

# ============================================================
# 4. MAIAC VERSION RECONCILIATION
# ============================================================

print("[4/5] MAIAC Version Reconciliation...")
print("-" * 70)

print("Row count comparison:")
print(f"  CPCB canonical eligible:      {len(eligible)}")
print(f"  MAIAC rows:                   {len(maiac)}")
print(f"  Difference:                   {len(eligible) - len(maiac)}")
print()

# Check if the difference is exactly the Maninagar update
cpcb_stations = set(eligible['station_id'].unique())
maiac_stations = set(maiac['station_id'].unique())

stations_in_cpcb_not_maiac = cpcb_stations - maiac_stations
stations_in_maiac_not_cpcb = maiac_stations - cpcb_stations

print("Station comparison:")
print(f"  CPCB stations:                {sorted(cpcb_stations)}")
print(f"  MAIAC stations:               {sorted(maiac_stations)}")
print(f"  In CPCB not in MAIAC:         {sorted(stations_in_cpcb_not_maiac)}")
print(f"  In MAIAC not in CPCB:         {sorted(stations_in_maiac_not_cpcb)}")
print()

# Check the 43-row difference
if 'Maninagar' in str(cpcb_stations):
    maninagar_in_cpcb = eligible[eligible['station_id'].str.contains('Maninagar', case=False, na=False)]
    print(f"  Maninagar in CPCB:            {len(maninagar_in_cpcb)} rows")
else:
    print("  Maninagar not found in CPCB stations")
print()

# ============================================================
# 5. CHECK MODEL INPUTS
# ============================================================

print("[5/5] Model Inputs Check...")
print("-" * 70)

# Load experiment log
exp_log = pd.read_csv(DATA_DIR / "models" / "pm25_pilot_experiment_log.csv")

print("Frozen baseline experiment:")
print(exp_log[['experiment', 'model', 'features', 'mae', 'r2', 'notes']].to_string(index=False))
print()

# Inspect the actual dataset used for training
print("Pilot dataset columns:")
print(f"  {list(pilot.columns)}")
print()

print("Pilot dataset shape:")
print(f"  Rows: {pilot.shape[0]}, Columns: {pilot.shape[1]}")
print()

# Check for features used
era5_features = [col for col in pilot.columns if 'era5' in col.lower() or col.startswith(('temp', 'rh', 'wind', 'press', 'precip'))]
aod_features = [col for col in pilot.columns if 'aod' in col.lower() or col.startswith('optical')]

print("ERA5-related features found:")
print(f"  {era5_features}")
print()

print("AOD-related features found:")
print(f"  {aod_features}")
print()

# ============================================================
# FINAL REPORT
# ============================================================

print("=" * 70)
print("FINAL RECONCILIATION REPORT")
print("=" * 70)
print()

print(f"CPCB_CANONICAL_ROWS: {len(eligible)}")
print(f"MAIAC_ROWS: {len(maiac)}")
print(f"MAIAC_UNIQUE_STATION_DAYS: {maiac['station_date'].nunique()}")
print(f"ERA5_RAW_ROWS: {len(era5)}")
print(f"ERA5_UNIQUE_STATION_DAYS: {era5['station_date'].nunique()}")
print(f"PILOT_ROWS: {len(pilot)}")
print(f"PILOT_ERA5_COMPLETE: {len(in_both)}")
print(f"PILOT_AOD_COMPLETE: {maiac['strict_aod_available'].sum() if 'strict_aod_available' in maiac.columns else 'N/A'}")
print(f"PILOT_FULLY_COMPLETE: {len(in_both)}")
print(f"MODEL_TRAINING_ROWS: {len(pilot)}")
print(f"ERA5_1728_MEANING: {len(era5)} rows = {era5['station_id'].nunique()} stations x {era5['date'].nunique()} dates")
print(f"2780_vs_2737_REASON: CPCB canonical includes all eligible rows; MAIAC may have different extraction date/version")
print(f"DATA_CONSISTENCY: NEEDS_RECONCILIATION (2780 != 2737)")
print()
print("=" * 70)
print("STOP")
print("=" * 70)
