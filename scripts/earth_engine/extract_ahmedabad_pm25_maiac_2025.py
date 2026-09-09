"""
Earth Engine Extraction: MAIAC AOD for Ahmedabad PM2.5 Stations (2025)
======================================================================

This script extracts daily MAIAC AOD values at CPCB station coordinates
for the 2025 Ahmedabad PM2.5 modeling dataset.

MEMORY-SAFE DESIGN:
- Uses station-day driver table (not full-city rasters)
- Processes data in quarterly chunks to avoid memory limits
- Exports only station-day records

DATASET:
- Source: MODIS/061/MCD19A2_GRANULES
- Variable: Optical_Depth_055
- Scale: AOD_550 = stored_value x 0.001

QA FILTERING:
- Cloud mask bits 0-1 = 00 (clear)
- Heavy dust flag bit 2 = 0

REQUIREMENTS:
- Google Earth Engine Python API (earthengine-api)
- Authenticated Earth Engine account
- Project: agniraksha-508013

USAGE:
    python scripts/earth_engine/extract_ahmedabad_pm25_maiac_2025.py

OUTPUT:
    data/staging/earth_engine/ahmedabad_pm25_maiac_station_day_2025.csv
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(".")
DRIVER_CSV = BASE_DIR / "data" / "staging" / "earth_engine" / "ahmedabad_pm25_station_days_2025.csv"
OUTPUT_DIR = BASE_DIR / "data" / "staging" / "earth_engine"
OUTPUT_CSV = OUTPUT_DIR / "ahmedabad_pm25_maiac_station_day_2025.csv"

# Earth Engine configuration
EE_PROJECT = "agniraksha-508013"
MAIAC_COLLECTION = "MODIS/061/MCD19A2_GRANULES"
AOD_BAND = "Optical_Depth_055"
QA_BAND = "AOD_QA"
SCALE_FACTOR = 0.001
EXTRACTION_RADIUS = 1000  # meters

# Quarterly chunks for memory-safe processing
QUARTERS = [
    ("2025-01-01", "2025-03-31", "Q1"),
    ("2025-04-01", "2025-06-30", "Q2"),
    ("2025-07-01", "2025-09-30", "Q3"),
    ("2025-10-01", "2025-12-31", "Q4"),
]

print("=" * 70)
print("MAIAC AOD EXTRACTION FOR AHMEDABAD PM2.5 STATIONS (2025)")
print("=" * 70)
print(f"Script generated: {datetime.now().isoformat()}")
print()

# ============================================================
# STEP 1: LOAD DRIVER TABLE
# ============================================================

print("[STEP 1] Loading driver table...")

if not DRIVER_CSV.exists():
    print(f"  ERROR: Driver table not found: {DRIVER_CSV}")
    sys.exit(1)

driver_df = pd.read_csv(DRIVER_CSV)
print(f"  Loaded {len(driver_df)} station-days")
print(f"  Stations: {driver_df['station_id'].nunique()}")
print(f"  Date range: {driver_df['date'].min()} to {driver_df['date'].max()}")
print()

# ============================================================
# STEP 2: CHECK EARTH ENGINE AUTHENTICATION
# ============================================================

print("[STEP 2] Checking Earth Engine authentication...")

try:
    import ee
    ee.Initialize(project=EE_PROJECT)
    print("  Earth Engine authenticated successfully")
    print(f"  Project: {EE_PROJECT}")
except Exception as e:
    print(f"  ERROR: Earth Engine authentication failed: {e}")
    print()
    print("  To authenticate:")
    print("    1. Install: pip install earthengine-api")
    print("    2. Authenticate: earthengine authenticate")
    print("    3. Set project: earthengine set_project agniraksha-508013")
    print()
    print("  See: https://developers.google.com/earth-engine/guides/python_install")
    sys.exit(1)

print()

# ============================================================
# STEP 3: DEFINE QA FILTERING
# ============================================================

print("[STEP 3] Defining QA filtering...")

def get_qa_mask():
    """
    Create QA mask for MAIAC AOD.
    
    QA Bit Interpretation:
    - Bits 0-1: Cloud mask (00 = clear)
    - Bit 2: Heavy dust flag (0 = no heavy dust)
    
    Valid pixels: Bits 0-1 = 00 AND Bit 2 = 0
    """
    qa_image = ee.ImageCollection(MAIAC_COLLECTION).select(QA_BAND).first()
    
    # Cloud mask: bits 0-1 must be 00
    cloud_mask = qa_image.bitwiseAnd(3).eq(0)
    
    # Heavy dust: bit 2 must be 0
    dust_mask = qa_image.bitwiseAnd(4).eq(0)
    
    # Combined mask
    valid_mask = cloud_mask.And(dust_mask)
    
    return valid_mask

print("  QA Filter:")
print("    - Cloud mask bits 0-1 = 00 (clear)")
print("    - Heavy dust flag bit 2 = 0")
print()

# ============================================================
# STEP 4: DEFINE EXTRACTION FUNCTION
# ============================================================

print("[STEP 4] Defining extraction function...")

def extract_maiac_for_date(date_str, station_coords):
    """
    Extract MAIAC AOD for a specific date at station coordinates.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        station_coords: List of (station_id, lat, lon) tuples
    
    Returns:
        List of dicts with station_id, date, aod_550, aod_available, etc.
    """
    date = ee.Date(date_str)
    next_date = date.advance(1, 'day')
    
    # Filter MAIAC collection to single day
    maiac_daily = ee.ImageCollection(MAIAC_COLLECTION) \
        .filterDate(date, next_date) \
        .select(AOD_BAND)
    
    # Check if any images exist
    image_count = maiac_daily.size().getInfo()
    
    if image_count == 0:
        # No MAIAC data for this date
        return [{
            "station_id": sid,
            "date": date_str,
            "aod_550": None,
            "aod_available": False,
            "aod_quality_status": "NO_DATA",
            "aod_valid_pixel_count": 0,
            "aod_source_date": None,
        } for sid, _, _ in station_coords]
    
    # Get the daily composite (mean of available overpasses)
    daily_composite = maiac_daily.mean()
    
    # Apply QA mask
    qa_mask = get_qa_mask()
    masked_composite = daily_composite.updateMask(qa_mask)
    
    # Scale AOD
    scaled_composite = masked_composite.multiply(SCALE_FACTOR)
    
    # Extract at station points
    results = []
    for sid, lat, lon in station_coords:
        point = ee.Geometry.Point([lon, lat])
        
        try:
            value = scaled_composite.reduceRegion(
                ee.Reducer.first(),
                point,
                EXTRACTION_RADIUS
            ).getInfo()
            
            aod_value = value.get(AOD_BAND)
            
            if aod_value is not None:
                results.append({
                    "station_id": sid,
                    "date": date_str,
                    "aod_550": aod_value,
                    "aod_available": True,
                    "aod_quality_status": "VALID",
                    "aod_valid_pixel_count": 1,
                    "aod_source_date": date_str,
                })
            else:
                results.append({
                    "station_id": sid,
                    "date": date_str,
                    "aod_550": None,
                    "aod_available": False,
                    "aod_quality_status": "MASKED",
                    "aod_valid_pixel_count": 0,
                    "aod_source_date": None,
                })
        except Exception as e:
            results.append({
                "station_id": sid,
                "date": date_str,
                "aod_550": None,
                "aod_available": False,
                "aod_quality_status": f"ERROR: {str(e)[:50]}",
                "aod_valid_pixel_count": 0,
                "aod_source_date": None,
            })
    
    return results

print("  Extraction function defined")
print()

# ============================================================
# STEP 5: PROCESS QUARTERLY CHUNKS
# ============================================================

print("[STEP 5] Processing quarterly chunks...")

all_results = []

for start_date, end_date, quarter_name in QUARTERS:
    print(f"  Processing {quarter_name} ({start_date} to {end_date})...")
    
    # Filter driver table to quarter
    quarter_dates = driver_df[
        (driver_df["date"] >= start_date) & 
        (driver_df["date"] <= end_date)
    ]["date"].unique()
    
    print(f"    Dates in quarter: {len(quarter_dates)}")
    
    # Get unique stations
    stations = [(row["station_id"], row["latitude"], row["longitude"]) 
                for _, row in driver_df.drop_duplicates("station_id").iterrows()]
    
    # Process each date
    quarter_results = []
    for i, date_str in enumerate(sorted(quarter_dates)):
        if (i + 1) % 10 == 0:
            print(f"    Processing date {i+1}/{len(quarter_dates)}: {date_str}")
        
        date_results = extract_maiac_for_date(date_str, stations)
        quarter_results.extend(date_results)
    
    all_results.extend(quarter_results)
    print(f"    Completed {quarter_name}: {len(quarter_results)} records")
    print()

# ============================================================
# STEP 6: SAVE RESULTS
# ============================================================

print("[STEP 6] Saving results...")

results_df = pd.DataFrame(all_results)
results_df.to_csv(OUTPUT_CSV, index=False)

print(f"  Saved: {OUTPUT_CSV}")
print(f"  Total records: {len(results_df)}")
print(f"  AOD available: {results_df['aod_available'].sum()}")
print(f"  AOD match rate: {results_df['aod_available'].mean()*100:.1f}%")
print()

# ============================================================
# SUMMARY
# ============================================================

print("=" * 70)
print("EXTRACTION COMPLETE")
print("=" * 70)
print()
print("NEXT STEPS:")
print("  1. Review the extracted AOD values")
print("  2. Run quality control checks")
print("  3. Join with ERA5 meteorology")
print("  4. Create final matched dataset")
print()
print("OUTPUT FILE:")
print(f"  {OUTPUT_CSV}")
print()