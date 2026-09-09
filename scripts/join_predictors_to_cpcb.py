"""
Join CPCB PM2.5 Target with MAIAC AOD and ERA5 Predictors
==========================================================

This script joins the extracted MAIAC AOD and ERA5 meteorological data
with the CPCB PM2.5 target to create the final matched dataset.

INPUTS:
- data/staging/earth_engine/ahmedabad_pm25_station_days_2025.csv (CPCB target)
- data/staging/earth_engine/ahmedabad_pm25_maiac_station_day_2025.csv (MAIAC AOD)
- data/staging/earth_engine/ahmedabad_pm25_era5_station_day_2025.csv (ERA5 meteo)

OUTPUT:
- data/curated/air_quality/ahmedabad_pm25_station_day_2025_matched.parquet
- data/metadata/ahmedabad_pm25_predictor_match_qc.csv

STRICT MATCHING RULES:
- One row = one station + one date
- Never alter PM2.5 target during joining
- Predictor missingness is allowed and must be explicit
- Do not drop rows merely because predictors are missing
"""

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(".")
EE_DIR = BASE_DIR / "data" / "staging" / "earth_engine"
OUTPUT_DIR = BASE_DIR / "data" / "curated" / "air_quality"
METADATA_DIR = BASE_DIR / "data" / "metadata"

# Input files
CPCB_CSV = EE_DIR / "ahmedabad_pm25_station_days_2025.csv"
MAIAC_CSV = EE_DIR / "ahmedabad_pm25_maiac_station_day_2025.csv"
ERA5_CSV = EE_DIR / "ahmedabad_pm25_era5_station_day_2025.csv"

# Output files
MATCHED_PARQUET = OUTPUT_DIR / "ahmedabad_pm25_station_day_2025_matched.parquet"
QC_CSV = METADATA_DIR / "ahmedabad_pm25_predictor_match_qc.csv"

# Station coordinates (verified from CPCB CAAQMS)
STATION_COORDS = {
    "site_5453": {"name": "Chandkheda", "lat": 23.107969, "lon": 72.574648, "agency": "IITM"},
    "site_5450": {"name": "Gyaspur", "lat": 22.977134, "lon": 72.553024, "agency": "IITM"},
    "site_308":  {"name": "Maninagar", "lat": 23.002657, "lon": 72.591912, "agency": "GPCB"},
    "site_5452": {"name": "Raikhad", "lat": 23.020509, "lon": 72.579261, "agency": "IITM"},
    "site_5451": {"name": "Rakhial", "lat": 23.016834, "lon": 72.625775, "agency": "IITM"},
    "site_5454": {"name": "SAC ISRO Bopal", "lat": 23.041137, "lon": 72.456691, "agency": "IITM"},
    "site_5455": {"name": "SAC ISRO Satellite", "lat": 23.023389, "lon": 72.515201, "agency": "IITM"},
    "site_5449": {"name": "SVPS Stadium", "lat": 23.04307, "lon": 72.562968, "agency": "IITM"},
    "site_5456": {"name": "SVPI Airport Hansol", "lat": 23.076793, "lon": 72.627874, "agency": "IITM"},
}

print("=" * 70)
print("JOIN CPCB PM2.5 WITH MAIAC AOD AND ERA5 PREDICTORS")
print("=" * 70)
print(f"Script generated: {datetime.now().isoformat()}")
print()

# ============================================================
# STEP 1: LOAD INPUT FILES
# ============================================================

print("[STEP 1] Loading input files...")

# Load CPCB target
if not CPCB_CSV.exists():
    print(f"  ERROR: CPCB file not found: {CPCB_CSV}")
    sys.exit(1)

cpcb_df = pd.read_csv(CPCB_CSV)
cpcb_df["date"] = pd.to_datetime(cpcb_df["date"])
print(f"  CPCB target: {len(cpcb_df)} rows")

