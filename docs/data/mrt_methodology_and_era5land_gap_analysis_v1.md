# MRT METHODOLOGY AND ERA5-LAND VARIABLE GAP ANALYSIS

## 1. Objective

Before implementing any MRT calculation, verify the scientific methodology used by ERA5-HEAT and determine whether our actual ERA5-Land variables are sufficient to reproduce or approximate it. This is research + gap analysis only — no production code changes.

## 2. Primary Sources

| # | Source | Authors/Org | Type | DOI/URL |
|---|--------|-------------|------|---------|
| 1 | "Mean radiant temperature from global-scale numerical weather prediction models" | Di Napoli, Hogan, Pappenberger (2020) | Peer-reviewed paper | doi:10.1007/s00484-020-01900-5 |
| 2 | ERA5-HEAT: Universal Thermal Climate Index on a single grid | ECMWF | Documentation | https://atmosphere.copernicus.eu/era5-heat-universal-thermal-climate-index-single-grid |
| 3 | ERA5-Land hourly data from 1950 to present | ECMWF/Copernicus CDS | Dataset documentation | https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land |
| 4 | ERA5 data documentation | ECMWF | Technical documentation | https://confluence.ecmwf.int/spaces/CKB/pages/76414402/ERA5+data+documentation |
| 5 | ERA5 Land data documentation | ECMWF | Technical documentation | https://confluence.ecmwf.int/spaces/CKB/pages/140385202/ERA5-Land+data+documentation |
| 6 | UTCI User Guide (Fiala et al. 2012) | Fiala et al. | Peer-reviewed paper | doi:10.1007/s00484-011-0424-z |
| 7 | Reference UTCI Fortran implementation | marvell/utci (GitHub) | Code | https://github.com/marvell/utci |

## 3. ERA5-HEAT MRT Methodology

### 3.1 Overview

ERA5-HEAT computes MRT following Di Napoli et al. (2020), which implements the general MRT framework from Fanger (1972) and Jendritzky et al. (1990) using NWP radiation outputs. The method divides the surroundings into upper (sky) and lower (ground) hemispheres.

### 3.2 Required Radiation Fluxes (Table 1 from Di Napoli et al. 2020)

| Name | Symbol | ECMWF Variable | Description |
|------|--------|----------------|-------------|
| Surface solar radiation downwards | S_srf_dn | `ssrd` (paramId 169) | Total downward shortwave at surface = direct + diffuse |
| Surface net solar radiation | S_srf_net | `ssr` (paramId 176) | Net shortwave = downward - upward |
| Direct solar radiation at surface | S_srf_dn,direct | `fdir` (paramId 228021) | Direct (beam) shortwave at surface |
| Surface thermal radiation downwards | L_srf_dn | `strd` (paramId 175) | Downward longwave at surface |
| Surface net thermal radiation | L_srf_net | `str` (paramId 178) | Net longwave = downward - upward |

### 3.3 Derived Quantities (Equations 3-5)

From the 5 primary fluxes, the following are derived:

- **L_srf_up** = L_srf_dn − L_srf_net (Equation 3: upward longwave from ground)
- **S_srf_dn,diffuse** = S_srf_dn − S_srf_dn,direct (Equation 4: diffuse shortwave)
- **S_srf_up** = S_srf_dn − S_srf_net (Equation 5: upward shortwave reflected from ground)

### 3.4 Solar Geometry (Equations 6-12)

**Solar zenith angle** (Equation 6):
```
cos(θ₀) = sin(δ)·sin(φ) + cos(δ)·cos(φ)·cos(h)
```

**Solar declination** δ from Julian day (Equation 8):
```
δ = (180/π) × [0.006918 − 0.399912·cos(g) + 0.070257·sin(g) − 0.006758·cos(2g) + 0.000907·sin(2g) − 0.002697·cos(3g) + 0.001480·sin(3g)]
```
where g = 360/365.25 × (JD + hr/24)

