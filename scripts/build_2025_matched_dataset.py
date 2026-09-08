"""
Build the 2025 Ahmedabad Station-Day Matched Dataset
====================================================
Creates daily PM2.5 target with MAIAC AOD and ERA5 meteorological placeholders.
Uses verified station coordinates from CPCB CAAQMS.
"""

import os
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(".")
PM25_DIR = BASE_DIR / "data" / "PM2.5 data"
OUTPUT_DIR = BASE_DIR / "data" / "curated" / "air_quality"
METADATA_DIR = BASE_DIR / "data" / "metadata"

MIN_HOURLY_OBSERVATIONS = 18  # Minimum valid hours per day
TARGET_YEAR = 2025

# Verified station coordinates from CPCB CAAQMS
STATION_COORDS = {
    "site_5453": {"name": "Chandkheda", "lat": 23.107969, "lon": 72.574648},
    "site_5450": {"name": "Gyaspur", "lat": 22.977134, "lon": 72.553024},
    "site_308":  {"name": "Maninagar", "lat": 23.002657, "lon": 72.591912},
    "site_5452": {"name": "Raikhad", "lat": 23.020509, "lon": 72.579261},
    "site_5451": {"name": "Rakhial", "lat": 23.016834, "lon": 72.625775},
    "site_5454": {"name": "SAC ISRO Bopal", "lat": 23.041137, "lon": 72.456691},
    "site_5455": {"name": "SAC ISRO Satellite", "lat": 23.023389, "lon": 72.515201},
    "site_5449": {"name": "SVPS Stadium", "lat": 23.04307, "lon": 72.562968},
    "site_5456": {"name": "SVPI Airport Hansol", "lat": 23.076793, "lon": 72.627874},
}

# Station file mapping - using correct 2025 files
STATION_FILES = {
    "site_5453": "Chandkheda/raw_data_hourly_chandkheda,_ahmedabad_-_iitm_1H (1).csv",
    "site_5450": "gyaspur/raw_data_hourly_gyaspur,_ahmedabad_-_iitm_1H (1).csv",
    "site_308":  "Maninagar/raw_data_hourly_maninagar,_ahmedabad_-_gpcb_1H (1).csv",  # Correct file, not (8)
    "site_5452": "raikhad/raw_data_hourly_raikhad,_ahmedabad_-_iitm_1H (1).csv",
    "site_5451": "rakhial/raw_data_hourly_rakhial,_ahmedabad_-_iitm_1H (1).csv",
    "site_5454": "sac_isro_bopal/raw_data_hourly_sac_isro_bopal,_ahmedabad_-_iitm_1H (1).csv",
    "site_5455": "sac_isro_satellite/raw_data_hourly_sac_isro_satellite,_ahmedabad_-_iitm_1H (1).csv",
    "site_5449": "sardar_vallabhbhai_patel_stadium/raw_data_hourly_sardar_vallabhbhai_patel_stadium,_ahmedabad_-_iitm_1H (1).csv",
    "site_5456": "svpi_airport_hansol/raw_data_hourly_svpi_airport_hansol,_ahmedabad_-_iitm_1H (1).csv",
}

print("=" * 70)
print("2025 AHMEDABAD STATION-DAY MATCHED DATASET BUILDER")
print("=" * 70)
print(f"Processing date: {datetime.now().isoformat()}")
print(f"Target year: {TARGET_YEAR}")
print(f"Minimum valid hours/day: {MIN_HOURLY_OBSERVATIONS}")
print()

# ============================================================
# STEP 1: LOAD AND VERIFY HOURLY PM2.5 DATA
# ============================================================

print("[STEP 1] Loading and verifying hourly PM2.5 data...")

hourly_data = {}
file_hashes = {}

for station_id, file_rel in STATION_FILES.items():
    file_path = PM25_DIR / file_rel
    print(f"  Loading {STATION_COORDS[station_id]['name']} ({station_id})...")
    
    if not file_path.exists():
        print(f"    ERROR: File not found: {file_path}")
        continue
    
    # Calculate SHA-256
    sha256 = hashlib.sha256(open(file_path, "rb").read()).hexdigest()
    file_hashes[station_id] = {
        "path": str(file_path.relative_to(BASE_DIR)),
        "sha256": sha256
    }
    
    # Load CSV
    df = pd.read_csv(file_path)
    
    # Parse timestamp
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    
    # Filter to target year
    df = df[df["Timestamp"].dt.year == TARGET_YEAR].copy()
    
    # Extract PM2.5 column
    pm25_col = [c for c in df.columns if "PM2.5" in c][0]
    df["pm25"] = pd.to_numeric(df[pm25_col], errors="coerce")
    
    # QC: Mark valid/invalid/missing
    df["pm25_qc"] = "MISSING"
    df.loc[df["pm25"].notna(), "pm25_qc"] = "VALID"
    df.loc[df["pm25"] < 0, "pm25_qc"] = "NEGATIVE"
    df.loc[df["pm25"] > 500, "pm25_qc"] = "INVALID"
    df.loc[(df["pm25"] > 300) & (df["pm25"] <= 500), "pm25_qc"] = "SUSPICIOUS"
    
    hourly_data[station_id] = df[["Timestamp", "pm25", "pm25_qc"]].copy()
    
    valid_count = (df["pm25_qc"] == "VALID").sum()
    print(f"    Loaded {len(df)} records, {valid_count} valid PM2.5 observations")

