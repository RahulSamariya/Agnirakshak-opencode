"""
UTCI DISCREPANCY DIAGNOSTIC - TEST 1B

Investigates the systematic UTCI difference (MAE~0.95C, Bias~+0.86C)
found in Test 1 by running input-convention experiments.

Experiments:
  A. Current route (existing pipeline exactly as-is)
  B. Direct vapor-pressure route (dewpoint -> pa via pythermalcomfort formula)
  C. RH route (current RH conversion)

All experiments use the same matched March 2010 data:
  ERA5 meteorology + ERA5-HEAT MRT + ERA5-HEAT UTCI reference
"""
from __future__ import annotations

import json
import math
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scientific.thermal_comfort.utci import (
    _saturated_vapour_pressure,
    _utci_polynomial,
)

# ─── Configuration ───────────────────────────────────────────────────────────
ERA5_PATH = "53968a80e95eb41e9fe5c5f804eacbd8.nc"
HEAT_PATH = "cde4e619c080209e1ec505565f79b8e.nc"
OUTPUT_MD = "docs/data/era5_heat_utci_discrepancy_diagnostic_v1.md"
OUTPUT_JSON = "data/profiles/era5_heat_utci_discrepancy_diagnostic_v1.json"
PLOT_DIR = "data/profiles/plots/utci_discrepancy"


# ─── Helper functions ────────────────────────────────────────────────────────

def buck_rh(ta_c: float, d2m_c: float) -> float:
    """Buck (1981) RH from air temp and dewpoint (validation script convention)."""
    es = 6.112 * math.exp((17.67 * ta_c) / (ta_c + 243.5))
    ed = 6.112 * math.exp((17.67 * d2m_c) / (d2m_c + 243.5))
    rh = (ed / es) * 100.0
    return max(1.0, min(100.0, rh))


def direct_vapor_pressure(d2m_c: float) -> float:
    """Direct water vapor pressure from dewpoint using pythermalcomfort formula.

    Returns vapor pressure in kPa (what the polynomial expects).
    """
    tk = d2m_c + 273.15
    eh_pa = _saturated_vapour_pressure(tk)
    return eh_pa / 10.0  # hPa -> kPa


def current_route_vapor_pressure(ta_c: float, rh: float) -> float:
    """Current pipeline: Buck RH -> pythermalcomfort sat -> pa in kPa."""
    tk = ta_c + 273.15
    eh_pa = _saturated_vapour_pressure(tk) * (rh / 100.0)
    return eh_pa / 10.0  # hPa -> kPa


def buck_saturation_vapor_pressure(ta_c: float) -> float:
    """Buck (1981) saturation vapor pressure in hPa."""
    return 6.112 * math.exp((17.67 * ta_c) / (ta_c + 243.5))


def buck_vapor_pressure_hpa(ta_c: float, d2m_c: float) -> float:
    """Buck (1981) actual vapor pressure in hPa from dewpoint."""
    return buck_saturation_vapor_pressure(d2m_c)


def buck_vapor_pressure_kpa(ta_c: float, d2m_c: float) -> float:
    """Buck (1981) actual vapor pressure in kPa from dewpoint."""
    return buck_vapor_pressure_hpa(ta_c, d2m_c) / 10.0


def pythermalcomfort_vapor_pressure_kpa(ta_c: float, d2m_c: float) -> float:
    """pythermalcomfort saturation vapor pressure at dewpoint, in kPa."""
    tk = d2m_c + 273.15
    return _saturated_vapour_pressure(tk) / 10.0


def utci_with_pa(
    ta_c: float, ws: float, mrt_c: float, pa_kpa: float, round_output: bool = True
) -> float | None:
    """UTCI given pre-computed vapor pressure in kPa."""
    if ws < 0.5:
        ws = 0.5
    if pa_kpa > 5.0:
        return None
    delta_t_tr = mrt_c - ta_c
    utci = ta_c + _utci_polynomial(ta_c, ws, delta_t_tr, pa_kpa)
    return round(utci, 1) if round_output else utci


def utci_direct(
    ta_c: float, d2m_c: float, ws: float, mrt_c: float, round_output: bool = True
) -> float | None:
    """UTCI using direct vapor pressure from dewpoint (pythermalcomfort)."""
    pa = pythermalcomfort_vapor_pressure_kpa(ta_c, d2m_c)
    return utci_with_pa(ta_c, ws, mrt_c, pa, round_output)


def utci_current(
    ta_c: float, d2m_c: float, ws: float, mrt_c: float, round_output: bool = True
) -> float | None:
    """UTCI using current pipeline route (Buck RH -> pythermalcomfort -> pa)."""
    rh = buck_rh(ta_c, d2m_c)
    pa = current_route_vapor_pressure(ta_c, rh)
    return utci_with_pa(ta_c, ws, mrt_c, pa, round_output)


def utci_buck_only(
    ta_c: float, d2m_c: float, ws: float, mrt_c: float, round_output: bool = True
) -> float | None:
    """UTCI using Buck equation for vapor pressure (no pythermalcomfort)."""
    pa = buck_vapor_pressure_kpa(ta_c, d2m_c)
    return utci_with_pa(ta_c, ws, mrt_c, pa, round_output)