**Hour angle** h (Equation 9):
```
h = (hr − 12)·15 + λ + TC
```

**Time correction** TC (Equation 10):
```
TC = 0.004297 + 0.107029·cos(g) − 1.837877·sin(g) − 0.837378·cos(2g) − 2.340475·sin(2g)
```

**Sunrise/sunset hour angle** (Equation 11):
```
cos(h₀) = −tan(δ)·tan(φ)
```

**Average daytime cosine of solar zenith angle** (Equation 12):
```
cos(θ̄₀) = sin(δ)·sin(φ) + [1/(h_max − h_min)]·cos(δ)·cos(φ)·[sin(h_max) − sin(h_min)]
```

### 3.5 Direct Solar Component Projection (Equation 13)

```
I* = S_srf_dn,direct / cos(θ̄₀)
```

This converts horizontal flux to perpendicular-to-sun flux, accounting for Sun's movement during accumulation period.

### 3.6 Surface Projection Factor (Equation 15)

For rotationally symmetric standing/walking person (γ in degrees):
```
f_p = 0.308·cos(γ·(0.998 − γ²/50000))
```

### 3.7 MRT Equation (Equation 14)

```
MRT* = [1/σ · (f_a·L_srf_dn + f_a·L_srf_up + (α_ir/ε_p)·f_a·S_srf_dn,diffuse + (α_ir/ε_p)·f_a·S_srf_up + f_p·I*)]^0.25
```

**Constants:**
- σ = 5.67 × 10⁻⁸ W/m²K⁴ (Stefan-Boltzmann constant)
- f_a = 0.5 (angle factors for upper/lower hemispheres)
- α_ir = 0.7 (solar absorption coefficient of clothed human body)
- ε_p = 0.97 (emissivity of clothed human body)

### 3.8 Validation Results (Di Napoli et al. 2020)

Against 11 WRMC-BSRN stations worldwide:
- R² > 0.88
- Average bias: 0.42°C
- Average RMSE: 5.99°C

## 4. ERA5-Land Available Variables

### 4.1 Our Actual Data (`data/raw/weather/data_0.nc`)

| Variable | Long Name | Units | GRIB ParamId | Step Type | Shape | Grid |
|----------|-----------|-------|--------------|-----------|-------|------|
| `d2m` | 2 metre dewpoint temperature | K | 168 | instant | (124, 5, 5) | 0.25° |
| `t2m` | 2 metre temperature | K | 167 | instant | (124, 5, 5) | 0.25° |
| `ssrd` | Surface short-wave (solar) radiation downwards | J m⁻² | 169 | accum | (124, 5, 5) | 0.25° |
| `strd` | Surface long-wave (thermal) radiation downwards | J m⁻² | 175 | accum | (124, 5, 5) | 0.25° |
| `u10` | 10 metre U wind component | m s⁻¹ | 165 | instant | (124, 5, 5) | 0.25° |
| `v10` | 10 metre V wind component | m s⁻¹ | 166 | instant | (124, 5, 5) | 0.25° |
| `sp` | Surface pressure | Pa | 134 | instant | (124, 5, 5) | 0.25° |

**Source:** ERA5-Land hourly data from 1950 to present (CDS dataset: `reanalysis-era5-land`)

### 4.2 ERA5-Land Available Radiation Variables (Per Documentation)

From ECMWF documentation and CDS, ERA5-Land provides:

| Variable | GRIB Name | Units | Type |
|----------|-----------|-------|------|
| `ssrd` | Surface solar radiation downwards | J m⁻² | Accumulated |
| `strd` | Surface thermal radiation downwards | J m⁻² | Accumulated |
| `ssr` | Surface net solar radiation | J m⁻² | Accumulated |
| `str` | Surface net thermal radiation | J m⁻² | Accumulated |

**NOT available in ERA5-Land:**
- `fdir` — Direct solar radiation at surface (only in ERA5 single levels)
- `ssrdc` — Surface solar radiation downward clear-sky (only in ERA5 single levels)
- `cdir` — Clear-sky direct solar radiation at surface (only in ERA5 single levels)

