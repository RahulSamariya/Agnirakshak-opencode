"""ERA5-Land NetCDF profiling script."""
import xarray as xr
import json
from pathlib import Path

# Load the NetCDF file
ds = xr.open_dataset('ERA5/data_0.nc')

# Get basic info
print('=== ERA5-Land NetCDF Profile ===')
print(f'Dimensions: {dict(ds.sizes)}')
print(f'Variables: {list(ds.data_vars)}')
print(f'Coordinates: {list(ds.coords)}')

# Get variable details
for var in ds.data_vars:
    print(f'\nVariable: {var}')
    print(f'  Dimensions: {ds[var].dims}')
    print(f'  Shape: {ds[var].shape}')
    print(f'  Units: {ds[var].attrs.get("units", "N/A")}')
    print(f'  Long name: {ds[var].attrs.get("long_name", "N/A")}')

# Get coordinate ranges
print(f'\nLatitude range: {float(ds.latitude.min())} to {float(ds.latitude.max())}')
print(f'Longitude range: {float(ds.longitude.min())} to {float(ds.longitude.max())}')
print(f'Time range: {ds.valid_time.values[0]} to {ds.valid_time.values[-1]}')
print(f'Time size: {len(ds.valid_time)}')

# Check for missing values
for var in ds.data_vars:
    missing = ds[var].isnull().sum().item()
    total = ds[var].size
    print(f'{var} missing values: {missing}/{total} ({100*missing/total:.2f}%)')

# Get CRS info
if 'crs' in ds.coords:
    print(f'CRS: {ds.crs.attrs}')
elif 'spatial_ref' in ds.coords:
    print(f'Spatial ref: {ds.spatial_ref.attrs}')

# Save profile as JSON
profile = {
    "file": "data_0.nc",
    "dimensions": dict(ds.sizes),
    "variables": list(ds.data_vars),
    "coordinates": list(ds.coords),
    "latitude_range": [float(ds.latitude.min()), float(ds.latitude.max())],
    "longitude_range": [float(ds.longitude.min()), float(ds.longitude.max())],
    "time_range": [str(ds.valid_time.values[0]), str(ds.valid_time.values[-1])],
    "time_size": len(ds.valid_time),
    "variable_details": {}
}

for var in ds.data_vars:
    profile["variable_details"][var] = {
        "dims": list(ds[var].dims),
        "shape": list(ds[var].shape),
        "units": ds[var].attrs.get("units", "N/A"),
        "long_name": ds[var].attrs.get("long_name", "N/A"),
        "missing_values": int(ds[var].isnull().sum().item()),
        "total_values": int(ds[var].size)
    }

# Save to JSON
output_path = Path("data/profiles/era5land_ahmedabad_2010_03.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(profile, f, indent=2, default=str)

print(f'\nProfile saved to: {output_path}')

ds.close()
