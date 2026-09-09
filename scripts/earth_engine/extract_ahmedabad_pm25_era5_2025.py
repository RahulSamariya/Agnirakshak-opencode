"""
Earth Engine Extraction: ERA5 Meteorology for Ahmedabad PM2.5 Stations (2025)
==============================================================================

This script extracts daily ERA5 meteorological values at CPCB station coordinates
for the 2025 Ahmedabad PM2.5 modeling dataset.

MEMORY-SAFE DESIGN:
- Uses station-day driver table (not full-city rasters)
- Processes data in quarterly chunks to avoid memory limits
- Exports only station-day records

DATASET:
- Source: ECMWF/ERA5/HOURLY
- Variables: temperature_2m, dewpoint_temperature_2m, u/v wind, surface_pressure, precipitation

DERIVED PREDICTORS:
- temperature_daily_c: Daily mean temperature (K -> degC)
- relative_humidity_daily_pct: Derived from T and Td using Tetens formula
- wind_speed_daily_ms: sqrt(u^2 + v^2), then daily mean
- surface_pressure_daily_hpa: Daily mean pressure (Pa -> hPa)
- precipitation_daily_m: Daily total precipitation (m -> mm)

REQUIREMENTS:
- Google Earth Engine Python API (earthengine-api)
- Authenticated Earth Engine account
- Project: agniraksha-508013

USAGE:
    python scripts/earth_engine/extract_ahmedabad_pm25_era5_2025.py

OUTPUT:
    data/staging/earth_engine/ahmedabad_pm25_era5_station_day_2025.csv
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(".")
DRIVER_CSV = BASE_DIR / "data" / "staging" / "earth_engine" / "ahmedabad_pm25_station_days_2025.csv"
OUTPUT_DIR = BASE_DIR / "data" / "staging" / "earth_engine"
OUTPUT_CSV = OUTPUT_DIR / "ahmedabad_pm25_era5_station_day_2025.csv"

# Earth Engine configuration
EE_PROJECT = "agniraksha-508013"
ERA5_COLLECTION = "ECMWF/ERA5/HOURLY"
EXTRACTION_RADIUS = 25000  # meters (0.25 deg ~ 25km)

# ERA5 variable names
ERA5_VARS = {
    "temperature_2m": "t2m",
    "dewpoint_temperature_2m": "d2m",
    "u_component_of_wind_10m": "u10",
    "v_component_of_wind_10m": "v10",
    "surface_pressure": "sp",
    "total_precipitation": "tp",
}

# Quarterly chunks for memory-safe processing
QUARTERS = [
    ("2025-01-01", "2025-03-31", "Q1"),
    ("2025-04-01", "2025-06-30", "Q2"),
    ("2025-07-01", "2025-09-30", "Q3"),
    ("2025-10-01", "2025-12-31", "Q4"),
]

print("=" * 70)
print("ERA5 METEOROLOGY EXTRACTION FOR AHMEDABAD PM2.5 STATIONS (2025)")
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
# STEP 3: DEFINE HUMIDITY CALCULATION
# ============================================================

print("[STEP 3] Defining humidity calculation...")

print("  Relative Humidity Calculation (Tetens Formula):")
print("    es(T) = 6.1078 x exp(17.27 x T / (T + 237.3))")
print("    RH = (es(Td) / es(T)) x 100")
print("    where T = temperature (degC), Td = dewpoint temperature (degC)")
print()

def calculate_rh_from_ee(t2m, d2m):
    """
    Calculate relative humidity from temperature and dewpoint.
    
    Args:
        t2m: 2m temperature in Kelvin
        d2m: 2m dewpoint temperature in Kelvin
    
    Returns:
        Relative humidity in percent
    """
    # Convert K to degC
    t_c = t2m.subtract(273.15)
    td_c = d2m.subtract(273.15)
    
    # Tetens formula for saturation vapor pressure
    # es = 6.1078 x exp(17.27 x T / (T + 237.3))
    es_t = ee.Image(6.1078).multiply(
        ee.Image(17.27).multiply(t_c).divide(t_c.add(237.3)).exp()
    )
    es_td = ee.Image(6.1078).multiply(
        ee.Image(17.27).multiply(td_c).divide(td_c.add(237.3)).exp()
    )
    
    # RH = (es(Td) / es(T)) x 100
    rh = es_td.divide(es_t).multiply(100)
    
    return rh

print("  Humidity function defined")
print()

# ============================================================
# STEP 4: DEFINE EXTRACTION FUNCTION
# ============================================================

print("[STEP 4] Defining extraction function...")

def extract_era5_for_date(date_str, station_coords):
    """
    Extract ERA5 meteorology for a specific date at station coordinates.
    
    Args:
        date_str: Date string in YYYY-MM-DD format
        station_coords: List of (station_id, lat, lon) tuples
    
    Returns:
        List of dicts with station_id, date, and meteorological variables
    """
    date = ee.Date(date_str)
    next_date = date.advance(1, 'day')
    
    # Filter ERA5 collection to single day (hourly data)
    era5_hourly = ee.ImageCollection(ERA5_COLLECTION) \
        .filterDate(date, next_date) \
        .select(list(ERA5_VARS.keys()))
    
    # Check if any images exist
    image_count = era5_hourly.size().getInfo()
    
    if image_count == 0:
        # No ERA5 data for this date
        return [{
            "station_id": sid,
            "date": date_str,
            "temperature_daily_c": None,
            "relative_humidity_daily_pct": None,
            "wind_speed_daily_ms": None,
            "surface_pressure_daily_hpa": None,
            "precipitation_daily_m": None,
            "meteo_available": False,
        } for sid, _, _ in station_coords]
    
    # Calculate daily aggregates
    # Temperature: daily mean of hourly 2m temperature (K -> degC)
    temp_daily = era5_hourly.select("temperature_2m").mean().subtract(273.15)
    
    # Wind speed: sqrt(u^2 + v^2), then daily mean
    wind_daily = era5_hourly.map(lambda img: 
        img.select("u_component_of_wind_10m").pow(2)
        .add(img.select("v_component_of_wind_10m").pow(2))
        .sqrt()
    ).mean()
    
    # Surface pressure: daily mean (Pa -> hPa)
    pressure_daily = era5_hourly.select("surface_pressure").mean().divide(100)
    
    # Precipitation: daily total (m -> mm)
    precip_daily = era5_hourly.select("total_precipitation").sum().multiply(1000)
    
    # Relative humidity: derive from temperature and dewpoint
    rh_daily = era5_hourly.map(lambda img: 
        calculate_rh_from_ee(
            img.select("temperature_2m"),
            img.select("dewpoint_temperature_2m")
        )
    ).mean()
    
    # Extract at station points
    results = []
    for sid, lat, lon in station_coords:
        point = ee.Geometry.Point([lon, lat])
        
        try:
            # Extract all variables
            temp_val = temp_daily.reduceRegion(
                ee.Reducer.first(), point, EXTRACTION_RADIUS
            ).get("temperature_2m")
            
            rh_val = rh_daily.reduceRegion(
                ee.Reducer.first(), point, EXTRACTION_RADIUS
            ).get("relative_humidity_daily_pct")
            
            wind_val = wind_daily.reduceRegion(
                ee.Reducer.first(), point, EXTRACTION_RADIUS
            ).get("u_component_of_wind_10m")
            
            pressure_val = pressure_daily.reduceRegion(
                ee.Reducer.first(), point, EXTRACTION_RADIUS
            ).get("surface_pressure")
            
            precip_val = precip_daily.reduceRegion(
                ee.Reducer.first(), point, EXTRACTION_RADIUS
            ).get("total_precipitation")
            
            # Get values
            temp_c = temp_val.getInfo()
            rh_pct = rh_val.getInfo()
            wind_ms = wind_val.getInfo()
            pressure_hpa = pressure_val.getInfo()
            precip_m = precip_val.getInfo()
            
            # Check if all values are available
            meteo_available = all(v is not None for v in 
                [temp_c, rh_pct, wind_ms, pressure_hpa, precip_m])
            
            results.append({
                "station_id": sid,
                "date": date_str,
                "temperature_daily_c": temp_c,
                "relative_humidity_daily_pct": rh_pct,
                "wind_speed_daily_ms": wind_ms,
                "surface_pressure_daily_hpa": pressure_hpa,
                "precipitation_daily_m": precip_m,
                "meteo_available": meteo_available,
            })
            
        except Exception as e:
            results.append({
                "station_id": sid,
                "date": date_str,
                "temperature_daily_c": None,
                "relative_humidity_daily_pct": None,
                "wind_speed_daily_ms": None,
                "surface_pressure_daily_hpa": None,
                "precipitation_daily_m": None,
                "meteo_available": False,
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
        
        date_results = extract_era5_for_date(date_str, stations)
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
print(f"  ERA5 available: {results_df['meteo_available'].sum()}")
print(f"  ERA5 match rate: {results_df['meteo_available'].mean()*100:.1f}%")
print()

# ============================================================
# SUMMARY
# ============================================================

print("=" * 70)
print("EXTRACTION COMPLETE")
print("=" * 70)
print()
print("NEXT STEPS:")
print("  1. Review the extracted ERA5 values")
print("  2. Run quality control checks")
print("  3. Join with MAIAC AOD")
print("  4. Create final matched dataset")
print()
print("OUTPUT FILE:")
print(f"  {OUTPUT_CSV}")
print()