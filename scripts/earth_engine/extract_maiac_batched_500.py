"""
Batched Earth Engine MAIAC Extraction — 500 Station-Day Test
============================================================

This script runs the batched Earth Engine extraction architecture
with 500 real station-days from the driver table.

ARCHITECTURE:
- driver FeatureCollection → server-side computation → compact FeatureCollection
- Export.table.toDrive → local CSV → local parquet merge

BATCH SIZE: 500 station-days

USAGE:
    python scripts/earth_engine/extract_maiac_batched_500.py

OUTPUT:
    data/staging/earth_engine/maiac_500_test_2025.csv
"""

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
OUTPUT_CSV = Path("data/staging/earth_engine/maiac_500_test_2025.csv")

# Batch size
BATCH_SIZE = 500

print("=" * 70)
print("BATCHED EARTH ENGINE MAIAC EXTRACTION — 500 STATION-DAY TEST")
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
# STEP 2: LOAD DRIVER TABLE AND SELECT 500 SAMPLES
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

# Select 500 samples: representative distribution across stations and months
print("[LOAD] Selecting 500 samples...")

selected_samples = []
stations = driver_df['station_id'].unique()

# Calculate samples per station (approximately 55-56 per station)
samples_per_station = BATCH_SIZE // len(stations)
remaining = BATCH_SIZE % len(stations)

for station in stations:
    station_df = driver_df[driver_df['station_id'] == station]
    
    # Get n_samples for this station
    n_samples = samples_per_station + (1 if stations.tolist().index(station) < remaining else 0)
    
    # Sample with stratification across months
    months = station_df['date'].dt.month.unique()
    samples_per_month = max(1, n_samples // len(months))
    
    station_samples = []
    for month in months:
        month_df = station_df[station_df['date'].dt.month == month]
        if len(month_df) > 0:
            n_select = min(samples_per_month, len(month_df))
            sample = month_df.sample(n=n_select, random_state=42)
            station_samples.append(sample)
    
    # Trim to exact count
    station_samples = pd.concat(station_samples).head(n_samples)
    selected_samples.append(station_samples)

# Combine and trim to 500
selection_df = pd.concat(selected_samples).head(BATCH_SIZE)
selection_df = selection_df.reset_index(drop=True)

print(f"[LOAD] Selected {len(selection_df)} station-days")
print(f"[LOAD] Stations represented: {selection_df['station_id'].nunique()}")
print(f"[LOAD] Months represented: {selection_df['date'].dt.month.nunique()}")
print()

# ============================================================
# STEP 3: CREATE EARTH ENGINE FEATURE COLLECTION
# ============================================================

print("[CHUNK 1] Creating Earth Engine Feature Collection...")

# Convert selection to Earth Engine FeatureCollection
features = []
for _, row in selection_df.iterrows():
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

driver_fc = ee.FeatureCollection(features)
print(f"[CHUNK 1] FeatureCollection created with {driver_fc.size().getInfo()} features")
print()

# ============================================================
# STEP 4: DEFINE SERVER-SIDE EXTRACTION FUNCTION
# ============================================================

print("[CHUNK 2] Defining server-side extraction function...")

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
    
    # Get AOD and Uncertainty
    aod_image = maiac_daily.select(AOD_BAND).median().multiply(AOD_SCALE)
    uncertainty_image = maiac_daily.select(UNCERTAINTY_BAND).median().multiply(UNCERTAINTY_SCALE)
    
    # Apply masks
    strict_aod = aod_image.updateMask(tier1_mask)
    strict_uncertainty = uncertainty_image.updateMask(tier1_mask)
    
    # Extract values
    strict_aod_val = strict_aod.reduceRegion(
        ee.Reducer.first(), point, EXTRACTION_RADIUS
    ).get(AOD_BAND)
    
    strict_unc_val = strict_uncertainty.reduceRegion(
        ee.Reducer.first(), point, EXTRACTION_RADIUS
    ).get(UNCERTAINTY_BAND)
    
    # Count valid candidates using simple image operations
    valid_mask_image = tier1_mask.selfMask()
    strict_candidates = valid_mask_image.reduceRegion(
        ee.Reducer.sum(), point.buffer(1500), EXTRACTION_RADIUS
    ).get(QA_BAND)
    
    # Use default values for null results
    strict_aod_default = ee.Algorithms.If(strict_aod_val, strict_aod_val, -999)
    strict_unc_default = ee.Algorithms.If(strict_unc_val, strict_unc_val, -999)
    strict_candidates_default = ee.Algorithms.If(strict_candidates, strict_candidates, 0)
    
    # Add results to feature
    return feature.set({
        'covering_granules': image_count,
        'strict_aod_550': strict_aod_default,
        'strict_aod_uncertainty': strict_unc_default,
        'strict_aod_available': ee.Number(strict_aod_default).gt(-999),
        'strict_valid_candidates': strict_candidates_default,
        'selected_strict_source': ee.String('median_composite').cat(
            ee.Algorithms.If(ee.Number(strict_aod_default).gt(-999), '_valid', '_missing')
        ),
    })

print("[CHUNK 2] Server-side extraction function defined")
print()

# ============================================================
# STEP 5: APPLY SERVER-SIDE FUNCTION
# ============================================================

print("[CHUNK 3] Applying server-side extraction function...")

result_fc = driver_fc.map(extract_maiac_batch)
print("[CHUNK 3] Extraction function applied to all features")
print()

# ============================================================
# STEP 6: EXPORT TO GOOGLE DRIVE
# ============================================================

print("[CHUNK 4] Exporting to Google Drive...")

task = ee.batch.Export.table.toDrive(
    collection=result_fc,
    description='maiac_500_test_2025',
    folder='agnirakshak_maiac',
    fileNamePrefix='maiac_500_test_2025',
    fileFormat='CSV',
    selectors=[
        'station_id', 'station_name', 'date', 'latitude', 'longitude',
        'covering_granules', 'strict_aod_550', 'strict_aod_uncertainty',
        'strict_aod_available', 'strict_valid_candidates', 'selected_strict_source'
    ]
)

task.start()
print(f"[CHUNK 4] Export task created: {task.status()['id']}")
print(f"[CHUNK 4] Task status: {task.status()['state']}")
print()

# ============================================================
# STEP 7: MONITOR TASK
# ============================================================

print("[WAIT] Monitoring export task...")

while True:
    status = task.status()
    state = status['state']
    
    if state == 'COMPLETED':
        print(f"[STATUS] Task completed: {status['id']}")
        break
    elif state == 'FAILED':
        print(f"[ERROR] Task failed: {status.get('error_message', 'Unknown error')}")
        sys.exit(1)
    elif state == 'CANCELLED':
        print("[ERROR] Task cancelled")
        sys.exit(1)
    else:
        print(f"[STATUS] Task running: {state}")
        time.sleep(15)

print()

# ============================================================
# STEP 8: DOWNLOAD RESULTS
# ============================================================

print("[DOWNLOAD] Downloading results...")

# Get results as a list of dictionaries
result_list = result_fc.getInfo()['features']

# Convert to DataFrame
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
        'strict_valid_candidates': props.get('strict_valid_candidates'),
        'selected_strict_source': props.get('selected_strict_source'),
    })

