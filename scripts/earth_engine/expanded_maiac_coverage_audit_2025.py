"""
Expanded MAIAC QA Coverage Audit — 150 Station/Day Samples
==========================================================

This script runs an expanded coverage audit for ~150 real station/date
combinations from the driver table to assess MAIAC AOD availability
under different QA rules.

OFFICIAL MAIAC AOD_QA BIT DEFINITION (16-bit unsigned integer):
- Bits 0-2: Cloud Mask
  - 000 = Undefined
  - 001 = Clear
  - 010 = Possibly Cloudy (detected by AOD filter)
  - 011 = Cloudy (detected by cloud mask algorithm)
  - 101 = Cloud Shadow
  - 110 = Hot spot of fire
  - 111 = Water Sediments

- Bits 3-4: Land Water Snow/Ice Mask
  - 00 = Land
  - 01 = Water
  - 10 = Snow
  - 11 = Ice

- Bits 5-7: Adjacency Mask
  - 000 = Normal condition/Clear
  - 001 = Adjacent to clouds
  - 010 = Surrounded by >4 cloudy pixels
  - 011 = Adjacent to a single cloudy pixel
  - 100 = Adjacent to snow
  - 101 = Snow was previously detected

- Bits 8-11: QA for AOD
  - 0000 = Best quality
  - 0001 = Water Sediments detected
  - 0011 = 1 neighbor cloud
  - 0100 = >1 neighbor clouds
  - 0101 = No retrieval (cloudy, or whatever)
  - 0110 = No retrieval near detected or previously snow
  - 0111 = Climatology AOD (altitude above 3.5km water, 4.2km land)
  - 1000 = No retrieval due to sun glint
  - 1001 = Retrieved AOD very low (<0.05) due to glint
  - 1010 = AOD within +-2km from coastline replaced by nearby AOD
  - 1011 = Land, research quality: AOD retrieved but CM is possibly cloudy

- Bit 12: Glint Mask
  - 0 = No glint
  - 1 = Glint (glint angle < 40°)

- Bits 13-14: Aerosol Model
  - 00 = Background model (regional)
  - 01 = Smoke model (regional)
  - 10 = Dust model

QA RULES TESTED:

RULE A (Strict Best Quality):
- AOD QA = 0 (Best quality)
- Land = 0 (Land)
- Cloud Mask = 1 (Clear)

RULE B (Research Quality):
- AOD QA = 11 (Research quality: AOD retrieved but CM is possibly cloudy)
- Land = 0 (Land)

RULE C (Neighbor Cloud Tolerance):
- AOD QA in {0, 3, 4} (Best quality, 1 neighbor cloud, >1 neighbor clouds)
- Land = 0 (Land)

USAGE:
    python scripts/earth_engine/expanded_maiac_coverage_audit_2025.py

OUTPUT:
    data/metadata/maiac_2025_expanded_coverage_audit.csv
    data/metadata/maiac_2025_qa_coverage_summary.csv
"""

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
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

# Input/Output files
DRIVER_CSV = Path("data/staging/earth_engine/ahmedabad_pm25_station_days_2025.csv")
EXPANDED_AUDIT_CSV = Path("data/metadata/maiac_2025_expanded_coverage_audit.csv")
SUMMARY_CSV = Path("data/metadata/maiac_2025_qa_coverage_summary.csv")

# Sample size
TARGET_SAMPLES = 150

print("=" * 70)
print("EXPANDED MAIAC QA COVERAGE AUDIT — 150 STATION/DAY SAMPLES")
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
# STEP 2: LOAD DRIVER TABLE AND SELECT SAMPLES
# ============================================================

print("[STEP 2] Loading driver table and selecting samples...")

if not DRIVER_CSV.exists():
    print(f"  ERROR: Driver table not found: {DRIVER_CSV}")
    sys.exit(1)

