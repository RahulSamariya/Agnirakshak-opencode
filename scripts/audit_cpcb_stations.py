"""Audit 9 Ahmedabad CPCB/GPCB stations for PM2.5 calibration feasibility."""
import hashlib
import json
from pathlib import Path
from datetime import datetime

import pandas as pd

ROOT = Path(".")

# Verified station inventory
STATIONS = {
    "Chandkheda": {"station_id": "site_5453", "agency": "IITM", "lat": 23.108, "lon": 72.5746},
    "Gyaspur": {"station_id": "site_5450", "agency": "IITM", "lat": 22.9771, "lon": 72.553},
    "Maninagar": {"station_id": "site_308", "agency": "GPCB", "lat": 23.0027, "lon": 72.5919},
    "Raikhad": {"station_id": "site_5452", "agency": "IITM", "lat": 23.0205, "lon": 72.5793},
    "Rakhial": {"station_id": "site_5451", "agency": "IITM", "lat": 23.0168, "lon": 72.6258},
    "SAC ISRO Bopal": {"station_id": "site_5454", "agency": "IITM", "lat": 23.0411, "lon": 72.4567},
    "SAC ISRO Satellite": {"station_id": "site_5455", "agency": "IITM", "lat": 23.0234, "lon": 72.5152},
    "SVPI Airport Hansol": {"station_id": "site_5456", "agency": "IITM", "lat": 23.0768, "lon": 72.6279},
    "Sardar Vallabhbhai Patel Stadium": {"station_id": "site_5449", "agency": "IITM", "lat": 23.0431, "lon": 72.563},
}

# Find all station-level xlsx files
station_files = sorted(ROOT.glob("aqi_hourly_station_level_*.xlsx"))
print(f"Found {len(station_files)} station-level xlsx files:\n")

results = []
for fpath in station_files:
    fname = fpath.name
    sha256 = hashlib.sha256(fpath.read_bytes()).hexdigest()

    # Parse station name from filename
    # Format: aqi_hourly_station_level_<station>,_ahmedabad_-_<agency>_2025_January_ahmedabad_2025.xlsx
    parts = fname.replace("aqi_hourly_station_level_", "").replace("_ahmedabad_2025.xlsx", "")
    station_raw = parts.split("_-_")[0].replace("_", " ").rstrip(",").strip()
    agency_raw = parts.split("_-_-")[1].split("_")[0] if "_-_ " in parts else "UNKNOWN"

    print(f"{'='*70}")
    print(f"FILE: {fname}")
    print(f"  SHA256: {sha256}")
    print(f"  Parsed station: {station_raw}")
    print(f"  Parsed agency: {agency_raw}")

    # Read xlsx
    try:
        df = pd.read_excel(fpath)
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  First 3 rows:")
        print(df.head(3).to_string(index=False))

        # Check for PM2.5
        has_pm25 = any("pm2.5" in c.lower() or "pm25" in c.lower() for c in df.columns)
        has_pm10 = any("pm10" in c.lower() for c in df.columns)
        has_no2 = any("no2" in c.lower() for c in df.columns)
        has_so2 = any("so2" in c.lower() for c in df.columns)
        has_co = any("co" in c.lower() for c in df.columns)
        has_o3 = any("o3" in c.lower() for c in df.columns)
        has_nh3 = any("nh3" in c.lower() for c in df.columns)
        has_aqi = any("aqi" in c.lower() for c in df.columns)
        has_timestamp = any("timestamp" in c.lower() or "date" in c.lower() or "time" in c.lower() for c in df.columns)
        has_lat = any("lat" in c.lower() for c in df.columns)
        has_lon = any("lon" in c.lower() or "lng" in c.lower() for c in df.columns)
        has_station_id = any("station" in c.lower() and "id" in c.lower() for c in df.columns)

        print(f"\n  VARIABLE DETECTION:")
        print(f"    PM2.5:   {'YES' if has_pm25 else 'NO'}")
        print(f"    PM10:    {'YES' if has_pm10 else 'NO'}")
        print(f"    NO2:     {'YES' if has_no2 else 'NO'}")
        print(f"    SO2:     {'YES' if has_so2 else 'NO'}")
        print(f"    CO:      {'YES' if has_co else 'NO'}")
        print(f"    O3:      {'YES' if has_o3 else 'NO'}")
        print(f"    NH3:     {'YES' if has_nh3 else 'NO'}")
        print(f"    AQI:     {'YES' if has_aqi else 'NO'}")
        print(f"    Timestamp: {'YES' if has_timestamp else 'NO'}")
        print(f"    Lat:     {'YES' if has_lat else 'NO'}")
        print(f"    Lon:     {'YES' if has_lon else 'NO'}")
        print(f"    Station ID: {'YES' if has_station_id else 'NO'}")

        # If PM2.5 present, analyze it
        pm25_col = None
        for c in df.columns:
            if "pm2.5" in c.lower() or "pm25" in c.lower():
                pm25_col = c
                break

        pm25_stats = None
        if pm25_col:
            vals = pd.to_numeric(df[pm25_col], errors="coerce")
            pm25_stats = {
                "count": int(vals.count()),
                "nulls": int(vals.isna().sum()),
                "negatives": int((vals < 0).sum()),
                "min": float(vals.min()) if vals.count() > 0 else None,
                "max": float(vals.max()) if vals.count() > 0 else None,
                "mean": float(vals.mean()) if vals.count() > 0 else None,
            }
            print(f"\n  PM2.5 ANALYSIS ({pm25_col}):")
            print(f"    Records:  {pm25_stats['count']}")
            print(f"    Nulls:    {pm25_stats['nulls']}")
            print(f"    Negatives:{pm25_stats['negatives']}")
            print(f"    Min:      {pm25_stats['min']}")
            print(f"    Max:      {pm25_stats['max']}")
            print(f"    Mean:     {pm25_stats['mean']:.2f}")

            # Check temporal coverage
            if has_timestamp:
                ts_col = None
                for c in df.columns:
                    if "timestamp" in c.lower() or "date" in c.lower() or "time" in c.lower():
                        ts_col = c
                        break
                if ts_col:
                    dates = pd.to_datetime(df[ts_col], errors="coerce")
                    valid_dates = dates.dropna()
                    if len(valid_dates) > 0:
                        print(f"    Date range: {valid_dates.min()} to {valid_dates.max()}")

        result = {
            "file": fname,
            "sha256": sha256,
            "station_name": station_raw,
            "agency": agency_raw,
            "has_pm25": has_pm25,
            "has_pm10": has_pm10,
            "has_no2": has_no2,
            "has_so2": has_so2,
            "has_co": has_co,
            "has_o3": has_o3,
            "has_nh3": has_nh3,
            "has_aqi": has_aqi,
            "has_timestamp": has_timestamp,
            "has_lat": has_lat,
            "has_lon": has_lon,
            "has_station_id": has_station_id,
            "pm25_stats": pm25_stats,
            "columns": list(df.columns),
            "shape": df.shape,
        }
        results.append(result)

    except Exception as e:
        print(f"  ERROR reading: {e}")
        results.append({"file": fname, "sha256": sha256, "error": str(e)})

    print()

# Save results
out_path = Path("data/profiles/cpcb_station_audit_2025_01.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nResults saved to {out_path}")
