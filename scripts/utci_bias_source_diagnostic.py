"""Test: does ERA5-HEAT use a different wind speed height?"""
import sys
from pathlib import Path
import math
import numpy as np
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scientific.thermal_comfort.utci import _utci_polynomial, _saturated_vapour_pressure

ERA5_PATH = "53968a80e95eb41e9fe5c5f804eacbd8.nc"
HEAT_PATH = "cde4e619c080209e1ec505565f79b8e.nc"

ds_era5 = xr.open_dataset(ERA5_PATH)
ds_heat = xr.open_dataset(HEAT_PATH)

t_era5 = ds_era5.valid_time.values
mask = np.array([np.datetime64("2010-03-01") <= t <= np.datetime64("2010-03-31T23:59:59") for t in t_era5])
common_times = sorted(set(t_era5[mask]) & set(ds_heat.valid_time.values))

lat_era5 = ds_era5.latitude.values
lon_era5 = ds_era5.longitude.values
lat_heat = {float(lat): i for i, lat in enumerate(ds_heat.latitude.values)}
lon_heat = {float(lon): i for i, lon in enumerate(ds_heat.longitude.values)}
heat_time = {t: i for i, t in enumerate(ds_heat.valid_time.values)}
era5_time = {t: i for i, t in enumerate(ds_era5.valid_time.values)}

# Build arrays for regression analysis
ta_list, mrt_list, ws_list, pa_list = [], [], [], []
utci_agn_list, utci_ref_list = [], []

for t in common_times:
    i5 = era5_time[t]
    ih = heat_time[t]
    for ilat in range(len(lat_era5)):
        for ilon in range(len(lon_era5)):
            jlat = lat_heat[float(lat_era5[ilat])]
            jlon = lon_heat[float(lon_era5[ilon])]

            ta_k = float(ds_era5.t2m.values[i5, ilat, ilon])
            d2m_k = float(ds_era5.d2m.values[i5, ilat, ilon])
            u10 = float(ds_era5.u10.values[i5, ilat, ilon])
            v10 = float(ds_era5.v10.values[i5, ilat, ilon])
            mrt_k = float(ds_heat.mrt.values[ih, jlat, jlon])
            utci_ref_k = float(ds_heat.utci.values[ih, jlat, jlon])

            ta_c = ta_k - 273.15
            mrt_c = mrt_k - 273.15
            utci_ref_c = utci_ref_k - 273.15
            ws = math.sqrt(u10**2 + v10**2)
            if ws < 0.5:
                ws = 0.5
            dtt = mrt_c - ta_c
            pa = _saturated_vapour_pressure(d2m_k) / 10.0
            utci_agn = ta_c + _utci_polynomial(ta_c, ws, dtt, pa)

            ta_list.append(ta_c)
            mrt_list.append(mrt_c)
            ws_list.append(ws)
            pa_list.append(pa)
            utci_agn_list.append(utci_agn)
            utci_ref_list.append(utci_ref_c)

ds_era5.close()
ds_heat.close()

ta_arr = np.array(ta_list)
mrt_arr = np.array(mrt_list)
ws_arr = np.array(ws_list)
pa_arr = np.array(pa_list)
agn_arr = np.array(utci_agn_list)
ref_arr = np.array(utci_ref_list)
dtt_arr = mrt_arr - ta_arr
offset_agn = agn_arr - ta_arr  # Our polynomial offset
offset_ref = ref_arr - ta_arr  # ERA5-HEAT polynomial offset

print("=== Offset analysis (UTCI - Ta) ===")
print(f"Our offset:    mean={offset_agn.mean():.4f}, std={offset_agn.std():.4f}")
print(f"ERA5-HEAT offset: mean={offset_ref.mean():.4f}, std={offset_ref.std():.4f}")
print(f"Offset diff:   mean={(offset_agn - offset_ref).mean():.4f}, std={(offset_agn - offset_ref).std():.4f}")

print("\n=== Linear regression: offset_diff ~ f(dTT, ta, ws, pa) ===")
X = np.column_stack([np.ones(len(dtt_arr)), dtt_arr, ta_arr, ws_arr, pa_arr, 
                       dtt_arr**2, ta_arr**2, dtt_arr*ta_arr, dtt_arr*ws_arr, ta_arr*ws_arr])
