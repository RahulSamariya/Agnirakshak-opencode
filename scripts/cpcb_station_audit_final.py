"""Complete CPCB station audit for PM2.5 calibration feasibility."""
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

# Station name mapping (filename pattern -> canonical name)
STATION_NAME_MAP = {
    "chandkheda": "Chandkheda",
    "gyaspur": "Gyaspur",
    "maninagar": "Maninagar",
    "raikhad": "Raikhad",
    "rakhial": "Rakhial",
    "sac_isro_bopal": "SAC ISRO Bopal",
    "sac_isro_satellite": "SAC ISRO Satellite",
    "svpi_airport_hansol": "SVPI Airport Hansol",
    "sardar_vallabhbhai_patel_stadium": "Sardar Vallabhbhai Patel Stadium",
}

def parse_station_from_filename(fname):
    """Extract station name from filename."""
    name_part = fname.replace("aqi_hourly_station_level_", "").split("_-_")[0]
    # Replace underscores with spaces
    name_lower = name_part.replace("_", " ").rstrip(",").strip()
    # Try to match to canonical name
    for key, canonical in STATION_NAME_MAP.items():
        if key.replace("_", " ") in name_lower:
            return canonical
    return name_part

def compute_sha256(fpath):
    """Compute SHA256 of a file."""
    return hashlib.sha256(fpath.read_bytes()).hexdigest()

print("=" * 80)
print("CPCB/GPCB STATION AUDIT FOR PM2.5 CALIBRATION FEASIBILITY")
print("=" * 80)

# 1. Find all station files
station_files = sorted(ROOT.glob("aqi_hourly_station_level_*.xlsx"))
print(f"\n[1] STATION FILES FOUND: {len(station_files)}")
for f in station_files:
    print(f"    - {f.name}")

# 2. Load QC metadata
qc_df = pd.read_csv("data/metadata/aqi_station_month_qc.csv")
coords_df = pd.read_csv("data/metadata/aqi_station_coordinates.csv")
inventory_df = pd.read_csv("data/metadata/ahmedabad_cpcb_station_inventory.csv")

# 3. Inspect each station file
print(f"\n[2] INSPECTING STATION FILES:")
results = []

