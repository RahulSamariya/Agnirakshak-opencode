"""Numerical parity test: Our MRT vs Thermofeel."""
import sys
sys.path.insert(0, ".")

import math
import numpy as np
from thermofeel.thermofeel import calculate_mean_radiant_temperature
from scientific.thermal_comfort.mrt import calculate_mrt_single

cases = [
    {"name": "daytime_high_sun", "ssrd": 783.16, "strd": 343.41, "fdir": 654.31,
     "ssr": 631.52, "str_val": -166.58, "lat": 23.0, "lon": 72.5, "hour": 6},
    {"name": "daytime_mid_sun", "ssrd": 500.0, "strd": 350.0, "fdir": 400.0,
     "ssr": 450.0, "str_val": -150.0, "lat": 23.0, "lon": 72.5, "hour": 8},
    {"name": "low_sun", "ssrd": 100.0, "strd": 330.0, "fdir": 50.0,
     "ssr": 80.0, "str_val": -170.0, "lat": 23.0, "lon": 72.5, "hour": 5},
    {"name": "nighttime", "ssrd": 0.0, "strd": 320.0, "fdir": 0.0,
     "ssr": 0.0, "str_val": -80.0, "lat": 23.0, "lon": 72.5, "hour": 0},
    {"name": "high_latitude", "ssrd": 300.0, "strd": 310.0, "fdir": 200.0,
     "ssr": 250.0, "str_val": -120.0, "lat": 65.0, "lon": 25.0, "hour": 10},
]

print("NUMERICAL PARITY TEST: Ours vs Thermofeel")
print("=" * 80)
max_diff = 0.0
diffs = []

for c in cases:
    t = np.datetime64(f"2010-03-01T{c['hour']:02d}:00:00")
    ours = calculate_mrt_single(
        ssrd=c["ssrd"], strd=c["strd"], fdir=c["fdir"],
        ssr=c["ssr"], str_val=c["str_val"],
        latitude_deg=c["lat"], longitude_deg=c["lon"],
        time_utc=t, accumulation_seconds=3600.0,
    )
    tf_mrt = calculate_mean_radiant_temperature(
        ssrd=np.array([c["ssrd"]]),
        ssr=np.array([c["ssr"]]),
        dsrp=np.array([ours.dsrp]),
        strd=np.array([c["strd"]]),
        fdir=np.array([c["fdir"]]),
        strr=np.array([c["str_val"]]),
        cossza=np.array([ours.cossza]),
    )[0]
    diff = abs(ours.mrt_kelvin - tf_mrt)
    diffs.append(diff)
    max_diff = max(max_diff, diff)
    status = "PASS" if diff < 0.001 else "FAIL"
    print(f"{c['name']:20s} | Ours: {ours.mrt_kelvin:.4f} K | TF: {tf_mrt:.4f} K | Diff: {diff:.6f} K | {status}")

print("=" * 80)
print(f"Max absolute difference: {max_diff:.6f} K")
print(f"Median absolute difference: {np.median(diffs):.6f} K")
print(f"P95 absolute difference: {np.percentile(diffs, 95):.6f} K")
if max_diff < 0.001:
    print("EXACT PARITY ACHIEVED")
else:
    print("PARITY NOT YET ACHIEVED")