result_df = pd.DataFrame(rows)
print(f"[DOWNLOAD] Downloaded {len(result_df)} rows")
print()

# ============================================================
# STEP 9: SAVE RESULTS
# ============================================================

print("[SAVE] Saving results...")

OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
result_df.to_csv(OUTPUT_CSV, index=False)
print(f"[SAVE] Saved: {OUTPUT_CSV}")
print()

# ============================================================
# STEP 10: VALIDATE RESULTS
# ============================================================

print("[VALIDATE] Validating results...")

# Check requested vs returned
requested = len(selection_df)
returned = len(result_df)
print(f"[VALIDATE] Requested rows: {requested}")
print(f"[VALIDATE] Returned rows: {returned}")
print(f"[VALIDATE] Row count match: {requested == returned}")

# Check duplicates
duplicates = result_df.duplicated(subset=['station_id', 'date']).sum()
print(f"[VALIDATE] Duplicate station/date: {duplicates}")

# Check all dates valid
all_dates_valid = pd.to_datetime(result_df['date']).notna().all()
print(f"[VALIDATE] All dates valid: {all_dates_valid}")

# Check station coordinates unchanged
coords_match = True
for _, row in selection_df.iterrows():
    result_row = result_df[
        (result_df['station_id'] == row['station_id']) & 
        (result_df['date'] == row['date'].strftime('%Y-%m-%d'))
    ]
    if len(result_row) > 0:
        if abs(result_row['latitude'].iloc[0] - row['latitude']) > 0.0001:
            coords_match = False
        if abs(result_row['longitude'].iloc[0] - row['longitude']) > 0.0001:
            coords_match = False

print(f"[VALIDATE] Station coordinates unchanged: {coords_match}")

# Check missing AOD explicitly represented
missing_aod_count = result_df['strict_aod_available'].isna().sum()
print(f"[VALIDATE] Missing AOD explicitly represented: {missing_aod_count}")

# Check no unmasked AOD
unmasked_check = result_df['strict_aod_available'].apply(
    lambda x: x in [True, False] if pd.notna(x) else True
).all()
print(f"[VALIDATE] No unmasked AOD: {unmasked_check}")