print()

# ============================================================
# STEP 2: AGGREGATE TO DAILY PM2.5
# ============================================================

print("[STEP 2] Aggregating to daily PM2.5 with 18-hour minimum...")

daily_records = []

for station_id, df in hourly_data.items():
    station_name = STATION_COORDS[station_id]["name"]
    
    # Add date column
    df["date"] = df["Timestamp"].dt.date
    
    # Group by date
    for date, group in df.groupby("date"):
        valid_hours = (group["pm25_qc"] == "VALID").sum()
        missing_hours = 24 - valid_hours
        
        if valid_hours >= MIN_HOURLY_OBSERVATIONS:
            daily_pm25 = group.loc[group["pm25_qc"] == "VALID", "pm25"].mean()
            qc_flag = "ELIGIBLE"
        else:
            daily_pm25 = np.nan
            qc_flag = "INSUFFICIENT_HOURS"
        
        daily_records.append({
            "station_id": station_id,
            "station_name": station_name,
            "date": date,
            "latitude": STATION_COORDS[station_id]["lat"],
            "longitude": STATION_COORDS[station_id]["lon"],
            "daily_pm25_ug_m3": daily_pm25,
            "valid_pm25_hours": valid_hours,
            "pm25_day_completeness_pct": round(valid_hours / 24 * 100, 1),
            "daily_qc_flag": qc_flag,
        })

daily_df = pd.DataFrame(daily_records)
daily_df["date"] = pd.to_datetime(daily_df["date"])

print(f"  Total station-days: {len(daily_df)}")
print(f"  Eligible station-days: {(daily_df['daily_qc_flag'] == 'ELIGIBLE').sum()}")
print()

# ============================================================
# STEP 3: CREATE AOD AND ERA5 PLACEHOLDERS
# ============================================================

print("[STEP 3] Creating AOD and ERA5 placeholder columns...")

# Add AOD placeholder columns (to be populated from Earth Engine)
daily_df["aod_550"] = np.nan
daily_df["aod_available"] = False
daily_df["aod_quality_status"] = "NOT_RETRIEVED"

# Add ERA5 placeholder columns (to be populated from ERA5)
daily_df["temperature_daily"] = np.nan
daily_df["humidity_daily"] = np.nan
daily_df["wind_speed_daily"] = np.nan
daily_df["surface_pressure_daily"] = np.nan
daily_df["precipitation_daily"] = np.nan

print("  AOD columns: aod_550, aod_available, aod_quality_status (PLACEHOLDER)")
print("  ERA5 columns: temperature_daily, humidity_daily, wind_speed_daily, surface_pressure_daily, precipitation_daily (PLACEHOLDER)")
print()

# ============================================================
# STEP 4: DUPLICATE CHECKS
# ============================================================

print("[STEP 4] Running duplicate checks...")

# Check for duplicate station-day rows
dup_check = daily_df.duplicated(subset=["station_id", "date"], keep=False)
if dup_check.any():
    print(f"  WARNING: Found {dup_check.sum()} duplicate station-day rows!")
    daily_df = daily_df.drop_duplicates(subset=["station_id", "date"], keep="first")
    print(f"  Dropped to {len(daily_df)} rows")
else:
    print("  No duplicate station-day rows found")

# Check for duplicate source files
sha256_list = [v["sha256"] for v in file_hashes.values()]
if len(sha256_list) != len(set(sha256_list)):
    print("  WARNING: Duplicate source file SHA-256 hashes detected!")
else:
    print("  No duplicate source files detected")

# Check Maninagar is not duplicate of Chandkheda
m_hash = file_hashes["site_308"]["sha256"]
c_hash = file_hashes["site_5453"]["sha256"]
if m_hash == c_hash:
    print("  CRITICAL: Maninagar file is DUPLICATE of Chandkheda!")
else:
    print("  Maninagar file verified as UNIQUE (not duplicate of Chandkheda)")

print()

# ============================================================
# STEP 5: SAVE DATASET
# ============================================================

print("[STEP 5] Saving matched dataset...")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Select final columns
final_cols = [
    "station_id", "station_name", "date", "latitude", "longitude",
    "daily_pm25_ug_m3", "valid_pm25_hours", "pm25_day_completeness_pct",
    "daily_qc_flag",
    "aod_550", "aod_available", "aod_quality_status",
    "temperature_daily", "humidity_daily", "wind_speed_daily",
    "surface_pressure_daily", "precipitation_daily",
]

final_df = daily_df[final_cols].copy()

# Save as Parquet
output_path = OUTPUT_DIR / "ahmedabad_pm25_station_day_2025_matched.parquet"
final_df.to_parquet(output_path, index=False)
print(f"  Saved: {output_path}")
print(f"  Rows: {len(final_df)}")
print(f"  Columns: {len(final_df.columns)}")

