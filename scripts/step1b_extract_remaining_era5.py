"""
Extract remaining ERA5 dates for pilot dataset
===============================================
Continues from where the previous extraction left off.
"""

import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(".")
CURATED_DIR = BASE_DIR / "data" / "curated" / "air_quality"
STAGING_DIR = BASE_DIR / "data" / "staging" / "earth_engine"

PM25_FILE = CURATED_DIR / "ahmedabad_pm25_station_day_2025.parquet"
MAIAC_FILE = CURATED_DIR / "ahmedabad_pm25_maiac_station_day_2025.parquet"
ERA5_OUTPUT = STAGING_DIR / "ahmedabad_pm25_era5_pilot_500.csv"

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

import math

print("=" * 70)
print("EXTRACT REMAINING ERA5 DATES")
print("=" * 70)
print(f"Started: {datetime.now().isoformat()}")

# Load pilot selection
pm25 = pd.read_parquet(PM25_FILE)
pm25['date'] = pd.to_datetime(pm25['date'])
eligible = pm25[pm25['daily_qc_flag'] == 'ELIGIBLE']

np.random.seed(RANDOM_SEED)
stations = eligible['station_id'].unique()
spp = 500 // len(stations)
rem = 500 % len(stations)

selected = []
i = 0
for station in stations:
    sdf = eligible[eligible['station_id'] == station]
    ns = spp + (1 if i < rem else 0)
    months = sdf['date'].dt.month.unique()
    spm = math.ceil(ns / len(months))
    sels = []
    for m in months:
        mf = sdf[sdf['date'].dt.month == m]
        if len(mf) > 0:
            sels.append(mf.sample(n=min(spm, len(mf)), random_state=42))
    selected.append(pd.concat(sels).head(ns))
    i += 1

pilot = pd.concat(selected).head(500)

# Check existing ERA5
era5 = pd.read_csv(ERA5_OUTPUT)
era5['date'] = pd.to_datetime(era5['date'])
extracted = set(era5['date'].dt.strftime('%Y-%m-%d'))
needed = set(pilot['date'].dt.strftime('%Y-%m-%d'))
missing = sorted(needed - extracted)

print(f"Missing dates: {len(missing)}")

if len(missing) == 0:
    print("All dates already extracted!")
else:
    import ee
    ee.Initialize(project=EE_PROJECT)
    print("Earth Engine authenticated")

    # Create station FeatureCollection
    station_features = []
    for sid, info in STATION_COORDS.items():
        feature = ee.Feature(
            ee.Geometry.Point([info['lon'], info['lat']]),
            {'station_id': sid}
        )
        station_features.append(feature)
    station_fc = ee.FeatureCollection(station_features)

    new_results = []

    for i, date_str in enumerate(missing):
        print(f"  {i+1}/{len(missing)}: {date_str}")
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
                for sid in STATION_COORDS:
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

                composite = temp_daily.addBands(rh_daily.rename('rh')) \
                    .addBands(wind_daily.rename('wind')) \
                    .addBands(pressure_daily.rename('pressure')) \
                    .addBands(precip_daily.rename('precip'))

                results = composite.reduceRegions(
                    collection=station_fc,
                    reducer=ee.Reducer.first(),
                    scale=25000
                )

                result_list = results.getInfo()['features']

                for feature in result_list:
                    props = feature['properties']
                    sid = props['station_id']

                    new_results.append({
                        'station_id': sid, 'date': date_str,
                        'temperature_daily_c': props.get('temperature_2m'),
                        'relative_humidity_daily_pct': props.get('rh'),
                        'wind_speed_daily_ms': props.get('wind'),
                        'surface_pressure_daily_hpa': props.get('pressure'),
                        'precipitation_daily_m': props.get('precip'),
                        'meteo_available': all(props.get(k) is not None for k in ['temperature_2m', 'rh', 'wind', 'pressure', 'precip']),
                    })

        except Exception as e:
            print(f"    Error: {e}")
            for sid in STATION_COORDS:
                new_results.append({
                    'station_id': sid, 'date': date_str,
                    'temperature_daily_c': np.nan,
                    'relative_humidity_daily_pct': np.nan,
                    'wind_speed_daily_ms': np.nan,
                    'surface_pressure_daily_hpa': np.nan,
                    'precipitation_daily_m': np.nan,
                    'meteo_available': False,
                })

        # Save every 5 dates
        if (i + 1) % 5 == 0 and new_results:
            new_df = pd.DataFrame(new_results)
            new_df['date'] = pd.to_datetime(new_df['date'])
            combined = pd.concat([era5, new_df]).drop_duplicates(subset=['station_id', 'date'], keep='last')
            combined.to_csv(ERA5_OUTPUT, index=False)
            era5 = combined
            new_results = []
            print(f"    Saved: {len(combined)} records")

        time.sleep(0.5)

    # Final save
    if new_results:
        new_df = pd.DataFrame(new_results)
        new_df['date'] = pd.to_datetime(new_df['date'])
        combined = pd.concat([era5, new_df]).drop_duplicates(subset=['station_id', 'date'], keep='last')
        combined.to_csv(ERA5_OUTPUT, index=False)
        print(f"  Final: {len(combined)} records")

print()
print("=" * 70)
print("ERA5 EXTRACTION COMPLETE")
print("=" * 70)
