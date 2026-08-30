"""AQI profiling script for Ahmedabad."""
import json
import hashlib
from pathlib import Path
import pandas as pd
import glob

# Get all AQI files
aqi_files = glob.glob('ERA5/aqi_hourly_city_level__*.xlsx')

print('=== Ahmedabad AQI Profile ===')
print(f'File count: {len(aqi_files)}')

# Combine all files
all_data = []
for file in sorted(aqi_files):
    print(f'\nProcessing: {file}')
    try:
        df = pd.read_excel(file)
        print(f'  Rows: {len(df)}')
        print(f'  Columns: {list(df.columns)}')
        all_data.append(df)
    except Exception as e:
        print(f'  Error: {e}')

if all_data:
    combined = pd.concat(all_data, ignore_index=True)
    print(f'\n=== Combined Profile ===')
    print(f'Total rows: {len(combined)}')
    print(f'Columns: {list(combined.columns)}')
    
    # Check for timestamp column
    timestamp_col = None
    for col in combined.columns:
        if 'time' in col.lower() or 'date' in col.lower():
            timestamp_col = col
            break
    
    if timestamp_col:
        print(f'\nTimestamp column: {timestamp_col}')
        print(f'Time range: {combined[timestamp_col].min()} to {combined[timestamp_col].max()}')
        
        # Check for missing timestamps
        missing_ts = combined[timestamp_col].isnull().sum()
        print(f'Missing timestamps: {missing_ts}')
        
        # Check for duplicate timestamps
        duplicate_ts = combined[timestamp_col].duplicated().sum()
        print(f'Duplicate timestamps: {duplicate_ts}')
    
    # Check for AQI column
    aqi_col = None
    for col in combined.columns:
        if 'aqi' in col.lower():
            aqi_col = col
            break
    
    if aqi_col:
        print(f'\nAQI column: {aqi_col}')
        print(f'AQI min: {combined[aqi_col].min()}')
        print(f'AQI max: {combined[aqi_col].max()}')
        print(f'AQI mean: {combined[aqi_col].mean():.2f}')
        print(f'Missing AQI values: {combined[aqi_col].isnull().sum()}')
    
    # Save profile as JSON
    profile = {
        "files": [Path(f).name for f in aqi_files],
        "file_count": len(aqi_files),
        "total_rows": len(combined),
        "columns": list(combined.columns),
        "timestamp_column": timestamp_col,
        "aqi_column": aqi_col,
        "data_quality": {
            "missing_timestamps": int(combined[timestamp_col].isnull().sum()) if timestamp_col else None,
            "duplicate_timestamps": int(combined[timestamp_col].duplicated().sum()) if timestamp_col else None,
            "missing_aqi": int(combined[aqi_col].isnull().sum()) if aqi_col else None
        }
    }
    
    if timestamp_col:
        profile["time_range"] = {
            "start": str(combined[timestamp_col].min()),
            "end": str(combined[timestamp_col].max())
        }
    
    if aqi_col:
        profile["aqi_stats"] = {
            "min": float(combined[aqi_col].min()),
            "max": float(combined[aqi_col].max()),
            "mean": float(combined[aqi_col].mean())
        }
    
    # Save to JSON
    output_path = Path("data/profiles/cpcb_ahmedabad_2025_01_05.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(profile, f, indent=2, default=str)
    
    print(f'\nProfile saved to: {output_path}')
else:
    print('\nNo AQI files found or all files failed to load.')
