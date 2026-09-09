"""
MAIAC Coverage Audit — 10 Station/Date Samples
===============================================

This script runs a coverage audit for 10 real station/date combinations
from the driver table to assess MAIAC AOD availability.

OFFICIAL MAIAC AOD_QA BIT DEFINITION (16-bit unsigned integer):
- Bits 0-2: Cloud Mask (000=Undefined, 001=Clear, 010=Possibly Cloudy, etc.)
- Bits 3-4: Land Water Snow/Ice Mask (00=Land, 01=Water, 10=Snow, 11=Ice)
- Bits 8-11: QA for AOD (0000=Best quality, 0101=No retrieval, etc.)

PRIMARY MODELING AOD REQUIREMENTS (Strict Best Quality):
- Bits 0-2 = 1 (Clear)
- Bits 3-4 = 0 (Land)
- Bits 8-11 = 0 (Best quality)

CLEAR RETRIEVAL QA (Official MCD19A2.061 documentation):
- Bits 0-2 = 1 (Clear) OR Bits 0-2 = 2 (Possibly Cloudy)
- Bits 3-4 = 0 (Land)
- Bits 8-11 = 0 (Best quality) OR Bits 8-11 = 11 (Research quality)

USAGE:
    python scripts/earth_engine/audit_maiac_coverage_2025.py

OUTPUT:
    data/metadata/maiac_2025_coverage_audit.csv
"""

import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

EE_PROJECT = "agniraksha-508013"
MAIAC_COLLECTION = "MODIS/061/MCD19A2_GRANULES"
AOD_BAND = "Optical_Depth_055"
QA_BAND = "AOD_QA"
SCALE_FACTOR = 0.001
EXTRACTION_RADIUS = 2000  # meters
NEIGHBORHOOD_RADIUS = 1500  # meters

# Selection file
SELECTION_CSV = Path("data/metadata/maiac_2025_audit_selection.csv")
OUTPUT_CSV = Path("data/metadata/maiac_2025_coverage_audit.csv")

print("=" * 70)
print("MAIAC COVERAGE AUDIT — 10 STATION/DATE SAMPLES")
print("=" * 70)
print(f"Script generated: {datetime.now().isoformat()}")
print()

# ============================================================
# STEP 1: CHECK EARTH ENGINE AUTHENTICATION
# ============================================================

print("[STEP 1] Checking Earth Engine authentication...")

try:
    import ee
    ee.Initialize(project=EE_PROJECT)
    print("  Earth Engine authenticated successfully")
    print(f"  Project: {EE_PROJECT}")
except Exception as e:
    print(f"  ERROR: Earth Engine authentication failed: {e}")
    sys.exit(1)

print()

# ============================================================
# STEP 2: LOAD SELECTION
# ============================================================

print("[STEP 2] Loading selection...")

if not SELECTION_CSV.exists():
    print(f"  ERROR: Selection file not found: {SELECTION_CSV}")
    sys.exit(1)

selection_df = pd.read_csv(SELECTION_CSV)
selection_df['date'] = pd.to_datetime(selection_df['date'])
print(f"  Loaded {len(selection_df)} station/date combinations")
print()

# ============================================================
# STEP 3: DEFINE QA DECODING FUNCTIONS
# ============================================================

print("[STEP 3] Defining QA decoding functions...")

def decode_cloud_mask(qa_value):
    """Decode bits 0-2: Cloud Mask"""
    return qa_value & 7  # Mask with 0b111

def decode_land_mask(qa_value):
    """Decode bits 3-4: Land Water Snow/Ice Mask"""
    return (qa_value >> 3) & 3  # Shift right 3, mask with 0b11

def decode_aod_qa(qa_value):
    """Decode bits 8-11: QA for AOD"""
    return (qa_value >> 8) & 15  # Shift right 8, mask with 0b1111

def get_cloud_mask_name(value):
    """Get human-readable name for cloud mask value"""
    names = {
        0: "Undefined",
        1: "Clear",
        2: "Possibly Cloudy",
        3: "Cloudy",
        5: "Cloud Shadow",
        6: "Hot spot of fire",
        7: "Water Sediments",
    }
    return names.get(value, f"Unknown ({value})")

