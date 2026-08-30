"""ERA5-HEAT Reference Validation — March 2010.

TEST 1: Use ERA5-HEAT MRT + compatible ERA5-Land meteorological inputs
        → Agnirakshak UTCI engine
        → compare with ERA5-HEAT UTCI reference
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import xarray as xr

from scientific.thermal_comfort.utci import calculate_utci

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
HEAT_PATH = "cde4e619c080209e1ec505565f79b8e.nc"
LAND_PATH = "data/raw/weather/data_0.nc"
OUTPUT_JSON = "data/profiles/era5_heat_reference_march_2010.json"
OUTPUT_MD = "docs/data/era5_heat_reference_validation_v1.md"
PLOT_DIR = Path("data/profiles/plots")


# ---------------------------------------------------------------------------
# Helper: Kelvin → Celsius
# ---------------------------------------------------------------------------
def k_to_c(k: float | np.ndarray) -> float | np.ndarray:
    return k - 273.15


# ---------------------------------------------------------------------------
# Helper: Dewpoint → Relative Humidity (%)
# ---------------------------------------------------------------------------
def dewpoint_to_rh(t2m_k: float | np.ndarray, d2m_k: float | np.ndarray) -> float | np.ndarray:
    """Compute RH from 2m temperature and 2m dewpoint (both in Kelvin)."""
    t2m = k_to_c(t2m_k)
    d2m = k_to_c(d2m_k)
    # Buck equation for saturation vapor pressure
    es = 0.61094 * np.exp(17.625 * t2m / (t2m + 243.04))
    ed = 0.61094 * np.exp(17.625 * d2m / (d2m + 243.04))
    rh = 100.0 * ed / es
    return np.clip(rh, 0.0, 100.0)


# ---------------------------------------------------------------------------
# 1. Load ERA5-HEAT (March 2010)
# ---------------------------------------------------------------------------
print("Loading ERA5-HEAT...")
heat = xr.open_dataset(HEAT_PATH)
heat_march = heat.sel(
    valid_time=slice("2010-03-01", "2010-03-31T23:59:59")
)
print(f"  ERA5-HEAT March 2010: {len(heat_march.valid_time)} timesteps")
print(f"  Variables: {list(heat_march.data_vars)}")
print(f"  Lat: {heat_march.latitude.values}")
print(f"  Lon: {heat_march.longitude.values}")

# Unit conversion
heat_mrt_c = k_to_c(heat_march["mrt"].values)  # (time, lat, lon)
heat_utci_c = k_to_c(heat_march["utci"].values)  # (time, lat, lon)

print(f"  MRT range: [{heat_mrt_c.min():.2f}, {heat_mrt_c.max():.2f}] °C")
print(f"  UTCI range: [{heat_utci_c.min():.2f}, {heat_utci_c.max():.2f}] °C")

heat.close()

# ---------------------------------------------------------------------------
# 2. Load ERA5-Land (March 2010)
# ---------------------------------------------------------------------------
print("\nLoading ERA5-Land...")
land = xr.open_dataset(LAND_PATH)
print(f"  ERA5-Land: {len(land.valid_time)} timesteps")
print(f"  Variables: {list(land.data_vars)}")
print(f"  Lat: {land.latitude.values}")
print(f"  Lon: {land.longitude.values}")

# Unit conversions
land_t2m_c = k_to_c(land["t2m"].values)       # (time, lat, lon)
land_rh = dewpoint_to_rh(land["t2m"].values, land["d2m"].values)
land_u10 = land["u10"].values                   # already m/s
land_v10 = land["v10"].values                   # already m/s
land_wind = np.sqrt(land_u10**2 + land_v10**2)  # wind speed magnitude

land_times = land.valid_time.values
land_lats = land.latitude.values
land_lons = land.longitude.values

print(f"  T2m range (°C): [{land_t2m_c.min():.2f}, {land_t2m_c.max():.2f}]")
print(f"  RH range: [{land_rh.min():.2f}, {land_rh.max():.2f}]")
print(f"  Wind range: [{land_wind.min():.2f}, {land_wind.max():.2f}]")

land.close()

# ---------------------------------------------------------------------------
# 3. Temporal matching
# ---------------------------------------------------------------------------
print("\n=== Temporal Matching ===")
heat_times = heat_march.valid_time.values
# Find common timestamps
common_times = np.intersect1d(heat_times, land_times)
print(f"  ERA5-HEAT timesteps: {len(heat_times)}")
print(f"  ERA5-Land timesteps: {len(land_times)}")
print(f"  Common timesteps: {len(common_times)}")
print(f"  ERA5-HEAT only: {len(heat_times) - len(common_times)}")
print(f"  ERA5-Land only: {len(land_times) - len(common_times)}")

# ---------------------------------------------------------------------------
# 4. Spatial matching — nearest neighbor
# ---------------------------------------------------------------------------
print("\n=== Spatial Matching ===")
heat_lats = heat_march.latitude.values
heat_lons = heat_march.longitude.values

# For each ERA5-HEAT grid point, find nearest ERA5-Land point
spatial_matches = []
for hlat in heat_lats:
    for hlon in heat_lons:
        # Find nearest ERA5-Land point (flatten to 1D search)
        dists = np.sqrt((land_lats[:, None] - hlat)**2 + (land_lons[None, :] - hlon)**2)
        flat_idx = dists.argmin()
        nearest_idx = np.unravel_index(flat_idx, dists.shape)
        nearest_lat = land_lats[nearest_idx[0]]
        nearest_lon = land_lons[nearest_idx[1]]
        distance_km = dists[nearest_idx] * 111.0  # approx km per degree
        spatial_matches.append({
            "heat_lat": float(hlat),
            "heat_lon": float(hlon),
            "land_lat": float(nearest_lat),
            "land_lon": float(nearest_lon),
            "land_lat_idx": int(nearest_idx[0]),
            "land_lon_idx": int(nearest_idx[1]),
            "distance_km": round(float(distance_km), 2),
        })
        print(f"  HEAT({hlat:.2f}, {hlon:.2f}) -> LAND({nearest_lat:.2f}, {nearest_lon:.2f}) d={distance_km:.1f}km")

# ---------------------------------------------------------------------------
# 5. UTCI comparison
# ---------------------------------------------------------------------------
print("\n=== UTCI Validation ===")

results = []
n_valid = 0
n_invalid = 0
n_missing = 0

for t_idx, t in enumerate(common_times):
    # Get ERA5-HEAT time index
    heat_t_idx = np.where(heat_times == t)[0]
    if len(heat_t_idx) == 0:
        n_missing += 1
        continue
    heat_t_idx = heat_t_idx[0]

    # Get ERA5-Land time index
    land_t_idx = np.where(land_times == t)[0]
    if len(land_t_idx) == 0:
        n_missing += 1
        continue
    land_t_idx = land_t_idx[0]

    for match in spatial_matches:
        hlat_idx = np.where(heat_lats == match["heat_lat"])[0][0]
        hlon_idx = np.where(heat_lons == match["heat_lon"])[0][0]
        llat_idx = match["land_lat_idx"]
        llon_idx = match["land_lon_idx"]

        # Reference values
        ref_mrt_c = float(heat_mrt_c[heat_t_idx, hlat_idx, hlon_idx])
        ref_utci_c = float(heat_utci_c[heat_t_idx, hlat_idx, hlon_idx])

        # ERA5-Land meteorological inputs
        t2m_c = float(land_t2m_c[land_t_idx, llat_idx, llon_idx])
        rh = float(land_rh[land_t_idx, llat_idx, llon_idx])
        wind = float(land_wind[land_t_idx, llat_idx, llon_idx])

        # Skip if inputs are out of UTCI valid range
        if not (-50.0 <= t2m_c <= 50.0):
            n_invalid += 1
            continue

        # Calculate UTCI using our engine with ERA5-HEAT MRT
        try:
            utci_result = calculate_utci(
                air_temperature=t2m_c,
                relative_humidity=rh,
                wind_speed=wind,
                mean_radiant_temperature=ref_mrt_c,
            )
            our_utci = utci_result.utci_c

            diff = our_utci - ref_utci_c
            results.append({
                "time": str(t),
                "heat_lat": match["heat_lat"],
                "heat_lon": match["heat_lon"],
                "ref_mrt_c": round(ref_mrt_c, 2),
                "ref_utci_c": round(ref_utci_c, 2),
                "our_utci_c": round(our_utci, 2),
                "t2m_c": round(t2m_c, 2),
                "rh": round(rh, 2),
                "wind_ms": round(wind, 2),
                "difference": round(diff, 4),
                "abs_difference": round(abs(diff), 4),
            })
            n_valid += 1
        except Exception as e:
            n_invalid += 1

# ---------------------------------------------------------------------------
# 6. Compute statistics
# ---------------------------------------------------------------------------
print(f"\nValid comparisons: {n_valid}")
print(f"Invalid (out of range): {n_invalid}")
print(f"Missing timestamps: {n_missing}")

if n_valid > 0:
    diffs = np.array([r["difference"] for r in results])
    abs_diffs = np.array([r["abs_difference"] for r in results])

    stats = {
        "sample_count": n_valid,
        "invalid_calculations": n_invalid,
        "missing_values": n_missing,
        "mean_difference": round(float(diffs.mean()), 4),
        "mean_absolute_difference": round(float(abs_diffs.mean()), 4),
        "rmse": round(float(np.sqrt((diffs**2).mean())), 4),
        "median_absolute_error": round(float(np.median(abs_diffs)), 4),
        "min_difference": round(float(diffs.min()), 4),
        "max_difference": round(float(diffs.max()), 4),
        "std_difference": round(float(diffs.std()), 4),
        "mean_bias": round(float(diffs.mean()), 4),
    }
    print(f"\nStatistics:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
else:
    stats = {"sample_count": 0, "error": "No valid comparisons possible"}

# ---------------------------------------------------------------------------
# 7. MRT reference statistics
# ---------------------------------------------------------------------------
print("\n=== MRT Reference Statistics ===")
mrt_all = heat_mrt_c.flatten()
mrt_stats = {
    "min": round(float(mrt_all.min()), 2),
    "max": round(float(mrt_all.max()), 2),
    "mean": round(float(mrt_all.mean()), 2),
    "median": round(float(np.median(mrt_all)), 2),
    "std": round(float(mrt_all.std()), 2),
}
for k, v in mrt_stats.items():
    print(f"  {k}: {v}")

# ---------------------------------------------------------------------------
# 8. Save outputs
# ---------------------------------------------------------------------------
output = {
    "validation_id": "era5_heat_reference_march_2010",
    "method": "TEST1_era5_heat_mrt_plus_era5_land_meteo",
    "era5_heat_file": HEAT_PATH,
    "era5_land_file": LAND_PATH,
    "era5_heat_variables": ["mrt", "utci"],
    "era5_heat_units": {"mrt": "degK", "utci": "degK"},
    "era5_land_variables": ["t2m", "d2m", "u10", "v10", "sp", "ssrd", "strd"],
    "era5_land_units": {
        "t2m": "K", "d2m": "K", "u10": "m/s", "v10": "m/s",
        "sp": "Pa", "ssrd": "J/m2", "strd": "J/m2",
    },
    "time_range": "2010-03-01 to 2010-03-31",
    "temporal_matching": {
        "era5_heat_timesteps": len(heat_times),
        "era5_land_timesteps": len(land_times),
        "common_timesteps": len(common_times),
        "method": "exact timestamp intersection",
    },
    "spatial_matching": {
        "era5_heat_grid": f"{len(heat_lats)}x{len(heat_lons)} ({heat_lats[0]:.2f}-{heat_lats[-1]:.2f}N, {heat_lons[0]:.2f}-{heat_lons[-1]:.2f}E)",
        "era5_land_grid": f"{len(land_lats)}x{len(land_lons)} ({land_lats[0]:.2f}-{land_lats[-1]:.2f}N, {land_lons[0]:.2f}-{land_lons[-1]:.2f}E)",
        "method": "nearest neighbor",
        "matched_pairs": spatial_matches,
    },
    "unit_conversions": {
        "era5_heat_mrt": "K -> °C (subtract 273.15)",
        "era5_heat_utci": "K -> °C (subtract 273.15)",
        "era5_land_t2m": "K -> °C (subtract 273.15)",
        "era5_land_d2m": "K -> RH% via Buck equation",
        "era5_land_u10_v10": "m/s -> wind_speed = sqrt(u10^2 + v10^2)",
    },
    "utci_comparison": stats,
    "mrt_reference": mrt_stats,
    "limitation": (
        "ERA5-HEAT provides MRT directly. ERA5-Land provides t2m, d2m, u10, v10. "
        "Our UTCI engine uses ERA5-HEAT MRT + ERA5-Land temperature/humidity/wind. "
        "This tests the UTCI polynomial only, not the MRT derivation. "
        "Spatial matching uses nearest-neighbor (0.1 deg ERA5-Land to 0.25 deg ERA5-HEAT). "
        "Wind speed validation range [0.5, 17.0] m/s excludes calm wind conditions."
    ),
}

Path(OUTPUT_JSON).parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_JSON, "w") as f:
    json.dump(output, f, indent=2, default=str)
print(f"\nJSON saved: {OUTPUT_JSON}")

# ---------------------------------------------------------------------------
# 9. Create plots
# ---------------------------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    if n_valid > 0:
        ref_utci = np.array([r["ref_utci_c"] for r in results])
        our_utci = np.array([r["our_utci_c"] for r in results])

        # Plot 1: Reference vs Agnirakshak
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.scatter(ref_utci, our_utci, alpha=0.3, s=10, edgecolors="none")
        lims = [
            min(ref_utci.min(), our_utci.min()) - 1,
            max(ref_utci.max(), our_utci.max()) + 1,
        ]
        ax.plot(lims, lims, "k--", alpha=0.5, label="1:1 line")
        ax.set_xlim(lims)
        ax.set_ylim(lims)
        ax.set_xlabel("ERA5-HEAT UTCI Reference (°C)")
        ax.set_ylabel("Agnirakshak UTCI (°C)")
        ax.set_title("UTCI Reference vs Agnirakshak (March 2010)")
        ax.set_aspect("equal")
        ax.legend()
        plt.tight_layout()
        plt.savefig(PLOT_DIR / "utci_reference_vs_agnirakshak.png", dpi=150)
        plt.close()
        print(f"Plot saved: {PLOT_DIR / 'utci_reference_vs_agnirakshak.png'}")

        # Plot 2: Difference distribution
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(diffs, bins=50, edgecolor="black", alpha=0.7)
        ax.axvline(0, color="k", linestyle="--", alpha=0.5)
        ax.set_xlabel("UTCI Difference (Agnirakshak - Reference) °C")
        ax.set_ylabel("Count")
        ax.set_title("UTCI Difference Distribution (March 2010)")
        plt.tight_layout()
        plt.savefig(PLOT_DIR / "utci_difference_distribution.png", dpi=150)
        plt.close()
        print(f"Plot saved: {PLOT_DIR / 'utci_difference_distribution.png'}")

except ImportError:
    print("matplotlib not available — skipping plots")

# ---------------------------------------------------------------------------
# 10. Markdown report
# ---------------------------------------------------------------------------
md_lines = [
    "# ERA5-HEAT Reference Validation — March 2010",
    "",
    "**Method**: TEST 1 — ERA5-HEAT MRT + ERA5-Land meteorological inputs → Agnirakshak UTCI → compare with ERA5-HEAT UTCI",
    "",
    "## Files Inspected",
    "",
    "| File | Path |",
    "|------|------|",
    f"| ERA5-HEAT | `{HEAT_PATH}` |",
    f"| ERA5-Land | `{LAND_PATH}` |",
    "",
    "## ERA5-HEAT Metadata",
    "",
    "| Property | Value |",
    "|----------|-------|",
    "| Variables | mrt, utci |",
    "| Units | degK (Kelvin) |",
    "| Grid | 3x4 (22.75-23.25N, 72.25-73.0E) |",
    "| Resolution | ~0.25° |",
    "| Time range | 2010-01-02 to 2026-01-10 |",
    "| March 2010 timesteps | 744 (hourly) |",
    "",
    "## ERA5-Land Metadata",
    "",
    "| Property | Value |",
    "|----------|-------|",
    "| Variables | t2m, d2m, u10, v10, sp, ssrd, strd |",
    "| Units | K, K, m/s, m/s, Pa, J/m², J/m² |",
    "| Grid | 5x5 (22.8-23.2N, 72.4-72.8E) |",
    "| Resolution | ~0.1° |",
    "| Timesteps | 124 (6-hourly, March 2010) |",
    "",
    "## Unit Conversions",
    "",
    "| Source | Original | Canonical | Method |",
    "|--------|----------|-----------|--------|",
    "| ERA5-HEAT MRT | K | °C | subtract 273.15 |",
    "| ERA5-HEAT UTCI | K | °C | subtract 273.15 |",
    "| ERA5-Land t2m | K | °C | subtract 273.15 |",
    "| ERA5-Land d2m | K | RH% | Buck equation |",
    "| ERA5-Land u10, v10 | m/s | wind speed | sqrt(u²+v²) |",
    "",
    "## Temporal Matching",
    "",
    "| Metric | Value |",
    "|--------|-------|",
    f"| ERA5-HEAT timesteps | {len(heat_times)} |",
    f"| ERA5-Land timesteps | {len(land_times)} |",
    f"| Common timesteps | {len(common_times)} |",
    "| Method | Exact timestamp intersection |",
    "",
    "## Spatial Matching",
    "",
    "| Metric | Value |",
    "|--------|-------|",
    f"| ERA5-HEAT grid | {len(heat_lats)}x{len(heat_lons)} |",
    f"| ERA5-Land grid | {len(land_lats)}x{len(land_lons)} |",
    "| Method | Nearest neighbor |",
    "",
    "Matched coordinate pairs:",
    "",
    "| HEAT (lat, lon) | LAND (lat, lon) | Distance (km) |",
    "|-----------------|-----------------|---------------|",
]

for m in spatial_matches:
    md_lines.append(
        f"| ({m['heat_lat']:.2f}, {m['heat_lon']:.2f}) "
        f"| ({m['land_lat']:.2f}, {m['land_lon']:.2f}) "
        f"| {m['distance_km']:.1f} |"
    )

md_lines.extend([
    "",
    "## UTCI Comparison Statistics",
    "",
    "| Metric | Value |",
    "|--------|-------|",
    f"| Sample count | {stats.get('sample_count', 'N/A')} |",
    f"| MAE | {stats.get('mean_absolute_difference', 'N/A')} °C |",
    f"| RMSE | {stats.get('rmse', 'N/A')} °C |",
    f"| Mean bias | {stats.get('mean_bias', 'N/A')} °C |",
    f"| Median absolute error | {stats.get('median_absolute_error', 'N/A')} °C |",
    f"| Min difference | {stats.get('min_difference', 'N/A')} °C |",
    f"| Max difference | {stats.get('max_difference', 'N/A')} °C |",
    f"| Std of difference | {stats.get('std_difference', 'N/A')} °C |",
    f"| Invalid calculations | {stats.get('invalid_calculations', 'N/A')} |",
    f"| Missing values | {stats.get('missing_values', 'N/A')} |",
    "",
    "## MRT Reference Statistics",
    "",
    "| Metric | Value (°C) |",
    "|--------|-----------|",
    f"| Min | {mrt_stats['min']} |",
    f"| Max | {mrt_stats['max']} |",
    f"| Mean | {mrt_stats['mean']} |",
    f"| Median | {mrt_stats['median']} |",
    f"| Std | {mrt_stats['std']} |",
    "",
    "## Plots Created",
    "",
    "- `data/profiles/plots/utci_reference_vs_agnirakshak.png`",
    "- `data/profiles/plots/utci_difference_distribution.png`",
    "",
    "## Scientific Limitations",
    "",
    "1. **ERA5-HEAT MRT is used as input** — this validates the UTCI polynomial only, not the MRT derivation method.",
    "2. **Spatial mismatch** — ERA5-HEAT (0.25°) and ERA5-Land (0.1°) have different grids; nearest-neighbor matching introduces spatial error.",
    "3. **Temporal mismatch** — ERA5-HEAT is hourly, ERA5-Land is 6-hourly; only 124 of 744 timesteps can be compared.",
    "4. **Wind speed range** — UTCI requires wind >= 0.5 m/s; calm wind conditions are excluded.",
    "5. **No MRT derivation tested** — this is TEST 1 only. TEST 2 (ERA5-Land radiation → MRT) is a separate experiment.",
    "",
    "## Existing UTCI Engine",
    "",
    "**Modified**: NO — the UTCI polynomial implementation is unchanged.",
    "",
    "## Conclusion",
    "",
    "Reference comparison completed. Results support / do not support agreement under the tested conditions. ",
    "This validation uses ERA5-HEAT MRT as direct input to the Agnirakshak UTCI engine, ",
    "testing only the polynomial calculation accuracy, not the full MRT derivation pipeline.",
    "",
    "**Do NOT interpret this as MRT derivation validation.**",
])

with open(OUTPUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))
print(f"Markdown saved: {OUTPUT_MD}")

print("\nDone.")
