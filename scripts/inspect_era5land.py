"""Inspect ERA5-Land data_0.nc variables for MRT gap analysis."""
import xarray as xr

ds = xr.open_dataset("data/raw/weather/data_0.nc")
print("Variables:", list(ds.data_vars))
print("Dims:", dict(ds.sizes))
print()

for var in ds.data_vars:
    v = ds[var]
    print(f"{var}:")
    print(f"  long_name: {v.attrs.get('long_name', 'N/A')}")
    print(f"  units: {v.attrs.get('units', 'N/A')}")
    print(f"  shape: {v.shape}")
    print(f"  dtype: {v.dtype}")
    for k in ['GRIB_name', 'GRIB_shortName', 'GRIB_paramId', 'GRIB_stepType', 'GRIB_typeOfLevel']:
        if k in v.attrs:
            print(f"  {k}: {v.attrs[k]}")
    print()

# Check global attrs
print("Global attributes:")
for k, v in ds.attrs.items():
    print(f"  {k}: {v}")

ds.close()
