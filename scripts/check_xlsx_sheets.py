"""Check if station xlsx files have any metadata or second sheets indicating variable type."""
import pandas as pd
from pathlib import Path

station_files = sorted(Path(".").glob("aqi_hourly_station_level_*.xlsx"))

for fpath in station_files[:2]:  # Check first 2
    print(f"\n{'='*60}")
    print(f"FILE: {fpath.name}")
    
    # Check all sheet names
    xls = pd.ExcelFile(fpath)
    print(f"  Sheets: {xls.sheet_names}")
    
    for sheet in xls.sheet_names:
        df = pd.read_excel(fpath, sheet_name=sheet, header=None)
        print(f"\n  Sheet '{sheet}': shape={df.shape}")
        print(f"  First 5 rows (raw):")
        print(df.head(5).to_string(index=False))
        
        # Check row 0 for possible variable name
        row0 = df.iloc[0].tolist()
        print(f"\n  Row 0 values: {row0}")

# Also check city-level files for comparison
print(f"\n\n{'='*60}")
print("CITY-LEVEL FILE COMPARISON:")
city_files = sorted(Path("data/raw/aqi").glob("aqi_hourly_city_level_*.xlsx"))
for fpath in city_files[:2]:
    print(f"\nFILE: {fpath.name}")
    xls = pd.ExcelFile(fpath)
    print(f"  Sheets: {xls.sheet_names}")
    df = pd.read_excel(fpath, header=None)
    print(f"  First 3 rows:")
    print(df.head(3).to_string(index=False))
