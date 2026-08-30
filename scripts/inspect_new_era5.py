"""Inspect new ERA5 meteorology and ERA5-HEAT reference."""
import xarray as xr
import numpy as np

era5_path = "53968a80e95eb41e9fe5c5f804eacbd8.nc"
heat_path = "cde4e619c080209e1ec505565f79b8e.nc"

print("=== ERA5 METEOROLOGY ===")
ds = xr.open_dataset(era5_path)
print(f"Dims: {dict(ds.sizes)}")
print(f"Variables: {list(ds.data_vars)}")
for var in ds.data_vars:
    v = ds[var]
    units = v.attrs.get("units", "?")
    print(f"  {var}: units={units}, shape={v.shape}, dims={v.dims}")

if "time" in ds.coords:
    t = ds.time
    print(f"Time: {t.values[0]} to {t.values[-1]}, count={len(t)}")
elif "valid_time" in ds.coords:
    t = ds.valid_time
    print(f"Time: {t.values[0]} to {t.values[-1]}, count={len(t)}")

for c in ["latitude", "longitude", "lat", "lon"]:
    if c in ds.coords:
        v = ds[c]
        print(f"{c}: {float(v.min())} to {float(v.max())}, count={len(v)}")
ds.close()

print()
print("=== ERA5-HEAT REFERENCE ===")
heat = xr.open_dataset(heat_path)
print(f"Dims: {dict(heat.sizes)}")
print(f"Variables: {list(heat.data_vars)}")
for var in heat.data_vars:
    v = heat[var]
    units = v.attrs.get("units", "?")
    print(f"  {var}: units={units}, shape={v.shape}, dims={v.dims}")

if "valid_time" in heat.coords:
    t = heat.valid_time
    print(f"Time: {t.values[0]} to {t.values[-1]}, count={len(t)}")

for c in ["latitude", "longitude"]:
    if c in heat.coords:
        print(f"{c}: {heat[c].values}")

print(f"Global attrs: {dict(heat.attrs)}")
heat.close()
print("Done.")
