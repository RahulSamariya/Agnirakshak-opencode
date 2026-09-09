"""
Batched Earth Engine MAIAC Extraction — Full 2025 Dataset
==========================================================

This script extracts MAIAC AOD for the full 2025 dataset using
automatic batching with the validated BATCH_EXPORT architecture.

ARCHITECTURE:
- driver FeatureCollection → server-side computation → compact FeatureCollection
- Export.table.toDrive → Google Drive → local CSV via Drive API → local parquet
- Automatic batching: ~500 station-days per batch
- Checkpointing: each batch saved separately
- Resumable: skips completed batches

CRITICAL: No FeatureCollection.getInfo() calls on large collections.

USAGE:
    python scripts/earth_engine/extract_maiac_full_2025.py

OUTPUT:
    data/staging/earth_engine/maiac_2025_batch_*.csv (intermediate)
    data/curated/air_quality/ahmedabad_pm25_maiac_station_day_2025.parquet (final)
"""

import math
import os
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
DRIVE_FOLDER_NAME = "agnirakshak_maiac"

# ============================================================
# GOOGLE DRIVE DOWNLOAD HELPER
# ============================================================

def get_drive_service():
    """Build Google Drive API service using EE credentials."""
    import ee
    from googleapiclient.discovery import build
    
    cred = ee.data.get_persistent_credentials()
    service = build('drive', 'v3', credentials=cred)
    return service


def find_drive_folder(service, folder_name):
    """Find a folder by name in Google Drive."""
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    folders = results.get('files', [])
    return folders[0]['id'] if folders else None


def download_drive_file(service, file_id, local_path):
    """Download a file from Google Drive by its ID."""
    import io
    from googleapiclient.http import MediaIoBaseDownload
    
    request = service.files().get_media(fileId=file_id)
    with io.FileIO(str(local_path), 'wb') as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()


def download_batch_from_drive(batch_num, staging_dir):
    """Download a batch CSV from Google Drive."""
    filename = f"maiac_2025_batch_{batch_num:03d}.csv"
    local_path = staging_dir / filename
    
    if local_path.exists():
        return local_path
    
    try:
        service = get_drive_service()
        
        # Find the folder
        query = f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        folders = results.get('files', [])
        
        if not folders:
            print(f"    Folder '{DRIVE_FOLDER_NAME}' not found")
            return None
        
        folder_id = folders[0]['id']
        
        # Find the file in the folder
        query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        files = results.get('files', [])
        
        if not files:
            print(f"    File '{filename}' not found in Drive folder")
            return None
        
        # Download the file
        staging_dir.mkdir(parents=True, exist_ok=True)
        download_drive_file(service, files[0]['id'], local_path)
        
        return local_path if local_path.exists() else None
        
    except Exception as e:
        print(f"    Drive download error: {e}")
        return None


# ============================================================
# MAIN
# ============================================================

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

total_batches = len(batches)
print(f"[BATCH] Total batches: {total_batches}")
for i, batch in enumerate(batches):
    print(f"[BATCH] Batch {i + 1}: {len(batch)} rows")
print()

# ============================================================
# STEP 3: CHECK FOR COMPLETED BATCHES
# ============================================================

print("[CHECK] Checking for completed batches...")

completed_batches = []
for i in range(total_batches):
    batch_file = STAGING_DIR / f"maiac_2025_batch_{i + 1:03d}.csv"
    if batch_file.exists():
        completed_batches.append(i + 1)
        print(f"[CHECK] Batch {i + 1}: COMPLETED")

if len(completed_batches) == total_batches:
    print("[CHECK] All batches already completed!")
else:
    print(f"[CHECK] {len(completed_batches)}/{total_batches} batches completed")
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
    point = feature.geometry()
    date_str = feature.get('date')
    
    # Filter MAIAC collection to single day
    date = ee.Date(date_str)
    next_date = date.advance(1, 'day')
    
    maiac_daily = ee.ImageCollection(MAIAC_COLLECTION) \
        .filterDate(date, next_date) \
        .filterBounds(point) \
        .select([AOD_BAND, UNCERTAINTY_BAND, QA_BAND])
    
    image_count = maiac_daily.size()
    
    # Create QA masks
    qa_image = maiac_daily.select(QA_BAND).median().toInt()
    
    # TIER 1: cloud_mask=1, land_mask=0, aod_quality=0, glint_mask=0
    tier1_cloud = qa_image.bitwiseAnd(7).eq(1)
    tier1_land = qa_image.rightShift(3).bitwiseAnd(3).eq(0)
    tier1_aod_qa = qa_image.rightShift(8).bitwiseAnd(15).eq(0)
    tier1_glint = qa_image.rightShift(12).bitwiseAnd(1).eq(0)
    tier1_mask = tier1_cloud.And(tier1_land).And(tier1_aod_qa).And(tier1_glint)
    
    # TIER 2: land_mask=0, aod_quality=11, glint_mask=0
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

