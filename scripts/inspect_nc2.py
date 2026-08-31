import xarray as xr
import sys
import hashlib

path = sys.argv[1]
ds = xr.open_dataset(path)
print("File:", path)

# hash
with open(path, "rb") as f:
    h = hashlib.md5(f.read()).hexdigest()
print("MD5:", h)

print("Variables:", list(ds.data_vars))
print("Dimensions:", dict(ds.sizes))
print()

for var in ds.data_vars:
    a = ds[var].attrs
    print(f"  {var}: units={a.get('units','?')} stepType={a.get('stepType','?')} long_name={a.get('long_name','?')}")

print()
# Time
if "valid_time" in ds.coords:
    t = ds.valid_time.values
    print(f"Time: {t[0]} -> {t[-1]} ({len(t)} steps)")
    # Show first few and gaps
    if len(t) > 4:
        diffs = [(t[i+1] - t[i]) for i in range(min(5, len(t)-1))]
        print(f"  First diffs: {diffs}")

# Coordinates
for coord_name in ["latitude", "longitude", "lat", "lon"]:
    if coord_name in ds.coords:
        print(f"{coord_name}: {ds[coord_name].values}")

ds.close()