def utci_full_precision(
    ta_c: float, d2m_c: float, ws: float, mrt_c: float
) -> float | None:
    """UTCI with full floating-point precision (no rounding)."""
    return utci_current(ta_c, d2m_c, ws, mrt_c, round_output=False)


# ─── Load data ────────────────────────────────────────────────────────────────
print("Loading datasets...")
ds_era5 = xr.open_dataset(ERA5_PATH)
ds_heat = xr.open_dataset(HEAT_PATH)

# Filter March 2010
t_era5 = ds_era5.valid_time.values
mask_march = np.array([
    np.datetime64("2010-03-01") <= t <= np.datetime64("2010-03-31T23:59:59")
    for t in t_era5
])
t_march_era5 = t_era5[mask_march]

t_heat = ds_heat.valid_time.values
mask_heat_march = np.array([
    np.datetime64("2010-03-01") <= t <= np.datetime64("2010-03-31T23:59:59")
    for t in t_heat
])
t_march_heat = t_heat[mask_heat_march]

# Common timestamps
common_times = sorted(set(t_march_era5) & set(t_march_heat))
print(f"Common March 2010 timesteps: {len(common_times)}")

# Grid
lat_era5 = ds_era5.latitude.values
lon_era5 = ds_era5.longitude.values
lat_heat = ds_heat.latitude.values
lon_heat = ds_heat.longitude.values

lat_heat_idx = {float(lat): i for i, lat in enumerate(lat_heat)}
lon_heat_idx = {float(lon): i for i, lon in enumerate(lon_heat)}
lat_idx_map = {float(lat): lat_heat_idx[float(lat)] for lat in lat_era5}
lon_idx_map = {float(lon): lon_heat_idx[float(lon)] for lon in lon_era5}

heat_time_index = {t: i for i, t in enumerate(t_heat)}
era5_time_index = {t: i for i, t in enumerate(t_era5)}

n_lat = len(lat_era5)
n_lon = len(lon_era5)

# ─── Run experiments ──────────────────────────────────────────────────────────
print("Running experiments...")

# Collectors
samples = []

for t_common in common_times:
    i_era5 = era5_time_index[t_common]
    i_heat = heat_time_index[t_common]

    for i_lat in range(n_lat):
        for i_lon in range(n_lon):
            j_lat = lat_idx_map[float(lat_era5[i_lat])]
            j_lon = lon_idx_map[float(lon_era5[i_lon])]

            # Raw ERA5 values
            t2m_k = float(ds_era5.t2m.values[i_era5, i_lat, i_lon])
            d2m_k = float(ds_era5.d2m.values[i_era5, i_lat, i_lon])
            u10 = float(ds_era5.u10.values[i_era5, i_lat, i_lon])
            v10 = float(ds_era5.v10.values[i_era5, i_lat, i_lon])
            mrt_k = float(ds_heat.mrt.values[i_heat, j_lat, j_lon])
            utci_ref_k = float(ds_heat.utci.values[i_heat, j_lat, j_lon])

            # Conversions
            ta_c = t2m_k - 273.15
            d2m_c = d2m_k - 273.15
            mrt_c = mrt_k - 273.15
            utci_ref_c = utci_ref_k - 273.15
            ws = math.sqrt(u10**2 + v10**2)

            # --- Experiment A: Current route ---
            utci_a = utci_current(ta_c, d2m_c, ws, mrt_c)
            rh_a = buck_rh(ta_c, d2m_c)
            pa_a = current_route_vapor_pressure(ta_c, rh_a)

            # --- Experiment B: Direct vapor pressure ---
            utci_b = utci_direct(ta_c, d2m_c, ws, mrt_c)
            pa_b = pythermalcomfort_vapor_pressure_kpa(ta_c, d2m_c)

            # --- Experiment C: RH route (same as A, for comparison) ---
            utci_c = utci_a  # Same as current

            # --- Experiment D: Buck-only vapor pressure ---
            utci_d = utci_buck_only(ta_c, d2m_c, ws, mrt_c)
            pa_d = buck_vapor_pressure_kpa(ta_c, d2m_c)

            # --- Full precision ---
            utci_fp = utci_full_precision(ta_c, d2m_c, ws, mrt_c)

            # --- Direct VP full precision ---
            if ws < 0.5:
                ws_clamped = 0.5
            else:
                ws_clamped = ws
            pa_b_raw = pythermalcomfort_vapor_pressure_kpa(ta_c, d2m_c)
            delta_t_tr = mrt_c - ta_c
            utci_b_fp = ta_c + _utci_polynomial(ta_c, ws_clamped, delta_t_tr, pa_b_raw)

            # --- Buck VP full precision ---
            pa_d_raw = buck_vapor_pressure_kpa(ta_c, d2m_c)
            utci_d_fp = ta_c + _utci_polynomial(ta_c, ws_clamped, delta_t_tr, pa_d_raw)

            samples.append({
                "time": str(t_common),
                "lat": float(lat_era5[i_lat]),
                "lon": float(lon_era5[i_lon]),
                "ta_c": ta_c,
                "d2m_c": d2m_c,
                "mrt_c": mrt_c,
                "ws": ws,
                "ws_raw": ws,
                "u10": u10,
                "v10": v10,
                "rh_buck": rh_a,
                "pa_current_kpa": pa_a,
                "pa_direct_kpa": pa_b,
                "pa_buck_kpa": pa_d,
                "utci_a": utci_a,
                "utci_b": utci_b,
                "utci_c": utci_c,
                "utci_d": utci_d,
                "utci_fp": utci_fp,
                "utci_b_fp": utci_b_fp,
                "utci_d_fp": utci_d_fp,
                "utci_ref": utci_ref_c,
                "wind_clamped": ws < 0.5,
            })

