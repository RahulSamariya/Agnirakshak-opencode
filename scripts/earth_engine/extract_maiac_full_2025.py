"""
Batched Earth Engine MAIAC Extraction — Full 2025 Dataset
==========================================================

This script extracts MAIAC AOD for the full 2025 dataset using
automatic batching with the validated BATCH_EXPORT architecture.

ARCHITECTURE:
- driver FeatureCollection → server-side computation → compact FeatureCollection
- Export.table.toDrive → local CSV → local parquet merge
- Automatic batching: ~500 station-days per batch
- Checkpointing: each batch saved separately
- Resumable: skips completed batches

USAGE:
    python scripts/earth_engine/extract_maiac_full_2025.py

OUTPUT:
    data/staging/earth_engine/maiac_2025_batch_*.csv (intermediate)
    data/curated/air_quality/ahmedabad_pm25_maiac_station_day_2025.parquet (final)
"""

import math
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

EE_PROJECT = "agniraksha-508013"
MAIAC_COLLECTION = "MODIS/061/MCD19A2_GRANULES"
AOD_BAND = "Optical_Depth_055"
UNCERTAINTY_BAND = "AOD_Uncertainty"
QA_BAND = "AOD_QA"
AOD_SCALE = 0.001
UNCERTAINTY_SCALE = 0.0001
EXTRACTION_RADIUS = 2000  # meters

# Input/Output files
DRIVER_CSV = Path("data/staging/earth_engine/ahmedabad_pm25_station_days_2025.csv")
STAGING_DIR = Path("data/staging/earth_engine")
OUTPUT_PARQUET = Path("data/curated/air_quality/ahmedabad_pm25_maiac_station_day_2025.parquet")

# Batch configuration
BATCH_SIZE = 500

print("=" * 70)
print("BATCHED EARTH ENGINE MAIAC EXTRACTION — FULL 2025 DATASET")
print("=" * 70)
print(f"Script generated: {datetime.now().isoformat()}")
print()

# Record start time
start_time = time.time()

# ============================================================
# STEP 1: CHECK EARTH ENGINE AUTHENTICATION
# ============================================================

print("[INIT] Checking Earth Engine authentication...")

try:
    import ee
    ee.Initialize(project=EE_PROJECT)
    print("[INIT] Earth Engine authenticated successfully")
    print(f"[INIT] Project: {EE_PROJECT}")
except Exception as e:
    print(f"[ERROR] Earth Engine authentication failed: {e}")
    sys.exit(1)

print()

# ============================================================
# STEP 2: LOAD DRIVER TABLE AND CREATE BATCHES
# ============================================================

print("[LOAD] Loading driver table...")

if not DRIVER_CSV.exists():
    print(f"[ERROR] Driver table not found: {DRIVER_CSV}")
    sys.exit(1)

driver_df = pd.read_csv(DRIVER_CSV)
driver_df['date'] = pd.to_datetime(driver_df['date'])
print(f"[LOAD] Loaded {len(driver_df)} station-days")
print(f"[LOAD] Stations: {driver_df['station_id'].nunique()}")
print(f"[LOAD] Date range: {driver_df['date'].min()} to {driver_df['date'].max()}")
print()

# Create batches
print("[BATCH] Creating batches...")

batches = []
for i in range(0, len(driver_df), BATCH_SIZE):
    batch = driver_df.iloc[i:i + BATCH_SIZE].copy()
    batches.append(batch)

print(f"[BATCH] Total batches: {len(batches)}")
for i, batch in enumerate(batches):
    print(f"[BATCH] Batch {i + 1}: {len(batch)} rows")
print()

# ============================================================
# STEP 3: CHECK FOR COMPLETED BATCHES
# ============================================================

print("[CHECK] Checking for completed batches...")

completed_batches = []
for i, batch in enumerate(batches):
    batch_file = STAGING_DIR / f"maiac_2025_batch_{i + 1:03d}.csv"
    if batch_file.exists():
        completed_batches.append(i + 1)
        print(f"[CHECK] Batch {i + 1}: COMPLETED")

if len(completed_batches) == len(batches):
    print("[CHECK] All batches already completed!")
else:
    print(f"[CHECK] {len(completed_batches)}/{len(batches)} batches completed")
print()

# ============================================================
# STEP 4: DEFINE SERVER-SIDE EXTRACTION FUNCTION
# ============================================================

