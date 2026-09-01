import xarray as xr
import numpy as np
import hashlib
import sys

path = sys.argv[1]
ds = xr.open_dataset(path)
print("File:", path)

h = hashlib.sha256(open(path, "rb").read()).hexdigest()
print("SHA256:", h[:16])

print("Variables:", list(ds.data_vars))
print("Dims:", dict(ds.sizes))

for var in ds.data_vars:
    a = ds[var].attrs
    print(f"  {var}: units={a.get('units','?')} long_name={a.get('long_name','?')}")

if "valid_time" in ds.coords:
    t = ds.valid_time.values
    print(f"Time: {t[0]} -> {t[-1]} ({len(t)} steps)")
    dt = np.diff(t.astype("datetime64[h]").astype(int))
    print(f"Interval: {int(np.median(dt))} hours ({int(np.median(dt))*3600} s)")

if "latitude" in ds.coords:
    print(f"Lat: {ds.latitude.values}")
if "longitude" in ds.coords:
    print(f"Lon: {ds.longitude.values}")

# Check values for physical sanity
for var in ["ssrd", "ssr", "fdir", "strd", "str"]:
    if var in ds:
        vals = ds[var].values
        print(f"  {var} range: [{np.nanmin(vals):.2f}, {np.nanmax(vals):.2f}]")
ds.close()