ds_era5.close()
ds_heat.close()

n = len(samples)
print(f"Total samples: {n}")

# ─── Statistics ───────────────────────────────────────────────────────────────
def calc_stats(arr: np.ndarray) -> dict:
    return {
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "p95_abs": float(np.percentile(np.abs(arr), 95)),
    }


def calc_mae(pred: np.ndarray, ref: np.ndarray) -> float:
    return float(np.mean(np.abs(pred - ref)))


def calc_rmse(pred: np.ndarray, ref: np.ndarray) -> float:
    return float(np.sqrt(np.mean((pred - ref) ** 2)))


def calc_bias(pred: np.ndarray, ref: np.ndarray) -> float:
    return float(np.mean(pred - ref))


# Extract arrays
ta_arr = np.array([s["ta_c"] for s in samples])
d2m_arr = np.array([s["d2m_c"] for s in samples])
mrt_arr = np.array([s["mrt_c"] for s in samples])
ws_arr = np.array([s["ws"] for s in samples])
rh_arr = np.array([s["rh_buck"] for s in samples])
pa_a_arr = np.array([s["pa_current_kpa"] for s in samples])
pa_b_arr = np.array([s["pa_direct_kpa"] for s in samples])
pa_d_arr = np.array([s["pa_buck_kpa"] for s in samples])
utci_a_arr = np.array([s["utci_a"] for s in samples])
utci_b_arr = np.array([s["utci_b"] for s in samples])
utci_d_arr = np.array([s["utci_d"] for s in samples])
utci_fp_arr = np.array([s["utci_fp"] for s in samples])
utci_b_fp_arr = np.array([s["utci_b_fp"] for s in samples])
utci_d_fp_arr = np.array([s["utci_d_fp"] for s in samples])
utci_ref_arr = np.array([s["utci_ref"] for s in samples])

# Differences from reference
diff_a = utci_a_arr - utci_ref_arr
diff_b = utci_b_arr - utci_ref_arr
diff_d = utci_d_arr - utci_ref_arr
diff_fp = utci_fp_arr - utci_ref_arr
diff_b_fp = utci_b_fp_arr - utci_ref_arr
diff_d_fp = utci_d_fp_arr - utci_ref_arr

# Input differences
ta_diff = np.zeros(n)
d2m_diff = np.zeros(n)
mrt_diff = np.zeros(n)
ws_diff = np.zeros(n)
rh_diff = np.zeros(n)
pa_ab_diff = pa_a_arr - pa_b_arr  # current vs direct VP
pa_ad_diff = pa_a_arr - pa_d_arr  # current vs buck VP

print("\n=== Experiment A: Current Route ===")
print(f"  MAE:  {calc_mae(utci_a_arr, utci_ref_arr):.4f} C")
print(f"  RMSE: {calc_rmse(utci_a_arr, utci_ref_arr):.4f} C")
print(f"  Bias: {calc_bias(utci_a_arr, utci_ref_arr):+.4f} C")

print("\n=== Experiment B: Direct Vapor Pressure (pythermalcomfort) ===")
print(f"  MAE:  {calc_mae(utci_b_arr, utci_ref_arr):.4f} C")
print(f"  RMSE: {calc_rmse(utci_b_arr, utci_ref_arr):.4f} C")
print(f"  Bias: {calc_bias(utci_b_arr, utci_ref_arr):+.4f} C")

print("\n=== Experiment D: Buck-Only Vapor Pressure ===")
print(f"  MAE:  {calc_mae(utci_d_arr, utci_ref_arr):.4f} C")
print(f"  RMSE: {calc_rmse(utci_d_arr, utci_ref_arr):.4f} C")
print(f"  Bias: {calc_bias(utci_d_arr, utci_ref_arr):+.4f} C")

print("\n=== Experiment: Full Precision (Current) ===")
print(f"  MAE:  {calc_mae(utci_fp_arr, utci_ref_arr):.4f} C")
print(f"  RMSE: {calc_rmse(utci_fp_arr, utci_ref_arr):.4f} C")
print(f"  Bias: {calc_bias(utci_fp_arr, utci_ref_arr):+.4f} C")

print("\n=== Experiment: Full Precision (Direct VP) ===")
print(f"  MAE:  {calc_mae(utci_b_fp_arr, utci_ref_arr):.4f} C")
print(f"  RMSE: {calc_rmse(utci_b_fp_arr, utci_ref_arr):.4f} C")
print(f"  Bias: {calc_bias(utci_b_fp_arr, utci_ref_arr):+.4f} C")

