"""
Efficient ERA5 extraction using server-side batching
=====================================================
Processes all stations for each date in a single server-side operation.
"""

import math
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(".")
CURATED_DIR = BASE_DIR / "data" / "curated" / "air_quality"
STAGING_DIR = BASE_DIR / "data" / "staging" / "earth_engine"

PM25_FILE = CURATED_DIR / "ahmedabad_pm25_station_day_2025.parquet"
MAIAC_FILE = CURATED_DIR / "ahmedabad_pm25_maiac_station_day_2025.parquet"
ERA5_OUTPUT = STAGING_DIR / "ahmedabad_pm25_era5_pilot_500.csv"
PILOT_OUTPUT = CURATED_DIR / "ahmedabad_pm25_station_day_2025_pilot_500.parquet"

EE_PROJECT = "agniraksha-508013"
ERA5_COLLECTION = "ECMWF/ERA5/HOURLY"
EXTRACTION_RADIUS = 25000
RANDOM_SEED = 42

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

print("=" * 70)
print("EFFICIENT ERA5 EXTRACTION")
print("=" * 70)
print(f"Started: {datetime.now().isoformat()}")
print()

# ============================================================
# STEP 1: SELECT 500 PILOT ROWS
# ============================================================

print("[1/4] Selecting 500 pilot rows...")

pm25_df = pd.read_parquet(PM25_FILE)
pm25_df['date'] = pd.to_datetime(pm25_df['date'])
eligible = pm25_df[pm25_df['daily_qc_flag'] == 'ELIGIBLE'].copy()

maiac_df = pd.read_parquet(MAIAC_FILE)
maiac_df['date'] = pd.to_datetime(maiac_df['date'])

np.random.seed(RANDOM_SEED)
stations = eligible['station_id'].unique()
samples_per_station = 500 // len(stations)
remaining = 500 % len(stations)

selected_samples = []
for i, station in enumerate(stations):
    station_df = eligible[eligible['station_id'] == station]
    n_samples = samples_per_station + (1 if i < remaining else 0)
    
    station_months = station_df['date'].dt.month.unique()
    samples_per_month = math.ceil(n_samples / len(station_months))
    
    station_selections = []
    for month in station_months:
        month_df = station_df[station_df['date'].dt.month == month]
        if len(month_df) > 0:
            n_select = min(samples_per_month, len(month_df))
            sample = month_df.sample(n=n_select, random_state=RANDOM_SEED)
            station_selections.append(sample)
    
    station_selections = pd.concat(station_selections).head(n_samples)
    selected_samples.append(station_selections)

pilot_df = pd.concat(selected_samples).head(500).reset_index(drop=True)

# Join with MAIAC
pilot_with_maiac = pilot_df.merge(
    maiac_df[['station_id', 'date', 'strict_aod_550', 'strict_aod_uncertainty', 'strict_aod_available']],
    on=['station_id', 'date'], how='left'
)
pilot_with_maiac['strict_aod_available'] = pilot_with_maiac['strict_aod_available'].fillna(False)

print(f"  Selected: {len(pilot_with_maiac)} rows")
print(f"  AOD available: {pilot_with_maiac['strict_aod_available'].sum()}")
print()

# ============================================================
# STEP 2: CHECK EXISTING ERA5
# ============================================================

print("[2/4] Checking ERA5 progress...")

if ERA5_OUTPUT.exists():
    existing_era5 = pd.read_csv(ERA5_OUTPUT)
    existing_era5['date'] = pd.to_datetime(existing_era5['date'])
    extracted_dates = set(existing_era5['date'].dt.strftime('%Y-%m-%d').unique())
    print(f"  Found: {len(existing_era5)} records, {len(extracted_dates)} dates")
else:
    existing_era5 = pd.DataFrame()
    extracted_dates = set()
    print("  No existing ERA5")

pilot_dates = set(pilot_with_maiac['date'].dt.strftime('%Y-%m-%d').unique())
dates_to_extract = sorted(pilot_dates - extracted_dates)
print(f"  Remaining: {len(dates_to_extract)} dates")
print()

