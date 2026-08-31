# ERA5 RADIATION INPUT VERIFICATION

## 1. Objective

Verify the newly downloaded ERA5 radiation NetCDF file contains the required radiation variables for the Di Napoli et al. (2020) MRT methodology. This is inspection only — no MRT implementation.

## 2. File Under Inspection

| Property | Value |
|----------|-------|
| **File** | `2b5663f2dae9337c125c5159b0f4ccce.nc` |
| **Intended destination** | `data/raw/weather/era5_radiation_march_2010.nc` |
| **Source** | ERA5 single levels (ECMWF CDS) |
| **File size** | 56,064 bytes |
| **Last modified** | 2026-08-31 22:23:37 |

## 3. Required Variables Check

| Variable | Long Name | GRIB paramId | Required? | Status |
|----------|-----------|-------------|-----------|--------|
| `fdir` | Surface direct short-wave (solar) radiation | 228021 | YES | **PRESENT** |
| `ssr` | Surface net short-wave (solar) radiation | 176 | YES | **PRESENT** |
| `str` | Surface net long-wave (thermal) radiation | 177 | YES | **PRESENT** |

**Result: All 3 required radiation variables are present.**

## 4. Variable Metadata

### 4.1 `fdir` — Direct Solar Radiation

| Property | Value |
|----------|-------|
| long_name | Surface direct short-wave (solar) radiation |
| units | J m⁻² |
| GRIB_paramId | 228021 |
| GRIB_stepType | accum |
| GRIB_stepUnits | 1 (hours) |
| dimensions | (valid_time, latitude, longitude) |
| shape | (124, 3, 4) |
| dtype | float32 |
| min | 0.0 J m⁻² |
| max | 2,653,504.0 J m⁻² |
| missing_values | 0 |
| total_values | 1,488 |

### 4.2 `ssr` — Net Shortwave Radiation

| Property | Value |
|----------|-------|
| long_name | Surface net short-wave (solar) radiation |
| units | J m⁻² |
| GRIB_paramId | 176 |
| GRIB_stepType | accum |
| GRIB_stepUnits | 1 (hours) |
| standard_name | surface_net_downward_shortwave_flux |
| dimensions | (valid_time, latitude, longitude) |
| shape | (124, 3, 4) |
| dtype | float32 |
| min | 3.6×10⁻¹² J m⁻² |
| max | 2,569,920.0 J m⁻² |
| missing_values | 0 |
| total_values | 1,488 |

### 4.3 `str` — Net Longwave Radiation

| Property | Value |
|----------|-------|
| long_name | Surface net long-wave (thermal) radiation |
| units | J m⁻² |
| GRIB_paramId | 177 |
| GRIB_stepType | accum |
| GRIB_stepUnits | 1 (hours) |
| standard_name | surface_net_upward_longwave_flux |
| dimensions | (valid_time, latitude, longitude) |
| shape | (124, 3, 4) |
| dtype | float32 |
| min | -673,117.0 J m⁻² |
| max | -153,639.0 J m⁻² |
| missing_values | 0 |
| total_values | 1,488 |

## 5. Time Coverage

| Property | Value |
|----------|-------|
| Time range | 2010-03-01 00:00 to 2010-03-31 18:00 |
| Number of timestamps | 124 |
| Time interval | 6 hours |
| Time encoding | UTC (ERA5 standard) |
| Duplicates | 0 |

**Note:** The data is 6-hourly (not hourly). Accumulation period = 6 hours = 21,600 seconds.

## 6. Spatial Coverage

| Property | Value |
|----------|-------|
| Latitude range | 22.75°N to 23.25°N |
| Longitude range | 72.25°E to 73.00°E |
| Grid resolution | 0.25° × 0.25° |
| Grid points | 3 × 4 = 12 |
| Grid type | Regular latitude/longitude |
| Scanning direction | Standard (i positive, j negative) |

## 7. Accumulation Analysis

All three radiation variables are **accumulated quantities** (GRIB_stepType: accum):

| Variable | Units | Accumulation Period | Conversion to W/m² |
|----------|-------|--------------------|--------------------|
| `fdir` | J m⁻² | 6 hours | Divide by 21,600 |
| `ssr` | J m⁻² | 6 hours | Divide by 21,600 |
| `str` | J m⁻² | 6 hours | Divide by 21,600 |

**Source:** ECMWF ERA5 data documentation — "To get Watts per square metre, the accumulated values need to be divided by the time period in seconds over which the data has been accumulated."

## 8. Comparison with Existing Datasets

### 8.1 vs ERA5-Land (`data/raw/weather/data_0.nc`)

