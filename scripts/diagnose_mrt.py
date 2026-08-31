"""Diagnose the MRT discrepancy."""
import xarray as xr
import numpy as np

ds_rad = xr.open_dataset("2b5663f2dae9337c125c5159b0f4ccce.nc")
ds_land = xr.open_dataset("data/raw/weather/data_0.nc")
ds_heat = xr.open_dataset("cde4e619c080209e1ec505565f79b8e.nc")

t_idx = 10

# ERA5-Land at (23.0, 72.5)
land_lat_idx = np.argmin(np.abs(ds_land.latitude.values - 23.0))
land_lon_idx = np.argmin(np.abs(ds_land.longitude.values - 72.5))

# ERA5 Radiation at (23.0, 72.5)
rad_lat_idx = np.argmin(np.abs(ds_rad.latitude.values - 23.0))
rad_lon_idx = np.argmin(np.abs(ds_rad.longitude.values - 72.5))

# ERA5-HEAT at (23.0, 72.5)
heat_lat_idx = np.argmin(np.abs(ds_heat.latitude.values - 23.0))
heat_lon_idx = np.argmin(np.abs(ds_heat.longitude.values - 72.5))

accum = 21600

ssrd = float(ds_land["ssrd"].values[t_idx, land_lat_idx, land_lon_idx]) / accum
strd = float(ds_land["strd"].values[t_idx, land_lat_idx, land_lon_idx]) / accum
fdir = float(ds_rad["fdir"].values[t_idx, rad_lat_idx, rad_lon_idx]) / accum
ssr = float(ds_rad["ssr"].values[t_idx, rad_lat_idx, rad_lon_idx]) / accum
str_val = float(ds_rad["str"].values[t_idx, rad_lat_idx, rad_lon_idx]) / accum

heat_t_idx = np.argmin(np.abs(ds_heat.valid_time.values - ds_land.valid_time.values[t_idx]))
heat_mrt = float(ds_heat["mrt"].values[heat_t_idx, heat_lat_idx, heat_lon_idx])

print("=== RADIATION VALUES (W/m2) ===")
print(f"ssrd = {ssrd:.2f}")
print(f"strd = {strd:.2f}")
print(f"fdir = {fdir:.2f}")
print(f"ssr  = {ssr:.2f}")
print(f"str  = {str_val:.2f}")
print(f"ERA5-HEAT MRT = {heat_mrt:.2f} K")

# Check if ssr is from ERA5 single levels (different from ERA5-Land ssrd)
print("\n=== ALBEDO CHECK ===")
if ssrd > 0:
    albedo_net = (ssrd - ssr) / ssrd
    print(f"Net shortwave albedo = {albedo_net:.3f} ({albedo_net*100:.1f}%)")
    print(f"If ssr is NET: albedo = 1 - ssr/ssrd = {1 - ssr/ssrd:.3f}")

# The key insight: ssrd (from ERA5-Land) and ssr (from ERA5 single levels)
# are from DIFFERENT datasets. The ssr at this grid point might represent
# a different area average than ssrd.

# Let's check if using only ERA5 single levels variables would work better
# We don't have ssrd and strd from ERA5 single levels in this file

# What if we COMPUTE ssrd from the other variables?
# ssrd = ssr + S_srf_up
# But we don't know S_srf_up independently

# The fundamental issue: we need ALL 5 radiation variables from the SAME source
print("\n=== DIAGNOSIS ===")
print("The Di Napoli method requires 5 radiation variables from the SAME source:")
print("  ssrd, strd, fdir, ssr, str")
print()
print("We have:")
print("  ssrd, strd from ERA5-Land (0.1 deg)")
print("  fdir, ssr, str from ERA5 single levels (0.25 deg)")
print()
print("These are from DIFFERENT datasets and the values are not consistent.")
print("This causes the MRT calculation to produce incorrect results.")
print()
print("SOLUTION: Download all 5 variables from ERA5 single levels.")

# Alternative: what if we use ONLY the variables from ERA5 single levels?
# We can compute:
#   L_srf_up = strd - str (but strd is from ERA5-Land)
#   S_diffuse = ssrd - fdir (but ssrd is from ERA5-Land)
#   S_srf_up = ssrd - ssr (but ssrd is from ERA5-Land)

# We're stuck because we need ssrd and strd from the same source as fdir, ssr, str

ds_rad.close()
ds_land.close()
ds_heat.close()