# Load MAIAC AOD
if not MAIAC_CSV.exists():
    print(f"  WARNING: MAIAC file not found: {MAIAC_CSV}")
    print("  Creating empty MAIAC dataframe")
    maiac_df = pd.DataFrame(columns=["station_id", "date", "aod_550", "aod_available", 
                                      "aod_quality_status", "aod_valid_pixel_count", "aod_source_date"])
else:
    maiac_df = pd.read_csv(MAIAC_CSV)
    maiac_df["date"] = pd.to_datetime(maiac_df["date"])
    print(f"  MAIAC AOD: {len(maiac_df)} rows")

# Load ERA5
if not ERA5_CSV.exists():
    print(f"  WARNING: ERA5 file not found: {ERA5_CSV}")
    print("  Creating empty ERA5 dataframe")
    era5_df = pd.DataFrame(columns=["station_id", "date", "temperature_daily_c",
                                     "relative_humidity_daily_pct", "wind_speed_daily_ms",
                                     "surface_pressure_daily_hpa", "precipitation_daily_m",
                                     "meteo_available"])
else:
    era5_df = pd.read_csv(ERA5_CSV)
    era5_df["date"] = pd.to_datetime(era5_df["date"])
    print(f"  ERA5 meteorology: {len(era5_df)} rows")

print()

# ============================================================
# STEP 2: JOIN DATA
# ============================================================

print("[STEP 2] Joining data...")

# Start with CPCB target as the authoritative base
merged_df = cpcb_df.copy()

# Add station coordinates
merged_df["latitude"] = merged_df["station_id"].map(lambda x: STATION_COORDS.get(x, {}).get("lat"))
merged_df["longitude"] = merged_df["station_id"].map(lambda x: STATION_COORDS.get(x, {}).get("lon"))
merged_df["station_name"] = merged_df["station_id"].map(lambda x: STATION_COORDS.get(x, {}).get("name"))
merged_df["agency"] = merged_df["station_id"].map(lambda x: STATION_COORDS.get(x, {}).get("agency"))

# Join MAIAC AOD
maiac_cols = ["station_id", "date", "aod_550", "aod_available", "aod_quality_status", 
              "aod_valid_pixel_count", "aod_source_date"]
if len(maiac_df) > 0:
    merged_df = merged_df.merge(
        maiac_df[maiac_cols],
        on=["station_id", "date"],
        how="left"
    )
else:
    for col in ["aod_550", "aod_available", "aod_quality_status", "aod_valid_pixel_count", "aod_source_date"]:
        merged_df[col] = None

# Join ERA5
era5_cols = ["station_id", "date", "temperature_daily_c", "relative_humidity_daily_pct",
             "wind_speed_daily_ms", "surface_pressure_daily_hpa", "precipitation_daily_m",
             "meteo_available"]
if len(era5_df) > 0:
    merged_df = merged_df.merge(
        era5_df[era5_cols],
        on=["station_id", "date"],
        how="left"
    )
else:
    for col in ["temperature_daily_c", "relative_humidity_daily_pct", "wind_speed_daily_ms",
                "surface_pressure_daily_hpa", "precipitation_daily_m", "meteo_available"]:
        merged_df[col] = None

# Add fully_matched indicator
merged_df["fully_matched"] = (
    (merged_df["aod_available"] == True) & 
    (merged_df["meteo_available"] == True)
)

print(f"  Merged dataset: {len(merged_df)} rows")
print()

# ============================================================
# STEP 3: STRICT MATCHING RULES
# ============================================================

print("[STEP 3] Verifying strict matching rules...")

# Check: one row = one station + one date
duplicates = merged_df.duplicated(subset=["station_id", "date"], keep=False).sum()
print(f"  Duplicate station/date rows: {duplicates}")

if duplicates > 0:
    print("  ERROR: Duplicate station/date rows detected!")
    sys.exit(1)

# Check: row count unchanged
print(f"  CPCB rows before join: {len(cpcb_df)}")
print(f"  Merged rows after join: {len(merged_df)}")
print(f"  Row count unchanged: {len(merged_df) == len(cpcb_df)}")