driver_df = pd.read_csv(DRIVER_CSV)
driver_df['date'] = pd.to_datetime(driver_df['date'])
print(f"  Loaded {len(driver_df)} station-days")
print(f"  Stations: {driver_df['station_id'].nunique()}")
print(f"  Date range: {driver_df['date'].min()} to {driver_df['date'].max()}")
print()

# Stratified sampling: all 9 stations, all 12 months
# Calculate samples per station-month
stations = driver_df['station_id'].unique()
months = range(1, 13)

# Create stratified selection
samples_per_cell = 1  # Start with 1 sample per station-month
total_samples_needed = TARGET_SAMPLES

# Calculate how many samples we can get
station_month_counts = driver_df.groupby(['station_id', driver_df['date'].dt.month]).size().reset_index(name='count')
print(f"  Station-month combinations with data: {len(station_month_counts)}")

# Select samples with stratification
selected_samples = []
for station in stations:
    for month in months:
        # Get eligible dates for this station-month
        eligible = driver_df[
            (driver_df['station_id'] == station) & 
            (driver_df['date'].dt.month == month)
        ]
        
        if len(eligible) > 0:
            # Select up to 2 samples per station-month
            n_select = min(2, len(eligible))
            selected = eligible.sample(n=n_select, random_state=42)
            selected_samples.append(selected)

# Combine all selected samples
selection_df = pd.concat(selected_samples)

# Trim to target size if oversampled
if len(selection_df) > TARGET_SAMPLES:
    selection_df = selection_df.sample(n=TARGET_SAMPLES, random_state=42)

# Reset index
selection_df = selection_df.reset_index(drop=True)

print(f"  Selected {len(selection_df)} station/day samples")
print(f"  Stations represented: {selection_df['station_id'].nunique()}")
print(f"  Months represented: {selection_df['date'].dt.month.nunique()}")
print()

# ============================================================
# STEP 3: DEFINE QA DECODING FUNCTIONS
# ============================================================

print("[STEP 3] Defining QA decoding functions...")

def decode_cloud_mask(qa_value):
    """Decode bits 0-2: Cloud Mask"""
    return int(qa_value) & 7

def decode_land_mask(qa_value):
    """Decode bits 3-4: Land Water Snow/Ice Mask"""
    return (int(qa_value) >> 3) & 3

def decode_adjacency_mask(qa_value):
    """Decode bits 5-7: Adjacency Mask"""
    return (int(qa_value) >> 5) & 7

def decode_aod_qa(qa_value):
    """Decode bits 8-11: QA for AOD"""
    return (int(qa_value) >> 8) & 15

def decode_glint_mask(qa_value):
    """Decode bit 12: Glint Mask"""
    return (int(qa_value) >> 12) & 1

def decode_aerosol_model(qa_value):
    """Decode bits 13-14: Aerosol Model"""
    return (int(qa_value) >> 13) & 3

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