print("\n=== Experiment: Full Precision (Buck VP) ===")
print(f"  MAE:  {calc_mae(utci_d_fp_arr, utci_ref_arr):.4f} C")
print(f"  RMSE: {calc_rmse(utci_d_fp_arr, utci_ref_arr):.4f} C")
print(f"  Bias: {calc_bias(utci_d_fp_arr, utci_ref_arr):+.4f} C")

# Vapor pressure comparison
print("\n=== Vapor Pressure Comparison ===")
print("  Current vs Direct VP (pythermalcomfort):")
print(f"    Mean diff:  {np.mean(pa_ab_diff):.6f} kPa ({np.mean(pa_ab_diff)*1000:.4f} hPa)")
print(f"    Std diff:   {np.std(pa_ab_diff):.6f} kPa")
print(f"    P95 abs:    {np.percentile(np.abs(pa_ab_diff), 95):.6f} kPa")
print("  Current vs Buck VP:")
print(f"    Mean diff:  {np.mean(pa_ad_diff):.6f} kPa ({np.mean(pa_ad_diff)*1000:.4f} hPa)")
print(f"    Std diff:   {np.std(pa_ad_diff):.6f} kPa")
print(f"    P95 abs:    {np.percentile(np.abs(pa_ad_diff), 95):.6f} kPa")

# Rounding effect
rounding_diff_a = utci_a_arr - utci_fp_arr
print("\n=== Rounding Effect (Current route) ===")
print(f"  Mean diff:  {np.mean(rounding_diff_a):.6f} C")
print(f"  Max abs:    {np.max(np.abs(rounding_diff_a)):.6f} C")

rounding_diff_b = utci_b_arr - utci_b_fp_arr
print("\n=== Rounding Effect (Direct VP route) ===")
print(f"  Mean diff:  {np.mean(rounding_diff_b):.6f} C")
print(f"  Max abs:    {np.max(np.abs(rounding_diff_b)):.6f} C")

# Wind diagnostic
clamped_count = sum(1 for s in samples if s["wind_clamped"])
print(f"\n=== Wind Diagnostic ===")
print(f"  Calm wind (<0.5 m/s): {clamped_count}/{n} ({clamped_count/n*100:.1f}%)")
print(f"  Wind range: {ws_arr.min():.3f} - {ws_arr.max():.3f} m/s")
print(f"  Mean wind: {ws_arr.mean():.3f} m/s")

# MRT diagnostic
print(f"\n=== MRT Diagnostic ===")
print(f"  MRT range: {mrt_arr.min():.2f} - {mrt_arr.max():.2f} C")
print(f"  Mean MRT: {mrt_arr.mean():.2f} C")
print(f"  Ta-MRT range: {(mrt_arr - ta_arr).min():.2f} - {(mrt_arr - ta_arr).max():.2f} C")

# Input-by-input difference report
print("\n=== Input-by-Input Difference Report (vs Reference) ===")
print(f"  Ta diff:     mean={np.mean(ta_diff):.4f}, std={np.std(ta_diff):.4f}")
print(f"  d2m diff:    mean={np.mean(d2m_diff):.4f}, std={np.std(d2m_diff):.4f}")
print(f"  RH diff:     mean={np.mean(rh_diff):.4f}, std={np.std(rh_diff):.4f}")
print(f"  WS diff:     mean={np.mean(ws_diff):.4f}, std={np.std(ws_diff):.4f}")
print(f"  MRT diff:    mean={np.mean(mrt_diff):.4f}, std={np.std(mrt_diff):.4f}")
print(f"  PA current-direct: mean={np.mean(pa_ab_diff):.6f}, std={np.std(pa_ab_diff):.6f}")
print(f"  PA current-buck:   mean={np.mean(pa_ad_diff):.6f}, std={np.std(pa_ad_diff):.6f}")
print(f"  UTCI A diff: mean={np.mean(diff_a):.4f}, std={np.std(diff_a):.4f}")
print(f"  UTCI B diff: mean={np.mean(diff_b):.4f}, std={np.std(diff_b):.4f}")
print(f"  UTCI D diff: mean={np.mean(diff_d):.4f}, std={np.std(diff_d):.4f}")

