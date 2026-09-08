"""Comprehensive PM2.5 availability audit for 9 Ahmedabad CPCB/GPCB stations."""
import hashlib
import json
from pathlib import Path
from datetime import datetime

import pandas as pd

ROOT = Path(".")

# Verified station inventory
STATIONS = {
    "Chandkheda": {"station_id": "site_5453", "agency": "IITM", "lat": 23.108, "lon": 72.5746, "cpcb_code": "#5453"},
    "Gyaspur": {"station_id": "site_5450", "agency": "IITM", "lat": 22.9771, "lon": 72.553, "cpcb_code": "#5450"},
    "Maninagar": {"station_id": "site_308", "agency": "GPCB", "lat": 23.0027, "lon": 72.5919, "cpcb_code": "#308"},
    "Raikhad": {"station_id": "site_5452", "agency": "IITM", "lat": 23.0205, "lon": 72.5793, "cpcb_code": "#5452"},
    "Rakhial": {"station_id": "site_5451", "agency": "IITM", "lat": 23.0168, "lon": 72.6258, "cpcb_code": "#5451"},
    "SAC ISRO Bopal": {"station_id": "site_5454", "agency": "IITM", "lat": 23.0411, "lon": 72.4567, "cpcb_code": "#5454"},
    "SAC ISRO Satellite": {"station_id": "site_5455", "agency": "IITM", "lat": 23.0234, "lon": 72.5152, "cpcb_code": "#5455"},
    "SVPI Airport Hansol": {"station_id": "site_5456", "agency": "IITM", "lat": 23.0768, "lon": 72.6279, "cpcb_code": "#5456"},
    "Sardar Vallabhbhai Patel Stadium": {"station_id": "site_5449", "agency": "IITM", "lat": 23.0431, "lon": 72.563, "cpcb_code": "#5449"},
}

# PM2.5 column patterns to search for
PM25_PATTERNS = [
    "pm2.5", "pm25", "pm_2_5", "pm2_5",
    "pm2.5 (µg/m³)", "pm2.5 (ug/m3)", "pm2.5 concentration",
    "particulate matter 2.5", "particulate matter 2.5 (µg/m³)",
    "pm 2.5", "pm 25", "particulate matter2.5",
]

# Pollutant patterns
POLLUTANT_PATTERNS = {
    "PM10": ["pm10", "pm 10", "particulate matter 10"],
    "NO2": ["no2", "nitrogen dioxide"],
    "SO2": ["so2", "sulphur dioxide", "sulfur dioxide"],
    "CO": ["co", "carbon monoxide"],
    "O3": ["o3", "ozone"],
    "NH3": ["nh3", "ammonia"],
}

def compute_sha256(fpath):
    """Compute SHA256 of a file."""
    return hashlib.sha256(fpath.read_bytes()).hexdigest()

def parse_station_from_filename(fname):
    """Extract station name from filename."""
    name_lower = fname.lower()
    for canonical_name in STATIONS.keys():
        # Check various patterns
        search_terms = [
            canonical_name.lower().replace(" ", "_"),
            canonical_name.lower().replace(" ", " "),
            canonical_name.lower().replace("sac isro ", "sac_isro_"),
            canonical_name.lower().replace("sardar vallabhbhai patel stadium", "sardar_vallabhbhai_patel_stadium"),
            canonical_name.lower().replace("svpi airport hansol", "svpi_airport_hansol"),
        ]
        for term in search_terms:
            if term in name_lower:
                return canonical_name
    return None

def check_pm25_in_columns(columns):
    """Check if any column matches PM2.5 patterns."""
    for col in columns:
        col_lower = str(col).lower().strip()
        for pattern in PM25_PATTERNS:
            if pattern in col_lower:
                return True, col
    return False, None

def check_pollutants_in_columns(columns):
    """Check for pollutant columns."""
    found = {}
    for pollutant, patterns in POLLUTANT_PATTERNS.items():
        for col in columns:
            col_lower = str(col).lower().strip()
            for pattern in patterns:
                if pattern in col_lower:
                    found[pollutant] = col
                    break
    return found

print("=" * 80)
print("PM2.5 AVAILABILITY AUDIT - 9 AHMEDABAD CPCB/GPCB STATIONS")
print("=" * 80)

# 1. Find all files
print("\n[1] FINDING ALL FILES...")

# Search for all relevant file types
all_files = []
for ext in ["*.xlsx", "*.xls", "*.csv", "*.json", "*.parquet", "*.zip"]:
    all_files.extend(ROOT.glob(ext))
    all_files.extend(ROOT.glob(f"data/**/{ext}"))
    all_files.extend(ROOT.glob(f"data/raw/**/{ext}"))
    all_files.extend(ROOT.glob(f"data/staging/**/{ext}"))

# Filter to station-related files
station_files = []
for f in all_files:
    fname = f.name.lower()
    # Check if file relates to any station
    for station_name in STATIONS.keys():
        if station_name.lower().replace(" ", "_") in fname or \
           station_name.lower().replace(" ", " ") in fname or \
           station_name.lower().replace("sac isro ", "sac_isro_") in fname:
            station_files.append((station_name, f))
            break

# Also check for station-level xlsx files specifically
for f in ROOT.glob("aqi_hourly_station_level_*.xlsx"):
    station_name = parse_station_from_filename(f.name)
    if station_name and (station_name, f) not in station_files:
        station_files.append((station_name, f))

