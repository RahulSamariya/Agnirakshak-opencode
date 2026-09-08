"""Test CPCB CAAQMS PM2.5 acquisition with SSL bypass."""
import json
import hashlib
import time
import base64
from datetime import datetime
from pathlib import Path
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

# Test date range
FROM_DATE = "01-01-2026 T00:00:00Z"
TO_DATE = "03-01-2026 T23:59:59Z"

print("=" * 70)
print("CPCB CAAQMS PM2.5 ACQUISITION TEST (SSL BYPASS)")
print("=" * 70)
print(f"\nStation: {STATION['station_name']} ({STATION['station_id']})")
print(f"Parameter: PM2.5 (parameter_193)")
print(f"Date range: {FROM_DATE} to {TO_DATE}")

# Method 1: Try the comparison-data API endpoint with SSL bypass
print("\n" + "=" * 70)
print("METHOD 1: Testing comparison-data API endpoint (SSL bypass)")
print("=" * 70)

url = "https://airquality.cpcb.gov.in/ccr/caaqm-comparison-data/caaqm-comparison-data"

payload = {
    "draw": 1,
    "columns": [
        {
            "data": 0,
            "name": "",
            "searchable": True,
            "orderable": False,
            "search": {"value": "", "regex": False}
        }
    ],
    "order": [],
    "start": 0,
    "length": 100,
    "search": {"value": "", "regex": False},
    "filtersToApply": {
        "parameter_list": [
            {
                "id": 0,
                "itemName": "PM2.5",
                "itemValue": "parameter_193"
            }
        ],
        "criteria": "24 Hours",
        "reportFormat": "Tabular",
        "fromDate": FROM_DATE,
        "toDate": TO_DATE,
        "state": STATION["state"],
        "city": STATION["city"],
        "station": STATION["station_id"],
        "parameter": ["parameter_193"],
        "parameterNames": ["PM2.5"]
    },
    "pagination": 1
}

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Origin": "https://airquality.cpcb.gov.in",
    "Referer": "https://airquality.cpcb.gov.in/ccr/#/caaqm-dashboard-all/caaqm-landing/caaqm-comparison-data",
}

print(f"\nURL: {url}")
print("Sending request with SSL verification disabled...")

try:
    response = requests.post(url, json=payload, headers=headers, timeout=30, verify=False)
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response type: {type(data)}")
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            
            # Check if data contains results
            if isinstance(data, dict):
                if "data" in data:
                    print(f"Number of data rows: {len(data['data'])}")
                    if data["data"]:
                        print(f"First row: {data['data'][0]}")
                elif "recordsTotal" in data:
                    print(f"Total records: {data['recordsTotal']}")
                    if "data" in data:
                        print(f"Data rows: {len(data['data'])}")
            
            print(f"Response content (first 1000 chars): {json.dumps(data, indent=2)[:1000]}")
        except Exception as e:
            print(f"JSON parse error: {e}")
            print(f"Response text (first 1000 chars): {response.text[:1000]}")
    else:
        print(f"Response text (first 1000 chars): {response.text[:1000]}")
        
except Exception as e:
    print(f"Error: {e}")

# Method 2: Try the view-data-report endpoint
print("\n" + "=" * 70)
print("METHOD 2: Testing view-data-report endpoint")
print("=" * 70)

# Try different URL patterns
urls_to_try = [
    "https://airquality.cpcb.gov.in/ccr/caaqm-view-data-report/caaqm-view-data-report",
    "https://airquality.cpcb.gov.in/ccr/view-data-report",
    "https://airquality.cpcb.gov.in/ccr/api/caaqm-comparison-data",
]

for url in urls_to_try:
    print(f"\nTrying: {url}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15, verify=False)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Response keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
                print(f"  Content (first 500 chars): {json.dumps(data, indent=2)[:500]}")
            except:
                print(f"  Text (first 500 chars): {response.text[:500]}")
    except Exception as e:
        print(f"  Error: {e}")

# Method 3: Try to get station list first
print("\n" + "=" * 70)
print("METHOD 3: Testing station list endpoint")
print("=" * 70)

station_list_urls = [
    "https://airquality.cpcb.gov.in/ccr/caaqm-comparison-data/getStationList",
    "https://airquality.cpcb.gov.in/ccr/getStationList",
    "https://airquality.cpcb.gov.in/ccr/caaqm-comparison-data/stations",
]

for url in station_list_urls:
    print(f"\nTrying: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=15, verify=False)
        print(f"  Status: {response.status_code}")
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"  Response type: {type(data)}")
                if isinstance(data, list):
                    print(f"  Number of stations: {len(data)}")
                    if data:
                        print(f"  First station: {data[0]}")
                elif isinstance(data, dict):
                    print(f"  Keys: {list(data.keys())}")
            except:
                print(f"  Text (first 500 chars): {response.text[:500]}")
    except Exception as e:
        print(f"  Error: {e}")

# Method 4: Check the actual HTML page for API clues
print("\n" + "=" * 70)
print("METHOD 4: Fetching main page for API clues")
print("=" * 70)

try:
    response = requests.get("https://airquality.cpcb.gov.in/ccr/", headers=headers, timeout=15, verify=False)
    print(f"Status: {response.status_code}")
    # Look for API URLs in the page
    text = response.text
    if "api" in text.lower():
        # Find API-related strings
        import re
        api_patterns = re.findall(r'["\']([^"\']*(?:api|endpoint|url)[^"\']*)["\']', text, re.IGNORECASE)
        if api_patterns:
            print("Found API-related strings:")
            for p in api_patterns[:10]:
                print(f"  {p}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