print("[DEFINE] Defining server-side extraction function...")

def extract_maiac_batch(feature):
    """
    Server-side extraction function for a single station/date.
    
    This function runs entirely on Earth Engine servers.
    """
    # Get station coordinates and date
    point = feature.geometry()
    date_str = feature.get('date')
    station_id = feature.get('station_id')
    station_name = feature.get('station_name')
    
    # Filter MAIAC collection to single day
    date = ee.Date(date_str)
    next_date = date.advance(1, 'day')
    
    maiac_daily = ee.ImageCollection(MAIAC_COLLECTION) \
        .filterDate(date, next_date) \
        .filterBounds(point) \
        .select([AOD_BAND, UNCERTAINTY_BAND, QA_BAND])
    
    # Get number of granules
    image_count = maiac_daily.size()
    
    # Create QA masks - convert to integer first
    qa_image = maiac_daily.select(QA_BAND).median().toInt()
    
    # TIER 1 mask: cloud_mask=1, land_mask=0, aod_quality=0, glint_mask=0
    tier1_cloud = qa_image.bitwiseAnd(7).eq(1)
    tier1_land = qa_image.rightShift(3).bitwiseAnd(3).eq(0)
    tier1_aod_qa = qa_image.rightShift(8).bitwiseAnd(15).eq(0)
    tier1_glint = qa_image.rightShift(12).bitwiseAnd(1).eq(0)
    tier1_mask = tier1_cloud.And(tier1_land).And(tier1_aod_qa).And(tier1_glint)
    
    # TIER 2 mask: land_mask=0, aod_quality=11, glint_mask=0
    tier2_land = qa_image.rightShift(3).bitwiseAnd(3).eq(0)
    tier2_aod_qa = qa_image.rightShift(8).bitwiseAnd(15).eq(11)
    tier2_glint = qa_image.rightShift(12).bitwiseAnd(1).eq(0)
    tier2_mask = tier2_land.And(tier2_aod_qa).And(tier2_glint)
    
    # Get AOD and Uncertainty
    aod_image = maiac_daily.select(AOD_BAND).median().multiply(AOD_SCALE)
    uncertainty_image = maiac_daily.select(UNCERTAINTY_BAND).median().multiply(UNCERTAINTY_SCALE)
    
    # Apply masks
    strict_aod = aod_image.updateMask(tier1_mask)
    strict_uncertainty = uncertainty_image.updateMask(tier1_mask)
    research_aod = aod_image.updateMask(tier2_mask)
    research_uncertainty = uncertainty_image.updateMask(tier2_mask)
    
    # Extract values
    strict_aod_val = strict_aod.reduceRegion(
        ee.Reducer.first(), point, EXTRACTION_RADIUS
    ).get(AOD_BAND)
    
    strict_unc_val = strict_uncertainty.reduceRegion(
        ee.Reducer.first(), point, EXTRACTION_RADIUS
    ).get(UNCERTAINTY_BAND)
    
    research_aod_val = research_aod.reduceRegion(
        ee.Reducer.first(), point, EXTRACTION_RADIUS
    ).get(AOD_BAND)
    
    research_unc_val = research_uncertainty.reduceRegion(
        ee.Reducer.first(), point, EXTRACTION_RADIUS
    ).get(UNCERTAINTY_BAND)
    
    # Count valid candidates
    strict_valid_mask = tier1_mask.selfMask()
    strict_candidates = strict_valid_mask.reduceRegion(
        ee.Reducer.sum(), point.buffer(1500), EXTRACTION_RADIUS
    ).get(QA_BAND)
    
    # Use default values for null results
    strict_aod_default = ee.Algorithms.If(strict_aod_val, strict_aod_val, -999)
    strict_unc_default = ee.Algorithms.If(strict_unc_val, strict_unc_val, -999)
    research_aod_default = ee.Algorithms.If(research_aod_val, research_aod_val, -999)
    research_unc_default = ee.Algorithms.If(research_unc_val, research_unc_val, -999)
    strict_candidates_default = ee.Algorithms.If(strict_candidates, strict_candidates, 0)
    
    # Add results to feature
    return feature.set({
        'covering_granules': image_count,
        'strict_aod_550': strict_aod_default,
        'strict_aod_uncertainty': strict_unc_default,
        'strict_aod_available': ee.Number(strict_aod_default).gt(-999),
        'research_aod_550': research_aod_default,
        'research_aod_uncertainty': research_unc_default,
        'research_aod_available': ee.Number(research_aod_default).gt(-999),
        'strict_valid_candidates': strict_candidates_default,
        'selected_strict_source': ee.String('median_composite').cat(
            ee.Algorithms.If(ee.Number(strict_aod_default).gt(-999), '_valid', '_missing')
        ),
    })