### 4.3 ERA5 (Single Levels) vs ERA5-Land

| Variable | ERA5 Single Levels | ERA5-Land |
|----------|-------------------|-----------|
| `ssrd` (downward shortwave) | ✓ | ✓ |
| `ssr` (net shortwave) | ✓ | ✓ |
| `strd` (downward longwave) | ✓ | ✓ |
| `str` (net longwave) | ✓ | ✓ |
| `fdir` (direct shortwave) | ✓ | **✗ NOT AVAILABLE** |
| `ssrdc` (downward SW clear-sky) | ✓ | ✗ |
| `cdir` (direct SW clear-sky) | ✓ | ✗ |

**Critical finding:** ERA5-Land does NOT provide `fdir` (direct solar radiation at surface), which is essential for the Di Napoli et al. MRT method.

## 5. Variable Gap Matrix

| MRT Requirement | Needed by Method | Present in ERA5-Land? | Exact Variable | Can Reproduce Directly? | Notes |
|-----------------|------------------|----------------------|----------------|------------------------|-------|
| Surface temperature | Stefan-Boltzmann | **PARTIALLY** | `t2m` (air temp), no surface skin temp | NO | ERA5-Land has `t2m` but not `skt` (skin temperature). For longwave, `L_srf_up = ε·σ·T_skin⁴` requires skin temp. |
| Air temperature | UTCI input | **AVAILABLE** | `t2m` | YES | 2m air temperature, K |
| Dewpoint temperature | Humidity conversion | **AVAILABLE** | `d2m` | YES | 2m dewpoint, K. Convert to vapor pressure: `e = 6.112 × exp(17.67×(T-273.15)/(T-29.65))` |
| Wind speed | UTCI input | **AVAILABLE** | `u10`, `v10` | YES | `ws = sqrt(u² + v²)`. May need height adjustment to 1.5m. |
| Surface pressure | UTCI input | **AVAILABLE** | `sp` | YES | Pa |
| S_srf_dn (ssrd) | MRT Eq. 14 | **AVAILABLE** | `ssrd` | YES | J m⁻², accumulated. Convert to W/m² by dividing by accumulation period (3600s for hourly). |
| S_srf_net (ssr) | MRT Eqs. 5, 14 | **NOT IN OUR FILE** | Not downloaded | NO | Available in ERA5-Land but not in our current data_0.nc. Needed to compute `S_srf_up`. |
| S_srf_dn,direct (fdir) | MRT Eqs. 4, 13, 14 | **MISSING** | Not in ERA5-Land | NO | **Critical gap.** Only available in ERA5 single levels. Needed for direct/diffuse separation. |
| L_srf_dn (strd) | MRT Eq. 14 | **AVAILABLE** | `strd` | YES | J m⁻², accumulated. Convert to W/m². |
| L_srf_net (str) | MRT Eqs. 3, 14 | **NOT IN OUR FILE** | Not downloaded | NO | Available in ERA5-Land but not in our current data_0.nc. Needed to compute `L_srf_up`. |
| Solar declination δ | MRT Eq. 8 | **DERIVABLE** | Computed from Julian day | YES | Pure astronomical calculation |
| Hour angle h | MRT Eq. 9 | **DERIVABLE** | Computed from time + longitude | YES | Pure astronomical calculation |
| Solar zenith angle θ₀ | MRT Eqs. 6, 12 | **DERIVABLE** | Computed from δ, φ, h | YES | Pure astronomical calculation |
| Solar elevation angle γ | MRT Eq. 16 | **DERIVABLE** | γ = 90° − θ₀ | YES | Complementary to zenith angle |
| Average daytime cos(θ̄₀) | MRT Eq. 12 | **DERIVABLE** | Computed from δ, φ, h₁, h₂ | YES | Requires sunrise/sunset calculation |

### 5.1 Gap Classification Summary

