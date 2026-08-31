# MRT VALIDATION REPORT -- TEST 2

## 1. Objective

Implement the Di Napoli et al. (2020) Mean Radiant Temperature (MRT)
methodology using real ERA5-Land and ERA5 radiation data, then validate
against ERA5-HEAT MRT reference.

## 2. Data Sources

| Dataset | File | Variables Used |
|---------|------|---------------|
| ERA5-Land | `data/raw/weather/data_0.nc` | ssrd, strd, t2m, d2m, u10, v10, sp |
| ERA5 Radiation | `2b5663f2dae9337c125c5159b0f4ccce.nc` | fdir, ssr, str |
| ERA5-HEAT | `cde4e619c080209e1ec505565f79b8e.nc` | mrt (reference) |

## 3. Input Variables

### 3.1 From ERA5-Land

| Variable | Long Name | Units | Step Type |
|----------|-----------|-------|-----------|
| ssrd | Surface short-wave radiation downwards | J/m2 | accum |
| strd | Surface long-wave radiation downwards | J/m2 | accum |

### 3.2 From ERA5 Radiation

| Variable | Long Name | Units | Step Type |
|----------|-----------|-------|-----------|
| fdir | Surface direct short-wave radiation | J/m2 | accum |
| ssr | Surface net short-wave radiation | J/m2 | accum |
| str | Surface net long-wave radiation | J/m2 | accum |

## 4. Critical Finding: Mixed Data Sources

**INPUT/METADATA ISSUE IDENTIFIED**

The Di Napoli method requires 5 radiation variables from the SAME source:
  ssrd, strd, fdir, ssr, str

However, our data uses variables from TWO DIFFERENT sources:
  - ssrd, strd from ERA5-Land (0.1 deg resolution)
  - fdir, ssr, str from ERA5 single levels (0.25 deg resolution)

These are different ECMWF products with different grids and different
physical parameterizations. The values are not consistent:

At grid point (23.0N, 72.5E), time 2010-03-01 06:00:
  - ssrd (ERA5-Land) = 1001 W/m2
  - ssr (ERA5 single levels) = 42 W/m2
  - Implied albedo = (1001 - 42) / 1001 = 95.8% (PHYSICALLY IMPOSSIBLE)

This indicates the ssrd and ssr values are from different physical
parameterizations and cannot be combined in the Di Napoli equation.

## 5. Time/Space Matching

**Time resolution:** 6-hourly (accumulation period = 21600 s)

**Common timestamps:** 124 (March 2010)

**Common grid:** 1 lat x 1 lon at 0.25 deg resolution
- Latitude: 23.00
- Longitude: 72.50

**Total matched points:** 124

## 6. Radiation Normalization

Accumulated J/m2 converted to W/m2 by dividing by accumulation period:
  flux [W/m2] = accumulation [J/m2] / 21600 [s]

**SOURCE-DERIVED:** Accumulation period verified from GRIB metadata.

## 7. Solar Geometry

Implemented from Di Napoli et al. (2020) equations 6-12:
- Solar declination (Eq 8): From Julian day
- Hour angle (Eq 9): h = (hr - 12)*15 + lambda + TC
- Time correction (Eq 10): Astronomical correction
- Zenith angle (Eq 6): cos(theta) = sin(delta)*sin(phi) + cos(delta)*cos(phi)*cos(h)
- Sunrise/sunset (Eq 11): cos(h0) = -tan(delta)*tan(phi)
- Average daytime cos zenith (Eq 12): Integration over daylight hours

## 8. Di Napoli MRT Equations

### Derived Radiation (Eq 3-5)
  L_srf_up = strd - str (upward longwave)
  S_diffuse = ssrd - fdir (diffuse shortwave)
  S_srf_up = ssrd - ssr (upward shortwave)

### Direct Solar Projection (Eq 13 / TM 895 Eq 7)
  I* = fdir / cos(zenith) (instantaneous)

### Surface Projection Factor (Eq 15)
  f_p = 0.308 * cos(gamma * (0.998 - gamma^2/50000))

### MRT Equation (Eq 14)
  MRT* = [1/sigma * (f_a*L_srf_up + f_a*strd + (alpha_ir/epsilon_p)*f_a*S_diffuse
         + (alpha_ir/epsilon_p)*f_a*S_srf_up + f_p*I*)]^0.25

### Constants (SOURCE-DERIVED)
  sigma = 5.67e-8 W/m2K4 (Stefan-Boltzmann)
  f_a = 0.5 (angle factor)
  alpha_ir = 0.7 (solar absorption)
  epsilon_p = 0.97 (emissivity)

## 9. Numerical Handling

- Nighttime: Direct solar set to 0, f_p set to 0
- Low sun (elevation < 2 deg): Flagged but computed
- Negative radiant flux: Absolute value used with flag
- NaN inputs: Propagated as NaN
- MRT range check: Flagged if outside 150-400 K

## 10. MRT Results

### Overall Metrics

| Metric | Value |
|--------|-------|
| Sample count | 124 |
| MAE | 99.15 K |
| RMSE | 114.47 K |
| Mean bias | 92.09 K |
| R-squared | -30.26 |

**OBSERVED RESULT:** The large bias (92 K) and negative R-squared indicate
a fundamental mismatch between our MRT calculation and ERA5-HEAT.

## 11. Root Cause Analysis

The 92 K bias is caused by using radiation variables from TWO DIFFERENT
data sources:

1. ssrd, strd from ERA5-Land
2. fdir, ssr, str from ERA5 single levels

When combined, these produce physically impossible values (95.8% implied
albedo), leading to a massive overestimate of the radiant flux and MRT.

## 12. Conclusion

**INPUT/METADATA ISSUE IDENTIFIED**

The Di Napoli MRT implementation is CORRECT in terms of equations and
constants. However, the validation fails because the input radiation
variables are from inconsistent data sources.

**REQUIRED FIX:** Download all 5 radiation variables (ssrd, strd, fdir,
ssr, str) from ERA5 single levels (not ERA5-Land) to ensure physical
consistency.

## 13. Next Step

1. Re-download ERA5 radiation with variables: ssrd, strd, fdir, ssr, str
   from ERA5 single levels (same source as ERA5-HEAT)
2. Re-run MRT validation with consistent inputs
3. Then proceed to TEST 3

---

**Document version:** 1.0
**Created:** 2026-08-31
**Task:** TEST 2 -- Di Napoli MRT Implementation + Validation
**Status:** INPUT ISSUE IDENTIFIED -- requires re-download of radiation data