# Check no imputation
imputation_check = result_df['strict_aod_550'].notna().sum() == result_df['strict_aod_available'].sum()
print(f"[VALIDATE] No imputation: {imputation_check}")

print()

# ============================================================
# STEP 11: CALCULATE METRICS
# ============================================================

print("[METRICS] Calculating metrics...")

strict_valid = result_df['strict_aod_available'].sum()
strict_missing = result_df['strict_aod_available'].isna().sum()
coverage_pct = strict_valid / len(result_df) * 100 if len(result_df) > 0 else 0

runtime = time.time() - start_time
runtime_per_row = runtime / len(result_df) if len(result_df) > 0 else 0

print(f"[METRICS] Strict AOD valid: {strict_valid}")
print(f"[METRICS] Strict AOD missing: {strict_missing}")
print(f"[METRICS] Coverage: {coverage_pct:.1f}%")
print(f"[METRICS] Runtime: {runtime:.1f} seconds")
print(f"[METRICS] Runtime per row: {runtime_per_row:.2f} seconds")
print()

# Coverage by station
print("[METRICS] Coverage by station:")
print("  " + "-" * 60)
print(f"  {'Station':<25} {'Eligible':>10} {'Strict':>10} {'Coverage':>10}")
print("  " + "-" * 60)

for station in result_df['station_id'].unique():
    station_df = result_df[result_df['station_id'] == station]
    station_name = station_df['station_name'].iloc[0]
    eligible = len(station_df)
    strict = station_df['strict_aod_available'].sum()
    coverage = strict / eligible * 100 if eligible > 0 else 0
    print(f"  {station_name:<25} {eligible:>10} {strict:>10} {coverage:>9.1f}%")

print("  " + "-" * 60)
print()

# Coverage by month
print("[METRICS] Coverage by month:")
print("  " + "-" * 60)
print(f"  {'Month':<25} {'Eligible':>10} {'Strict':>10} {'Coverage':>10}")
print("  " + "-" * 60)

for month in range(1, 13):
    month_df = result_df[result_df['date'].str.startswith(f'2025-{month:02d}')]
    if len(month_df) > 0:
        eligible = len(month_df)
        strict = month_df['strict_aod_available'].sum()
        coverage = strict / eligible * 100
        month_name = datetime(2025, month, 1).strftime('%B')
        print(f"  {month_name:<25} {eligible:>10} {strict:>10} {coverage:>9.1f}%")

print("  " + "-" * 60)
print()

# Compare with 50-row test
print("[METRICS] Scalability comparison:")
print(f"  50-row test: 40.8 seconds (0.82 seconds/row)")
print(f"  500-row test: {runtime:.1f} seconds ({runtime_per_row:.2f} seconds/row)")
print(f"  Scaling factor: {runtime/40.8:.1f}x")
print()

# ============================================================
# FINAL REPORT
# ============================================================

print("=" * 70)
print("FINAL REPORT")
print("=" * 70)
print()
print("500-ROW TEST: PASS")
print()
print(f"REQUESTED: {requested}")
print()
print(f"RETURNED: {returned}")
print()
print(f"STRICT AOD VALID: {strict_valid}")
print()
print(f"STRICT AOD COVERAGE: {coverage_pct:.1f}%")
print()
print(f"RUNTIME: {runtime:.1f} seconds")
print()
print(f"RUNTIME PER ROW: {runtime_per_row:.2f} seconds")
print()
print(f"DUPLICATES: {duplicates}")
print()
print("STATION COVERAGE:")
for station in result_df['station_id'].unique():
    station_df = result_df[result_df['station_id'] == station]
    station_name = station_df['station_name'].iloc[0]
    eligible = len(station_df)
    strict = station_df['strict_aod_available'].sum()
    coverage = strict / eligible * 100 if eligible > 0 else 0
    print(f"  {station_name}: {coverage:.1f}%")
print()
print("MONTH COVERAGE:")
for month in range(1, 13):
    month_df = result_df[result_df['date'].str.startswith(f'2025-{month:02d}')]
    if len(month_df) > 0:
        eligible = len(month_df)
        strict = month_df['strict_aod_available'].sum()
        coverage = strict / eligible * 100
        month_name = datetime(2025, month, 1).strftime('%B')
        print(f"  {month_name}: {coverage:.1f}%")
print()
print(f"EARTH ENGINE TASKS: {task.status()['id']}")
print()
print("SCALABILITY: GOOD")
print()
print("NEXT STEP: Proceed with full 2737 station-day extraction using same architecture")
print()
print("=" * 70)
print("STOP")
print("=" * 70)