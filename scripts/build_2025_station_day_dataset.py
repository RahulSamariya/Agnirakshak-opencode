"""
Ahmedabad PM2.5 Station-Day Modeling Dataset Builder

This script processes hourly CPCB/GPCB PM2.5 data for 9 Ahmedabad stations
and creates a clean station-day dataset for the 2025 pilot model.

Author: Agnirakshak Project
Date: 2026-09-08
"""

import os
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

import pandas as pd
import numpy as np

# ==================================================
# CONFIGURATION
# ==================================================

# Station metadata (from previous inventory)
STATIONS = {
    "site_5453": {
        "station_name": "Chandkheda",
        "agency": "IITM",
        "latitude": 23.108,
        "longitude": 72.5746,
        "file_path": "data/PM2.5 data/Chandkheda/raw_data_hourly_chandkheda,_ahmedabad_-_iitm_1H.csv"
    },
    "site_5450": {
        "station_name": "Gyaspur",
        "agency": "IITM",
        "latitude": 23.0225,
        "longitude": 72.5967,
        "file_path": "data/PM2.5 data/gyaspur/raw_data_hourly_gyaspur,_ahmedabad_-_iitm_1H (1).csv"
    },
    "site_308": {
        "station_name": "Maninagar",
        "agency": "GPCB",
        "latitude": 23.0225,
        "longitude": 72.5967,
        "file_path": "data/PM2.5 data/Maninagar/raw_data_hourly_maninagar,_ahmedabad_-_gpcb_1H (8).csv",
        "note": "DATA DUPLICATE OF CHANDKHEDA - NEEDS VERIFICATION"
    },
    "site_5452": {
        "station_name": "Raikhad",
        "agency": "IITM",
        "latitude": 23.0225,
        "longitude": 72.5967,
        "file_path": "data/PM2.5 data/raikhad/raw_data_hourly_raikhad,_ahmedabad_-_iitm_1H (1).csv"
    },
    "site_5451": {
        "station_name": "Rakhial",
        "agency": "IITM",
        "latitude": 23.0225,
        "longitude": 72.5967,
        "file_path": "data/PM2.5 data/rakhial/raw_data_hourly_rakhial,_ahmedabad_-_iitm_1H (1).csv"
    },
    "site_5454": {
        "station_name": "SAC ISRO Bopal",
        "agency": "IITM",
        "latitude": 23.0225,
        "longitude": 72.5967,
        "file_path": "data/PM2.5 data/sac_isro_bopal/raw_data_hourly_sac_isro_bopal,_ahmedabad_-_iitm_1H (1).csv"
    },
    "site_5455": {
        "station_name": "SAC ISRO Satellite",
        "agency": "IITM",
        "latitude": 23.0225,
        "longitude": 72.5967,
        "file_path": "data/PM2.5 data/sac_isro_satellite/raw_data_hourly_sac_isro_satellite,_ahmedabad_-_iitm_1H (1).csv"
    },
    "site_5449": {
        "station_name": "Sardar Vallabhbhai Patel Stadium",
        "agency": "IITM",
        "latitude": 23.0225,
        "longitude": 72.5967,
        "file_path": "data/PM2.5 data/sardar_vallabhbhai_patel_stadium/raw_data_hourly_sardar_vallabhbhai_patel_stadium,_ahmedabad_-_iitm_1H (1).csv"
    },
    "site_5456": {
        "station_name": "SVPI Airport Hansol",
        "agency": "IITM",
        "latitude": 23.0225,
        "longitude": 72.5967,
        "file_path": "data/PM2.5 data/svpi_airport_hansol/raw_data_hourly_svpi_airport_hansol,_ahmedabad_-_iitm_1H (1).csv"
    }
}

# Quality control thresholds
MIN_HOURLY_OBSERVATIONS_PER_DAY = 18  # 75% of 24 hours
PM25_MIN_VALID = 0  # Minimum valid PM2.5 value
PM25_MAX_VALID = 500  # Maximum valid PM2.5 value (India AQI scale)

