"""MRT Method Comparison: Di Napoli vs Thermofeel vs ERA5-HEAT."""
import sys
sys.path.insert(0, ".")

import math
import json
import numpy as np
import xarray as xr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

# =============================================================================
# CONSTANTS
# =============================================================================
SIGMA = 5.67e-8
F_A = 0.5
ALPHA_IR = 0.7
EPSILON_P = 0.97

# =============================================================================
# SOLAR GEOMETRY (shared by Di Napoli and Thermofeel)
# =============================================================================

def day_of_year(t):
    year = int(t.astype("datetime64[Y]").astype(int) + 1970)
    jan1 = np.datetime64(f"{year}-01-01")
    return float((t - jan1) / np.timedelta64(1, "D")) + 1.0

def solar_declination(jd):
    g = (360.0 / 365.25) * (jd - 1.0)
    g_rad = math.radians(g)
    delta_rad = (0.006918 - 0.399912 * math.cos(g_rad) + 0.070257 * math.sin(g_rad)
                 - 0.006758 * math.cos(2 * g_rad) + 0.000907 * math.sin(2 * g_rad)
                 - 0.002697 * math.cos(3 * g_rad) + 0.001480 * math.sin(3 * g_rad))
    return math.degrees(delta_rad)

def time_correction(jd):
    g = (360.0 / 365.25) * (jd - 1.0)
    g_rad = math.radians(g)
    return (0.004297 + 0.107029 * math.cos(g_rad) - 1.837877 * math.sin(g_rad)
            - 0.837378 * math.cos(2 * g_rad) - 2.340475 * math.sin(2 * g_rad))

def hour_angle(hr_utc, lon, tc):
    return (hr_utc - 12.0) * 15.0 + lon + tc

def solar_zenith(delta, lat, h):
    d = math.radians(delta)
    p = math.radians(lat)
    hr = math.radians(h)
    cos_z = math.sin(d) * math.sin(p) + math.cos(d) * math.cos(p) * math.cos(hr)
    return math.degrees(math.acos(max(-1.0, min(1.0, cos_z))))

def sunrise_sunset_ha(delta, lat):
    d = math.radians(delta)
    p = math.radians(lat)
    cos_h0 = -math.tan(d) * math.tan(p)
    if cos_h0 < -1.0: return 180.0
    if cos_h0 > 1.0: return 0.0
    return math.degrees(math.acos(cos_h0))

def avg_daytime_cos_zenith(delta, lat, h_min, h_max):
    d = math.radians(delta)
    p = math.radians(lat)
    hmin = math.radians(h_min)
    hmax = math.radians(h_max)
    dh = h_max - h_min
    if abs(dh) < 1e-10: return 0.0
    cos_avg = (math.sin(d) * math.sin(p) +
               (1.0 / math.radians(dh)) * math.cos(d) * math.cos(p) *
               (math.sin(hmax) - math.sin(hmin)))
    return max(0.0, cos_avg)

def sunlit_hour_angles(h_start, h_end, h0):
    return max(h_start, -h0), min(h_end, h0)

# =============================================================================
# METHOD A: DI NAPOLI (published paper, Eq 12-15)
# =============================================================================

def mrt_di_napoli(ssrd, strd, fdir, ssr, str_val, lat, lon, t):
    """Di Napoli et al. (2020) — exact published methodology."""
    L_up = strd - str_val
    S_diff = ssrd - fdir
    S_up = ssrd - ssr

    jd = day_of_year(t)
    hr = (t - np.datetime64(t.astype("datetime64[D]"))) / np.timedelta64(1, "h")
    delta = solar_declination(jd)
    tc = time_correction(jd)
    h_end = hour_angle(hr, lon, tc)
    zen = solar_zenith(delta, lat, h_end)
    elev = 90.0 - zen
    h0 = sunrise_sunset_ha(delta, lat)

    # Eq 13: I* = fdir / cos(theta_bar_0) over sunlit interval
    h_start = hour_angle(hr - 1.0, lon, tc)
    h_min, h_max = sunlit_hour_angles(h_start, h_end, h0)

    if elev < 0.0 or h_min >= h_max:
        I_star = 0.0
    else:
        cos_bar = avg_daytime_cos_zenith(delta, lat, h_min, h_max)
        I_star = fdir / cos_bar if cos_bar > 1e-6 else 0.0

    # Eq 15: fp with gamma = elevation
    gamma = elev
    fp = 0.308 * math.cos(math.radians(gamma * (0.998 - gamma**2 / 50000.0))) if elev > 0 else 0.0

    # Eq 14: MRT (note: fp*I* OUTSIDE alpha_ratio multiplier)
    alpha_ratio = ALPHA_IR / EPSILON_P
    rf = (F_A * strd + F_A * L_up +
          alpha_ratio * F_A * S_diff + alpha_ratio * F_A * S_up + fp * I_star)

    cossza = math.cos(math.radians(zen))
    dsrp = fdir / cossza if cossza > 0.1 else fdir

    mrt = (abs(rf) / SIGMA) ** 0.25
    return {"mrt": mrt, "elev": elev, "cossza": cossza, "dsrp": dsrp,
            "fp": fp, "I_star": I_star, "rf": rf, "L_up": L_up,
            "S_diff": S_diff, "S_up": S_up}