| Classification | Count | Variables |
|----------------|-------|-----------|
| **AVAILABLE** | 5 | `t2m`, `d2m`, `u10`/`v10`, `sp`, `ssrd`, `strd` |
| **DERIVABLE** | 5 | Solar geometry (δ, h, θ₀, γ, cos(θ̄₀)) |
| **MISSING (not in ERA5-Land)** | 1 | `fdir` (direct solar radiation) — **critical** |
| **NOT DOWNLOADED** | 2 | `ssr` (net shortwave), `str` (net longwave) — available in ERA5-Land but not in our file |

## 6. Radiation Unit Analysis

### 6.1 ERA5-Land Accumulated Radiation Variables

All ERA5-Land radiation variables (`ssrd`, `strd`, `ssr`, `str`) are stored as **accumulated energy** in **J m⁻²** (Joules per square meter).

**Accumulation period:** For ERA5-Land hourly data, accumulations are over the hour ending at the validity time (same as ERA5 reanalysis).

**Source:** ECMWF ERA5 data documentation — "The accumulations (over the accumulation/processing period) in the short forecasts (from 06 and 18 UTC) of ERA5 are treated differently... in the short forecasts of ERA5, the accumulations are since the previous post processing (archiving)... for reanalysis: accumulations are over the hour (the accumulation/processing period) ending at the validity date/time."

### 6.2 Conversion to W/m²

To convert accumulated J/m² to mean flux W/m²:
```
Flux [W/m²] = Accumulation [J/m²] / 3600 [s]
```

For 3-hourly data:
```
Flux [W/m²] = Accumulation [J/m²] / 10800 [s]
```

**Source:** ECMWF Forum — "To get Watts per square metre, the accumulated values need to be divided by the time period in seconds over which the data has been accumulated."

### 6.3 Instantaneous vs Accumulated

| Variable | Type | Interpretation |
|----------|------|----------------|
| `t2m` | Instantaneous | Value at validity time |
| `d2m` | Instantaneous | Value at validity time |
| `u10`, `v10` | Instantaneous | Value at validity time |
| `sp` | Instantaneous | Value at validity time |
| `ssrd` | Accumulated | Total energy over previous hour |
| `strd` | Accumulated | Total energy over previous hour |
| `ssr` | Accumulated | Total energy over previous hour |
| `str` | Accumulated | Total energy over previous hour |

## 7. Exact Reproduction Feasibility

### Answer: NO — Exact reproduction is not possible from ERA5-Land alone.

**Reason:** The Di Napoli et al. (2020) MRT method requires `fdir` (direct solar radiation at surface), which is **not available in ERA5-Land**. This variable is only available in ERA5 single levels.

### 7.1 What `fdir` Enables

`fdir` is essential for:
1. **Direct/diffuse separation** (Equation 4): `S_srf_dn,diffuse = S_srf_dn − S_srf_dn,direct`
2. **Perpendicular plane projection** (Equation 13): `I* = S_srf_dn,direct / cos(θ̄₀)`
3. **Direct solar MRT contribution** (Equation 14): The `f_p·I*` term

### 7.2 Information Lost Without `fdir`

Without `fdir`, we lose:
- Ability to separate direct beam from diffuse shortwave radiation
- Ability to project direct solar radiation onto perpendicular-to-sun plane
- The direct solar heating component of MRT (which can contribute 10-30°C in clear-sky conditions)

### 7.3 What IS Possible Without `fdir`

We CAN compute:
- Thermal longwave MRT component (from `strd` + `str`)
- Solar diffuse component estimation (if we make assumptions)
- Solar geometry (declination, zenith angle, hour angle)

We CANNOT compute without assumptions:
- Direct vs diffuse shortwave partition
- The `f_p·I*` direct solar term

## 8. Candidate MRT Approaches

### 8.1 Approach A: Use ERA5-HEAT MRT Directly