def get_adjacency_mask_name(value):
    """Get human-readable name for adjacency mask value"""
    names = {
        0: "Normal/Clear",
        1: "Adjacent to clouds",
        2: "Surrounded by >4 cloudy pixels",
        3: "Adjacent to single cloudy pixel",
        4: "Adjacent to snow",
        5: "Snow previously detected",
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

def get_glint_mask_name(value):
    """Get human-readable name for glint mask value"""
    names = {
        0: "No glint",
        1: "Glint detected",
    }
    return names.get(value, f"Unknown ({value})")

def get_aerosol_model_name(value):
    """Get human-readable name for aerosol model value"""
    names = {
        0: "Background (regional)",
        1: "Smoke (regional)",
        2: "Dust",
    }
    return names.get(value, f"Unknown ({value})")

print("  QA decoding functions defined")
print()

# ============================================================
# STEP 4: DEFINE QA RULE CHECK FUNCTIONS
# ============================================================

print("[STEP 4] Defining QA rule check functions...")

def check_rule_a(qa_value):
    """
    RULE A: Strict Best Quality
    
    Official MCD19A2.061 documentation:
    - Bits 8-11 = 0 (Best quality)
    - Bits 3-4 = 0 (Land)
    - Bits 0-2 = 1 (Clear)
    """
    aod_qa = decode_aod_qa(qa_value) == 0
    land = decode_land_mask(qa_value) == 0
    cloud = decode_cloud_mask(qa_value) == 1
    return aod_qa and land and cloud

def check_rule_b(qa_value):
    """
    RULE B: Research Quality
    
    Official MCD19A2.061 documentation:
    - Bits 8-11 = 11 (Research quality: AOD retrieved but CM is possibly cloudy)
    - Bits 3-4 = 0 (Land)
    """
    aod_qa = decode_aod_qa(qa_value) == 11
    land = decode_land_mask(qa_value) == 0
    return aod_qa and land

def check_rule_c(qa_value):
    """
    RULE C: Neighbor Cloud Tolerance
    
    Official MCD19A2.061 documentation:
    - Bits 8-11 in {0, 3, 4} (Best quality, 1 neighbor cloud, >1 neighbor clouds)
    - Bits 3-4 = 0 (Land)
    """
    aod_qa = decode_aod_qa(qa_value) in [0, 3, 4]
    land = decode_land_mask(qa_value) == 0
    return aod_qa and land

print("  QA Rule Definitions:")
print("    RULE A: AOD QA=0 + Land=0 + Cloud Mask=1 (Strict Best Quality)")
print("    RULE B: AOD QA=11 + Land=0 (Research Quality)")
print("    RULE C: AOD QA in {0,3,4} + Land=0 (Neighbor Cloud Tolerance)")
print()

# ============================================================
# STEP 5: RUN AUDIT FOR EACH SAMPLE
# ============================================================

print("[STEP 5] Running audit for each sample...")

audit_results = []

for idx, row in selection_df.iterrows():
    station_id = row['station_id']
    station_name = row['station_name']
    date_str = row['date'].strftime('%Y-%m-%d')
    lat = row['latitude']
    lon = row['longitude']
    
    if (idx + 1) % 25 == 0 or idx == 0:
        print(f"  [{idx+1}/{len(selection_df)}] Processing {station_name} ({station_id}), {date_str}...")
    
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
            'raw_station_aod': None,
            'raw_station_qa': None,
            'cloud_mask': None,
            'cloud_mask_name': None,
            'land_mask': None,
            'land_mask_name': None,
            'adjacency_mask': None,
            'adjacency_mask_name': None,
            'aod_quality': None,
            'aod_quality_name': None,
            'glint_mask': None,
            'glint_mask_name': None,
            'aerosol_model': None,
            'aerosol_model_name': None,
            'rule_a_valid': False,
            'rule_a_neighborhood_valid_count': 0,
            'rule_a_neighborhood_mean_aod': None,
            'rule_b_valid': False,
            'rule_b_neighborhood_valid_count': 0,
            'rule_b_neighborhood_mean_aod': None,
            'rule_c_valid': False,
            'rule_c_neighborhood_valid_count': 0,
            'rule_c_neighborhood_mean_aod': None,
        })
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
        adjacency_mask_val = decode_adjacency_mask(raw_qa)
        aod_qa_val = decode_aod_qa(raw_qa)
        glint_mask_val = decode_glint_mask(raw_qa)
        aerosol_model_val = decode_aerosol_model(raw_qa)
        
        # Check rules
        rule_a_valid = check_rule_a(raw_qa)
        rule_b_valid = check_rule_b(raw_qa)
        rule_c_valid = check_rule_c(raw_qa)
    else:
        cloud_mask_val = None
        land_mask_val = None
        adjacency_mask_val = None
        aod_qa_val = None
        glint_mask_val = None
        aerosol_model_val = None
        rule_a_valid = False
        rule_b_valid = False
        rule_c_valid = False
    
    # Neighborhood analysis
    neighborhood_values = composite_image.select([AOD_BAND, QA_BAND]).reduceRegion(
        ee.Reducer.toList(),
        point.buffer(NEIGHBORHOOD_RADIUS),
        EXTRACTION_RADIUS
    ).getInfo()
    
    qa_values = neighborhood_values.get(QA_BAND, [])
    aod_values = neighborhood_values.get(AOD_BAND, [])
    
    # Count valid pixels for each rule
    rule_a_valid_count = 0
    rule_a_aod_values = []
    rule_b_valid_count = 0
    rule_b_aod_values = []
    rule_c_valid_count = 0
    rule_c_aod_values = []
    
    for i, qa in enumerate(qa_values):
        if check_rule_a(qa):
            rule_a_valid_count += 1
            if aod_values[i] is not None:
                rule_a_aod_values.append(aod_values[i] * SCALE_FACTOR)
        
        if check_rule_b(qa):
            rule_b_valid_count += 1
            if aod_values[i] is not None:
                rule_b_aod_values.append(aod_values[i] * SCALE_FACTOR)
        
        if check_rule_c(qa):
            rule_c_valid_count += 1
            if aod_values[i] is not None:
                rule_c_aod_values.append(aod_values[i] * SCALE_FACTOR)
    
    rule_a_neighborhood_mean = sum(rule_a_aod_values) / len(rule_a_aod_values) if rule_a_aod_values else None
    rule_b_neighborhood_mean = sum(rule_b_aod_values) / len(rule_b_aod_values) if rule_b_aod_values else None
    rule_c_neighborhood_mean = sum(rule_c_aod_values) / len(rule_c_aod_values) if rule_c_aod_values else None
    
    # Store results
    audit_results.append({
        'station_id': station_id,
        'station_name': station_name,
        'date': date_str,
        'latitude': lat,
        'longitude': lon,
        'covering_granules': image_count,
        'raw_station_aod': raw_aod,
        'raw_station_qa': raw_qa,
        'cloud_mask': cloud_mask_val,
        'cloud_mask_name': get_cloud_mask_name(cloud_mask_val) if cloud_mask_val is not None else None,
        'land_mask': land_mask_val,
        'land_mask_name': get_land_mask_name(land_mask_val) if land_mask_val is not None else None,
        'adjacency_mask': adjacency_mask_val,
        'adjacency_mask_name': get_adjacency_mask_name(adjacency_mask_val) if adjacency_mask_val is not None else None,
        'aod_quality': aod_qa_val,
        'aod_quality_name': get_aod_qa_name(aod_qa_val) if aod_qa_val is not None else None,
        'glint_mask': glint_mask_val,
        'glint_mask_name': get_glint_mask_name(glint_mask_val) if glint_mask_val is not None else None,
        'aerosol_model': aerosol_model_val,
        'aerosol_model_name': get_aerosol_model_name(aerosol_model_val) if aerosol_model_val is not None else None,
        'rule_a_valid': rule_a_valid,
        'rule_a_neighborhood_valid_count': rule_a_valid_count,
        'rule_a_neighborhood_mean_aod': rule_a_neighborhood_mean,
        'rule_b_valid': rule_b_valid,
        'rule_b_neighborhood_valid_count': rule_b_valid_count,
        'rule_b_neighborhood_mean_aod': rule_b_neighborhood_mean,
        'rule_c_valid': rule_c_valid,
        'rule_c_neighborhood_valid_count': rule_c_valid_count,
        'rule_c_neighborhood_mean_aod': rule_c_neighborhood_mean,
    })