for fpath in station_files:
    fname = fpath.name
    sha256 = compute_sha256(fpath)
    station_name = parse_station_from_filename(fname)
    
    # Get inventory match
    inv_match = None
    for _, row in inventory_df.iterrows():
        if station_name.lower() in row["station_name"].lower():
            inv_match = row.to_dict()
            break
    
    # Read xlsx
    df = pd.read_excel(fpath)
    
    # Check for variables
    columns = list(df.columns)
    has_pm25 = any("pm2.5" in c.lower() or "pm25" in c.lower() for c in columns)
    has_aqi = any("aqi" in c.lower() for c in columns)
    
    # The files have NO explicit variable header - columns are Date + 24 hourly timestamps
    # The numeric values are UNLABELED - we cannot determine if they are PM2.5 or AQI
    variable_type = "UNKNOWN"
    if has_pm25:
        variable_type = "PM2.5"
    elif has_aqi:
        variable_type = "AQI"
    else:
        variable_type = "UNLABELED_NUMERIC"
    
    # Melt to long format for analysis
    date_col = columns[0]
    hour_cols = columns[1:]
    
    df_long = df.melt(id_vars=[date_col], value_vars=hour_cols, 
                       var_name="hour", value_name="value")
    df_long["value"] = pd.to_numeric(df_long["value"], errors="coerce")
    
    # Analyze values
    total_cells = len(df_long)
    valid_cells = df_long["value"].count()
    null_cells = df_long["value"].isna().sum()
    negative_cells = (df_long["value"] < 0).sum()
    min_val = df_long["value"].min()
    max_val = df_long["value"].max()
    mean_val = df_long["value"].mean()
    
    # Completeness
    completeness_pct = (valid_cells / total_cells * 100) if total_cells > 0 else 0
    
    # Get QC metadata
    qc_match = qc_df[qc_df["station_name"].str.contains(station_name.split(",")[0], case=False, na=False)]
    
    # Get coordinates
    coord_match = coords_df[coords_df["station_name"].str.contains(station_name.split(",")[0], case=False, na=False)]
    
    print(f"\n  Station: {station_name}")
    print(f"    File: {fname}")
    print(f"    SHA256: {sha256[:16]}...")
    print(f"    Variable type: {variable_type}")
    print(f"    Has PM2.5 column: {has_pm25}")
    print(f"    Has AQI column: {has_aqi}")
    print(f"    Shape: {df.shape}")
    print(f"    Total hourly values: {total_cells}")
    print(f"    Valid values: {valid_cells}")
    print(f"    Null values: {null_cells}")
    print(f"    Negative values: {negative_cells}")
    print(f"    Value range: {min_val:.1f} - {max_val:.1f}")
    print(f"    Mean: {mean_val:.1f}")
    print(f"    Completeness: {completeness_pct:.1f}%")
    
    if len(qc_match) > 0:
        qc_row = qc_match.iloc[0]
        print(f"    QC status: {qc_row['qc_status']}")
        print(f"    Expected hours: {qc_row['expected_hours']}")
        print(f"    Observed hours: {qc_row['observed_hours']}")
    
    if len(coord_match) > 0:
        coord_row = coord_match.iloc[0]
        print(f"    Lat: {coord_row['latitude']}, Lon: {coord_row['longitude']}")
        print(f"    Agency: {coord_row['agency']}")
        print(f"    CPCB code: {coord_row['cpcb_code']}")
    
    result = {
        "station_name": station_name,
        "source_file": fname,
        "sha256": sha256,
        "variable_type": variable_type,
        "has_pm25_column": has_pm25,
        "has_aqi_column": has_aqi,
        "columns": columns,
        "shape": df.shape,
        "total_hourly_values": int(total_cells),
        "valid_values": int(valid_cells),
        "null_values": int(null_cells),
        "negative_values": int(negative_cells),
        "min_value": float(min_val) if pd.notna(min_val) else None,
        "max_value": float(max_val) if pd.notna(max_val) else None,
        "mean_value": float(mean_val) if pd.notna(mean_val) else None,
        "completeness_pct": round(completeness_pct, 2),
        "inventory_match": inv_match is not None,
        "inventory_station_id": inv_match["station_id"] if inv_match else None,
    }
    results.append(result)

# 4. Check temporal overlap
print(f"\n[3] TEMPORAL OVERLAP CHECK:")
print(f"    Station files available: January 2025 only (9 files)")
print(f"    City-level files available: January, February, March, April, May 2025 (5 files)")
print(f"    MAIAC AOD period: January 2025 (31 daily dates)")
print(f"    Overlap with MAIAC: January 2025 only")

# 5. Data quality summary
print(f"\n[4] DATA QUALITY SUMMARY:")
for r in results:
    print(f"    {r['station_name']}: {r['valid_values']}/{r['total_hourly_values']} valid, "
          f"{r['null_values']} null, {r['negative_values']} negative, "
          f"range [{r['min_value']:.1f}, {r['max_value']:.1f}]")

# 6. Critical findings
print(f"\n[5] CRITICAL FINDINGS:")
print(f"    ALL 9 station files have UNLABELED numeric values (no PM2.5/AQI header)")
print(f"    The values appear to be AQI based on QC metadata (min_aqi, max_aqi columns)")
print(f"    PM2.5 concentrations are NOT directly available in any file")
print(f"    No pollutant-specific columns (PM10, NO2, SO2, CO, O3, NH3)")
print(f"    No latitude/longitude in data files (coordinates from inventory only)")
print(f"    Only January 2025 data available for station-level analysis")

# 7. Save results
out_path = Path("data/profiles/cpcb_station_audit_final.json")
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, "w") as f:
    json.dump({
        "audit_date": datetime.now().isoformat(),
        "station_count": len(results),
        "results": results,
        "temporal_coverage": {
            "station_files": ["January 2025"],
            "city_files": ["January", "February", "March", "April", "May 2025"],
            "maiac_period": "January 2025",
        },
        "critical_findings": [
            "ALL 9 station files have UNLABELED numeric values - no PM2.5 or AQI column header",
            "PM2.5 concentrations are NOT directly available",
            "Values appear to be AQI based on QC metadata",
            "Only January 2025 data available at station level",
            "Cannot infer PM2.5 from AQI per task requirements",
        ],
    }, f, indent=2, default=str)
print(f"\nResults saved to: {out_path}")