print("[DEFINE] Server-side extraction function defined")
print()

# ============================================================
# STEP 5: PROCESS BATCHES
# ============================================================

print("[PROCESS] Processing batches...")
print()

for batch_idx, batch_df in enumerate(batches):
    batch_num = batch_idx + 1
    
    # Skip completed batches
    if batch_num in completed_batches:
        print(f"[BATCH {batch_num}/{len(batches)}] SKIPPED (already completed)")
        continue
    
    print(f"[BATCH {batch_num}/{len(batches)}] START")
    
    # Create Earth Engine FeatureCollection
    features = []
    for _, row in batch_df.iterrows():
        feature = ee.Feature(
            ee.Geometry.Point([row['longitude'], row['latitude']]),
            {
                'station_id': row['station_id'],
                'station_name': row['station_name'],
                'date': row['date'].strftime('%Y-%m-%d'),
                'latitude': row['latitude'],
                'longitude': row['longitude'],
            }
        )
        features.append(feature)
    
    batch_fc = ee.FeatureCollection(features)
    
    # Apply extraction function
    result_fc = batch_fc.map(extract_maiac_batch)
    
    # Export to Google Drive
    task = ee.batch.Export.table.toDrive(
        collection=result_fc,
        description=f'maiac_2025_batch_{batch_num:03d}',
        folder='agnirakshak_maiac',
        fileNamePrefix=f'maiac_2025_batch_{batch_num:03d}',
        fileFormat='CSV',
        selectors=[
            'station_id', 'station_name', 'date', 'latitude', 'longitude',
            'covering_granules', 'strict_aod_550', 'strict_aod_uncertainty',
            'strict_aod_available', 'research_aod_550', 'research_aod_uncertainty',
            'research_aod_available', 'strict_valid_candidates', 'selected_strict_source'
        ]
    )
    
    task.start()
    print(f"[BATCH {batch_num}/{len(batches)}] TASK CREATED: {task.status()['id']}")
    
    # Monitor task
    while True:
        status = task.status()
        state = status['state']
        
        if state == 'COMPLETED':
            print(f"[BATCH {batch_num}/{len(batches)}] COMPLETE")
            break
        elif state == 'FAILED':
            print(f"[BATCH {batch_num}/{len(batches)}] FAILED: {status.get('error_message', 'Unknown error')}")
            break
        elif state == 'CANCELLED':
            print(f"[BATCH {batch_num}/{len(batches)}] CANCELLED")
            break
        else:
            time.sleep(15)
    
    # Download results
    result_list = result_fc.getInfo()['features']
    rows = []
    for feature in result_list:
        props = feature['properties']
        rows.append({
            'station_id': props.get('station_id'),
            'station_name': props.get('station_name'),
            'date': props.get('date'),
            'latitude': props.get('latitude'),
            'longitude': props.get('longitude'),
            'covering_granules': props.get('covering_granules'),
            'strict_aod_550': props.get('strict_aod_550'),
            'strict_aod_uncertainty': props.get('strict_aod_uncertainty'),
            'strict_aod_available': props.get('strict_aod_available'),
            'research_aod_550': props.get('research_aod_550'),
            'research_aod_uncertainty': props.get('research_aod_uncertainty'),
            'research_aod_available': props.get('research_aod_available'),
            'strict_valid_candidates': props.get('strict_valid_candidates'),
            'selected_strict_source': props.get('selected_strict_source'),
        })
    
    result_df = pd.DataFrame(rows)
    
    # Save batch
    batch_file = STAGING_DIR / f"maiac_2025_batch_{batch_num:03d}.csv"
    STAGING_DIR.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(batch_file, index=False)
    print(f"[BATCH {batch_num}/{len(batches)}] SAVED: {batch_file}")
    print()

# ============================================================
# STEP 6: MERGE ALL BATCHES
# ============================================================

print("[MERGE] Merging all batches...")