print(f"  Found {len(station_files)} station-related files:")
for station_name, fpath in sorted(station_files):
    print(f"    [{station_name}] {fpath.name}")

# 2. Inspect each file
print("\n[2] INSPECTING FILE SCHEMAS...")

results = []
for station_name, fpath in sorted(station_files, key=lambda x: (x[0], x[1].name)):
    fname = fpath.name
    sha256 = compute_sha256(fpath)
    station_info = STATIONS[station_name]
    
    print(f"\n  {'='*60}")
    print(f"  STATION: {station_name}")
    print(f"  FILE: {fname}")
    print(f"  SHA256: {sha256[:32]}...")
    
    file_result = {
        "station_name": station_name,
        "station_id": station_info["station_id"],
        "agency": station_info["agency"],
        "file": fname,
        "sha256": sha256,
        "file_size_bytes": fpath.stat().st_size,
    }
    
    try:
        if fpath.suffix == ".xlsx" or fpath.suffix == ".xls":
            # Read Excel file
            xls = pd.ExcelFile(fpath)
            print(f"  Sheet names: {xls.sheet_names}")
            file_result["sheet_names"] = xls.sheet_names
            
            for sheet_name in xls.sheet_names:
                # Read with no header to inspect raw structure
                df_raw = pd.read_excel(fpath, sheet_name=sheet_name, header=None)
                print(f"\n  Sheet '{sheet_name}' raw structure:")
                print(f"    Shape: {df_raw.shape}")
                print(f"    First 5 rows:")
                for i in range(min(5, len(df_raw))):
                    row_vals = [str(v)[:30] for v in df_raw.iloc[i].tolist()]
                    print(f"      Row {i}: {row_vals}")
                
                # Read with header
                df = pd.read_excel(fpath, sheet_name=sheet_name)
                columns = list(df.columns)
                print(f"\n    Column names: {columns}")
                
                # Check for PM2.5
                pm25_found, pm25_col = check_pm25_in_columns(columns)
                print(f"    PM2.5 column found: {pm25_found} ({pm25_col})")
                
                # Check for pollutants
                pollutants = check_pollutants_in_columns(columns)
                print(f"    Pollutant columns: {pollutants}")
                
                # Check data types
                print(f"    Data types:")
                for col in columns[:10]:
                    print(f"      {col}: {df[col].dtype}")
                
                # Check for units in header rows
                for i in range(min(3, len(df_raw))):
                    row_text = " ".join([str(v).lower() for v in df_raw.iloc[i].tolist()])
                    if "µg/m³" in row_text or "ug/m3" in row_text or "μg/m3" in row_text:
                        print(f"    UNITS FOUND in row {i}: {row_text[:100]}")
                        file_result["units_detected"] = True
                
                file_result["columns"] = columns
                file_result["pm25_column"] = pm25_col
                file_result["pollutants_found"] = pollutants
                
        elif fpath.suffix == ".csv":
            df = pd.read_csv(fpath, nrows=5)
            columns = list(df.columns)
            print(f"  CSV columns: {columns}")
            pm25_found, pm25_col = check_pm25_in_columns(columns)
            print(f"  PM2.5 column found: {pm25_found} ({pm25_col})")
            file_result["columns"] = columns
            file_result["pm25_column"] = pm25_col
            
        elif fpath.suffix == ".json":
            with open(fpath) as f:
                data = json.load(f)
            print(f"  JSON keys: {list(data.keys()) if isinstance(data, dict) else 'array'}")
            file_result["json_keys"] = list(data.keys()) if isinstance(data, dict) else []
            
        elif fpath.suffix == ".parquet":
            df = pd.read_parquet(fpath)
            columns = list(df.columns)
            print(f"  Parquet columns: {columns}")
            pm25_found, pm25_col = check_pm25_in_columns(columns)
            print(f"  PM2.5 column found: {pm25_found} ({pm25_col})")
            file_result["columns"] = columns
            file_result["pm25_column"] = pm25_col
            
    except Exception as e:
        print(f"  ERROR: {e}")
        file_result["error"] = str(e)
    
    results.append(file_result)

# 3. Summary
print("\n\n" + "=" * 80)
print("STATION-BY-STATION SUMMARY")
print("=" * 80)

for r in results:
    print(f"\n{r['station_name']}:")
    print(f"  File: {r['file']}")
    print(f"  PM2.5 column: {r.get('pm25_column', 'NOT FOUND')}")
    print(f"  Pollutants: {r.get('pollutants_found', {})}")
    print(f"  Columns: {r.get('columns', [])[:10]}...")

# 4. Check for any PM2.5 data
print("\n\n" + "=" * 80)
print("PM2.5 AVAILABILITY CHECK")
print("=" * 80)

pm25_found_any = False
for r in results:
    if r.get("pm25_column"):
        pm25_found_any = True
        print(f"  PM2.5 FOUND: {r['station_name']} -> {r['pm25_column']}")

if not pm25_found_any:
    print("  NO PM2.5 COLUMN FOUND IN ANY FILE")

# 5. Save results
out_path = Path("data/profiles/cpcb_station_pm25_availability.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w") as f:
    json.dump({
        "audit_date": datetime.now().isoformat(),
        "station_count": len(results),
        "pm25_found_any": pm25_found_any,
        "results": results,
    }, f, indent=2, default=str)
print(f"\nResults saved to: {out_path}")
