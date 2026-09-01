"""Representative tests: 9 samples (3 day, 3 low-sun, 3 night)."""
import sys
sys.path.insert(0, ".")

import numpy as np
from thermofeel.thermofeel import calculate_mean_radiant_temperature
from scientific.thermal_comfort.mrt import calculate_mrt_single

cases = [
    {"name": "day_high_1", "ssrd": 783.16, "strd": 343.41, "fdir": 654.31,
     "ssr": 631.52, "str_val": -166.58, "lat": 23.0, "lon": 72.5, "hour": 6},
    {"name": "day_high_2", "ssrd": 700.0, "strd": 350.0, "fdir": 550.0,
     "ssr": 580.0, "str_val": -150.0, "lat": 23.0, "lon": 72.5, "hour": 7},
    {"name": "day_high_3", "ssrd": 600.0, "strd": 360.0, "fdir": 450.0,
     "ssr": 500.0, "str_val": -140.0, "lat": 23.0, "lon": 72.5, "hour": 8},
    {"name": "low_sun_1", "ssrd": 150.0, "strd": 330.0, "fdir": 80.0,
     "ssr": 120.0, "str_val": -170.0, "lat": 23.0, "lon": 72.5, "hour": 5},
    {"name": "low_sun_2", "ssrd": 100.0, "strd": 325.0, "fdir": 50.0,
     "ssr": 80.0, "str_val": -175.0, "lat": 23.0, "lon": 72.5, "hour": 5},
    {"name": "low_sun_3", "ssrd": 200.0, "strd": 335.0, "fdir": 120.0,
     "ssr": 160.0, "str_val": -165.0, "lat": 23.0, "lon": 72.5, "hour": 12},
    {"name": "night_1", "ssrd": 0.0, "strd": 320.0, "fdir": 0.0,
     "ssr": 0.0, "str_val": -80.0, "lat": 23.0, "lon": 72.5, "hour": 0},
    {"name": "night_2", "ssrd": 0.0, "strd": 315.0, "fdir": 0.0,
     "ssr": 0.0, "str_val": -85.0, "lat": 23.0, "lon": 72.5, "hour": 1},
    {"name": "night_3", "ssrd": 0.0, "strd": 310.0, "fdir": 0.0,
     "ssr": 0.0, "str_val": -90.0, "lat": 23.0, "lon": 72.5, "hour": 2},
]

print("REPRESENTATIVE TESTS (9 samples)")
print("=" * 100)
header = f"{'Name':15s} | {'elev':>6s} | {'cossza':>7s} | {'dsrp':>8s} | {'fp':>6s} | {'OURS':>8s} | {'TF':>8s} | {'Diff':>8s}"
print(header)
print("-" * 100)

all_pass = True
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
    status = "PASS" if diff < 0.001 else "FAIL"
    if diff >= 0.001:
        all_pass = False
    row = f"{c['name']:15s} | {ours.solar_elevation_deg:6.1f} | {ours.cossza:7.4f} | {ours.dsrp:8.2f} | {ours.f_p:6.4f} | {ours.mrt_kelvin:8.4f} | {tf_mrt:8.4f} | {diff:8.6f} | {status}"
    print(row)

print("=" * 100)
result = "YES" if all_pass else "NO"
print(f"All 9 samples consistent: {result}")