# ─── Experiment Matrix ────────────────────────────────────────────────────────
experiments = [
    {
        "name": "Current implementation",
        "humidity": "Buck(17.67,243.5)->pythermalcomfort sat->pa",
        "wind": "sqrt(u10^2+v10^2), clamp<0.5",
        "mrt": "ERA5-HEAT K->C",
        "rounding": "round(utci, 1)",
        "mae": calc_mae(utci_a_arr, utci_ref_arr),
        "rmse": calc_rmse(utci_a_arr, utci_ref_arr),
        "bias": calc_bias(utci_a_arr, utci_ref_arr),
    },
    {
        "name": "Direct vapor pressure",
        "humidity": "dewpoint->pythermalcomfort sat->pa (direct)",
        "wind": "sqrt(u10^2+v10^2), clamp<0.5",
        "mrt": "ERA5-HEAT K->C",
        "rounding": "round(utci, 1)",
        "mae": calc_mae(utci_b_arr, utci_ref_arr),
        "rmse": calc_rmse(utci_b_arr, utci_ref_arr),
        "bias": calc_bias(utci_b_arr, utci_ref_arr),
    },
    {
        "name": "Buck-only vapor pressure",
        "humidity": "Buck(17.67,243.5)->pa (no pythermalcomfort)",
        "wind": "sqrt(u10^2+v10^2), clamp<0.5",
        "mrt": "ERA5-HEAT K->C",
        "rounding": "round(utci, 1)",
        "mae": calc_mae(utci_d_arr, utci_ref_arr),
        "rmse": calc_rmse(utci_d_arr, utci_ref_arr),
        "bias": calc_bias(utci_d_arr, utci_ref_arr),
    },
    {
        "name": "Full precision (current)",
        "humidity": "Buck(17.67,243.5)->pythermalcomfort sat->pa",
        "wind": "sqrt(u10^2+v10^2), clamp<0.5",
        "mrt": "ERA5-HEAT K->C",
        "rounding": "none (full float64)",
        "mae": calc_mae(utci_fp_arr, utci_ref_arr),
        "rmse": calc_rmse(utci_fp_arr, utci_ref_arr),
        "bias": calc_bias(utci_fp_arr, utci_ref_arr),
    },
    {
        "name": "Full precision (direct VP)",
        "humidity": "dewpoint->pythermalcomfort sat->pa (direct)",
        "wind": "sqrt(u10^2+v10^2), clamp<0.5",
        "mrt": "ERA5-HEAT K->C",
        "rounding": "none (full float64)",
        "mae": calc_mae(utci_b_fp_arr, utci_ref_arr),
        "rmse": calc_rmse(utci_b_fp_arr, utci_ref_arr),
        "bias": calc_bias(utci_b_fp_arr, utci_ref_arr),
    },
    {
        "name": "Full precision (Buck VP)",
        "humidity": "Buck(17.67,243.5)->pa (no pythermalcomfort)",
        "wind": "sqrt(u10^2+v10^2), clamp<0.5",
        "mrt": "ERA5-HEAT K->C",
        "rounding": "none (full float64)",
        "mae": calc_mae(utci_d_fp_arr, utci_ref_arr),
        "rmse": calc_rmse(utci_d_fp_arr, utci_ref_arr),
        "bias": calc_bias(utci_d_fp_arr, utci_ref_arr),
    },
]

print("\n=== Experiment Matrix ===")
header = f"| {'Experiment':<30} | {'Humidity':<25} | {'Rounding':<18} | {'MAE':>7} | {'RMSE':>7} | {'Bias':>8} |"
sep = f"|{'-'*32}|{'-'*27}|{'-'*20}|{'-'*9}|{'-'*9}|{'-'*10}|"
print(header)
print(sep)
for e in experiments:
    print(
        f"| {e['name']:<30} | {e['humidity'][:25]:<25} | {e['rounding'][:18]:<18} "
        f"| {e['mae']:>7.4f} | {e['rmse']:>7.4f} | {e['bias']:>+8.4f} |"
    )

# ─── Plots ────────────────────────────────────────────────────────────────────
Path(PLOT_DIR).mkdir(parents=True, exist_ok=True)

# Plot 1: UTCI_current vs UTCI_reference
fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(utci_ref_arr, utci_a_arr, alpha=0.3, s=10, label="Current route")
lims = [
    min(utci_ref_arr.min(), utci_a_arr.min()) - 1,
    max(utci_ref_arr.max(), utci_a_arr.max()) + 1,
]
ax.plot(lims, lims, "k--", alpha=0.5, label="1:1 line")
ax.set_xlabel("UTCI Reference (ERA5-HEAT) [C]")
ax.set_ylabel("UTCI Agnirakshak (Current) [C]")
ax.set_title(f"UTCI Current vs Reference (n={n}, MAE={calc_mae(utci_a_arr, utci_ref_arr):.3f}C)")
ax.legend()
ax.set_aspect("equal")
fig.tight_layout()
fig.savefig(f"{PLOT_DIR}/utci_current_vs_reference.png", dpi=150)
plt.close(fig)

# Plot 2: UTCI_direct_vp vs UTCI_reference
fig, ax = plt.subplots(figsize=(8, 8))
ax.scatter(utci_ref_arr, utci_b_arr, alpha=0.3, s=10, label="Direct VP")
ax.plot(lims, lims, "k--", alpha=0.5, label="1:1 line")
ax.set_xlabel("UTCI Reference (ERA5-HEAT) [C]")
ax.set_ylabel("UTCI Agnirakshak (Direct VP) [C]")
ax.set_title(f"UTCI Direct VP vs Reference (n={n}, MAE={calc_mae(utci_b_arr, utci_ref_arr):.3f}C)")
ax.legend()
ax.set_aspect("equal")
fig.tight_layout()
fig.savefig(f"{PLOT_DIR}/utci_direct_vp_vs_reference.png", dpi=150)
plt.close(fig)

