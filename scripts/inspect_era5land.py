"""Inspect ERA5-Land NetCDF."""
import xarray as xr

ds = xr.open_dataset("data/raw/weather/data_0.nc")
print("=== ERA5-Land ===")
print(f"Dimensions: {dict(ds.sizes)}")
print(f"Variables: {list(ds.data_vars)}")
print(f"Coordinates: {list(ds.coords)}")
for var in ds.data_vars:
    v = ds[var]
    units = v.attrs.get("units", "N/A")
    print(f"  {var}: shape={v.shape}, units={units}, dims={v.dims}")
if "time" in ds.coords:
    t = ds.time
    print(f"Time: {t.values[0]} to {t.values[-1]}, count={len(t)}")
if "latitude" in ds.coords:
    lat = ds.latitude
    print(f"Lat: {float(lat.min())} to {float(lat.max())}, count={len(lat)}")
if "longitude" in ds.coords:
    lon = ds.longitude
    print(f"Lon: {float(lon.min())} to {float(lon.max())}, count={len(lon)}")
ds.close()
