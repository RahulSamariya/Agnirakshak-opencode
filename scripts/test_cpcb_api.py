"""Test CPCB CAAQMS PM2.5 acquisition for Chandkheda station."""
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

# Test date range
FROM_DATE = "01-01-2026 T00:00:00Z"
TO_DATE = "03-01-2026 T23:59:59Z"

print("=" * 70)
print("CPCB CAAQMS PM2.5 ACQUISITION TEST")
print("=" * 70)
print(f"\nStation: {STATION['station_name']} ({STATION['station_id']})")
print(f"Parameter: PM2.5 (parameter_193)")
print(f"Date range: {FROM_DATE} to {TO_DATE}")
print(f"State: {STATION['state']}")
print(f"City: {STATION['city']}")

# Method 1: Try the comparison-data API endpoint
print("\n" + "=" * 70)
print("METHOD 1: Testing comparison-data API endpoint")
print("=" * 70)

# Based on research, the API endpoint format is:
# https://airquality.cpcb.gov.in/ccr/caaqm-comparison-data/caaqm-comparison-data
# with POST request containing filters

url = "https://airquality.cpcb.gov.in/ccr/caaqm-comparison-data/caaqm-comparison-data"

# Build the request payload based on documented format
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
print(f"Method: POST")
print(f"Payload keys: {list(payload.keys())}")
print(f"Station filter: {payload['filtersToApply']['station']}")
print(f"Parameter filter: {payload['filtersToApply']['parameter']}")

try:
    print("\nSending request...")
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Response type: {type(data)}")
            print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
            print(f"Response content (first 500 chars): {json.dumps(data, indent=2)[:500]}")
        except:
            print(f"Response text (first 500 chars): {response.text[:500]}")
    else:
        print(f"Response text (first 500 chars): {response.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")

# Method 2: Try the data-repository endpoint
print("\n" + "=" * 70)
print("METHOD 2: Testing data-repository endpoint")
print("=" * 70)

url2 = "https://airquality.cpcb.gov.in/ccr/caaqm-data-repository/caaqm-data-repository"

print(f"\nURL: {url2}")
print("Sending request...")

try:
    response2 = requests.post(url2, json=payload, headers=headers, timeout=30)
    print(f"Status code: {response2.status_code}")
    
    if response2.status_code == 200:
        try:
            data2 = response2.json()
            print(f"Response type: {type(data2)}")
            print(f"Response content (first 500 chars): {json.dumps(data2, indent=2)[:500]}")
        except:
            print(f"Response text (first 500 chars): {response2.text[:500]}")
    else:
        print(f"Response text (first 500 chars): {response2.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")

# Method 3: Try the old app.cpcbccr.com endpoint
print("\n" + "=" * 70)
print("METHOD 3: Testing old app.cpcbccr.com endpoint")
print("=" * 70)

url3 = "https://app.cpcbccr.com/caaqm-comparison-data/caaqm-comparison-data"

print(f"\nURL: {url3}")
print("Sending request...")

try:
    response3 = requests.post(url3, json=payload, headers=headers, timeout=30)
    print(f"Status code: {response3.status_code}")
    
    if response3.status_code == 200:
        try:
            data3 = response3.json()
            print(f"Response type: {type(data3)}")
            print(f"Response content (first 500 chars): {json.dumps(data3, indent=2)[:500]}")
        except:
            print(f"Response text (first 500 chars): {response3.text[:500]}")
    else:
        print(f"Response text (first 500 chars): {response3.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")

# Method 4: Try the openaq API as alternative
print("\n" + "=" * 70)
print("METHOD 4: Testing OpenAQ API as alternative")
print("=" * 70)

# OpenAQ v3 API
url4 = "https://api.openaq.org/v3/measurements"
params4 = {
    "coordinates": f"{STATION['latitude']},{STATION['longitude']}",
    "radius": 5000,  # 5km radius
    "parameter": "pm25",
    "date_from": "2026-01-01T00:00:00Z",
    "date_to": "2026-01-03T23:59:59Z",
    "limit": 100
}

headers4 = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0"
}

print(f"\nURL: {url4}")
print(f"Params: {params4}")

try:
    response4 = requests.get(url4, params=params4, headers=headers4, timeout=30)
    print(f"Status code: {response4.status_code}")
    
    if response4.status_code == 200:
        try:
            data4 = response4.json()
            print(f"Response type: {type(data4)}")
            print(f"Response keys: {list(data4.keys()) if isinstance(data4, dict) else 'N/A'}")
            
            if isinstance(data4, dict) and "results" in data4:
                results = data4["results"]
                print(f"Number of results: {len(results)}")
                if results:
                    print(f"First result: {json.dumps(results[0], indent=2)}")
            else:
                print(f"Response content (first 500 chars): {json.dumps(data4, indent=2)[:500]}")
        except:
            print(f"Response text (first 500 chars): {response4.text[:500]}")
    else:
        print(f"Response text (first 500 chars): {response4.text[:500]}")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