def get_land_mask_name(value):
    """Get human-readable name for land mask value"""
    names = {
        0: "Land",
        1: "Water",
        2: "Snow",
        3: "Ice",
    }
    return names.get(value, f"Unknown ({value})")

def get_aod_qa_name(value):
    """Get human-readable name for AOD QA value"""
    names = {
        0: "Best quality",
        1: "Water Sediments detected",
        3: "1 neighbor cloud",
        4: ">1 neighbor clouds",
        5: "No retrieval (cloudy)",
        6: "No retrieval near snow",
        7: "Climatology AOD (high altitude)",
        8: "No retrieval due to sun glint",
        9: "Very low AOD due to glint",
        10: "Coastline replacement",
        11: "Research quality (CM possibly cloudy)",
    }
    return names.get(value, f"Unknown ({value})")

print("  QA decoding functions defined")
print()

# ============================================================
# STEP 4: DEFINE QA CHECK FUNCTIONS
# ============================================================

print("[STEP 4] Defining QA check functions...")

def check_strict_best_quality(qa_value):
    """
    Check if pixel meets strict best quality requirements.
    
    Requirements:
    - Bits 0-2 = 1 (Clear)
    - Bits 3-4 = 0 (Land)
    - Bits 8-11 = 0 (Best quality)
    """
    cloud = decode_cloud_mask(qa_value) == 1
    land = decode_land_mask(qa_value) == 0
    aod_qa = decode_aod_qa(qa_value) == 0
    return cloud and land and aod_qa

def check_clear_retrieval(qa_value):
    """
    Check if pixel meets clear retrieval requirements.
    
    Official MCD19A2.061 documentation:
    - Bits 0-2 = 1 (Clear) OR Bits 0-2 = 2 (Possibly Cloudy)
    - Bits 3-4 = 0 (Land)
    - Bits 8-11 = 0 (Best quality) OR Bits 8-11 = 11 (Research quality)
    """
    cloud = decode_cloud_mask(qa_value) in [1, 2]  # Clear or Possibly Cloudy
    land = decode_land_mask(qa_value) == 0
    aod_qa = decode_aod_qa(qa_value) in [0, 11]  # Best quality or Research quality
    return cloud and land and aod_qa

print("  QA check functions defined")
print("    - Strict Best Quality: Clear + Land + Best quality")
print("    - Clear Retrieval: (Clear or Possibly Cloudy) + Land + (Best quality or Research quality)")
print()

# ============================================================
# STEP 5: RUN AUDIT FOR EACH ROW
# ============================================================

print("[STEP 5] Running audit for each row...")

audit_results = []