print(f"  Completed audit for {len(audit_results)} samples")
print()

# ============================================================
# STEP 6: SAVE EXPANDED AUDIT RESULTS
# ============================================================

print("[STEP 6] Saving expanded audit results...")

audit_df = pd.DataFrame(audit_results)
EXPANDED_AUDIT_CSV.parent.mkdir(parents=True, exist_ok=True)
audit_df.to_csv(EXPANDED_AUDIT_CSV, index=False)
print(f"  Saved: {EXPANDED_AUDIT_CSV}")
print()

# ============================================================
# STEP 7: CREATE SUMMARY STATISTICS
# ============================================================

print("[STEP 7] Creating summary statistics...")

# Overall summary by rule
summary_rows = []

for rule_name, rule_col in [('RULE_A', 'rule_a_valid'), ('RULE_B', 'rule_b_valid'), ('RULE_C', 'rule_c_valid')]:
    valid_df = audit_df[audit_df[rule_col] == True]
    
    if len(valid_df) > 0:
        # Get neighborhood pixel counts and AOD values
        pixel_counts = valid_df[f'{rule_col.split("_valid")[0]}_neighborhood_valid_count'].dropna()
        aod_values = valid_df[f'{rule_col.split("_valid")[0]}_neighborhood_mean_aod'].dropna()
        
        summary_rows.append({
            'rule': rule_name,
            'sample_count': len(audit_df),
            'valid_station_days': len(valid_df),
            'coverage_pct': len(valid_df) / len(audit_df) * 100,
            'median_valid_neighborhood_pixels': pixel_counts.median() if len(pixel_counts) > 0 else None,
            'median_neighborhood_aod': aod_values.median() if len(aod_values) > 0 else None,
            'min_neighborhood_aod': aod_values.min() if len(aod_values) > 0 else None,
            'max_neighborhood_aod': aod_values.max() if len(aod_values) > 0 else None,
        })
    else:
        summary_rows.append({
            'rule': rule_name,
            'sample_count': len(audit_df),
            'valid_station_days': 0,
            'coverage_pct': 0.0,
            'median_valid_neighborhood_pixels': None,
            'median_neighborhood_aod': None,
            'min_neighborhood_aod': None,
            'max_neighborhood_aod': None,
        })

