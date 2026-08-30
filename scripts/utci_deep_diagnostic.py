"""Deep diagnostic: check MRT, wind, and per-variable sensitivity."""
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

# Check MRT variable attributes
print("=== ERA5-HEAT MRT variable attributes ===")
mrt_var = ds_heat["mrt"]
for k, v in mrt_var.attrs.items():
    print(f"  {k}: {v}")
print(f"  dtype: {mrt_var.dtype}")
print(f"  shape: {mrt_var.shape}")
print(f"  valid_range: {float(mrt_var.min())} to {float(mrt_var.max())}")

print("\n=== ERA5-HEAT UTCI variable attributes ===")
utci_var = ds_heat["utci"]
for k, v in utci_var.attrs.items():
    print(f"  {k}: {v}")

# Check for fill values or scaling
print(f"\nMRT first value: {float(mrt_var.values[0, 0, 0])}")
print(f"UTCI first value: {float(utci_var.values[0, 0, 0])}")

# Check all time values in heat
print(f"\nERA5-HEAT time range: {ds_heat.valid_time.values[0]} to {ds_heat.valid_time.values[-1]}")
print(f"ERA5-HEAT time count: {len(ds_heat.valid_time.values)}")

# Check if there are NaN patterns
mrt_all = mrt_var.values
utci_all = utci_var.values
print(f"\nMRT NaN count: {np.isnan(mrt_all).sum()}")
print(f"UTCI NaN count: {np.isnan(utci_all).sum()}")
print(f"MRT fill value count: {(mrt_all < -1e30).sum()}")
print(f"UTCI fill value count: {(utci_all < -1e30).sum()}")

# Check specific time: March 1, 2010 00:00
t0 = np.datetime64("2010-03-01T00:00:00")
ih0 = heat_time[t0]
print(f"\n=== Sample at 2010-03-01 00:00 ===")
for jlat in range(3):
    for jlon in range(4):
        m = float(mrt_var.values[ih0, jlat, jlon])
        u = float(utci_var.values[ih0, jlat, jlon])
        print(f"  lat={ds_heat.latitude.values[jlat]}, lon={ds_heat.longitude.values[jlon]}: MRT={m:.2f} K ({m-273.15:.2f} C), UTCI={u:.2f} K ({u-273.15:.2f} C)")

# Per-sample deep dive: check delta_t_tr vs UTCI relationship
print("\n=== Per-sample analysis (top 20 biases) ===")
samples = []
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
            ws_clamped = max(ws, 0.5)
            dtt = mrt_c - ta_c
            pa = _saturated_vapour_pressure(d2m_k) / 10.0
            utci_agn = ta_c + _utci_polynomial(ta_c, ws_clamped, dtt, pa)
            bias = utci_agn - utci_ref_c

            samples.append({
                "t": str(t), "lat": float(lat_era5[ilat]), "lon": float(lon_era5[ilon]),
                "ta": ta_c, "mrt": mrt_c, "ws": ws, "dtt": dtt, "pa": pa,
                "utci_agn": utci_agn, "utci_ref": utci_ref_c, "bias": bias
            })

ds_era5.close()
ds_heat.close()

samples.sort(key=lambda x: abs(x["bias"]), reverse=True)
print(f"{'Ta':>6} {'MRT':>6} {'WS':>6} {'dTT':>6} {'pa':>6} {'UTCI_agn':>9} {'UTCI_ref':>9} {'bias':>7}  time")
for s in samples[:20]:
    print(f"{s['ta']:6.1f} {s['mrt']:6.1f} {s['ws']:6.3f} {s['dtt']:6.1f} {s['pa']:6.3f} {s['utci_agn']:9.2f} {s['utci_ref']:9.2f} {s['bias']:+7.2f}  {s['t']}")

# Check bias by time of day
print("\n=== Bias by UTC hour ===")
from collections import defaultdict
hour_biases = defaultdict(list)
for s in samples:
    hour = int(s["t"].split("T")[1].split(":")[0])
    hour_biases[hour].append(s["bias"])

for h in sorted(hour_biases.keys()):
    arr = np.array(hour_biases[h])
    print(f"  {h:02d} UTC: n={len(arr):4d}, bias={np.mean(arr):+.3f}, std={np.std(arr):.3f}, MAE={np.mean(np.abs(arr)):.3f}")

# Check bias by grid point
print("\n=== Bias by grid point ===")
grid_biases = defaultdict(list)
for s in samples:
    key = f"({s['lat']:.2f}, {s['lon']:.2f})"
    grid_biases[key].append(s["bias"])

for g in sorted(grid_biases.keys()):
    arr = np.array(grid_biases[g])
    print(f"  {g}: n={len(arr):4d}, bias={np.mean(arr):+.3f}, std={np.std(arr):.3f}")

# Check bias by dTT range
print("\n=== Bias by delta_t_tr range ===")
dtt_ranges = [
    ("dTT < -15", lambda s: s["dtt"] < -15),
    ("-15 <= dTT < -5", lambda s: -15 <= s["dtt"] < -5),
    ("-5 <= dTT < 5", lambda s: -5 <= s["dtt"] < 5),
    ("5 <= dTT < 15", lambda s: 5 <= s["dtt"] < 15),
    ("dTT >= 15", lambda s: s["dtt"] >= 15),
]
for label, cond in dtt_ranges:
    arr = np.array([s["bias"] for s in samples if cond(s)])
    if len(arr) > 0:
        print(f"  {label:20s}: n={len(arr):4d}, bias={np.mean(arr):+.3f}, MAE={np.mean(np.abs(arr)):.3f}")
