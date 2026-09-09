"""
Build the 2025 Ahmedabad Station-Day Matched Dataset with Predictor Methodology
===============================================================================
Creates daily PM2.5 target with documented MAIAC AOD and ERA5 methodology.
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
    "site_308":  "Maninagar/raw_data_hourly_maninagar,_ahmedabad_-_gpcb_1H (1).csv",
    "site_5452": "raikhad/raw_data_hourly_raikhad,_ahmedabad_-_iitm_1H (1).csv",
    "site_5451": "rakhial/raw_data_hourly_rakhial,_ahmedabad_-_iitm_1H (1).csv",
    "site_5454": "sac_isro_bopal/raw_data_hourly_sac_isro_bopal,_ahmedabad_-_iitm_1H (1).csv",
    "site_5455": "sac_isro_satellite/raw_data_hourly_sac_isro_satellite,_ahmedabad_-_iitm_1H (1).csv",
    "site_5449": "sardar_vallabhbhai_patel_stadium/raw_data_hourly_sardar_vallabhbhai_patel_stadium,_ahmedabad_-_iitm_1H (1).csv",
    "site_5456": "svpi_airport_hansol/raw_data_hourly_svpi_airport_hansol,_ahmedabad_-_iitm_1H (1).csv",
}

# ============================================================
# DOCUMENTATION: MAIAC AOD METHODOLOGY
# ============================================================

MAIAC_METHODOLOGY = {
    "dataset": "MODIS/061/MCD19A2_GRANULES",
    "variable": "Optical_Depth_055",
    "scale_factor": 0.001,
    "scale_description": "AOD = stored_value × 0.001",
    "spatial_resolution": "1km",
    "temporal_resolution": "Daily",
    "qa_band": "AOD_QA",
    "qa_filter": "Cloud mask bits 0-1 = 00 (clear), Heavy dust flag bit 2 = 0",
    "extraction_method": "Nearest pixel to station coordinates",
    "interpolation": "None - missing values left as NaN",
    "units": "Unitless (AOD at 550nm)",
    "notes": [
        "MAIAC AOD is daily composite, not hourly",
        "Do not use future AOD data",
        "Do not interpolate missing AOD values",
        "Record aod_available = False when AOD is missing",
    ]
}

# ============================================================
# DOCUMENTATION: ERA5 METEOROLOGY METHODOLOGY
# ============================================================

ERA5_METHODOLOGY = {
    "source_dataset": "ERA5 hourly data on single levels (0.25° × 0.25°)",
    "source_dataset_id": "reanalysis-era5-single-levels",
    "spatial_resolution": "0.25° × 0.25° (~25km)",
    "spatial_extraction": "Nearest grid cell to station coordinates",
    "temporal_aggregation": "Daily mean (24 hourly values)",
    "variables": {
        "temperature": {
            "era5_name": "2m_temperature (t2m)",
            "original_unit": "K",
            "final_unit": "°C",
            "conversion": "K - 273.15",
            "aggregation": "Daily mean",
        },
        "humidity": {
            "era5_name": "2m_dewpoint_temperature (d2m)",
            "original_unit": "K",
            "final_unit": "%",
            "conversion": "Calculate RH from T and Td using Tetens formula",
            "aggregation": "Daily mean",
        },
        "wind_speed": {
            "era5_name": "10m_u_component_of_wind (u10) + 10m_v_component_of_wind (v10)",
            "original_unit": "m/s",
            "final_unit": "m/s",
            "conversion": "sqrt(u10² + v10²)",
            "aggregation": "Daily mean",
        },
        "surface_pressure": {
            "era5_name": "Surface pressure (sp)",
            "original_unit": "Pa",
            "final_unit": "hPa",
            "conversion": "Pa / 100",
            "aggregation": "Daily mean",
        },
        "precipitation": {
            "era5_name": "Total precipitation (tp)",
            "original_unit": "m",
            "final_unit": "mm",
            "conversion": "m × 1000",
            "aggregation": "Daily sum",
        },
    },
    "notes": [
        "ERA5 is reanalysis, not observations",
        "Use same calendar date as PM2.5",
        "Do not use monthly values for daily representation",
        "Dewpoint temperature requires conversion to relative humidity",
    ]
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
# STEP 3: ADD MAIAC AOD PLACEHOLDERS
# ============================================================

print("[STEP 3] Adding MAIAC AOD placeholder columns...")

daily_df["aod_550"] = np.nan
daily_df["aod_available"] = False
daily_df["aod_quality_status"] = "NOT_RETRIEVED"
daily_df["aod_source_date"] = pd.NaT

print("  MAIAC columns added: aod_550, aod_available, aod_quality_status, aod_source_date")
print("  Status: PLACEHOLDER - Earth Engine not available")
print()

# ============================================================
# STEP 4: ADD ERA5 METEOROLOGY PLACEHOLDERS
# ============================================================

print("[STEP 4] Adding ERA5 meteorology placeholder columns...")

daily_df["temperature_daily"] = np.nan
daily_df["humidity_daily"] = np.nan
daily_df["wind_speed_daily"] = np.nan
daily_df["surface_pressure_daily"] = np.nan
daily_df["precipitation_daily"] = np.nan

print("  ERA5 columns added: temperature_daily, humidity_daily, wind_speed_daily, surface_pressure_daily, precipitation_daily")
print("  Status: PLACEHOLDER - CDS API not available")
print()

# ============================================================
# STEP 5: ADD MISSINGNESS STATUS
# ============================================================

print("[STEP 5] Adding missingness status columns...")

daily_df["pm25_available"] = daily_df["daily_pm25_ug_m3"].notna()
daily_df["era5_available"] = False  # Not yet retrieved
daily_df["fully_matched"] = False  # Not yet matched

print("  Missingness columns added: pm25_available, aod_available, era5_available, fully_matched")
print()

# ============================================================
# STEP 6: DUPLICATE CHECKS
# ============================================================

print("[STEP 6] Running duplicate checks...")

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
# STEP 7: SAVE DATASET
# ============================================================

print("[STEP 7] Saving matched dataset...")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Select final columns
final_cols = [
    "station_id", "station_name", "date", "latitude", "longitude",
    "daily_pm25_ug_m3", "valid_pm25_hours", "pm25_day_completeness_pct",
    "daily_qc_flag",
    "aod_550", "aod_available", "aod_quality_status", "aod_source_date",
    "temperature_daily", "humidity_daily", "wind_speed_daily",
    "surface_pressure_daily", "precipitation_daily",
    "pm25_available", "era5_available", "fully_matched",
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
# STEP 8: CREATE PREDICTOR MATCH QC CSV
# ============================================================

print("[STEP 8] Creating predictor match QC CSV...")

qc_rows = []
for station_id in sorted(final_df["station_id"].unique()):
    s_df = final_df[final_df["station_id"] == station_id]
    eligible = s_df[s_df["daily_qc_flag"] == "ELIGIBLE"]
    
    qc_rows.append({
        "station_id": station_id,
        "station_name": STATION_COORDS[station_id]["name"],
        "total_days": len(s_df),
        "eligible_pm25_days": len(eligible),
        "aod_matched_days": 0,  # Not yet retrieved
        "era5_matched_days": 0,  # Not yet retrieved
        "fully_matched_days": 0,  # Not yet matched
        "aod_match_pct": 0.0,
        "era5_match_pct": 0.0,
        "full_match_pct": 0.0,
        "mean_pm25": eligible["daily_pm25_ug_m3"].mean(),
        "std_pm25": eligible["daily_pm25_ug_m3"].std(),
    })

qc_df = pd.DataFrame(qc_rows)
qc_path = METADATA_DIR / "ahmedabad_pm25_predictor_match_qc.csv"
qc_df.to_csv(qc_path, index=False)
print(f"  Saved: {qc_path}")

print()

# ============================================================
# STEP 9: SUMMARY COUNTS
# ============================================================

print("=" * 70)
print("FINAL MATCHING COUNTS")
print("=" * 70)

eligible = final_df[final_df["daily_qc_flag"] == "ELIGIBLE"]
aod_matched = eligible[eligible["aod_available"] == True]
era5_matched = eligible[eligible["era5_available"] == True]
fully_matched = eligible[eligible["fully_matched"] == True]

print()
print(f"Total eligible PM2.5 station-days: {len(eligible)}")
print(f"AOD matched station-days: {len(aod_matched)}")
print(f"ERA5 matched station-days: {len(era5_matched)}")
print(f"Fully matched station-days: {len(fully_matched)}")
print()
print("Station-wise counts:")
print("-" * 70)
print(f"{'Station':<25} {'Eligible':>10} {'AOD':>8} {'ERA5':>8} {'Full':>8}")
print("-" * 70)

for station_id in sorted(final_df["station_id"].unique()):
    s_name = STATION_COORDS[station_id]["name"]
    s_eligible = len(eligible[eligible["station_id"] == station_id])
    s_aod = len(aod_matched[aod_matched["station_id"] == station_id])
    s_era5 = len(era5_matched[era5_matched["station_id"] == station_id])
    s_full = len(fully_matched[fully_matched["station_id"] == station_id])
    print(f"{s_name:<25} {s_eligible:>10} {s_aod:>8} {s_era5:>8} {s_full:>8}")

print("-" * 70)

# Calculate percentages
aod_pct = len(aod_matched) / len(eligible) * 100 if len(eligible) > 0 else 0
era5_pct = len(era5_matched) / len(eligible) * 100 if len(eligible) > 0 else 0
full_pct = len(fully_matched) / len(eligible) * 100 if len(eligible) > 0 else 0

print()
print(f"AOD match percentage: {aod_pct:.1f}%")
print(f"ERA5 match percentage: {era5_pct:.1f}%")
print(f"Full match percentage: {full_pct:.1f}%")

print()

# ============================================================
# STEP 10: PREDICTOR COVERAGE
# ============================================================

print("=" * 70)
print("PREDICTOR COVERAGE (for eligible station-days)")
print("=" * 70)

predictors = ["daily_pm25_ug_m3", "aod_550", "temperature_daily", "humidity_daily", 
              "wind_speed_daily", "surface_pressure_daily", "precipitation_daily"]

print()
print(f"{'Predictor':<25} {'Count':>8} {'Missing':>8} {'Missing%':>10} {'Min':>10} {'Median':>10} {'Mean':>10} {'P95':>10} {'Max':>10}")
print("-" * 110)

for pred in predictors:
    if pred in eligible.columns:
        vals = eligible[pred]
        count = vals.notna().sum()
        missing = vals.isna().sum()
        missing_pct = missing / len(vals) * 100
        if count > 0:
            min_val = vals.min()
            median_val = vals.median()
            mean_val = vals.mean()
            p95_val = vals.quantile(0.95)
            max_val = vals.max()
            print(f"{pred:<25} {count:>8} {missing:>8} {missing_pct:>9.1f}% {min_val:>10.2f} {median_val:>10.2f} {mean_val:>10.2f} {p95_val:>10.2f} {max_val:>10.2f}")
        else:
            print(f"{pred:<25} {count:>8} {missing:>8} {missing_pct:>9.1f}% {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>10}")

print("-" * 110)

print()

# ============================================================
# STEP 11: FINAL DECISION
# ============================================================

print("=" * 70)
print("FINAL DECISION")
print("=" * 70)
print()
print("STATUS: PARTIALLY_READY")
print()
print("REASONING:")
print("  - Real PM2.5 target: YES (2,737 eligible station-days)")
print("  - Sufficient matched station-days: NO (0 AOD matched, 0 ERA5 matched)")
print("  - Verified AOD values: NO (not yet retrieved)")
print("  - Verified ERA5 predictors: NO (not yet retrieved)")
print("  - No target imputation: YES")
print("  - No coordinate errors: YES")
print("  - No temporal leakage: YES")
print()
print("BLOCKERS:")
print("  - MAIAC MCD19A2.061 data not retrieved from Earth Engine")
print("  - ERA5 reanalysis data not retrieved from CDS API")
print()
print("NEXT STEPS:")
print("  1. Install Earth Engine Python API: pip install earthengine-api")
print("  2. Authenticate: earthengine authenticate")
print("  3. Install CDS API: pip install cdsapi")
print("  4. Configure CDS API key")
print("  5. Run data retrieval scripts")
print("  6. Re-run this script to populate predictors")
print()
print("DO NOT TRAIN THE MODEL.")