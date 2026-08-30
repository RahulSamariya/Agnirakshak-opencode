"""Vapor pressure diagnostic: test all ERA5-HEAT pipeline routes."""
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

def ae_rh(ta_c, td_c):
    es_t = 6.1094 * math.exp(17.625 * ta_c / (ta_c + 243.04))
    es_td = 6.1094 * math.exp(17.625 * td_c / (td_c + 243.04))
    return (es_td / es_t) * 100.0

def buck_pa(ta_c, rh_pct):
    es = 6.1121 * math.exp((18.678 - ta_c / 234.5) * (ta_c / (257.14 + ta_c)))
    return (es * rh_pct / 100.0) / 10.0

method_names = [
    "direct_vp_utci_formula",
    "ae_rh_then_buck_pa",
    "ae_rh_then_utci_pa",
    "buck_rh_then_buck_pa",
    "utci_rh_then_utci_pa",
    "utci_rh_then_buck_pa",
]
biases = {name: [] for name in method_names}

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
            td_c = d2m_k - 273.15
            mrt_c = mrt_k - 273.15
            utci_ref_c = utci_ref_k - 273.15
            ws = math.sqrt(u10**2 + v10**2)
            if ws < 0.5:
                ws = 0.5
            dtt = mrt_c - ta_c

            # 1. Direct VP from dewpoint using UTCI internal formula
            pa1 = _saturated_vapour_pressure(d2m_k) / 10.0
            biases["direct_vp_utci_formula"].append(
                ta_c + _utci_polynomial(ta_c, ws, dtt, pa1) - utci_ref_c
            )

            # 2. AE RH -> Buck pa (ERA5-HEAT paper: AE for RH, then need pa)
            rh_ae = ae_rh(ta_c, td_c)
            pa2 = buck_pa(ta_c, rh_ae)
            biases["ae_rh_then_buck_pa"].append(
                ta_c + _utci_polynomial(ta_c, ws, dtt, pa2) - utci_ref_c
            )

            # 3. AE RH -> UTCI internal pa
            es_utci_ta = _saturated_vapour_pressure(ta_k)
            pa3 = (es_utci_ta * rh_ae / 100.0) / 10.0
            biases["ae_rh_then_utci_pa"].append(
                ta_c + _utci_polynomial(ta_c, ws, dtt, pa3) - utci_ref_c
            )

            # 4. Buck RH -> Buck pa
            es_buck_ta = 6.1121 * math.exp((18.678 - ta_c / 234.5) * (ta_c / (257.14 + ta_c)))
            es_buck_td = 6.1121 * math.exp((18.678 - td_c / 234.5) * (td_c / (257.14 + td_c)))
            rh_buck = (es_buck_td / es_buck_ta) * 100.0
            pa4 = buck_pa(ta_c, rh_buck)
            biases["buck_rh_then_buck_pa"].append(
                ta_c + _utci_polynomial(ta_c, ws, dtt, pa4) - utci_ref_c
            )

            # 5. UTCI internal RH -> UTCI internal pa
            es_utci_td = _saturated_vapour_pressure(d2m_k)
            rh_utci = (es_utci_td / es_utci_ta) * 100.0
            pa5 = (es_utci_ta * rh_utci / 100.0) / 10.0
            biases["utci_rh_then_utci_pa"].append(
                ta_c + _utci_polynomial(ta_c, ws, dtt, pa5) - utci_ref_c
            )

            # 6. UTCI internal RH -> Buck pa
            pa6 = buck_pa(ta_c, rh_utci)
            biases["utci_rh_then_buck_pa"].append(
                ta_c + _utci_polynomial(ta_c, ws, dtt, pa6) - utci_ref_c
            )

ds_era5.close()
ds_heat.close()

print("ERA5-HEAT UTCI Vapor Pressure Route Comparison")
print("=" * 80)
print(f"Samples: {len(common_times) * 12}")
print()
for name in method_names:
    arr = np.array(biases[name])
    mae = np.mean(np.abs(arr))
    bias = np.mean(arr)
    rmse = np.sqrt(np.mean(arr**2))
    print(f"  {name:35s}: MAE={mae:.4f}, Bias={bias:+.4f}, RMSE={rmse:.4f}")