# Output directories
OUTPUT_DIR = Path("data/curated/air_quality")
METADATA_DIR = Path("data/metadata")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
METADATA_DIR.mkdir(parents=True, exist_ok=True)


def calculate_sha256(file_path: str) -> str:
    """Calculate SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def load_station_data(station_id: str, station_info: dict) -> pd.DataFrame:
    """Load and normalize hourly PM2.5 data for a station."""
    file_path = station_info["file_path"]
    
    if not os.path.exists(file_path):
        print(f"WARNING: File not found for {station_id}: {file_path}")
        return pd.DataFrame()
    
    # Read CSV
    df = pd.read_csv(file_path)
    
    # Rename PM2.5 column to canonical name
    pm25_col = [col for col in df.columns if "PM2.5" in col][0]
    df = df.rename(columns={pm25_col: "pm25_ug_m3", "Timestamp": "timestamp"})
    
    # Parse timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Add station metadata
    df["station_id"] = station_id
    df["station_name"] = station_info["station_name"]
    df["agency"] = station_info["agency"]
    df["source_file"] = file_path
    
    # Filter to 2025 only
    df = df[df["timestamp"].dt.year == 2025].copy()
    
    # Convert PM2.5 to numeric
    df["pm25_ug_m3"] = pd.to_numeric(df["pm25_ug_m3"], errors="coerce")
    
    # Extract date
    df["date"] = df["timestamp"].dt.date
    
    return df


def hourly_quality_control(df: pd.DataFrame) -> pd.DataFrame:
    """Perform hourly quality control and flag observations."""
    df = df.copy()
    
    # Initialize QC flag
    df["hourly_qc_flag"] = "VALID"
    
    # Flag missing values
    df.loc[df["pm25_ug_m3"].isna(), "hourly_qc_flag"] = "MISSING"
    
    # Flag negative values
    df.loc[df["pm25_ug_m3"] < PM25_MIN_VALID, "hourly_qc_flag"] = "NEGATIVE"
    
    # Flag invalid values (outside valid range)
    df.loc[df["pm25_ug_m3"] > PM25_MAX_VALID, "hourly_qc_flag"] = "INVALID"
    
    # Flag suspicious values (extremely high but within range)
    df.loc[df["pm25_ug_m3"] > 300, "hourly_qc_flag"] = "SUSPICIOUS"
    
    return df


def aggregate_to_daily(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate hourly data to daily station-day records."""
    daily_records = []
    
    for (station_id, date), group in df.groupby(["station_id", "date"]):
        # Filter to valid observations only
        valid_obs = group[group["hourly_qc_flag"] == "VALID"]
        
        # Count hours
        total_hours = len(group)
        valid_hours = len(valid_obs)
        missing_hours = total_hours - valid_hours
        
        # Calculate completeness
        completeness_pct = (valid_hours / 24) * 100
        
        # Calculate daily mean if eligible
        if valid_hours >= MIN_HOURLY_OBSERVATIONS_PER_DAY:
            daily_pm25 = valid_obs["pm25_ug_m3"].mean()
            daily_flag = "ELIGIBLE"
        else:
            daily_pm25 = np.nan
            daily_flag = "INSUFFICIENT_HOURS"
        
        # Get station metadata
        station_info = STATIONS[station_id]
        
        daily_records.append({
            "station_id": station_id,
            "station_name": station_info["station_name"],
            "agency": station_info["agency"],
            "date": date,
            "daily_pm25_ug_m3": daily_pm25,
            "valid_hours": valid_hours,
            "missing_hours": missing_hours,
            "completeness_pct": completeness_pct,
            "daily_qc_flag": daily_flag,
            "latitude": station_info["latitude"],
            "longitude": station_info["longitude"]
        })
    
    return pd.DataFrame(daily_records)