failed_batches = []

for batch_idx, batch_df in enumerate(batches):
    batch_num = batch_idx + 1
    
    # Skip completed batches
    if batch_num in completed_batches:
        print(f"[BATCH {batch_num}/{total_batches}] SKIPPED (already completed)")
        continue
    
    print(f"[BATCH {batch_num}/{total_batches}] START")
    
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
        folder=DRIVE_FOLDER_NAME,
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
    print(f"[BATCH {batch_num}/{total_batches}] TASK CREATED: {task.status()['id']}")
    
    # Monitor task
    while True:
        status = task.status()
        state = status['state']
        
        if state == 'COMPLETED':
            print(f"[BATCH {batch_num}/{total_batches}] COMPLETE")
            break
        elif state == 'FAILED':
            error_msg = status.get('error_message', 'Unknown error')
            print(f"[BATCH {batch_num}/{total_batches}] FAILED: {error_msg}")
            failed_batches.append(batch_num)
            break
        elif state == 'CANCELLED':
            print(f"[BATCH {batch_num}/{total_batches}] CANCELLED")
            failed_batches.append(batch_num)
            break
        else:
            time.sleep(15)
    
    # Download from Google Drive if completed
    if state == 'COMPLETED':
        print(f"[BATCH {batch_num}/{total_batches}] Downloading from Drive...")
        
        local_path = download_batch_from_drive(batch_num, STAGING_DIR)
        if local_path:
            print(f"[BATCH {batch_num}/{total_batches}] SAVED: {local_path}")
        else:
            print(f"[BATCH {batch_num}/{total_batches}] Download failed")
            failed_batches.append(batch_num)
    
    print()

# ============================================================
# STEP 6: MERGE ALL BATCHES
# ============================================================

print("[MERGE] Merging all batches...")

all_batches = []
for i in range(total_batches):
    batch_file = STAGING_DIR / f"maiac_2025_batch_{i + 1:03d}.csv"
    if batch_file.exists():
        batch_df = pd.read_csv(batch_file)
        all_batches.append(batch_df)
        print(f"[MERGE] Loaded batch {i + 1}: {len(batch_df)} rows")
    else:
        print(f"[MERGE] Batch {i + 1}: NOT FOUND (skipping)")

if not all_batches:
    print("[MERGE] ERROR: No batches found!")
    sys.exit(1)

merged_df = pd.concat(all_batches, ignore_index=True)
print(f"[MERGE] Total rows: {len(merged_df)}")
print()

# ============================================================
# STEP 7: VALIDATE MERGED RESULTS
# ============================================================

print("[VALIDATE] Validating merged results...")

requested = len(driver_df)
returned = len(merged_df)
print(f"[VALIDATE] Requested rows: {requested}")
print(f"[VALIDATE] Returned rows: {returned}")
print(f"[VALIDATE] Row count match: {requested == returned}")

duplicates = merged_df.duplicated(subset=['station_id', 'date']).sum()
print(f"[VALIDATE] Duplicate station/date: {duplicates}")
print()

strict_valid = merged_df['strict_aod_available'].sum()
strict_coverage = strict_valid / len(merged_df) * 100

research_valid = merged_df['research_aod_available'].sum() if 'research_aod_available' in merged_df.columns else 0
research_coverage = research_valid / len(merged_df) * 100

print(f"[VALIDATE] Strict AOD valid: {strict_valid}")
print(f"[VALIDATE] Strict AOD coverage: {strict_coverage:.1f}%")
print(f"[VALIDATE] Research AOD valid: {research_valid}")
print(f"[VALIDATE] Research AOD coverage: {research_coverage:.1f}%")
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
print(f"[METRICS] Research AOD valid: {research_valid}")
print(f"[METRICS] Research AOD coverage: {research_coverage:.1f}%")
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
print(f"TOTAL ELIGIBLE: {requested}")
print(f"TOTAL EXTRACTED: {returned}")
print()
print(f"STRICT AOD VALID: {strict_valid}")
print(f"STRICT COVERAGE: {strict_coverage:.1f}%")
print()
print(f"RESEARCH QA=11 VALID: {research_valid}")
print(f"RESEARCH COVERAGE: {research_coverage:.1f}%")
print()
print(f"RUNTIME: {runtime:.1f} seconds")
print(f"RUNTIME PER ROW: {runtime_per_row:.2f} seconds")
print()
print(f"FAILED BATCHES: {len(failed_batches)} {failed_batches if failed_batches else ''}")
print()
print(f"OUTPUT: {OUTPUT_PARQUET}")
print()
print("=" * 70)
print("STOP")
print("=" * 70)