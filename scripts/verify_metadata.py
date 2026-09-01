"""Verify NetCDF metadata for accumulation period."""
import numpy as np
import xarray as xr

ds = xr.open_dataset("97c99a12bac0f84dae69bd5460cde459.nc")
print("=== NETCDF METADATA ===")
print("History:", ds.attrs.get("history", "N/A"))
print()
for var in ["ssrd", "strd", "fdir", "ssr", "str"]:
    v = ds[var]
    print(f"{var}:")
    print(f"  GRIB_stepUnits: {v.attrs.get('GRIB_stepUnits', 'N/A')}")
    print(f"  GRIB_stepType: {v.attrs.get('GRIB_stepType', 'N/A')}")
    print(f"  GRIB_dataType: {v.attrs.get('GRIB_dataType', 'N/A')}")
    print(f"  units: {v.attrs.get('units', 'N/A')}")
    print(f"  long_name: {v.attrs.get('long_name', 'N/A')}")
    print()

times = ds.valid_time.values
diffs = np.diff(times).astype("timedelta64[h]").astype(float)
print(f"Time range: {times[0]} to {times[-1]}")
print(f"N timestamps: {len(times)}")
print(f"Time step (hours): {np.unique(diffs)}")

# Check raw values at midnight for strd
t0_mask = ds.valid_time == times[0]
strd_raw = float(ds["strd"].sel(valid_time=t0_mask).values[0, 0, 0])
print(f"\nstrd raw at midnight: {strd_raw} J/m2")
print(f"  / 3600 = {strd_raw/3600:.1f} W/m2")
print(f"  / 21600 = {strd_raw/21600:.1f} W/m2")
print(f"  Expected strd for clear night: ~250-350 W/m2")
ds.close()