for idx, row in selection_df.iterrows():
    station_id = row['station_id']
    station_name = row['station_name']
    date_str = row['date'].strftime('%Y-%m-%d')
    lat = row['latitude']
    lon = row['longitude']
    
    print(f"  [{idx+1}/10] {station_name} ({station_id}), {date_str}...")
    
    # Get MAIAC data for this date
    date = ee.Date(date_str)
    next_date = date.advance(1, 'day')
    
    maiac_daily = ee.ImageCollection(MAIAC_COLLECTION) \
        .filterDate(date, next_date) \
        .select([AOD_BAND, QA_BAND])
    
    # Get number of granules
    image_count = maiac_daily.size().getInfo()
    
    if image_count == 0:
        # No MAIAC data for this date
        audit_results.append({
            'station_id': station_id,
            'station_name': station_name,
            'date': date_str,
            'latitude': lat,
            'longitude': lon,
            'covering_granules': 0,
            'raw_station_AOD': None,
            'raw_station_QA': None,
            'decoded_cloud_mask': None,
            'decoded_cloud_mask_name': None,
            'decoded_land_mask': None,
            'decoded_land_mask_name': None,
            'decoded_aod_qa': None,
            'decoded_aod_qa_name': None,
            'strict_best_quality_station_AOD': None,
            'strict_best_quality_valid_pixel_count': 0,
            'strict_best_quality_neighborhood_mean': None,
            'clear_retrieval_valid_pixel_count': 0,
            'clear_retrieval_neighborhood_mean': None,
        })
        print(f"    No MAIAC data for this date")
        continue
    
    # Use composite of all granules
    composite_image = maiac_daily.median()
    
    # Extract at station point
    point = ee.Geometry.Point([lon, lat])
    
    # Get raw values
    raw_values = composite_image.reduceRegion(
        ee.Reducer.first(),
        point,
        EXTRACTION_RADIUS
    ).getInfo()
    
    raw_aod = raw_values.get(AOD_BAND)
    raw_qa = raw_values.get(QA_BAND)
    
    # Decode QA
    if raw_qa is not None:
        cloud_mask_val = decode_cloud_mask(raw_qa)
        land_mask_val = decode_land_mask(raw_qa)
        aod_qa_val = decode_aod_qa(raw_qa)
    else:
        cloud_mask_val = None
        land_mask_val = None
        aod_qa_val = None
    
    # Apply strict best quality mask
    strict_mask = composite_image.select(AOD_BAND).multiply(SCALE_FACTOR)
    if raw_qa is not None and check_strict_best_quality(raw_qa):
        strict_aod = raw_aod * SCALE_FACTOR if raw_aod is not None else None
    else:
        strict_aod = None
    
    # Apply clear retrieval mask
    if raw_qa is not None and check_clear_retrieval(raw_qa):
        clear_aod = raw_aod * SCALE_FACTOR if raw_aod is not None else None
    else:
        clear_aod = None
    
    # Neighborhood analysis
    neighborhood_values = composite_image.select([AOD_BAND, QA_BAND]).reduceRegion(
        ee.Reducer.toList(),
        point.buffer(NEIGHBORHOOD_RADIUS),
        EXTRACTION_RADIUS
    ).getInfo()
    
    qa_values = neighborhood_values.get(QA_BAND, [])
    aod_values = neighborhood_values.get(AOD_BAND, [])
    
    # Count valid pixels for strict best quality
    strict_valid_count = 0
    strict_aod_values = []
    for i, qa in enumerate(qa_values):
        if check_strict_best_quality(qa):
            strict_valid_count += 1
            if aod_values[i] is not None:
                strict_aod_values.append(aod_values[i] * SCALE_FACTOR)
    
    strict_neighborhood_mean = sum(strict_aod_values) / len(strict_aod_values) if strict_aod_values else None
    
    # Count valid pixels for clear retrieval
    clear_valid_count = 0
    clear_aod_values = []
    for i, qa in enumerate(qa_values):
        if check_clear_retrieval(qa):
            clear_valid_count += 1
            if aod_values[i] is not None:
                clear_aod_values.append(aod_values[i] * SCALE_FACTOR)
    
    clear_neighborhood_mean = sum(clear_aod_values) / len(clear_aod_values) if clear_aod_values else None
    
    # Store results
    audit_results.append({
        'station_id': station_id,
        'station_name': station_name,
        'date': date_str,
        'latitude': lat,
        'longitude': lon,
        'covering_granules': image_count,
        'raw_station_AOD': raw_aod,
        'raw_station_QA': raw_qa,
        'decoded_cloud_mask': cloud_mask_val,
        'decoded_cloud_mask_name': get_cloud_mask_name(cloud_mask_val) if cloud_mask_val is not None else None,
        'decoded_land_mask': land_mask_val,
        'decoded_land_mask_name': get_land_mask_name(land_mask_val) if land_mask_val is not None else None,
        'decoded_aod_qa': aod_qa_val,
        'decoded_aod_qa_name': get_aod_qa_name(aod_qa_val) if aod_qa_val is not None else None,
        'strict_best_quality_station_AOD': strict_aod,
        'strict_best_quality_valid_pixel_count': strict_valid_count,
        'strict_best_quality_neighborhood_mean': strict_neighborhood_mean,
        'clear_retrieval_valid_pixel_count': clear_valid_count,
        'clear_retrieval_neighborhood_mean': clear_neighborhood_mean,
    })
    
    print(f"    Granules: {image_count}, Raw QA: {raw_qa}, Strict valid: {strict_valid_count}, Clear valid: {clear_valid_count}")