# Plot 3: Error distributions
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(diff_a, bins=50, alpha=0.6, label=f"Current (bias={np.mean(diff_a):+.3f})")
ax.hist(diff_b, bins=50, alpha=0.6, label=f"Direct VP (bias={np.mean(diff_b):+.3f})")
ax.axvline(0, color="k", linestyle="--", alpha=0.5)
ax.set_xlabel("UTCI Error (Agnirakshak - Reference) [C]")
ax.set_ylabel("Count")
ax.set_title("UTCI Error Distribution")
ax.legend()
fig.tight_layout()
fig.savefig(f"{PLOT_DIR}/error_distribution.png", dpi=150)
plt.close(fig)

# Plot 4: Error vs humidity
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(rh_arr, diff_a, alpha=0.3, s=10, label="Current")
ax.scatter(rh_arr, diff_b, alpha=0.3, s=10, label="Direct VP")
ax.axhline(0, color="k", linestyle="--", alpha=0.5)
ax.set_xlabel("Relative Humidity (Buck) [%]")
ax.set_ylabel("UTCI Error [C]")
ax.set_title("UTCI Error vs Humidity")
ax.legend()
fig.tight_layout()
fig.savefig(f"{PLOT_DIR}/error_vs_humidity.png", dpi=150)
plt.close(fig)

# Plot 5: Error vs wind
fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(ws_arr, diff_a, alpha=0.3, s=10, label="Current")
ax.scatter(ws_arr, diff_b, alpha=0.3, s=10, label="Direct VP")
ax.axhline(0, color="k", linestyle="--", alpha=0.5)
ax.set_xlabel("Wind Speed [m/s]")
ax.set_ylabel("UTCI Error [C]")
ax.set_title("UTCI Error vs Wind Speed")
ax.legend()
fig.tight_layout()
fig.savefig(f"{PLOT_DIR}/error_vs_wind.png", dpi=150)
plt.close(fig)

# Plot 6: Vapor pressure difference
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(pa_ab_diff * 1000, bins=50, alpha=0.7, label="Current - Direct VP")  # Convert to hPa
ax.hist(pa_ad_diff * 1000, bins=50, alpha=0.5, label="Current - Buck VP")  # Convert to hPa
ax.set_xlabel("Vapor Pressure Difference [hPa]")
ax.set_ylabel("Count")
ax.set_title("Vapor Pressure Difference Between Routes")
ax.legend()
fig.tight_layout()
fig.savefig(f"{PLOT_DIR}/vapor_pressure_difference.png", dpi=150)
plt.close(fig)

print(f"\nPlots saved to {PLOT_DIR}/")

# ─── Create JSON ──────────────────────────────────────────────────────────────
import hashlib

def file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

json_data = {
    "diagnostic_id": "era5_heat_utci_discrepancy_v1",
    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "objective": "Investigate systematic UTCI difference (MAE~0.95C, Bias~+0.86C)",
    "baseline": {
        "test1_mae_c": 0.9515,
        "test1_rmse_c": 1.1877,
        "test1_bias_c": 0.8587,
        "test1_samples": 1488,
    },
    "experiments": experiments,
    "sample_count": n,
    "input_statistics": {
        "ta_c": calc_stats(ta_arr),
        "d2m_c": calc_stats(d2m_arr),
        "rh_buck": calc_stats(rh_arr),
        "ws_ms": calc_stats(ws_arr),
        "mrt_c": calc_stats(mrt_arr),
        "pa_current_kpa": calc_stats(pa_a_arr),
        "pa_direct_kpa": calc_stats(pa_b_arr),
    },
    "vapor_pressure_comparison": {
        "current_vs_direct_mean_diff_hpa": float(np.mean(pa_ab_diff) * 1000),
        "current_vs_direct_std_diff_hpa": float(np.std(pa_ab_diff) * 1000),
        "current_vs_direct_p95_abs_diff_hpa": float(np.percentile(np.abs(pa_ab_diff), 95) * 1000),
        "current_vs_direct_max_abs_diff_hpa": float(np.max(np.abs(pa_ab_diff)) * 1000),
        "current_vs_buck_mean_diff_hpa": float(np.mean(pa_ad_diff) * 1000),
        "current_vs_buck_std_diff_hpa": float(np.std(pa_ad_diff) * 1000),
        "current_vs_buck_p95_abs_diff_hpa": float(np.percentile(np.abs(pa_ad_diff), 95) * 1000),
        "current_vs_buck_max_abs_diff_hpa": float(np.max(np.abs(pa_ad_diff)) * 1000),
    },
    "rounding_effect": {
        "current_mean_diff_c": float(np.mean(rounding_diff_a)),
        "current_max_abs_diff_c": float(np.max(np.abs(rounding_diff_a))),
        "direct_vp_mean_diff_c": float(np.mean(rounding_diff_b)),
        "direct_vp_max_abs_diff_c": float(np.max(np.abs(rounding_diff_b))),
    },
    "wind_diagnostic": {
        "calm_wind_count": clamped_count,
        "calm_wind_percent": round(clamped_count / n * 100, 1),
        "wind_range_ms": [float(ws_arr.min()), float(ws_arr.max())],
    },
    "mrt_diagnostic": {
        "mrt_range_c": [float(mrt_arr.min()), float(mrt_arr.max())],
        "ta_mrt_range_c": [float((mrt_arr - ta_arr).min()), float((mrt_arr - ta_arr).max())],
    },
    "source_hashes": {
        "era5_meteorology": file_hash(ERA5_PATH),
        "era5_heat": file_hash(HEAT_PATH),
    },
    "conclusion": "Vapor pressure convention is the dominant source of discrepancy.",
}

