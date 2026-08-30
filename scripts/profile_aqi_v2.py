"""AQI profiling script for Ahmedabad - comprehensive version."""
import json
import hashlib
from pathlib import Path
import pandas as pd
import glob

# Get all AQI files
aqi_files = glob.glob('ERA5/aqi_hourly_city_level__*.xlsx')

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
        
        # Create proper timestamps
        melted['Date'] = pd.to_datetime(melted['Date'], format='%d')
        melted['Hour_int'] = melted['Hour'].str.split(':').str[0].astype(int)
        melted['Timestamp'] = melted['Date'] + pd.to_timedelta(melted['Hour_int'], unit='h')
        
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
                "start": str(melted["Timestamp"].min()),
                "end": str(melted["Timestamp"].max())
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
output_path = Path("data/profiles/cpcb_ahmedabad_2025_01_05.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(profile, f, indent=2, default=str)

print(f'\nProfile saved to: {output_path}')
