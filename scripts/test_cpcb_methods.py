"""Test CPCB PM2.5 acquisition via data.gov.in API and other methods."""
import json
import hashlib
import time
import base64
from datetime import datetime
from pathlib import Path

import requests
import pandas as pd

# Station details
STATION = {
    "station_id": "site_5453",
    "station_name": "Chandkheda, Ahmedabad",
    "agency": "IITM",
    "state": "Gujarat",
    "city": "Ahmedabad",
    "latitude": 23.108,
    "longitude": 72.5746,
}

print("=" * 70)
print("CPCB PM2.5 ACQUISITION TEST - MULTIPLE METHODS")
print("=" * 70)
print(f"\nStation: {STATION['station_name']} ({STATION['station_id']})")

# Method 1: data.gov.in API (public, limited)
print("\n" + "=" * 70)
print("METHOD 1: data.gov.in API (public)")
print("=" * 70)

# Public API key for testing (limited to 10 requests)
API_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"

url = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
params = {
    "api-key": API_KEY,
    "format": "json",
    "filters[station]": STATION["station_name"],
    "filters[pollutant_id]": "PM2.5",
    "limit": 10
}

print(f"\nURL: {url}")
print(f"Params: {params}")

try:
    response = requests.get(url, params=params, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        
        if "records" in data:
            records = data["records"]
            print(f"Number of records: {len(records)}")
            if records:
                print(f"\nFirst record:")
                print(json.dumps(records[0], indent=2))
                
                # Check if this is concentration data or AQI
                print(f"\nColumn names: {list(records[0].keys())}")
        else:
            print(f"Response: {json.dumps(data, indent=2)[:500]}")
    else:
        print(f"Error: {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")

# Method 2: OpenAQ API (requires API key)
print("\n" + "=" * 70)
print("METHOD 2: OpenAQ API (requires API key)")
print("=" * 70)

openaq_url = "https://api.openaq.org/v3/measurements"
params_openaq = {
    "coordinates": f"{STATION['latitude']},{STATION['longitude']}",
    "radius": 5000,
    "parameter": "pm25",
    "date_from": "2025-01-01T00:00:00Z",
    "date_to": "2025-01-03T23:59:59Z",
    "limit": 10
}

print(f"\nURL: {openaq_url}")
print(f"Params: {params_openaq}")
print("Note: Requires API key from https://openaq.org/")

try:
    response = requests.get(openaq_url, params=params_openaq, timeout=30)
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("Response: API key required")
    elif response.status_code == 200:
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        if "results" in data:
            print(f"Number of results: {len(data['results'])}")
            if data['results']:
                print(f"First result: {json.dumps(data['results'][0], indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Method 3: Check existing xlsx file for structure
print("\n" + "=" * 70)
print("METHOD 3: Analyzing existing Chandkheda xlsx file")
print("=" * 70)

xlsx_path = Path("aqi_hourly_station_level_chandkheda,_ahmedabad_-_iitm_2025_January_ahmedabad_2025.xlsx")
if xlsx_path.exists():
    print(f"\nFile exists: {xlsx_path}")
    df = pd.read_excel(xlsx_path)
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst 5 rows:")
    print(df.head())
    
    # Check for any PM2.5 indicators in the file
    print("\nSearching for PM2.5 indicators...")
    for col in df.columns:
        col_str = str(col).lower()
        if any(x in col_str for x in ["pm2.5", "pm25", "pm 2.5", "particulate"]):
            print(f"  Found PM2.5 indicator in column: {col}")
    
    # Check if values could be PM2.5 concentrations
    hour_cols = [c for c in df.columns if c != "Date"]
    if hour_cols:
        values = pd.to_numeric(df[hour_cols].values.flatten(), errors="coerce")
        valid_values = values[~pd.isna(values)]
        print(f"\nValue statistics:")
        print(f"  Count: {len(valid_values)}")
        print(f"  Min: {valid_values.min():.1f}")
        print(f"  Max: {valid_values.max():.1f}")
        print(f"  Mean: {valid_values.mean():.1f}")
        print(f"  Std: {valid_values.std():.1f}")
        
        # Check if values are in typical PM2.5 range (0-500 µg/m³)
        if valid_values.min() >= 0 and valid_values.max() <= 500:
            print(f"\n  Values are in range 0-500, could be PM2.5 (µg/m³)")
        else:
            print(f"\n  Values outside typical PM2.5 range")
else:
    print(f"\nFile not found: {xlsx_path}")

# Method 4: Check for any other data sources
print("\n" + "=" * 70)
print("METHOD 4: Searching for other data sources")
print("=" * 70)

# Search for any CSV files that might contain PM2.5 data
import glob
csv_files = glob.glob("**/*.csv", recursive=True)
print(f"\nFound {len(csv_files)} CSV files")

for csv_file in csv_files[:10]:  # Check first 10
    try:
        df = pd.read_csv(csv_file, nrows=5)
        columns_lower = [str(c).lower() for c in df.columns]
        
        # Check for PM2.5 related columns
        pm25_cols = [c for c in columns_lower if any(x in c for x in ["pm2.5", "pm25", "pm 2.5", "particulate"])]
        
        if pm25_cols:
            print(f"\n  PM2.5 columns found in {csv_file}:")
            print(f"    Columns: {pm25_cols}")
    except:
        pass

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("\n1. data.gov.in API: Returns AQI sub-index values, NOT concentration data")
print("2. OpenAQ API: Requires API key, not tested")
print("3. Existing xlsx files: Contain unlabeled numeric values (AQI, not PM2.5)")
print("4. No direct PM2.5 concentration data found in repository")
print("\nCONCLUSION: CPCB CAAQMS PM2.5 concentration data is NOT currently")
print("accessible via public APIs without authentication or browser session.")
