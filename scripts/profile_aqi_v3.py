"""AQI profiling script for Ahmedabad."""
import json
import hashlib
from pathlib import Path
import pandas as pd
import glob

# Get all AQI files
aqi_files = glob.glob('data/raw/aqi/aqi_hourly_city_level__*.xlsx')

print('=== Ahmedabad AQI Profile ===')
print(f'File count: {len(aqi_files)}')

# Process each file
all_profiles = []
for file in sorted(aqi_files):
    print(f'\nProcessing: {file}')
    try:
        df = pd.read_excel(file)
        print(f'  Rows: {len(df)}')
        print(f'  Columns: {list(df.columns)}')
        
        # Melt the data to long format
        id_vars = ['Date']
        value_vars = [col for col in df.columns if col != 'Date']
        
        melted = df.melt(id_vars=id_vars, value_vars=value_vars, 
                         var_name='Hour', value_name='AQI')
        
        # Get month from filename
        month = Path(file).stem.split('_')[3]
        print(f'  Month: {month}')
        print(f'  AQI min: {melted["AQI"].min()}')
        print(f'  AQI max: {melted["AQI"].max()}')
        print(f'  Missing AQI: {melted["AQI"].isnull().sum()}')
        
        all_profiles.append({
            "file": Path(file).name,
            "month": month,
            "rows": len(df),
            "aqi_min": float(melted["AQI"].min()),
            "aqi_max": float(melted["AQI"].max()),
            "aqi_mean": float(melted["AQI"].mean()),
            "missing_aqi": int(melted["AQI"].isnull().sum()),
            "time_range": {
                "start": f"2025-{month}-01",
                "end": f"2025-{month}-31"
            }
        })
        
    except Exception as e:
        print(f'  Error: {e}')

# Save profile as JSON
profile = {
    "files": [Path(f).name for f in aqi_files],
    "file_count": len(aqi_files),
    "monthly_profiles": all_profiles,
    "overall_time_range": {
        "start": "2025-01-01",
        "end": "2025-05-31"
    },
    "data_format": "Wide format with Date column and 24 hourly columns (00:00:00 to 23:00:00)",
    "city": "Ahmedabad",
    "source": "CPCB"
}

# Save to JSON
output_path = Path("data/profiles/aqi_ahmedabad_2025.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(profile, f, indent=2, default=str)

print(f'\nProfile saved to: {output_path}')
