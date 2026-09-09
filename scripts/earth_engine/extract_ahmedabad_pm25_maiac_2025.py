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

QA FILTERING (OFFICIAL MAIAC AOD_QA BIT DEFINITION):
- Bits 0-2: Cloud Mask (must be 1 = Clear)
- Bits 3-4: Land Water Snow/Ice Mask (must be 0 = Land)
- Bits 8-11: QA for AOD (must be 0 = Best quality)

PRIMARY MODELING AOD REQUIREMENTS:
- Bits 0-2 = 1 (Clear)
- Bits 3-4 = 0 (Land)
- Bits 8-11 = 0 (Best quality)

NEVER use unmasked Optical_Depth_055 values.
Missing valid AOD must remain missing.
Do not spatially substitute a neighborhood mean for a missing station pixel.

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
    Create strict QA mask for MAIAC AOD.
    
    OFFICIAL MAIAC AOD_QA BIT DEFINITION (16-bit unsigned integer):
    - Bits 0-2: Cloud Mask
      - 000 = Undefined
      - 001 = Clear
      - 010 = Possibly Cloudy
      - 011 = Cloudy
      - 101 = Cloud Shadow
      - 110 = Hot spot of fire
      - 111 = Water Sediments
    
    - Bits 3-4: Land Water Snow/Ice Mask
      - 00 = Land
      - 01 = Water
      - 10 = Snow
      - 11 = Ice
    
    - Bits 8-11: QA for AOD
      - 0000 = Best quality
      - 0001 = Water Sediments detected
      - 0011 = 1 neighbor cloud
      - 0100 = >1 neighbor clouds
      - 0101 = No retrieval (cloudy)
      - 0110 = No retrieval near snow
      - 0111 = Climatology AOD (high altitude)
      - 1000 = No retrieval due to sun glint
      - 1001 = Very low AOD due to glint
      - 1010 = Coastline replacement
      - 1011 = Research quality (CM possibly cloudy)
    
    PRIMARY MODELING AOD REQUIREMENTS:
    - Bits 0-2 = 1 (Clear)
    - Bits 3-4 = 0 (Land)
    - Bits 8-11 = 0 (Best quality)
    """
    # Get the QA band
    qa_image = ee.ImageCollection(MAIAC_COLLECTION).select(QA_BAND).first()
    
    # Bits 0-2: Cloud Mask must be 1 (Clear)
    cloud_mask = qa_image.bitwiseAnd(7).eq(1)  # 0b111 = 7
    
    # Bits 3-4: Land Mask must be 0 (Land)
    land_mask = qa_image.rightShift(3).bitwiseAnd(3).eq(0)  # 0b11 = 3
    
    # Bits 8-11: AOD QA must be 0 (Best quality)
    aod_qa_mask = qa_image.rightShift(8).bitwiseAnd(15).eq(0)  # 0b1111 = 15
    
    # Combined mask: all conditions must be true
    valid_mask = cloud_mask.And(land_mask).And(aod_qa_mask)
    
    return valid_mask

print("  Strict QA Filter (OFFICIAL MAIAC AOD_QA BIT DEFINITION):")
print("    - Bits 0-2 = 1 (Clear)")
print("    - Bits 3-4 = 0 (Land)")
print("    - Bits 8-11 = 0 (Best quality)")
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
        .select([AOD_BAND, QA_BAND])
    
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
            "aod_total_granules": 0,
            "aod_valid_pixel_count": 0,
            "aod_station_pixel_qa": None,
            "aod_neighborhood_valid_count": 0,
            "aod_neighborhood_mean": None,
            "aod_source_date": None,
        } for sid, _, _ in station_coords]
    
    # Use composite of all granules for the day
    # This ensures we capture data from all overpasses
    composite_image = maiac_daily.median()
    
    # Apply QA mask
    qa_mask = get_qa_mask()
    masked_composite = composite_image.select(AOD_BAND).multiply(SCALE_FACTOR).updateMask(qa_mask)
    
    # Extract at station points
    results = []
    for sid, lat, lon in station_coords:
        point = ee.Geometry.Point([lon, lat])
        
        try:
            # Get masked AOD at station pixel
            value = masked_composite.reduceRegion(
                ee.Reducer.first(),
                point,
                EXTRACTION_RADIUS
            ).getInfo()
            
            aod_value = value.get(AOD_BAND)
            
            # Get raw QA value for diagnostics
            qa_value = composite_image.select(QA_BAND).reduceRegion(
                ee.Reducer.first(),
                point,
                EXTRACTION_RADIUS
            ).getInfo().get(QA_BAND)
            
            # Count valid neighborhood pixels
            neighborhood_radius = 1500  # meters
            neighborhood_values = composite_image.select([AOD_BAND, QA_BAND]).reduceRegion(
                ee.Reducer.toList(),
                point.buffer(neighborhood_radius),
                EXTRACTION_RADIUS
            ).getInfo()
            
            qa_values = neighborhood_values.get(QA_BAND, [])
            valid_count = 0
            masked_aod_values = []
            
            for i, qa in enumerate(qa_values):
                # Check if pixel is valid (strict QA)
                cloud = (qa & 7) == 1  # Bits 0-2 = 1 (Clear)
                land = ((qa >> 3) & 3) == 0  # Bits 3-4 = 0 (Land)
                aod_qa = ((qa >> 8) & 15) == 0  # Bits 8-11 = 0 (Best quality)
                
                if cloud and land and aod_qa:
                    valid_count += 1
                    aod_val = neighborhood_values.get(AOD_BAND, [])[i]
                    if aod_val is not None:
                        masked_aod_values.append(aod_val * SCALE_FACTOR)
            
            neighborhood_mean = sum(masked_aod_values) / len(masked_aod_values) if masked_aod_values else None
            
            if aod_value is not None:
                results.append({
                    "station_id": sid,
                    "date": date_str,
                    "aod_550": aod_value,
                    "aod_available": True,
                    "aod_quality_status": "VALID",
                    "aod_total_granules": image_count,
                    "aod_valid_pixel_count": 1,
                    "aod_station_pixel_qa": qa_value,
                    "aod_neighborhood_valid_count": valid_count,
                    "aod_neighborhood_mean": neighborhood_mean,
                    "aod_source_date": date_str,
                })
            else:
                results.append({
                    "station_id": sid,
                    "date": date_str,
                    "aod_550": None,
                    "aod_available": False,
                    "aod_quality_status": "MASKED",
                    "aod_total_granules": image_count,
                    "aod_valid_pixel_count": 0,
                    "aod_station_pixel_qa": qa_value,
                    "aod_neighborhood_valid_count": valid_count,
                    "aod_neighborhood_mean": neighborhood_mean,
                    "aod_source_date": None,
                })
        except Exception as e:
            results.append({
                "station_id": sid,
                "date": date_str,
                "aod_550": None,
                "aod_available": False,
                "aod_quality_status": f"ERROR: {str(e)[:50]}",
                "aod_total_granules": image_count,
                "aod_valid_pixel_count": 0,
                "aod_station_pixel_qa": None,
                "aod_neighborhood_valid_count": 0,
                "aod_neighborhood_mean": None,
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