# ============================================================
# STEP 3: EXTRACT ERA5
# ============================================================

if len(dates_to_extract) > 0:
    print("[3/4] Extracting ERA5 from Earth Engine...")
    
    try:
        import ee
        ee.Initialize(project=EE_PROJECT)
        print("  Earth Engine authenticated")
    except Exception as e:
        print(f"  ERROR: {e}")
        sys.exit(1)
    
    # Create FeatureCollection of station points
    station_features = []
    for sid, info in STATION_COORDS.items():
        feature = ee.Feature(
            ee.Geometry.Point([info['lon'], info['lat']]),
            {'station_id': sid, 'latitude': info['lat'], 'longitude': info['lon']}
        )
        station_features.append(feature)
    
    station_fc = ee.FeatureCollection(station_features)
    
    new_results = []
    
    for i, date_str in enumerate(dates_to_extract):
        if (i + 1) % 10 == 0:
            print(f"  Processing {i+1}/{len(dates_to_extract)}: {date_str}")
        
        try:
            date = ee.Date(date_str)
            next_date = date.advance(1, 'day')
            
            era5_hourly = ee.ImageCollection(ERA5_COLLECTION) \
                .filterDate(date, next_date) \
                .select(['temperature_2m', 'dewpoint_temperature_2m', 
                        'u_component_of_wind_10m', 'v_component_of_wind_10m',
                        'surface_pressure', 'total_precipitation'])
            
            image_count = era5_hourly.size().getInfo()
            
            if image_count == 0:
                for sid in STATION_COORDS.keys():
                    new_results.append({
                        'station_id': sid, 'date': date_str,
                        'temperature_daily_c': np.nan,
                        'relative_humidity_daily_pct': np.nan,
                        'wind_speed_daily_ms': np.nan,
                        'surface_pressure_daily_hpa': np.nan,
                        'precipitation_daily_m': np.nan,
                        'meteo_available': False,
                    })
            else:
                # Calculate daily aggregates server-side
                temp_daily = era5_hourly.select('temperature_2m').mean().subtract(273.15)
                wind_daily = era5_hourly.map(lambda img: 
                    img.select('u_component_of_wind_10m').pow(2)
                    .add(img.select('v_component_of_wind_10m').pow(2)).sqrt()
                ).mean()
                pressure_daily = era5_hourly.select('surface_pressure').mean().divide(100)
                precip_daily = era5_hourly.select('total_precipitation').sum().multiply(1000)
                
                def calc_rh(img):
                    t_c = img.select('temperature_2m').subtract(273.15)
                    td_c = img.select('dewpoint_temperature_2m').subtract(273.15)
                    es_t = ee.Image(6.1078).multiply(ee.Image(17.27).multiply(t_c).divide(t_c.add(237.3)).exp())
                    es_td = ee.Image(6.1078).multiply(ee.Image(17.27).multiply(td_c).divide(td_c.add(237.3)).exp())
                    return es_td.divide(es_t).multiply(100)
                
                rh_daily = era5_hourly.map(calc_rh).mean()
                
                # Use reduceRegions to extract all stations at once
                composite = temp_daily.addBands(rh_daily.rename('rh')) \
                    .addBands(wind_daily.rename('wind')) \
                    .addBands(pressure_daily.rename('pressure')) \
                    .addBands(precip_daily.rename('precip'))
                
                results = composite.reduceRegions(
                    collection=station_fc,
                    reducer=ee.Reducer.first(),
                    scale=25000
                )
                
                # Get results
                result_list = results.getInfo()['features']
                
                for feature in result_list:
                    props = feature['properties']
                    sid = props['station_id']
                    
                    temp_val = props.get('temperature_2m')
                    rh_val = props.get('rh')
                    wind_val = props.get('wind')
                    pressure_val = props.get('pressure')
                    precip_val = props.get('precip')
                    
                    meteo_available = all(v is not None for v in [temp_val, rh_val, wind_val, pressure_val, precip_val])
                    
                    new_results.append({
                        'station_id': sid, 'date': date_str,
                        'temperature_daily_c': temp_val,
                        'relative_humidity_daily_pct': rh_val,
                        'wind_speed_daily_ms': wind_val,
                        'surface_pressure_daily_hpa': pressure_val,
                        'precipitation_daily_m': precip_val,
                        'meteo_available': meteo_available,
                    })
        
        except Exception as e:
            print(f"    Error: {e}")
            for sid in STATION_COORDS.keys():
                new_results.append({
                    'station_id': sid, 'date': date_str,
                    'temperature_daily_c': np.nan,
                    'relative_humidity_daily_pct': np.nan,
                    'wind_speed_daily_ms': np.nan,
                    'surface_pressure_daily_hpa': np.nan,
                    'precipitation_daily_m': np.nan,
                    'meteo_available': False,
                })
        
        # Save every 10 dates
        if (i + 1) % 10 == 0 and new_results:
            new_df = pd.DataFrame(new_results)
            new_df['date'] = pd.to_datetime(new_df['date'])
            
            if not existing_era5.empty:
                combined = pd.concat([existing_era5, new_df]).drop_duplicates(
                    subset=['station_id', 'date'], keep='last'
                )
            else:
                combined = new_df
            
            STAGING_DIR.mkdir(parents=True, exist_ok=True)
            combined.to_csv(ERA5_OUTPUT, index=False)
            existing_era5 = combined
            extracted_dates = set(combined['date'].dt.strftime('%Y-%m-%d').unique())
            new_results = []
            
            print(f"    Saved: {len(combined)} records")
        
        time.sleep(0.5)  # Rate limiting
    
    # Final save
    if new_results:
        new_df = pd.DataFrame(new_results)
        new_df['date'] = pd.to_datetime(new_df['date'])
        
        if not existing_era5.empty:
            combined = pd.concat([existing_era5, new_df]).drop_duplicates(
                subset=['station_id', 'date'], keep='last'
            )
        else:
            combined = new_df
        
        STAGING_DIR.mkdir(parents=True, exist_ok=True)
        combined.to_csv(ERA5_OUTPUT, index=False)
        print(f"  Final save: {len(combined)} records")
    
    print("  ERA5 extraction complete")