# =============================================================================
# METHOD B: THERMOFEEL (ECMWF implementation)
# =============================================================================

def mrt_thermofeel(ssrd, strd, fdir, ssr, str_val, lat, lon, t):
    """ECMW thermofeel — exact implementation from thermofeel 2.3.0."""
    dsw = ssrd - fdir
    rsw = ssrd - ssr
    lur = strd - str_val

    jd = day_of_year(t)
    hr = (t - np.datetime64(t.astype("datetime64[D]"))) / np.timedelta64(1, "h")
    delta = solar_declination(jd)
    tc = time_correction(jd)
    h_end = hour_angle(hr, lon, tc)
    zen = solar_zenith(delta, lat, h_end)
    elev = 90.0 - zen

    cossza = math.cos(math.radians(zen))
    dsrp = fdir / cossza if cossza > 0.1 else fdir

    # Thermofeel fp: gamma = arcsin(cossza) = elevation
    gamma = math.degrees(math.asin(cossza))
    fp = 0.308 * math.cos(math.radians(gamma * (0.998 - gamma**2 / 50000.0)))

    # Thermofeel MRT: alpha_ratio multiplies (0.5*dsw + 0.5*rsw + fp*dsrp)
    alpha_ratio = ALPHA_IR / EPSILON_P
    rf = 0.5 * strd + 0.5 * lur + alpha_ratio * (0.5 * dsw + 0.5 * rsw + fp * dsrp)

    mrt = (abs(rf) / SIGMA) ** 0.25
    return {"mrt": mrt, "elev": elev, "cossza": cossza, "dsrp": dsrp,
            "fp": fp, "I_star": dsrp, "rf": rf, "L_up": lur,
            "S_diff": dsw, "S_up": rsw}

# =============================================================================
# METHOD C: ERA5-HEAT (loaded from reference file)
# =============================================================================

def load_era5heat(path):
    """Load ERA5-HEAT MRT from reference NetCDF."""
    ds = xr.open_dataset(path)
    return ds

# =============================================================================
# MAIN COMPARISON
# =============================================================================