**Description:** Download pre-computed MRT from ERA5-HEAT dataset (`cde4e619c080209e1ec505565f79b8e.nc`).

**Required inputs:** ERA5-HEAT MRT file
**Assumptions:** None — uses ERA5-HEAT's own MRT
**Source:** ERA5-HEAT dataset (CDS: `reanalysis-era5-single-levels-heat`)
**Limitations:**
- 0.25° resolution (not 0.1° like ERA5-Land)
- Temporal coverage limited to ERA5-HEAT availability
- Cannot compute MRT independently

**Validation strategy:** Compare against BSRN station observations (as in Di Napoli et al. 2020)

### 8.2 Approach B: Approximate MRT from ERA5-Land (Isotropic Shortwave)

**Description:** Assume isotropic diffuse shortwave and estimate direct component from `ssrd` and solar geometry.

**Required inputs:** `ssrd`, `strd`, `t2m`, `d2m`, `u10`, `v10`, `sp`
**Assumptions:**
1. All shortwave is diffuse (no direct beam separation) — **very strong assumption**
2. Or: Estimate direct/diffuse split using empirical clearness index (e.g., Orgill & Hollands 1977)
3. Ground reflectance albedo ≈ 0.2 (typical)

**Source:** Simplified version of Di Napoli et al. (2020), adapted for isotropic sky
**Limitations:**
- Significant error in clear-sky conditions (direct beam dominates)
- Better performance in overcast conditions
- Estimated RMSE: 10-20°C (vs 6°C for full method)

**Validation strategy:** Compare against ERA5-HEAT MRT as reference

### 8.3 Approach C: Empirical MRT Approximation

**Description:** Use empirical relationship MRT ≈ T_air + f(RH, wind, radiation)

**Required inputs:** `t2m`, `d2m`, `u10`, `v10`, `ssrd`
**Assumptions:**
- Linear or polynomial relationship between MRT and air temperature
- Radiation correction factor based on clearness index

**Source:** Thorsson et al. (2007), Lindberg et al. (2008) — simplified MRT estimation
**Limitations:**
- Site-specific calibration required
- Poor transferability across climates
- Estimated RMSE: 5-15°C

**Validation strategy:** Calibrate against ERA5-HEAT, validate against independent period

### 8.4 Approach D: Download Missing ERA5 Variables

**Description:** Download `fdir`, `ssr`, `str` from ERA5 single levels and combine with ERA5-Land data.

**Required inputs:** ERA5 single levels file + ERA5-Land file
**Assumptions:** ERA5 and ERA5-Land are consistent at 0.25° resolution
**Source:** ERA5 dataset (CDS: `reanalysis-era5-single-levels`)
**Limitations:**
- Requires additional data download
- Mixing two datasets (potential inconsistency)
- 0.25° resolution (not 0.1°)

**Validation strategy:** Full Di Napoli et al. (2020) methodology

## 9. Validation Methodology

### 9.1 Reference Data

- **ERA5-HEAT MRT** as primary reference (validated against BSRN, R² > 0.88)
- Our existing ERA5-HEAT file: `cde4e619c080209e1ec505565f79b8e.nc`

### 9.2 Comparison Metrics

For each candidate approach vs ERA5-HEAT MRT:
- Mean Absolute Error (MAE)
- Root Mean Square Error (RMSE)
- Bias (mean error)
- Median Absolute Error
- P95 Absolute Error
- Correlation coefficient (R²)

### 9.3 Stratification

Results should be stratified by:
- **Daytime vs nighttime** (MRT differs by 10-30°C)
- **Solar conditions** (clear vs overcast)
- **MRT − T_air difference** (indicates radiation contribution)
- **Radiation intensity** (high vs low solar input)

### 9.4 Acceptance Thresholds

No predetermined thresholds are set. The analysis should report observed performance and let the project team decide based on:
- Scientific requirements for heat stress assessment
- Comparison with UTCI sensitivity to MRT errors
- Operational needs

## 10. Architectural Options