| Property | ERA5 Radiation | ERA5-Land | Match? |
|----------|---------------|-----------|--------|
| Time range | 2010-03-01 to 2010-03-31 | 2010-03-01 to 2010-03-31 | YES |
| Timestamps | 124 | 124 | YES |
| Grid resolution | 0.25° | 0.1° | NO (different) |
| Latitude range | 22.75-23.25 | 22.8-23.2 | NO (radiation wider) |
| Longitude range | 72.25-73.0 | 72.4-72.8 | NO (radiation wider) |
| Variables | fdir, ssr, str | t2m, d2m, u10, v10, sp, ssrd, strd | Complementary |

**Key finding:** The radiation file has 0.25° resolution while ERA5-Land has 0.1° resolution. The radiation file covers a wider spatial domain. These are different ERA5 products (single levels vs land).

### 8.2 vs ERA5-HEAT Reference (`cde4e619...nc`)

| Property | ERA5 Radiation | ERA5-HEAT | Match? |
|----------|---------------|-----------|--------|
| Latitude range | 22.75-23.25 | 22.75-23.25 | YES |
| Longitude range | 72.25-73.0 | 72.25-73.0 | YES |
| Grid resolution | 0.25° | 0.25° | YES |
| Time range | March 2010 only | 2010-2026 | Radiation subset |
| Variables | fdir, ssr, str | mrt, utci | Different |

**Key finding:** The radiation file and ERA5-HEAT share the same spatial grid (0.25°, same lat/lon bounds). This is expected — both are ERA5 single-level products. The radiation file covers only March 2010 while ERA5-HEAT covers 2010-2026.

## 9. Suitability for Di Napoli MRT

The Di Napoli et al. (2020) MRT method requires 5 radiation fluxes:

| Required Flux | ECMWF Variable | Present? | Notes |
|---------------|---------------|----------|-------|
| S_srf_dn (downward shortwave) | `ssrd` | **NOT in this file** | Available in ERA5-Land (`data_0.nc`) |
| S_srf_net (net shortwave) | `ssr` | **YES** | In this radiation file |
| S_srf_dn,direct (direct shortwave) | `fdir` | **YES** | In this radiation file |
| L_srf_dn (downward longwave) | `strd` | **NOT in this file** | Available in ERA5-Land (`data_0.nc`) |
| L_srf_net (net longwave) | `str` | **YES** | In this radiation file |

**Required for MRT but missing from this file:** `ssrd` and `strd` — these are available in `data/raw/weather/data_0.nc` (ERA5-Land).

**Complete MRT input set requires combining:**
1. ERA5-Land (`data_0.nc`) for: `ssrd`, `strd`, `t2m`, `d2m`, `u10`, `v10`, `sp`
2. ERA5 radiation (this file) for: `fdir`, `ssr`, `str`

## 10. Derived Quantities Available

From the 5 radiation fluxes (3 from this file + 2 from ERA5-Land), the following can be computed per Di Napoli equations 3-5:

| Derived Quantity | Equation | Required Inputs |
|-----------------|----------|-----------------|
| L_srf_up (upward longwave) | L_srf_dn − L_srf_net | `strd` (ERA5-Land) + `str` (this file) |
| S_srf_dn,diffuse (diffuse shortwave) | S_srf_dn − S_srf_dn,direct | `ssrd` (ERA5-Land) + `fdir` (this file) |
| S_srf_up (upward shortwave) | S_srf_dn − S_srf_net | `ssrd` (ERA5-Land) + `ssr` (this file) |

Plus solar geometry (declination, zenith angle, hour angle) — all derivable from time and coordinates.

## 11. Issues and Considerations

### 11.1 Resolution Mismatch
The radiation file is at 0.25° resolution while ERA5-Land is at 0.1°. For MRT computation:
- Option A: Interpolate ERA5-Land to 0.25° grid
- Option B: Interpolate radiation to 0.1° grid
- Option C: Use 0.25° grid for all computations (simpler, recommended for initial validation)

### 11.2 Spatial Extent Mismatch
The radiation file covers 22.75-23.25°N, 72.25-73.0°E while ERA5-Land covers 22.8-23.2°N, 72.4-72.8°E. The radiation file is a superset. Extract the overlapping region for MRT computation.

### 11.3 6-Hourly Temporal Resolution
The radiation data is 6-hourly (not hourly). This means:
- MRT will be computed at 6-hour intervals
- For hourly MRT, would need to download hourly radiation data
- For initial validation, 6-hourly is acceptable

### 11.4 `str` Sign Convention
The `str` values are negative (net longwave is upward). This is correct — the surface loses energy via longwave radiation. The Di Napoli method accounts for this sign convention.

## 12. Final Status

```
ERA5 RADIATION INPUTS VERIFIED
```

All three required radiation variables (`fdir`, `ssr`, `str`) are present in the downloaded file with correct metadata, units, and accumulation type. The file is suitable for the Di Napoli et al. (2020) MRT methodology when combined with ERA5-Land for `ssrd` and `strd`.

---

**Document version:** 1.0
**Created:** 2026-08-31
**Task:** ERA5 Radiation Input Verification
**Next step:** Implement + validate full Di Napoli MRT against ERA5-HEAT MRT