# Summary by station
for station in audit_df['station_id'].unique():
    station_df = audit_df[audit_df['station_id'] == station]
    station_name = station_df['station_name'].iloc[0]
    
    for rule_name, rule_col in [('RULE_A', 'rule_a_valid'), ('RULE_B', 'rule_b_valid'), ('RULE_C', 'rule_c_valid')]:
        valid_df = station_df[station_df[rule_col] == True]
        
        summary_rows.append({
            'rule': f"{rule_name}_BY_STATION_{station_name}",
            'sample_count': len(station_df),
            'valid_station_days': len(valid_df),
            'coverage_pct': len(valid_df) / len(station_df) * 100 if len(station_df) > 0 else 0,
            'median_valid_neighborhood_pixels': None,
            'median_neighborhood_aod': None,
            'min_neighborhood_aod': None,
            'max_neighborhood_aod': None,
        })

# Summary by month
for month in range(1, 13):
    month_df = audit_df[audit_df['date'].str.startswith(f'2025-{month:02d}')]
    
    if len(month_df) > 0:
        for rule_name, rule_col in [('RULE_A', 'rule_a_valid'), ('RULE_B', 'rule_b_valid'), ('RULE_C', 'rule_c_valid')]:
            valid_df = month_df[month_df[rule_col] == True]
            
            summary_rows.append({
                'rule': f"{rule_name}_BY_MONTH_{month:02d}",
                'sample_count': len(month_df),
                'valid_station_days': len(valid_df),
                'coverage_pct': len(valid_df) / len(month_df) * 100 if len(month_df) > 0 else 0,
                'median_valid_neighborhood_pixels': None,
                'median_neighborhood_aod': None,
                'min_neighborhood_aod': None,
                'max_neighborhood_aod': None,
            })

# Summary by QA category
for qa_name in audit_df['aod_quality_name'].dropna().unique():
    qa_df = audit_df[audit_df['aod_quality_name'] == qa_name]
    
    summary_rows.append({
        'rule': f"QA_CATEGORY_{qa_name.replace(' ', '_').replace('(', '').replace(')', '')}",
        'sample_count': len(qa_df),
        'valid_station_days': len(qa_df),
        'coverage_pct': len(qa_df) / len(audit_df) * 100,
        'median_valid_neighborhood_pixels': None,
        'median_neighborhood_aod': None,
        'min_neighborhood_aod': None,
        'max_neighborhood_aod': None,
    })

summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(SUMMARY_CSV, index=False)
print(f"  Saved: {SUMMARY_CSV}")
print()

# ============================================================
# STEP 8: REPORT RESULTS
# ============================================================

print("=" * 70)
print("EXPANDED AUDIT RESULTS")
print("=" * 70)
print()

# Overall coverage
print("1. STRICT QA COVERAGE (RULE A: AOD QA=0 + Land=0 + Cloud Mask=1):")
rule_a_summary = summary_df[summary_df['rule'] == 'RULE_A'].iloc[0]
print(f"   Valid station-days: {rule_a_summary['valid_station_days']}/{rule_a_summary['sample_count']}")
print(f"   Coverage: {rule_a_summary['coverage_pct']:.1f}%")
print()

print("2. QA=11 COVERAGE (RULE B: AOD QA=11 + Land=0):")
rule_b_summary = summary_df[summary_df['rule'] == 'RULE_B'].iloc[0]
print(f"   Valid station-days: {rule_b_summary['valid_station_days']}/{rule_b_summary['sample_count']}")
print(f"   Coverage: {rule_b_summary['coverage_pct']:.1f}%")
print()

print("3. QA={0,3,4} COVERAGE (RULE C: AOD QA in {0,3,4} + Land=0):")
rule_c_summary = summary_df[summary_df['rule'] == 'RULE_C'].iloc[0]
print(f"   Valid station-days: {rule_c_summary['valid_station_days']}/{rule_c_summary['sample_count']}")
print(f"   Coverage: {rule_c_summary['coverage_pct']:.1f}%")
print()

# Station-level coverage
print("4. STATION-LEVEL COVERAGE:")
print("   " + "-" * 60)
print(f"   {'Station':<25} {'RULE_A':>10} {'RULE_B':>10} {'RULE_C':>10}")
print("   " + "-" * 60)

for station in audit_df['station_id'].unique():
    station_name = audit_df[audit_df['station_id'] == station]['station_name'].iloc[0]
    station_df = audit_df[audit_df['station_id'] == station]
    
    rule_a_pct = station_df['rule_a_valid'].sum() / len(station_df) * 100 if len(station_df) > 0 else 0
    rule_b_pct = station_df['rule_b_valid'].sum() / len(station_df) * 100 if len(station_df) > 0 else 0
    rule_c_pct = station_df['rule_c_valid'].sum() / len(station_df) * 100 if len(station_df) > 0 else 0
    
    print(f"   {station_name:<25} {rule_a_pct:>9.1f}% {rule_b_pct:>9.1f}% {rule_c_pct:>9.1f}%")

print("   " + "-" * 60)
print()

# Monthly coverage
print("5. MONTHLY COVERAGE:")
print("   " + "-" * 60)
print(f"   {'Month':<25} {'RULE_A':>10} {'RULE_B':>10} {'RULE_C':>10}")
print("   " + "-" * 60)

for month in range(1, 13):
    month_df = audit_df[audit_df['date'].str.startswith(f'2025-{month:02d}')]
    
    if len(month_df) > 0:
        rule_a_pct = month_df['rule_a_valid'].sum() / len(month_df) * 100
        rule_b_pct = month_df['rule_b_valid'].sum() / len(month_df) * 100
        rule_c_pct = month_df['rule_c_valid'].sum() / len(month_df) * 100
        
        print(f"   {datetime(2025, month, 1).strftime('%B'):<25} {rule_a_pct:>9.1f}% {rule_b_pct:>9.1f}% {rule_c_pct:>9.1f}%")

print("   " + "-" * 60)
print()

# QA category distribution
print("6. QA CATEGORY DISTRIBUTION:")
qa_counts = audit_df['aod_quality_name'].value_counts()
for qa_name, count in qa_counts.items():
    pct = count / len(audit_df) * 100
    print(f"   {qa_name:<40} {count:>5} ({pct:>5.1f}%)")
print()

print("=" * 70)
print("STOP")
print("=" * 70)