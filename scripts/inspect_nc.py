import xarray as xr
import sys

path = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\DELL\Desktop\Agnirakshak opencode\53968a80e95eb41e9fe5c5f804eacbd8.nc"
ds = xr.open_dataset(path)
print("File:", path)
print("Variables:", list(ds.data_vars))
print("Dimensions:", dict(ds.dims))
print("Coords:", list(ds.coords))
print()
for var in ds.data_vars:
    a = ds[var].attrs
    print(f"  {var}: units={a.get('units','?')} paramId={a.get('paramId','?')} stepType={a.get('stepType','?')} name={a.get('long_name','?')}")
print()
print("Time range:", ds.time.values[0], "->", ds.time.values[-1], f"({len(ds.time)} steps)")
if "latitude" in ds.coords:
    print("Latitude:", ds.latitude.values)
if "longitude" in ds.coords:
    print("Longitude:", ds.longitude.values)
if "lat" in ds.coords:
    print("Lat:", ds.lat.values)
if "lon" in ds.coords:
    print("Lon:", ds.lon.values)
ds.close()