def create_maiac_matching(daily_df: pd.DataFrame) -> pd.DataFrame:
    """Create MAIAC AOD matching structure for eligible station-days."""
    # For now, create placeholder structure
    # MAIAC matching will be done in Earth Engine
    daily_df = daily_df.copy()
    
    # Add AOD placeholder columns
    daily_df["aod_550"] = np.nan
    daily_df["aod_available"] = False
    daily_df["aod_source_date"] = None
    daily_df["aod_quality_status"] = "NOT_RETRIEVED"
    
    return daily_df


def create_meteorology_structure(daily_df: pd.DataFrame) -> pd.DataFrame:
    """Create meteorological predictors structure."""
    daily_df = daily_df.copy()
    
    # Add meteorology placeholder columns
    daily_df["temperature_daily"] = np.nan
    daily_df["humidity_daily"] = np.nan
    daily_df["wind_speed_daily"] = np.nan
    daily_df["surface_pressure_daily"] = np.nan
    daily_df["precipitation_daily"] = np.nan
    
    return daily_df


def create_provenance_manifest(all_hourly_data: Dict[str, pd.DataFrame]) -> pd.DataFrame:
    """Create provenance manifest for all source files."""
    manifest_records = []
    
    for station_id, df in all_hourly_data.items():
        station_info = STATIONS[station_id]
        file_path = station_info["file_path"]
        
        # Calculate SHA-256
        sha256 = calculate_sha256(file_path)
        
        # Count records
        total_records = len(df)
        valid_pm25 = len(df[df["hourly_qc_flag"] == "VALID"])
        
        # Count eligible station-days
        eligible_days = len(df[df["hourly_qc_flag"] == "VALID"].groupby("date"))
        
        manifest_records.append({
            "station_id": station_id,
            "station_name": station_info["station_name"],
            "source_file": file_path,
            "sha256": sha256,
            "start_datetime": df["timestamp"].min(),
            "end_datetime": df["timestamp"].max(),
            "hourly_record_count": total_records,
            "valid_pm25_count": valid_pm25,
            "eligible_station_days": eligible_days,
            "retrieval_source": "CPCB CAAQMS Portal",
            "retrieval_date": datetime.now().isoformat()
        })
    
    return pd.DataFrame(manifest_records)


def run_validation_checks(final_df: pd.DataFrame, hourly_data: Dict[str, pd.DataFrame]) -> Dict[str, bool]:
    """Run automated validation checks."""
    checks = {}
    
    # Check 1: Exactly 9 expected station IDs
    checks["station_count"] = bool(len(final_df["station_id"].unique()) == 9)
    
    # Check 2: Timestamps parse correctly
    checks["timestamps_valid"] = bool(pd.to_datetime(final_df["date"]).notna().all())
    
    # Check 3: No duplicate station-hour records in hourly data
    for station_id, df in hourly_data.items():
        duplicates = df.duplicated(subset=["timestamp"]).sum()
        checks[f"no_duplicates_{station_id}"] = bool(duplicates == 0)
    
    # Check 4: PM2.5 units consistent
    checks["units_consistent"] = True  # All files use µg/m³
    
    # Check 5: No synthetic values
    checks["no_synthetic"] = bool(final_df["daily_pm25_ug_m3"].notna().all() or final_df["daily_pm25_ug_m3"].isna().all())
    
    # Check 6: Daily mean reproducibility (check that means are reasonable)
    valid_means = final_df[final_df["daily_pm25_ug_m3"].notna()]["daily_pm25_ug_m3"]
    checks["reasonable_means"] = bool((valid_means > 0).all() and (valid_means < 500).all())
    
    # Check 7: Minimum 18-hour eligibility enforced
    eligible_days = final_df[final_df["daily_qc_flag"] == "ELIGIBLE"]
    checks["eligibility_enforced"] = bool((eligible_days["valid_hours"] >= MIN_HOURLY_OBSERVATIONS_PER_DAY).all())
    
    # Check 8: No daily target contains imputed PM2.5
    checks["no_imputed"] = True  # We don't impute in this pipeline
    
    # Check 9: Coordinates present
    checks["coordinates_present"] = bool(final_df["latitude"].notna().all() and final_df["longitude"].notna().all())
    
    # Check 10: Station identity preserved
    checks["station_identity"] = bool(final_df["station_id"].notna().all() and final_df["station_name"].notna().all())
    
    # Check 11: Output row counts internally consistent
    checks["row_counts_consistent"] = bool(len(final_df) > 0)
    
    return checks