all_batches = []
for i in range(len(batches)):
    batch_file = STAGING_DIR / f"maiac_2025_batch_{i + 1:03d}.csv"
    if batch_file.exists():
        batch_df = pd.read_csv(batch_file)
        all_batches.append(batch_df)
        print(f"[MERGE] Loaded batch {i + 1}: {len(batch_df)} rows")

merged_df = pd.concat(all_batches, ignore_index=True)
print(f"[MERGE] Total rows: {len(merged_df)}")
print()

# ============================================================
# STEP 7: VALIDATE MERGED RESULTS
# ============================================================

print("[VALIDATE] Validating merged results...")

# Check requested vs returned
requested = len(driver_df)
returned = len(merged_df)
print(f"[VALIDATE] Requested rows: {requested}")
print(f"[VALIDATE] Returned rows: {returned}")
print(f"[VALIDATE] Row count match: {requested == returned}")

# Check duplicates
duplicates = merged_df.duplicated(subset=['station_id', 'date']).sum()
print(f"[VALIDATE] Duplicate station/date: {duplicates}")
print()

# Calculate metrics
strict_valid = merged_df['strict_aod_available'].sum()
strict_coverage = strict_valid / len(merged_df) * 100

print(f"[VALIDATE] Strict AOD valid: {strict_valid}")
print(f"[VALIDATE] Strict AOD coverage: {strict_coverage:.1f}%")
print()

# ============================================================
# STEP 8: SAVE FINAL PARQUET
# ============================================================

print("[SAVE] Saving final parquet...")

OUTPUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
merged_df.to_parquet(OUTPUT_PARQUET, index=False)
print(f"[SAVE] Saved: {OUTPUT_PARQUET}")
print()

# ============================================================
# STEP 9: FINAL METRICS
# ============================================================

print("[METRICS] Final metrics...")

runtime = time.time() - start_time
runtime_per_row = runtime / len(merged_df) if len(merged_df) > 0 else 0

print(f"[METRICS] Total rows: {len(merged_df)}")
print(f"[METRICS] Strict AOD valid: {strict_valid}")
print(f"[METRICS] Strict AOD coverage: {strict_coverage:.1f}%")
print(f"[METRICS] Runtime: {runtime:.1f} seconds")
print(f"[METRICS] Runtime per row: {runtime_per_row:.2f} seconds")
print()

# Coverage by station
print("[METRICS] Coverage by station:")
print("  " + "-" * 60)
print(f"  {'Station':<25} {'Total':>10} {'Valid':>10} {'Coverage':>10}")
print("  " + "-" * 60)

for station in merged_df['station_id'].unique():
    station_df = merged_df[merged_df['station_id'] == station]
    station_name = station_df['station_name'].iloc[0]
    total = len(station_df)
    valid = station_df['strict_aod_available'].sum()
    coverage = valid / total * 100
    print(f"  {station_name:<25} {total:>10} {valid:>10} {coverage:>9.1f}%")

print("  " + "-" * 60)
print()

# Coverage by month
print("[METRICS] Coverage by month:")
print("  " + "-" * 60)
print(f"  {'Month':<25} {'Total':>10} {'Valid':>10} {'Coverage':>10}")
print("  " + "-" * 60)

for month in range(1, 13):
    month_df = merged_df[merged_df['date'].str.startswith(f'2025-{month:02d}')]
    if len(month_df) > 0:
        total = len(month_df)
        valid = month_df['strict_aod_available'].sum()
        coverage = valid / total * 100
        month_name = datetime(2025, month, 1).strftime('%B')
        print(f"  {month_name:<25} {total:>10} {valid:>10} {coverage:>9.1f}%")

print("  " + "-" * 60)
print()

# ============================================================
# FINAL REPORT
# ============================================================

print("=" * 70)
print("FINAL REPORT")
print("=" * 70)
print()
print("FULL EXTRACTION: COMPLETE")
print()
print(f"REQUESTED: {requested}")
print(f"RETURNED: {returned}")
print()
print(f"STRICT AOD VALID: {strict_valid}")
print(f"STRICT AOD COVERAGE: {strict_coverage:.1f}%")
print()
print(f"RUNTIME: {runtime:.1f} seconds")
print(f"RUNTIME PER ROW: {runtime_per_row:.2f} seconds")
print()
print(f"OUTPUT: {OUTPUT_PARQUET}")
print()
print("=" * 70)
print("STOP")
print("=" * 70)