def main():
    out_dir = Path("data/profiles/plots/mrt_method_comparison")
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    rad_ds = xr.open_dataset("97c99a12bac0f84dae69bd5460cde459.nc")
    heat_ds = xr.open_dataset("cde4e619c080209e1ec505565f79b8e.nc")

    # Extract variables
    ssrd = rad_ds["ssrd"].values / 3600.0
    strd = rad_ds["strd"].values / 3600.0
    fdir = rad_ds["fdir"].values / 3600.0
    ssr = rad_ds["ssr"].values / 3600.0
    strr = rad_ds["str"].values / 3600.0
    times = rad_ds["valid_time"].values
    lats = rad_ds["latitude"].values
    lons = rad_ds["longitude"].values

    # Select ERA5-HEAT for matching timestamps
    heat_mrt = heat_ds["mrt"].sel(valid_time=times).values
    # Flip ERA5-HEAT lat to match radiation grid
    if heat_ds["latitude"].values[0] < heat_ds["latitude"].values[-1]:
        heat_mrt = heat_mrt[:, ::-1, :]

    n_time, n_lat, n_lon = ssrd.shape

    # Compute MRT for all three methods
    mrt_a = np.full((n_time, n_lat, n_lon), np.nan)
    mrt_b = np.full((n_time, n_lat, n_lon), np.nan)
    elev_grid = np.full((n_time, n_lat, n_lon), np.nan)
    cossza_grid = np.full((n_time, n_lat, n_lon), np.nan)

    intermediates = []

    for ti in range(n_time):
        for la in range(n_lat):
            for lo in range(n_lon):
                s = ssrd[ti, la, lo]
                sd = strd[ti, la, lo]
                fd = fdir[ti, la, lo]
                sr = ssr[ti, la, lo]
                st = strr[ti, la, lo]
                lat = lats[la]
                lon = lons[lo]
                t = times[ti]

                if np.isnan(s) or np.isnan(sd) or np.isnan(fd) or np.isnan(sr) or np.isnan(st):
                    continue

                a = mrt_di_napoli(s, sd, fd, sr, st, lat, lon, t)
                b = mrt_thermofeel(s, sd, fd, sr, st, lat, lon, t)

                mrt_a[ti, la, lo] = a["mrt"]
                mrt_b[ti, la, lo] = b["mrt"]
                elev_grid[ti, la, lo] = a["elev"]
                cossza_grid[ti, la, lo] = a["cossza"]

                intermediates.append({
                    "time": str(t), "lat": float(lat), "lon": float(lon),
                    "elev": a["elev"], "cossza": a["cossza"],
                    "DiNapoli": {"mrt": a["mrt"], "fp": a["fp"], "I_star": a["I_star"],
                                 "rf": a["rf"], "L_up": a["L_up"], "S_diff": a["S_diff"], "S_up": a["S_up"]},
                    "Thermofeel": {"mrt": b["mrt"], "fp": b["fp"], "dsrp": b["dsrp"],
                                   "rf": b["rf"], "L_up": b["L_up"], "S_diff": b["S_diff"], "S_up": b["S_up"]},
                    "ERA5_HEAT": {"mrt": float(heat_mrt[ti, la, lo]) if not np.isnan(heat_mrt[ti, la, lo]) else None}
                })

    # Flatten for metrics
    valid = ~np.isnan(mrt_a) & ~np.isnan(mrt_b) & ~np.isnan(heat_mrt)
    a_flat = mrt_a[valid]
    b_flat = mrt_b[valid]
    e_flat = heat_mrt[valid]
    elev_flat = elev_grid[valid]

    def metrics(x, y):
        n = len(x)
        err = x - y
        ae = np.abs(err)
        ss_res = np.sum(err**2)
        ss_tot = np.sum((y - np.mean(y))**2)
        r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")
        return {
            "N": int(n), "MAE": float(np.mean(ae)), "RMSE": float(np.sqrt(np.mean(err**2))),
            "Bias": float(np.mean(err)), "MedianAE": float(np.median(ae)),
            "Std": float(np.std(err)), "P95": float(np.percentile(ae, 95)),
            "R2": float(r2), "Corr": float(np.corrcoef(x, y)[0, 1]) if n > 1 else float("nan")
        }

    m_dn_tf = metrics(a_flat, b_flat)
    m_dn_e5 = metrics(a_flat, e_flat)
    m_tf_e5 = metrics(b_flat, e_flat)

    print("PAIRWISE METRICS")
    print("=" * 60)
    for name, m in [("DiNapoli vs Thermofeel", m_dn_tf),
                    ("DiNapoli vs ERA5-HEAT", m_dn_e5),
                    ("Thermofeel vs ERA5-HEAT", m_tf_e5)]:
        print(f"\n{name}:")
        for k, v in m.items():
            print(f"  {k:8s}: {v}")

    # Term-by-term for representative observations
    print("\nTERM-BY-TERM COMPARISON")
    print("=" * 60)
    # Pick one observation per category
    night_idx = np.where(elev_flat < 0)[0]
    low_idx = np.where((elev_flat > 0) & (elev_flat < 25))[0]
    high_idx = np.where(elev_flat > 45)[0]

    for label, idx_arr in [("NIGHTTIME", night_idx[:3]),
                           ("LOW-SUN", low_idx[:3]),
                           ("HIGH-SUN", high_idx[:3])]:
        if len(idx_arr) == 0:
            continue
        print(f"\n{label}:")
        for i in idx_arr[:1]:
            print(f"  DiNapoli:  MRT={a_flat[i]:.2f} K, rf={intermediates[i]['DiNapoli']['rf']:.2f}")
            print(f"  Thermofeel: MRT={b_flat[i]:.2f} K, rf={intermediates[i]['Thermofeel']['rf']:.2f}")
            print(f"  ERA5-HEAT:  MRT={e_flat[i]:.2f} K")

    # Plots
    print("\nCreating plots...")

    # 1. Time series
    fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)
    t_idx = 0  # first timestamp
    for lo_idx in range(n_lon):
        axes[0].plot(lats, mrt_a[t_idx, :, lo_idx], "o-", label=f"lon={lons[lo_idx]}")
    axes[0].set_title("Di Napoli MRT")
    axes[0].set_ylabel("MRT [K]")
    axes[0].legend(fontsize=8)

    for lo_idx in range(n_lon):
        axes[1].plot(lats, mrt_b[t_idx, :, lo_idx], "s-", label=f"lon={lons[lo_idx]}")
    axes[1].set_title("Thermofeel MRT")
    axes[1].set_ylabel("MRT [K]")
    axes[1].legend(fontsize=8)

    for lo_idx in range(n_lon):
        axes[2].plot(lats, heat_mrt[t_idx, :, lo_idx], "^-", label=f"lon={lons[lo_idx]}")
    axes[2].set_title("ERA5-HEAT MRT")
    axes[2].set_ylabel("MRT [K]")
    axes[2].set_xlabel("Latitude")
    axes[2].legend(fontsize=8)

    plt.tight_layout()
    plt.savefig(out_dir / "method_comparison_timeseries.png", dpi=150)
    plt.close()

    # 2. Pairwise scatter
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, x, y, title in [(axes[0], a_flat, b_flat, "Di Napoli vs Thermofeel"),
                             (axes[1], a_flat, e_flat, "Di Napoli vs ERA5-HEAT"),
                             (axes[2], b_flat, e_flat, "Thermofeel vs ERA5-HEAT")]:
        lo = min(x.min(), y.min()) - 5
        hi = max(x.max(), y.max()) + 5
        ax.scatter(x, y, alpha=0.3, s=10)
        ax.plot([lo, hi], [lo, hi], "k--", alpha=0.5)
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_xlabel("Method 1 [K]")
        ax.set_ylabel("Method 2 [K]")
        ax.set_title(title)
        ax.set_aspect("equal")
    plt.tight_layout()
    plt.savefig(out_dir / "pairwise_scatter.png", dpi=150)
    plt.close()

    # 3. Error distributions
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, x, y, title in [(axes[0], a_flat, b_flat, "Di Napoli - Thermofeel"),
                             (axes[1], a_flat, e_flat, "Di Napoli - ERA5-HEAT"),
                             (axes[2], b_flat, e_flat, "Thermofeel - ERA5-HEAT")]:
        err = x - y
        ax.hist(err, bins=50, alpha=0.7, edgecolor="black")
        ax.axvline(0, color="k", linestyle="--")
        ax.set_xlabel("Error [K]")
        ax.set_ylabel("Count")
        ax.set_title(f"{title}\nMAE={np.mean(np.abs(err)):.2f} K, Bias={np.mean(err):.2f} K")
    plt.tight_layout()
    plt.savefig(out_dir / "pairwise_error_distributions.png", dpi=150)
    plt.close()

    # 4. Error vs solar elevation
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, x, y, title in [(axes[0], a_flat, b_flat, "Di Napoli - Thermofeel"),
                             (axes[1], a_flat, e_flat, "Di Napoli - ERA5-HEAT"),
                             (axes[2], b_flat, e_flat, "Thermofeel - ERA5-HEAT")]:
        ax.scatter(elev_flat, x - y, alpha=0.3, s=10)
        ax.axhline(0, color="k", linestyle="--")
        ax.set_xlabel("Solar Elevation [deg]")
        ax.set_ylabel("Error [K]")
        ax.set_title(title)
    plt.tight_layout()
    plt.savefig(out_dir / "error_vs_solar_elevation.png", dpi=150)
    plt.close()

    print("Plots saved to", out_dir)

    # Save JSON
    json_out = {
        "test_id": "TEST_2H_MRT_METHOD_COMPARISON",
        "status": "COMPLETE",
        "methods": {
            "DiNapoli": {"source": "Di Napoli et al. (2020)", "doi": "10.1007/s00484-020-01900-5",
                         "conventions": {"fp_gamma": "elevation", "I_star": "fdir/cos_bar (interval avg)",
                                         "alpha_placement": "fp*I* OUTSIDE alpha_ratio"}},
            "Thermofeel": {"source": "ECMWF thermofeel 2.3.0", "conventions": {
                           "fp_gamma": "arcsin(cossza)=elevation", "dsrp": "fdir/cossza (instantaneous)",
                           "alpha_placement": "fp*dsrp INSIDE alpha_ratio"}},
            "ERA5_HEAT": {"source": "ERA5-HEAT reference product", "type": "loaded from NetCDF"}
        },
        "pairwise_metrics": {"DiNapoli_vs_Thermofeel": m_dn_tf,
                             "DiNapoli_vs_ERA5_HEAT": m_dn_e5,
                             "Thermofeel_vs_ERA5_HEAT": m_tf_e5},
        "sample_intermediates": intermediates[:20],
        "files_created": [str(f) for f in out_dir.glob("*.png")]
    }
    with open("data/profiles/mrt_method_comparison_v1.json", "w") as f:
        json.dump(json_out, f, indent=2, default=str)
    print("JSON saved")

if __name__ == "__main__":
    main()