y = offset_agn - offset_ref

# OLS
beta = np.linalg.lstsq(X, y, rcond=None)[0]
y_pred = X @ beta
ss_res = np.sum((y - y_pred)**2)
ss_tot = np.sum((y - y.mean())**2)
r2 = 1 - ss_res / ss_tot
rmse = np.sqrt(np.mean((y - y_pred)**2))

print(f"R-squared: {r2:.6f}")
print(f"RMSE of regression: {rmse:.6f}")
print(f"Coefficients: {dict(zip(['const','dTT','ta','ws','pa','dTT2','ta2','dTT*ta','dTT*ws','ta*ws'], beta))}")

# Now: what wind speed would make our offset match ERA5-HEAT?
print("\n=== Wind speed sensitivity ===")
# For the worst-case sample (18 UTC, dTT < -10):
idx_night = np.where((dtt_arr < -10) & (ta_arr > 25))[0]
if len(idx_night) > 0:
    print(f"Nighttime hot samples (dTT<-10, Ta>25): n={len(idx_night)}")
    print(f"  Mean bias: {np.mean(agn_arr[idx_night] - ref_arr[idx_night]):.3f}")
    print(f"  Mean Ta: {ta_arr[idx_night].mean():.1f}, MRT: {mrt_arr[idx_night].mean():.1f}, WS: {ws_arr[idx_night].mean():.3f}")
    
    # Try adjusting wind speed to reduce bias
    for ws_mult in [0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5]:
        biases = []
        for i in idx_night:
            ws_test = ws_arr[i] * ws_mult
            if ws_test < 0.5:
                ws_test = 0.5
            utci_test = ta_arr[i] + _utci_polynomial(ta_arr[i], ws_test, dtt_arr[i], pa_arr[i])
            biases.append(utci_test - ref_arr[i])
        print(f"  WS mult={ws_mult:.1f}: mean_bias={np.mean(biases):+.3f}")

# Same for daytime
idx_day = np.where(dtt_arr > 10)[0]
if len(idx_day) > 0:
    print(f"\nDaytime samples (dTT>10): n={len(idx_day)}")
    print(f"  Mean bias: {np.mean(agn_arr[idx_day] - ref_arr[idx_day]):.3f}")
    for ws_mult in [0.5, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.5]:
        biases = []
        for i in idx_day:
            ws_test = ws_arr[i] * ws_mult
            if ws_test < 0.5:
                ws_test = 0.5
            utci_test = ta_arr[i] + _utci_polynomial(ta_arr[i], ws_test, dtt_arr[i], pa_arr[i])
            biases.append(utci_test - ref_arr[i])
        print(f"  WS mult={ws_mult:.1f}: mean_bias={np.mean(biases):+.3f}")

# Try adjusting ta or mrt
print("\n=== Ta/MRT offset test ===")
for ta_offset in [-0.5, -0.3, -0.1, 0, 0.1, 0.3, 0.5]:
    biases = agn_arr - ref_arr
    # If Ta is offset, both Ta and dTT change
    for i in range(len(ta_arr)):
        ta_test = ta_arr[i] + ta_offset
        dtt_test = mrt_arr[i] - ta_test
        utci_test = ta_test + _utci_polynomial(ta_test, ws_arr[i], dtt_test, pa_arr[i])
        biases[i] = utci_test - ref_arr[i]
    print(f"  Ta offset={ta_offset:+.1f}: mean_bias={biases.mean():+.4f}")

for mrt_offset in [-0.5, -0.3, -0.1, 0, 0.1, 0.3, 0.5]:
    biases = agn_arr - ref_arr
    for i in range(len(ta_arr)):
        mrt_test = mrt_arr[i] + mrt_offset
        dtt_test = mrt_test - ta_arr[i]
        utci_test = ta_arr[i] + _utci_polynomial(ta_arr[i], ws_arr[i], dtt_test, pa_arr[i])
        biases[i] = utci_test - ref_arr[i]
    print(f"  MRT offset={mrt_offset:+.1f}: mean_bias={biases.mean():+.4f}")