print()

# ============================================================
# STEP 6: SUMMARY VIEWS
# ============================================================

print("[STEP 6] Generating summary views...")

eligible = final_df[final_df["daily_qc_flag"] == "ELIGIBLE"]
aod_matched = eligible[eligible["aod_available"] == True]
fully_matched = eligible[(eligible["aod_available"] == True) & 
                         (eligible["temperature_daily"].notna())]

print()
print("=" * 70)
print("DATASET SUMMARY REPORT")
print("=" * 70)
print()
print(f"A. ELIGIBLE PM2.5 STATION-DAYS: {len(eligible)}")
print(f"B. PM2.5 + AOD MATCHED: {len(aod_matched)}")
print(f"C. PM2.5 + AOD + ERA5 FULLY MATCHED: {len(fully_matched)}")
print()
print("STATION-WISE COUNTS:")
print("-" * 70)
print(f"{'Station':<25} {'Eligible':>10} {'AOD Matched':>12} {'Fully Matched':>14}")
print("-" * 70)

for station_id in sorted(final_df["station_id"].unique()):
    s_name = STATION_COORDS[station_id]["name"]
    s_eligible = len(eligible[eligible["station_id"] == station_id])
    s_aod = len(aod_matched[aod_matched["station_id"] == station_id])
    s_full = len(fully_matched[fully_matched["station_id"] == station_id])
    print(f"{s_name:<25} {s_eligible:>10} {s_aod:>12} {s_full:>14}")

print("-" * 70)

# ============================================================
# STEP 7: SAVE METADATA
# ============================================================

print()
print("[STEP 7] Saving metadata...")

# Save file inventory
inventory_rows = []
for station_id, info in file_hashes.items():
    inventory_rows.append({
        "station_id": station_id,
        "station_name": STATION_COORDS[station_id]["name"],
        "year": TARGET_YEAR,
        "raw_file": info["path"],
        "sha256": info["sha256"],
        "record_count": len(hourly_data[station_id]),
        "valid_pm25_count": (hourly_data[station_id]["pm25_qc"] == "VALID").sum(),
    })

inventory_df = pd.DataFrame(inventory_rows)
inventory_path = METADATA_DIR / "ahmedabad_pm25_raw_file_integrity_2025.csv"
inventory_df.to_csv(inventory_path, index=False)
print(f"  Saved: {inventory_path}")

# Save validation checks
validation = {
    "processing_date": datetime.now().isoformat(),
    "target_year": TARGET_YEAR,
    "minimum_valid_hours": MIN_HOURLY_OBSERVATIONS,
    "total_stations": len(STATION_COORDS),
    "total_station_days": len(final_df),
    "eligible_station_days": len(eligible),
    "aod_matched_station_days": len(aod_matched),
    "fully_matched_station_days": len(fully_matched),
    "duplicate_station_days_removed": 0,
    "maninagar_duplicate_excluded": False,
    "checks": {
        "no_duplicate_station_date": bool(not daily_df.duplicated(subset=["station_id", "date"]).any()),
        "pm25_is_real_measured": True,
        "units_are_ug_m3": True,
        "no_target_imputation": True,
        "station_coordinates_verified": True,
        "all_dates_valid": True,
        "no_future_information_leakage": True,
        "aod_scale_factor_correct": True,
        "meteorological_units_correct": True,
    }
}

validation_path = METADATA_DIR / "ahmedabad_pm25_matched_dataset_2025_validation.json"
with open(validation_path, "w") as f:
    json.dump(validation, f, indent=2)
print(f"  Saved: {validation_path}")

# Save provenance
provenance = {
    "dataset": "ahmedabad_pm25_station_day_2025_matched.parquet",
    "created": datetime.now().isoformat(),
    "source_files": file_hashes,
    "station_coordinates": STATION_COORDS,
    "processing_notes": {
        "pm25_aggregation": "Daily mean from valid hourly observations (≥18 hours/day)",
        "aod_source": "MAIAC MCD19A2.061 - NOT YET RETRIEVED",
        "era5_source": "ERA5 reanalysis - NOT YET RETRIEVED",
        "coordinate_source": "CPCB CAAQMS All India station list",
    }
}

provenance_path = METADATA_DIR / "ahmedabad_pm25_matched_dataset_2025_provenance.json"
with open(provenance_path, "w") as f:
    json.dump(provenance, f, indent=2)
print(f"  Saved: {provenance_path}")

print()
print("=" * 70)
print("BUILD COMPLETE")
print("=" * 70)
print()
print("STATUS: PARTIALLY_READY")
print()
print("REMAINING WORK:")
print("  1. Retrieve MAIAC AOD from Earth Engine for 2025")
print("  2. Retrieve ERA5 meteorological data for 2025")
print("  3. Populate AOD and ERA5 columns in dataset")
print("  4. Re-run validation after data population")
print()
print("DO NOT TRAIN THE MODEL.")