# Check: PM2.5 targets unchanged
pm25_unchanged = merged_df["daily_pm25_ug_m3"].equals(cpcb_df["daily_pm25_ug_m3"])
print(f"  PM2.5 targets unchanged: {pm25_unchanged}")

# Check: coordinates present
coords_present = merged_df["latitude"].notna().all() and merged_df["longitude"].notna().all()
print(f"  Coordinates present: {coords_present}")

print()

# ============================================================
# STEP 4: SELECT FINAL COLUMNS
# ============================================================

print("[STEP 4] Selecting final columns...")

final_cols = [
    "station_id", "station_name", "agency", "date",
    "latitude", "longitude",
    "daily_pm25_ug_m3", "valid_pm25_hours", "pm25_day_completeness_pct",
    "aod_550", "aod_available", "aod_quality_status", "aod_source_date",
    "temperature_daily_c", "relative_humidity_daily_pct", "wind_speed_daily_ms",
    "surface_pressure_daily_hpa", "precipitation_daily_m",
    "meteo_available", "fully_matched",
]

# Ensure all columns exist
for col in final_cols:
    if col not in merged_df.columns:
        merged_df[col] = None

final_df = merged_df[final_cols].copy()

print(f"  Final columns: {len(final_df.columns)}")
print(f"  Final rows: {len(final_df)}")
print()

# ============================================================
# STEP 5: SAVE MATCHED DATASET
# ============================================================

print("[STEP 5] Saving matched dataset...")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

final_df.to_parquet(MATCHED_PARQUET, index=False)
print(f"  Saved: {MATCHED_PARQUET}")
print()

# ============================================================
# STEP 6: QUALITY CONTROL
# ============================================================

print("[STEP 6] Running quality control...")

# Calculate matching counts
eligible = final_df[final_df["daily_pm25_ug_m3"].notna()]
aod_matched = eligible[eligible["aod_available"] == True]
era5_matched = eligible[eligible["meteo_available"] == True]
fully_matched = eligible[eligible["fully_matched"] == True]

print(f"  Eligible PM2.5 station-days: {len(eligible)}")
print(f"  AOD matched station-days: {len(aod_matched)}")
print(f"  ERA5 matched station-days: {len(era5_matched)}")
print(f"  Fully matched station-days: {len(fully_matched)}")
print()

# Calculate percentages
aod_pct = len(aod_matched) / len(eligible) * 100 if len(eligible) > 0 else 0
era5_pct = len(era5_matched) / len(eligible) * 100 if len(eligible) > 0 else 0
full_pct = len(fully_matched) / len(eligible) * 100 if len(eligible) > 0 else 0

print(f"  AOD match rate: {aod_pct:.1f}%")
print(f"  ERA5 match rate: {era5_pct:.1f}%")
print(f"  Full match rate: {full_pct:.1f}%")
print()

# By station
print("  By station:")
print("  " + "-" * 70)
print(f"  {'Station':<25} {'Eligible':>10} {'AOD':>10} {'ERA5':>10} {'Full':>10}")
print("  " + "-" * 70)

for station_id in sorted(final_df["station_id"].unique()):
    s_name = STATION_COORDS.get(station_id, {}).get("name", station_id)
    s_eligible = len(eligible[eligible["station_id"] == station_id])
    s_aod = len(aod_matched[aod_matched["station_id"] == station_id])
    s_era5 = len(era5_matched[era5_matched["station_id"] == station_id])
    s_full = len(fully_matched[fully_matched["station_id"] == station_id])
    print(f"  {s_name:<25} {s_eligible:>10} {s_aod:>10} {s_era5:>10} {s_full:>10}")

print("  " + "-" * 70)
print()