### OPTION A: ERA5-HEAT MRT → UTCI

**For historical/reference processing:**
```
ERA5-HEAT MRT (0.25°) → UTCI → HSRI
```

**Advantages:**
- Scientifically validated (Di Napoli et al. 2020)
- MRT proven against BSRN stations
- No approximation needed
- Reproducible

**Disadvantages:**
- 0.25° resolution (~25 km)
- Limited temporal coverage
- Cannot compute MRT independently
- Dependency on ERA5-HEAT availability

### OPTION B: ERA5-Land → Derived MRT → UTCI

**For higher-resolution processing:**
```
ERA5-Land (0.1°) → Derived MRT → UTCI → HSRI
```

**Advantages:**
- 0.1° resolution (~10 km)
- Longer temporal coverage
- Can compute MRT independently
- More flexible

**Disadvantages:**
- Requires MRT approximation (introduces error)
- Missing `fdir` variable
- Validation needed
- Potential accuracy loss

### 10.1 Trade-off Summary

| Criterion | Option A (ERA5-HEAT) | Option B (ERA5-Land derived) |
|-----------|---------------------|------------------------------|
| Scientific fidelity | High | Medium (approximation) |
| Spatial resolution | 0.25° (~25 km) | 0.1° (~10 km) |
| Computational complexity | Low (pre-computed) | High (must compute) |
| Reproducibility | High | Medium |
| Data availability | Limited to ERA5-HEAT period | Longer coverage |
| Missing variable impact | None | Significant (no fdir) |

### 10.2 Recommendation

**For current implementation:** Use Option A (ERA5-HEAT MRT) for historical/reference processing where ERA5-HEAT data is available. This provides scientifically validated MRT with known accuracy.

**For future exploration:** Investigate Option B only if:
1. Higher spatial resolution is required
2. ERA5-HEAT data is unavailable for the target period
3. Acceptable approximation methods are identified and validated

## 11. Recommendation

### 11.1 Immediate Action

**Use ERA5-HEAT MRT directly** for UTCI computation when ERA5-HEAT data is available. This is the scientifically validated approach with proven accuracy.

### 11.2 Gap Analysis Conclusion

**Exact reproduction of ERA5-HEAT MRT from ERA5-Land variables alone is NOT possible** due to the missing `fdir` (direct solar radiation) variable, which is only available in ERA5 single levels, not ERA5-Land.

### 11.3 If Higher Resolution is Required

Consider Approach D (download missing ERA5 variables) as the most scientifically sound option, combining ERA5-Land for meteorological variables with ERA5 single levels for radiation components.

## 12. Open Scientific Questions

1. **Can the direct/diffuse shortwave split be estimated from `ssrd` alone?**
   - Possible approaches: clearness index methods (Orgill & Hollands 1977, Erbs et al. 1982)
   - Accuracy unknown without validation

2. **How sensitive is UTCI to MRT errors?**
   - UTCI has ±1.1°C accuracy for MRT input
   - MRT errors propagate through UTCI polynomial
   - Need sensitivity analysis

3. **Is the 0.25° to 0.1° resolution improvement worth the approximation error?**
   - Depends on spatial variability of heat stress in Ahmedabad
   - Urban heat island effects may require higher resolution
   - But MRT approximation error may exceed resolution benefit

4. **Can ERA5-Land skin temperature (`skt`) improve longwave MRT estimation?**
   - ERA5-Land does not provide `skt` in our current download
   - But it may be available in the full ERA5-Land dataset
   - Could improve `L_srf_up` computation

5. **What is the actual accumulation period for our ERA5-Land data?**
   - Documentation says hourly, but need to verify from data metadata
   - Critical for correct J/m² → W/m² conversion

---

**Document version:** 1.0
**Created:** 2026-08-30
**Task:** MRT Methodology Verification — ERA5-Land Variable Gap Analysis
**Production MRT code:** NOT IMPLEMENTED
**UTCI/H/V/E/HSRI:** UNCHANGED
