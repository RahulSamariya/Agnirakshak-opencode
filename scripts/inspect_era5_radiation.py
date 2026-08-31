"""Inspect ERA5 radiation NetCDF file for MRT methodology verification."""
import xarray as xr
import numpy as np
import json
import sys

RADIATION_PATH = "2b5663f2dae9337c125c5159b0f4ccce.nc"
ERASE5LAND_PATH = "data/raw/weather/data_0.nc"
ERA5HEAT_PATH = "cde4e619c080209e1ec505565f79b8e.nc"

REQUIRED_VARS = ["fdir", "ssr", "str"]

results = {
    "file": RADIATION_PATH,
    "variables_present": {},
    "required_variables_status": {},
    "time_analysis": {},
    "spatial_analysis": {},
    "comparison_with_era5land": {},
    "comparison_with_era5heat": {},
    "accumulation_analysis": {},
    "overall_status": "UNKNOWN"
}

print("=" * 70)
print("ERA5 RADIATION NETCDF INSPECTION")
print("=" * 70)

# Step 1: Open and inspect the radiation file
print(f"\n--- Opening: {RADIATION_PATH} ---")
try:
    ds = xr.open_dataset(RADIATION_PATH)
    print(f"Dimensions: {dict(ds.sizes)}")
    print(f"Coordinates: {list(ds.coords)}")
    print(f"Data variables: {list(ds.data_vars)}")
    print()

    # Check each variable
    all_required_present = True
    for var in REQUIRED_VARS:
        if var in ds.data_vars:
            v = ds[var]
            info = {
                "long_name": v.attrs.get("long_name", "N/A"),
                "units": v.attrs.get("units", "N/A"),
                "paramId": v.attrs.get("paramId", "N/A"),
                "step_type": v.attrs.get("cell_methods", "N/A"),
                "dimensions": list(v.dims),
                "shape": list(v.shape),
                "dtype": str(v.dtype),
                "min": float(v.min()),
                "max": float(v.max()),
                "missing_values": int(v.isnull().sum()),
                "total_values": int(v.size),
            }
            results["variables_present"][var] = info
            results["required_variables_status"][var] = "PRESENT"

            print(f"  {var}:")
            print(f"    long_name: {info['long_name']}")
            print(f"    units: {info['units']}")
            print(f"    paramId: {info['paramId']}")
            print(f"    step_type: {info['step_type']}")
            print(f"    dimensions: {info['dimensions']}")
            print(f"    shape: {info['shape']}")
            print(f"    dtype: {info['dtype']}")
            print(f"    min: {info['min']}")
            print(f"    max: {info['max']}")
            print(f"    missing_values: {info['missing_values']}")
            print(f"    total_values: {info['total_values']}")
            print()
        else:
            results["required_variables_status"][var] = "MISSING"
            all_required_present = False
            print(f"  {var}: NOT PRESENT IN FILE")
            print()

    # Time analysis
    if "time" in ds.coords:
        t = ds.time
    elif "valid_time" in ds.coords:
        t = ds.valid_time
    else:
        t = None

    if t is not None:
        time_vals = t.values
        time_analysis = {
            "time_min": str(time_vals[0]),
            "time_max": str(time_vals[-1]),
            "timestamp_count": len(time_vals),
        }
        # Calculate time interval
        if len(time_vals) > 1:
            diffs = np.diff(time_vals.astype("datetime64[h]").astype(int))
            unique_diffs = np.unique(diffs)
            time_analysis["time_interval_hours"] = [int(d) for d in unique_diffs]
            time_analysis["is_regular"] = len(unique_diffs) == 1

        results["time_analysis"] = time_analysis
        print(f"  Time range: {time_analysis['time_min']} to {time_analysis['time_max']}")
        print(f"  Timestamps: {time_analysis['timestamp_count']}")
        if "time_interval_hours" in time_analysis:
            print(f"  Time interval: {time_analysis['time_interval_hours']} hours")
        print()

    # Spatial analysis
    lat = ds.latitude if "latitude" in ds.coords else ds.lat if "lat" in ds.coords else None
    lon = ds.longitude if "longitude" in ds.coords else ds.lon if "lon" in ds.coords else None

    spatial = {}
    if lat is not None:
        spatial["latitude_min"] = float(lat.min())
        spatial["latitude_max"] = float(lat.max())
        spatial["latitude_count"] = len(lat)
        if len(lat) > 1:
            spatial["latitude_resolution"] = float(abs(lat[1] - lat[0]))
    if lon is not None:
        spatial["longitude_min"] = float(lon.min())
        spatial["longitude_max"] = float(lon.max())
        spatial["longitude_count"] = len(lon)
        if len(lon) > 1:
            spatial["longitude_resolution"] = float(abs(lon[1] - lon[0]))

    results["spatial_analysis"] = spatial
    print(f"  Latitude: {spatial.get('latitude_min', 'N/A')} to {spatial.get('latitude_max', 'N/A')}, count={spatial.get('latitude_count', 'N/A')}")
    print(f"  Longitude: {spatial.get('longitude_min', 'N/A')} to {spatial.get('longitude_max', 'N/A')}, count={spatial.get('longitude_count', 'N/A')}")
    if "latitude_resolution" in spatial:
        print(f"  Resolution: ~{spatial['latitude_resolution']:.2f} deg")
    print()

    # Print all global attributes
    print("  Global attributes:")
    for k, v in ds.attrs.items():
        print(f"    {k}: {v}")
    print()

    # Print variable-level attributes for all variables
    print("  All variable attributes:")
    for var in ds.data_vars:
        v = ds[var]
        print(f"    {var}:")
        for k, val in v.attrs.items():
            print(f"      {k}: {val}")
    print()

    ds.close()