# Save QC results
qc_rows = []
for station_id in sorted(final_df["station_id"].unique()):
    s_df = final_df[final_df["station_id"] == station_id]
    s_eligible = eligible[eligible["station_id"] == station_id]
    s_aod = aod_matched[aod_matched["station_id"] == station_id]
    s_era5 = era5_matched[era5_matched["station_id"] == station_id]
    s_full = fully_matched[fully_matched["station_id"] == station_id]
    
    qc_rows.append({
        "station_id": station_id,
        "station_name": STATION_COORDS.get(station_id, {}).get("name", station_id),
        "eligible_days": len(s_eligible),
        "aod_days": len(s_aod),
        "era5_days": len(s_era5),
        "fully_matched_days": len(s_full),
        "aod_match_rate": len(s_aod) / len(s_eligible) * 100 if len(s_eligible) > 0 else 0,
        "era5_match_rate": len(s_era5) / len(s_eligible) * 100 if len(s_eligible) > 0 else 0,
        "full_match_rate": len(s_full) / len(s_eligible) * 100 if len(s_eligible) > 0 else 0,
    })

qc_df = pd.DataFrame(qc_rows)
METADATA_DIR.mkdir(parents=True, exist_ok=True)
qc_df.to_csv(QC_CSV, index=False)
print(f"  Saved QC: {QC_CSV}")

print()

# ============================================================
# STEP 7: PREDICTOR STATISTICS
# ============================================================

print("[STEP 7] Predictor statistics (for eligible station-days)...")

predictors = ["daily_pm25_ug_m3", "aod_550", "temperature_daily_c", 
              "relative_humidity_daily_pct", "wind_speed_daily_ms",
              "surface_pressure_daily_hpa", "precipitation_daily_m"]

print()
print(f"  {'Predictor':<25} {'Count':>8} {'Missing':>8} {'Missing%':>10} {'Min':>10} {'Median':>10} {'Mean':>10} {'P95':>10} {'Max':>10}")
print("  " + "-" * 110)

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
            print(f"  {pred:<25} {count:>8} {missing:>8} {missing_pct:>9.1f}% {min_val:>10.2f} {median_val:>10.2f} {mean_val:>10.2f} {p95_val:>10.2f} {max_val:>10.2f}")
        else:
            print(f"  {pred:<25} {count:>8} {missing:>8} {missing_pct:>9.1f}% {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>10}")

print("  " + "-" * 110)
print()

# ============================================================
# FINAL REPORT
# ============================================================

print("=" * 70)
print("FINAL REPORT")
print("=" * 70)
print()

print("STATIONS: 9")
print()
print("PM2.5 ELIGIBLE STATION-DAYS:", len(eligible))
print()
print("AOD MATCHED:", len(aod_matched))
print()
print("ERA5 MATCHED:", len(era5_matched))
print()
print("FULLY MATCHED:", len(fully_matched))
print()
print(f"AOD MATCH RATE: {aod_pct:.1f}%")
print()
print(f"ERA5 MATCH RATE: {era5_pct:.1f}%")
print()
print(f"FULL MATCH RATE: {full_pct:.1f}%")
print()

# Weakest and strongest stations
if len(qc_df) > 0:
    weakest_idx = qc_df["full_match_rate"].idxmin()
    strongest_idx = qc_df["full_match_rate"].idxmax()
    print(f"WEAKEST STATION: {qc_df.loc[weakest_idx, 'station_name']} ({qc_df.loc[weakest_idx, 'full_match_rate']:.1f}% full match)")
    print()
    print(f"STRONGEST STATION: {qc_df.loc[strongest_idx, 'station_name']} ({qc_df.loc[strongest_idx, 'full_match_rate']:.1f}% full match)")

print()
print(f"DATE RANGE: {final_df['date'].min()} to {final_df['date'].max()}")
print()

# Determine readiness
if full_pct > 50:
    readiness = "READY_FOR_BASELINE_MODEL"
elif full_pct > 0:
    readiness = "PARTIALLY_READY"
else:
    readiness = "INSUFFICIENT"

print(f"MODEL READINESS: {readiness}")
print()
print("FILES CREATED:")
print(f"  - {MATCHED_PARQUET}")
print(f"  - {QC_CSV}")
print()
print("STOP.")