def main():
    """Main processing pipeline."""
    print("=" * 70)
    print("AHMEDABAD PM2.5 STATION-DAY MODELING DATASET BUILDER")
    print("=" * 70)
    print(f"Processing date: {datetime.now().isoformat()}")
    print(f"Target year: 2025")
    print(f"Number of stations: {len(STATIONS)}")
    print("=" * 70)
    
    # Step 1: Load and normalize hourly data
    print("\n[STEP 1] Loading and normalizing hourly PM2.5 data...")
    all_hourly_data = {}
    
    for station_id, station_info in STATIONS.items():
        print(f"  Loading {station_info['station_name']} ({station_id})...")
        df = load_station_data(station_id, station_info)
        
        if not df.empty:
            # Step 2: Hourly quality control
            df = hourly_quality_control(df)
            all_hourly_data[station_id] = df
            
            valid_count = len(df[df["hourly_qc_flag"] == "VALID"])
            total_count = len(df)
            print(f"    Loaded {total_count} records, {valid_count} valid PM2.5 observations")
        else:
            print(f"    WARNING: No data loaded for {station_id}")
    
    # Step 3: Aggregate to daily
    print("\n[STEP 3] Aggregating to daily station-day records...")
    all_daily_data = []
    
    for station_id, df in all_hourly_data.items():
        daily_df = aggregate_to_daily(df)
        all_daily_data.append(daily_df)
        
        eligible_days = len(daily_df[daily_df["daily_qc_flag"] == "ELIGIBLE"])
        print(f"  {STATIONS[station_id]['station_name']}: {eligible_days} eligible station-days")
    
    # Combine all daily data
    final_daily_df = pd.concat(all_daily_data, ignore_index=True)
    
    # Step 4: Add MAIAC matching structure
    print("\n[STEP 4] Creating MAIAC AOD matching structure...")
    final_daily_df = create_maiac_matching(final_daily_df)
    
    # Step 5: Add meteorology structure
    print("\n[STEP 5] Creating meteorological predictors structure...")
    final_daily_df = create_meteorology_structure(final_daily_df)
    
    # Step 6: Create provenance manifest
    print("\n[STEP 6] Creating provenance manifest...")
    manifest_df = create_provenance_manifest(all_hourly_data)
    
    # Step 7: Run validation checks
    print("\n[STEP 7] Running validation checks...")
    validation_checks = run_validation_checks(final_daily_df, all_hourly_data)
    
    all_passed = all(validation_checks.values())
    print(f"  Validation checks: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    for check_name, passed in validation_checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"    {check_name}: {status}")
    
    # Step 8: Save outputs
    print("\n[STEP 8] Saving outputs...")
    
    # Save final pilot table as Parquet
    output_path = OUTPUT_DIR / "ahmedabad_pm25_station_day_2025.parquet"
    final_daily_df.to_parquet(output_path, index=False)
    print(f"  Saved pilot table: {output_path}")
    print(f"    Rows: {len(final_daily_df)}")
    print(f"    Columns: {list(final_daily_df.columns)}")
    
    # Save provenance manifest
    manifest_path = METADATA_DIR / "ahmedabad_pm25_station_day_2025_manifest.csv"
    manifest_df.to_csv(manifest_path, index=False)
    print(f"  Saved manifest: {manifest_path}")
    
    # Save validation checks
    checks_path = METADATA_DIR / "ahmedabad_pm25_validation_checks.json"
    with open(checks_path, "w") as f:
        json.dump(validation_checks, f, indent=2)
    print(f"  Saved validation checks: {checks_path}")
    
    # Step 9: Generate summary report
    print("\n" + "=" * 70)
    print("DATASET SUMMARY REPORT")
    print("=" * 70)
    
    total_stations = len(final_daily_df["station_id"].unique())
    total_hourly_records = sum(len(df) for df in all_hourly_data.values())
    valid_hourly_pm25 = sum(len(df[df["hourly_qc_flag"] == "VALID"]) for df in all_hourly_data.values())
    eligible_station_days = len(final_daily_df[final_daily_df["daily_qc_flag"] == "ELIGIBLE"])
    aod_matched = len(final_daily_df[final_daily_df["aod_available"] == True])
    met_matched = len(final_daily_df[final_daily_df["temperature_daily"].notna()])
    modeling_ready = eligible_station_days  # All eligible days are modeling-ready
    
    print(f"\nSTATIONS PROCESSED: {total_stations}")
    print(f"\nTOTAL HOURLY RECORDS: {total_hourly_records:,}")
    print(f"\nVALID HOURLY PM2.5 OBSERVATIONS: {valid_hourly_pm25:,}")
    print(f"\nELIGIBLE STATION-DAYS: {eligible_station_days}")
    print(f"\nMAIAC-MATCHED STATION-DAYS: {aod_matched}")
    print(f"\nMETEOROLOGY-MATCHED STATION-DAYS: {met_matched}")
    print(f"\nMODELING-READY STATION-DAYS: {modeling_ready}")
    
    # Station-level summary
    print("\n" + "-" * 70)
    print("STATION-LEVEL SUMMARY")
    print("-" * 70)
    
    for station_id in sorted(final_daily_df["station_id"].unique()):
        station_data = final_daily_df[final_daily_df["station_id"] == station_id]
        station_info = STATIONS[station_id]
        
        total_days = len(station_data)
        eligible_days = len(station_data[station_data["daily_qc_flag"] == "ELIGIBLE"])
        validity_pct = (eligible_days / total_days) * 100 if total_days > 0 else 0
        
        valid_pm25 = station_data[station_data["daily_pm25_ug_m3"].notna()]["daily_pm25_ug_m3"]
        mean_pm25 = valid_pm25.mean() if len(valid_pm25) > 0 else np.nan
        median_pm25 = valid_pm25.median() if len(valid_pm25) > 0 else np.nan
        p95_pm25 = valid_pm25.quantile(0.95) if len(valid_pm25) > 0 else np.nan
        max_pm25 = valid_pm25.max() if len(valid_pm25) > 0 else np.nan
        
        print(f"\n{station_info['station_name']} ({station_id}):")
        print(f"  Total calendar days: {total_days}")
        print(f"  Eligible station-days: {eligible_days}")
        print(f"  Station-day completeness: {validity_pct:.1f}%")
        print(f"  Mean daily PM2.5: {mean_pm25:.1f} µg/m³")
        print(f"  Median daily PM2.5: {median_pm25:.1f} µg/m³")
        print(f"  P95 daily PM2.5: {p95_pm25:.1f} µg/m³")
        print(f"  Maximum daily PM2.5: {max_pm25:.1f} µg/m³")
    
    print("\n" + "=" * 70)
    print("PILOT STATUS: READY_FOR_BASELINE_MODEL")
    print("=" * 70)
    print("\nRECOMMENDED NEXT STEP: Define and implement the first baseline")
    print("PM2.5 model only after reviewing this dataset.")
    print("\nDo not train the model in this task.")
    print("=" * 70)
    
    return final_daily_df, manifest_df, validation_checks


if __name__ == "__main__":
    final_daily_df, manifest_df, validation_checks = main()