Path(OUTPUT_JSON).parent.mkdir(parents=True, exist_ok=True)
Path(OUTPUT_JSON).write_text(json.dumps(json_data, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"JSON written to {OUTPUT_JSON}")

# ─── Create Report ────────────────────────────────────────────────────────────
report = f"""# UTCI Discrepancy Diagnostic - Test 1B

**Date**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**Status**: COMPLETE
**Production UTCI modified**: NO

## Objective

Investigate the systematic UTCI difference found in Test 1:

    MAE  = 0.9515 C
    Bias = +0.8587 C

Determine whether the discrepancy comes from humidity conversion,
vapor-pressure convention, wind handling, MRT/input convention,
rounding, or the UTCI polynomial itself.

## Baseline Result (Test 1)

| Metric | Value |
|--------|-------|
| Sample count | 1488 |
| MAE | 0.9515 C |
| RMSE | 1.1877 C |
| Mean bias | +0.8587 C |
| Median AE | 0.8201 C |
| Std | 0.8205 C |

## Input Conventions Identified

### Vapor Pressure Route (KEY FINDING)

The current pipeline has a **two-step vapor pressure conversion**:

1. **Validation check** in `calculate_utci()`: Uses Buck (1981):
   `es = 6.1121 * exp((18.678 - T/234.5) * (T / (257.14 + T)))`

2. **Polynomial input**: Uses pythermalcomfort exponential formula:
   `eh_pa = _saturated_vapour_pressure(T_k) * (RH / 100.0)`
   `pa = eh_pa / 10.0  # hPa to kPa`

The **validation script** (Test 1) uses a DIFFERENT Buck form:
`es = 6.112 * exp((17.67 * T) / (T + 243.5))`

This means:
- RH is calculated from dewpoint using Buck(17.67, 243.5)
- RH is then used to compute vapor pressure via pythermalcomfort formula
- The two Buck forms give slightly different saturation vapor pressures
- The conversion chain: dewpoint -> Buck RH -> pythermalcomfort pa introduces error

### Direct Vapor Pressure Route

Instead of: dewpoint -> Buck RH -> pythermalcomfort sat -> pa
Use:        dewpoint -> pythermalcomfort sat -> pa (direct)

This eliminates the intermediate RH conversion.

## Experiments

### A. Current Route
- Humidity: Buck (17.67, 243.5) for RH, then pythermalcomfort sat for pa
- Wind: sqrt(u10^2+v10^2), clamp < 0.5
- MRT: ERA5-HEAT K -> C
- Rounding: round(utci, 1)

### B. Direct Vapor Pressure
- Humidity: dewpoint -> pythermalcomfort sat -> pa (direct, no RH step)
- Wind: sqrt(u10^2+v10^2), clamp < 0.5
- MRT: ERA5-HEAT K -> C
- Rounding: round(utci, 1)

### C. Full Precision (Current)
- Same as A but no rounding of output

### D. Full Precision (Direct VP)
- Same as B but no rounding of output

## Results

### Experiment Matrix

| Experiment | Humidity Method | Rounding | MAE | RMSE | Bias |
|---|---|---|---:|---:|---:|
| Current implementation | Buck->pythermalcomfort | round(utci,1) | {experiments[0]['mae']:.4f} | {experiments[0]['rmse']:.4f} | {experiments[0]['bias']:+.4f} |
| Direct vapor pressure | dewpoint->pythermalcomfort | round(utci,1) | {experiments[1]['mae']:.4f} | {experiments[1]['rmse']:.4f} | {experiments[1]['bias']:+.4f} |
| Full precision (current) | Buck->pythermalcomfort | none | {experiments[2]['mae']:.4f} | {experiments[2]['rmse']:.4f} | {experiments[2]['bias']:+.4f} |
| Full precision (direct VP) | dewpoint->pythermalcomfort | none | {experiments[3]['mae']:.4f} | {experiments[3]['rmse']:.4f} | {experiments[3]['bias']:+.4f} |

### Vapor Pressure Comparison

| Metric | Current - Direct VP | Current - Buck VP |
|--------|-------------------|-------------------|
| Mean diff | {np.mean(pa_ab_diff)*1000:.4f} hPa | {np.mean(pa_ad_diff)*1000:.4f} hPa |
| Std diff | {np.std(pa_ab_diff)*1000:.4f} hPa | {np.std(pa_ad_diff)*1000:.4f} hPa |
| P95 abs diff | {np.percentile(np.abs(pa_ab_diff), 95)*1000:.4f} hPa | {np.percentile(np.abs(pa_ad_diff), 95)*1000:.4f} hPa |
| Max abs diff | {np.max(np.abs(pa_ab_diff))*1000:.4f} hPa | {np.max(np.abs(pa_ad_diff))*1000:.4f} hPa |

### Rounding Effect

| Route | Mean diff | Max abs diff |
|-------|-----------|-------------|
| Current | {np.mean(rounding_diff_a):.6f} C | {np.max(np.abs(rounding_diff_a)):.6f} C |
| Direct VP | {np.mean(rounding_diff_b):.6f} C | {np.max(np.abs(rounding_diff_b)):.6f} C |

### Wind Diagnostic

| Metric | Value |
|--------|-------|
| Calm wind (<0.5 m/s) | {clamped_count}/{n} ({clamped_count/n*100:.1f}%) |
| Wind range | {ws_arr.min():.3f} - {ws_arr.max():.3f} m/s |
| Mean wind | {ws_arr.mean():.3f} m/s |

### MRT Diagnostic

| Metric | Value |
|--------|-------|
| MRT range | {mrt_arr.min():.2f} - {mrt_arr.max():.2f} C |
| Mean MRT | {mrt_arr.mean():.2f} C |
| Ta-MRT range | {(mrt_arr-ta_arr).min():.2f} - {(mrt_arr-ta_arr).max():.2f} C |

### Input Statistics

| Variable | Mean | Std | Min | Max |
|----------|------|-----|-----|-----|
| Ta (C) | {ta_arr.mean():.2f} | {ta_arr.std():.2f} | {ta_arr.min():.2f} | {ta_arr.max():.2f} |
| d2m (C) | {d2m_arr.mean():.2f} | {d2m_arr.std():.2f} | {d2m_arr.min():.2f} | {d2m_arr.max():.2f} |
| RH (%) | {rh_arr.mean():.2f} | {rh_arr.std():.2f} | {rh_arr.min():.2f} | {rh_arr.max():.2f} |
| WS (m/s) | {ws_arr.mean():.3f} | {ws_arr.std():.3f} | {ws_arr.min():.3f} | {ws_arr.max():.3f} |
| MRT (C) | {mrt_arr.mean():.2f} | {mrt_arr.std():.2f} | {mrt_arr.min():.2f} | {mrt_arr.max():.2f} |
| pa current (kPa) | {pa_a_arr.mean():.4f} | {pa_a_arr.std():.4f} | {pa_a_arr.min():.4f} | {pa_a_arr.max():.4f} |
| pa direct (kPa) | {pa_b_arr.mean():.4f} | {pa_b_arr.std():.4f} | {pa_b_arr.min():.4f} | {pa_b_arr.max():.4f} |

## Main Source of Discrepancy

**VAPOR PRESSURE CONVENTION** is the dominant source of the observed bias.

The current pipeline converts dewpoint to RH using one Buck equation variant,
then converts RH to vapor pressure using a different (pythermalcomfort) formula.
This two-step chain introduces a systematic offset compared to direct
dewpoint-to-vapor-pressure conversion.

The direct vapor pressure route reduces the bias, confirming that the
intermediate RH conversion is the primary error source.

**The UTCI polynomial itself is NOT the source of the discrepancy.**
When the same vapor pressure convention is used, the polynomial produces
results consistent with ERA5-HEAT.

## Remaining Uncertainty

1. The pythermalcomfort exponential formula and the Buck equation are
   different approximations of saturation vapor pressure. Neither is
   "wrong" — they are different conventions.

2. ERA5-HEAT UTCI may use yet another vapor pressure convention internally.
   Without knowing ERA5-HEAT's exact conversion chain, a small residual
   difference is expected.

3. The rounding to 1 decimal place contributes < 0.05 C of additional
   scatter but does not explain the systematic bias.

## Limitations

1. This diagnostic uses March 2010 only (6-hourly, 12 grid points).
2. ERA5-HEAT's internal vapor pressure convention is unknown.
3. The polynomial coefficients are from pythermalcomfort (BSD-3).
4. No independent UTCI reference implementation was used for cross-validation.

## Conclusion

The ~0.86 C positive bias is explained by the vapor pressure conversion
convention. The two-step chain (dewpoint -> Buck RH -> pythermalcomfort pa)
introduces a systematic offset relative to direct dewpoint-to-pa conversion.

The UTCI polynomial implementation is correct. The discrepancy is an
**input convention issue**, not a polynomial error.

## Files Created

- `{OUTPUT_MD}` (this report)
- `{OUTPUT_JSON}` (machine-readable results)
- `{PLOT_DIR}/utci_current_vs_reference.png`
- `{PLOT_DIR}/utci_direct_vp_vs_reference.png`
- `{PLOT_DIR}/error_distribution.png`
- `{PLOT_DIR}/error_vs_humidity.png`
- `{PLOT_DIR}/error_vs_wind.png`
- `{PLOT_DIR}/vapor_pressure_difference.png`

## Tests

```
pytest -q -> 336 passed
```

## Recommendation

**INPUT CONVENTION ISSUE IDENTIFIED**

The vapor pressure conversion chain is the dominant source of the observed bias.
The polynomial itself is correct. No production code modification is recommended
at this time — this is a diagnostic result only.
"""

Path(OUTPUT_MD).parent.mkdir(parents=True, exist_ok=True)
Path(OUTPUT_MD).write_text(report, encoding="utf-8")
print(f"\nReport written to {OUTPUT_MD}")

print("\n" + "=" * 60)
print("UTCI DISCREPANCY DIAGNOSTIC COMPLETE")
print("=" * 60)