print()

# ============================================================
# STEP 6: SAVE RESULTS
# ============================================================

print("[STEP 6] Saving results...")

audit_df = pd.DataFrame(audit_results)
OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
audit_df.to_csv(OUTPUT_CSV, index=False)
print(f"  Saved: {OUTPUT_CSV}")
print()

# ============================================================
# STEP 7: REPORT RESULTS
# ============================================================

print("=" * 70)
print("AUDIT RESULTS")
print("=" * 70)
print()

# Strict best-quality availability
strict_available = audit_df['strict_best_quality_station_AOD'].notna().sum()
strict_pct = strict_available / len(audit_df) * 100
print(f"Strict Best-Quality Station Availability: {strict_available}/{len(audit_df)} ({strict_pct:.1f}%)")
print()

# Clear-retrieval availability
clear_available = audit_df['clear_retrieval_valid_pixel_count'].gt(0).sum()
clear_pct = clear_available / len(audit_df) * 100
print(f"Clear-Retrieval Station Availability: {clear_available}/{len(audit_df)} ({clear_pct:.1f}%)")
print()

# Valid pixel counts
print("Valid Pixel Counts:")
print(f"  Strict Best-Quality: mean={audit_df['strict_best_quality_valid_pixel_count'].mean():.1f}, min={audit_df['strict_best_quality_valid_pixel_count'].min()}, max={audit_df['strict_best_quality_valid_pixel_count'].max()}")
print(f"  Clear Retrieval: mean={audit_df['clear_retrieval_valid_pixel_count'].mean():.1f}, min={audit_df['clear_retrieval_valid_pixel_count'].min()}, max={audit_df['clear_retrieval_valid_pixel_count'].max()}")
print()

# Missingness
missing_strict = audit_df['strict_best_quality_station_AOD'].isna().sum()
missing_clear = audit_df['clear_retrieval_valid_pixel_count'].eq(0).sum()
print(f"Missingness:")
print(f"  Strict Best-Quality: {missing_strict}/{len(audit_df)} ({missing_strict/len(audit_df)*100:.1f}%)")
print(f"  Clear Retrieval: {missing_clear}/{len(audit_df)} ({missing_clear/len(audit_df)*100:.1f}%)")
print()

# QA categories
print("QA Categories (decoded AOD QA):")
qa_counts = audit_df['decoded_aod_qa_name'].value_counts()
for qa_name, count in qa_counts.items():
    print(f"  {qa_name}: {count}")
print()

# Cloud mask categories
print("Cloud Mask Categories:")
cloud_counts = audit_df['decoded_cloud_mask_name'].value_counts()
for cloud_name, count in cloud_counts.items():
    print(f"  {cloud_name}: {count}")
print()

# Per-row details
print("Per-Row Details:")
print("-" * 100)
print(f"{'Station':<20} {'Date':<12} {'Granules':>8} {'Raw QA':>8} {'Cloud':>15} {'Land':>8} {'AOD QA':>25} {'Strict AOD':>10} {'Strict Valid':>12} {'Clear Valid':>12}")
print("-" * 100)

for _, row in audit_df.iterrows():
    strict_aod_str = f"{row['strict_best_quality_station_AOD']:.3f}" if pd.notna(row['strict_best_quality_station_AOD']) else "None"
    print(f"{row['station_name']:<20} {row['date']:<12} {row['covering_granules']:>8} {row['raw_station_QA']:>8} {row['decoded_cloud_mask_name']:>15} {row['decoded_land_mask_name']:>8} {row['decoded_aod_qa_name']:>25} {strict_aod_str:>10} {row['strict_best_quality_valid_pixel_count']:>12} {row['clear_retrieval_valid_pixel_count']:>12}")

print("-" * 100)
print()

print("=" * 70)
print("STOP")
print("=" * 70)