else:
    print("[3/4] ERA5 already complete, skipping...")

print()

# ============================================================
# STEP 4: CREATE FINAL PILOT DATASET
# ============================================================

print("[4/4] Creating final pilot dataset...")

era5_df = pd.read_csv(ERA5_OUTPUT)
era5_df['date'] = pd.to_datetime(era5_df['date'])

pilot_final = pilot_with_maiac.merge(era5_df, on=['station_id', 'date'], how='left')
pilot_final['era5_available'] = pilot_final['meteo_available'].fillna(False)
pilot_final['fully_matched'] = pilot_final['strict_aod_available'] & pilot_final['era5_available']

final_cols = [
    'station_id', 'station_name', 'date', 'latitude', 'longitude',
    'daily_pm25_ug_m3', 'valid_pm25_hours', 'pm25_day_completeness_pct',
    'strict_aod_550', 'strict_aod_uncertainty', 'strict_aod_available',
    'temperature_daily_c', 'relative_humidity_daily_pct', 'wind_speed_daily_ms',
    'surface_pressure_daily_hpa', 'precipitation_daily_m',
    'era5_available', 'fully_matched',
]

pilot_final[final_cols].to_parquet(PILOT_OUTPUT, index=False)

era5_count = pilot_final['era5_available'].sum()
aod_count = pilot_final['strict_aod_available'].sum()
full_count = pilot_final['fully_matched'].sum()

print(f"  Saved: {PILOT_OUTPUT}")
print(f"  Total: {len(pilot_final)}")
print(f"  ERA5: {era5_count} ({era5_count/len(pilot_final)*100:.1f}%)")
print(f"  AOD: {aod_count} ({aod_count/len(pilot_final)*100:.1f}%)")
print(f"  Full: {full_count} ({full_count/len(pilot_final)*100:.1f}%)")
print()
print("=" * 70)
print("EXTRACTION COMPLETE")
print("=" * 70)