except Exception as e:
    print(f"ERROR opening radiation file: {e}")
    results["overall_status"] = "FILE_ERROR"
    sys.exit(1)

# Step 2: Compare with ERA5-Land
print("--- Comparison with ERA5-Land (data_0.nc) ---")
try:
    ds_land = xr.open_dataset(ERASE5LAND_PATH)

    land_time = ds_land.time if "time" in ds_land.coords else ds_land.valid_time
    land_lat = ds_land.latitude
    land_lon = ds_land.longitude

    comparison_land = {
        "era5land_time_min": str(land_time.values[0]),
        "era5land_time_max": str(land_time.values[-1]),
        "era5land_timestamp_count": len(land_time),
        "era5land_lat_range": [float(land_lat.min()), float(land_lat.max())],
        "era5land_lon_range": [float(land_lon.min()), float(land_lon.max())],
        "era5land_variables": list(ds_land.data_vars),
    }
    results["comparison_with_era5land"] = comparison_land

    print(f"  ERA5-Land time: {comparison_land['era5land_time_min']} to {comparison_land['era5land_time_max']}")
    print(f"  ERA5-Land timestamps: {comparison_land['era5land_timestamp_count']}")
    print(f"  ERA5-Land lat: {comparison_land['era5land_lat_range']}")
    print(f"  ERA5-Land lon: {comparison_land['era5land_lon_range']}")
    print(f"  ERA5-Land variables: {comparison_land['era5land_variables']}")
    print()

    ds_land.close()
except Exception as e:
    print(f"ERROR comparing with ERA5-Land: {e}")

# Step 3: Compare with ERA5-HEAT
print("--- Comparison with ERA5-HEAT reference ---")
try:
    ds_heat = xr.open_dataset(ERA5HEAT_PATH)

    heat_time = ds_heat.valid_time if "valid_time" in ds_heat.coords else ds_heat.time
    heat_lat = ds_heat.latitude
    heat_lon = ds_heat.longitude

    comparison_heat = {
        "era5heat_time_min": str(heat_time.values[0]),
        "era5heat_time_max": str(heat_time.values[-1]),
        "era5heat_timestamp_count": len(heat_time),
        "era5heat_lat_range": [float(heat_lat.min()), float(heat_lat.max())],
        "era5heat_lon_range": [float(heat_lon.min()), float(heat_lon.max())],
        "era5heat_variables": list(ds_heat.data_vars),
    }
    results["comparison_with_era5heat"] = comparison_heat

    print(f"  ERA5-HEAT time: {comparison_heat['era5heat_time_min']} to {comparison_heat['era5heat_time_max']}")
    print(f"  ERA5-HEAT timestamps: {comparison_heat['era5heat_timestamp_count']}")
    print(f"  ERA5-HEAT lat: {comparison_heat['era5heat_lat_range']}")
    print(f"  ERA5-HEAT lon: {comparison_heat['era5heat_lon_range']}")
    print(f"  ERA5-HEAT variables: {comparison_heat['era5heat_variables']}")
    print()

    ds_heat.close()
except Exception as e:
    print(f"ERROR comparing with ERA5-HEAT: {e}")

# Step 4: Accumulation analysis
print("--- Accumulation Period Analysis ---")
# Re-open radiation file to check step_type more carefully
try:
    ds2 = xr.open_dataset(RADIATION_PATH)
    for var in REQUIRED_VARS:
        if var in ds2.data_vars:
            v = ds2[var]
            step_type = v.attrs.get("cell_methods", "N/A")
            accum = v.attrs.get("accumulation_period", "N/A")
            results["accumulation_analysis"][var] = {
                "cell_methods": step_type,
                "accumulation_period": accum,
                "all_attrs": dict(v.attrs)
            }
            print(f"  {var}: cell_methods={step_type}, accumulation_period={accum}")
    ds2.close()
except Exception as e:
    print(f"ERROR in accumulation analysis: {e}")

# Determine overall status
if all_required_present:
    results["overall_status"] = "ERA5 RADIATION INPUTS VERIFIED"
else:
    missing = [v for v, s in results["required_variables_status"].items() if s == "MISSING"]
    results["overall_status"] = f"ERA5 RADIATION INPUTS INCOMPLETE - missing: {', '.join(missing)}"

print()
print("=" * 70)
print(f"FINAL STATUS: {results['overall_status']}")
print("=" * 70)

# Save JSON profile
with open("data/profiles/era5_radiation_input_verification_v1.json", "w") as f:
    json.dump(results, f, indent=2, default=str)
print(f"\nJSON profile saved to: data/profiles/era5_radiation_input_verification_v1.json")
