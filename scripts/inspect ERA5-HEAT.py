"""Inspect ERA5-HEAT NetCDF file."""
import xarray as xr
import json

# ERA5-HEAT
heat_path = "cde4e619c080209e1ec505565f79b8e.nc"
ds = xr.open_dataset(heat_path)

print("=== ERA5-HEAT METADATA ===")
print(f"Dimensions: {dict(ds.dims)}")
print(f"Variables: {list(ds.data_vars)}")
print(f"Coordinates: {list(ds.coords)}")
print()

for var in ds.data_vars:
    v = ds[var]
    print(f"Variable: {var}")
    print(f"  Shape: {v.shape}")
    print(f"  Dims: {v.dims}")
    print(f"  Units: {v.attrs.get('units', 'N/A')}")
    print(f"  Long name: {v.attrs.get('long_name', 'N/A')}")
    print(f"  Missing value: {v.attrs.get('_FillValue', 'N/A')}")
    print(f"  Min: {float(v.min())}")
    print(f"  Max: {float(v.max())}")
    print(f"  Mean: {float(v.mean())}")
    print()

# Time info
if 'time' in ds.coords:
    t = ds.time
    print(f"Time range: {t.values[0]} to {t.values[-1]}")
    print(f"Time count: {len(t)}")
    print(f"Time attrs: {dict(t.attrs)}")
    print(f"Time dtype: {t.dtype}")
print()

# Lat/Lon info
if 'latitude' in ds.coords:
    lat = ds.latitude
    print(f"Latitude range: {float(lat.min())} to {float(lat.max())}")
    print(f"Latitude count: {len(lat)}")
    print(f"Latitude attrs: {dict(lat.attrs)}")
if 'longitude' in ds.coords:
    lon = ds.longitude
    print(f"Longitude range: {float(lon.min())} to {float(lon.max())}")
    print(f"Longitude count: {len(lon)}")
    print(f"Longitude attrs: {dict(lon.attrs)}")
print()

# Global attrs
print(f"Global attrs: {dict(ds.attrs)}")
print()
print(f"Data types: {dict(ds.dtypes)}")

# Save summary
summary = {
    "file": heat_path,
    "dimensions": dict(ds.dims),
    "variables": list(ds.data_vars),
    "coordinates": list(ds.coords),
}
for var in ds.data_vars:
    v = ds[var]
    summary[var] = {
        "shape": list(v.shape),
        "dims": list(v.dims),
        "units": v.attrs.get("units", "N/A"),
        "long_name": v.attrs.get("long_name", "N/A"),
        "fill_value": str(v.attrs.get("_FillValue", "N/A")),
        "min": float(v.min()),
        "max": float(v.max()),
        "mean": float(v.mean()),
    }

if 'time' in ds.coords:
    summary["time"] = {
        "start": str(ds.time.values[0]),
        "end": str(ds.time.values[-1]),
        "count": len(ds.time),
        "units": ds.time.attrs.get("units", "N/A"),
        "calendar": ds.time.attrs.get("calendar", "N/A"),
    }
if 'latitude' in ds.coords:
    summary["latitude"] = {
        "min": float(ds.latitude.min()),
        "max": float(ds.latitude.max()),
        "count": len(ds.latitude),
    }
if 'longitude' in ds.coords:
    summary["longitude"] = {
        "min": float(ds.longitude.min()),
        "max": float(ds.longitude.max()),
        "count": len(ds.longitude),
    }

with open("data/profiles/era5_heat_inspection.json", "w") as f:
    json.dump(summary, f, indent=2)

ds.close()
print("Done.")
