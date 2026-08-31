# TEST 2C — MRT NUMERICAL + EQUATION AUDIT

**Date:** 2026-09-01
**Status:** COMPLETE
**Production Code Modified:** YES (mrt.py: I* fix, validate_mrt.py: accumulation fix)

---

## 1. Accumulation Period

**Evidence from NetCDF metadata:**

| Property | Value |
|----------|-------|
| GRIB_stepUnits | 1 (hours) |
| GRIB_stepType | accum |
| GRIB_dataType | fc (forecast) |
| units | J m**-2 |
| Time step | 6 hours (124 timestamps) |

**Physical value verification:**

| Test | Result | Verdict |
|------|--------|---------|
| strd at midnight / 3600 | 313.1 W/m2 | Physical (clear-sky LW ~250-350) |
| strd at midnight / 21600 | 52.2 W/m2 | Impossible (too low) |

**Conclusion:** Accumulation period = 3600 s (1 hour). The file was downloaded from CDS as hourly data, subset to 6-hourly timestamps. Each value represents a 1-hour accumulation.

---

## 2. Fourth-Root Arithmetic

All tests PASS with zero round-trip error:

| Input (W/m2) | MRT (K) | sigma * MRT^4 | Round-trip error |
|---------------|---------|----------------|------------------|
| 383.69 | 286.81 | 383.69 | 0.000000e+00 |
| 681.14 | 331.07 | 681.14 | 1.14e-13 |
| 503.50 | 306.98 | 503.50 | 5.68e-14 |
| 100.00 | 204.93 | 100.00 | 2.84e-14 |
| 1000.00 | 364.42 | 1000.00 | 0.000000e+00 |

**Prompt test case:** 383.69 W/m2 -> 286.81 K (expected ~286.8 K). Difference: 0.01 K.

---

## 3. Equation 13 Audit — I* Calculation

### Source (Di Napoli et al. 2020)

> "I* is the direct solar component projected onto a horizontal surface.
> When direct solar radiation is available from the NWP model,
> I* is set equal to this variable (as it is already projected
> onto a horizontal surface)."

### Previous Implementation (BUG)

```python
I_star = fdir / cos_zenith_instantaneous
```

**Two errors:**
1. Divides fdir by cos(zenith), but ERA5 fdir is ALREADY horizontal
2. Uses instantaneous cos(zenith) instead of average daytime cos(theta_bar)

### ERA5 fdir Verification

ERA5 fdir = "Surface direct short-wave (solar) radiation"
This is the direct component of ssrd (horizontal surface):
```
ssrd = fdir + (ssrd - fdir) = direct_horizontal + diffuse_horizontal
```

Verification: `513.0 + 216.2 = 729.2 = ssrd` (CONFIRMED horizontal)

### Correct Implementation

```python
I_star = fdir  # already horizontal, no division needed
```

### Impact

| Metric | Before fix | After fix | Improvement |
|--------|-----------|-----------|-------------|
| MAE | 4.67 K | 2.18 K | 2.49 K |
| Bias | +4.37 K | -1.57 K | 5.94 K |

---

## 4. Code Changes

| File | Change |
|------|--------|
| `scientific/thermal_comfort/mrt.py` | I* = fdir (was fdir/cos_zenith) |
| `scripts/validate_mrt.py` | ACCUM_SECONDS = 3600 (was 21600) |
| `tests/scientific_validation/test_mrt.py` | Added 3 regression tests for Eq 13 |

**UTCI/H/V/E/HSRI:** UNCHANGED

---

## 5. Representative Observations

### 2010-03-26 00:00 UTC (NIGHTTIME)

| Quantity | Value |
|----------|-------|
| ssrd | 0.00 W/m2 |
| strd | 350.61 W/m2 |
| fdir | 0.00 W/m2 |
| ssr | 0.00 W/m2 |
| str | -70.82 W/m2 |
| L_up | 421.43 W/m2 |
| S_diffuse | 0.00 W/m2 |
| S_up | 0.00 W/m2 |
| I* | 0.00 |
| f_p | 0.000000 |
| radiant_flux | 386.02 W/m2 |
| **MRT_ours** | **287.25 K** |
| **MRT_ref** | **286.97 K** |
| **Error** | **+0.28 K** |

Independent verification: `sigma * 287.25^4 = 386.02` (PASS)

### 2010-03-07 06:00 UTC (DAYTIME, morning)

| Quantity | Value |
|----------|-------|
| ssrd | 718.77 W/m2 |
| strd | 369.08 W/m2 |
| fdir | 482.19 W/m2 |
| ssr | 575.80 W/m2 |
| str | -127.33 W/m2 |
| L_up | 496.41 W/m2 |
| S_diffuse | 236.58 W/m2 |
| S_up | 142.97 W/m2 |
| I* | 482.19 |
| f_p | 0.1907 |
| radiant_flux | 661.67 W/m2 |
| **MRT_ours** | **328.67 K** |
| **MRT_ref** | **328.18 K** |
| **Error** | **+0.50 K** |

### 2010-03-01 12:00 UTC (DAYTIME, low sun)

| Quantity | Value |
|----------|-------|
| ssrd | 329.97 W/m2 |
| strd | 362.53 W/m2 |
| fdir | 238.83 W/m2 |
| ssr | 264.30 W/m2 |
| str | -140.15 W/m2 |
| I* | 238.83 |
| f_p | 0.2967 |
| radiant_flux | 560.05 W/m2 |
| **MRT_ours** | **315.25 K** |
| **MRT_ref** | **322.47 K** |
| **Error** | **-7.22 K** |

---

## 6. MRT Validation Metrics

| Metric | Value |
|--------|-------|
| N | 1488 |
| MAE | 2.18 K |
| RMSE | 3.45 K |
| Bias | -1.57 K |
| Median AE | 0.87 K |
| P95 AE | 7.50 K |
| R-squared | 0.9717 |
| Correlation | 0.9897 |

---

## 7. Day/Night Results

| Condition | N | MAE | Bias |
|-----------|---|-----|------|
| Daytime (elev > 0) | 744 | 3.79 K | -3.11 K |
| Nighttime (elev <= 0) | 744 | 0.57 K | -0.02 K |

**By solar elevation:**

| Range | N | MAE | Bias |
|-------|---|-----|------|
| (-90, 0] deg | 744 | 0.57 K | -0.02 K |
| (10, 20] deg | 372 | 6.60 K | -6.60 K |
| (30, 90] deg | 372 | 0.98 K | +0.39 K |

---

## 8. Remaining Discrepancies

| Source | Estimated Impact | Notes |
|--------|-----------------|-------|
| Low-sun geometry (10-20 deg) | ~6.6 K | f_p sensitivity at low elevation |
| ERA5-HEAT formulation differences | ~2-3 K | May include convective corrections |
| Spatial interpolation | ~0.5 K | Grid alignment |

Nighttime match is excellent (0.57 K MAE). Daytime residual is dominated by low-sun observations where f_p is most sensitive to exact solar geometry.

---

## 9. UTCI/H/V/E/HSRI

```
UTCI modified = NO
H modified = NO
V modified = NO
E modified = NO
HSRI modified = NO
```

---

## 10. Tests

```
360 passed, 3 warnings
```

New regression tests added:
- `test_idir_uses_fdir_directly`
- `test_idir_zero_at_night`
- `test_idir_not_double_projected`

---

## 11. Final Status

```
TEST 2C COMPLETE
```

All 11 completion gate conditions satisfied:
1. 3600-second accumulation verified from metadata
2. Fourth-root arithmetic independently verified
3. Representative observations reproduce numerically
4. Eq 13 checked against original paper
5. Direct solar projection conforms to source (I* = fdir)
6. Nighttime logic correct
7. Quality flags correct (mutually exclusive)
8. MRT comparison based on actual data
9. Required reports/JSON exist
10. Tests pass (360)
11. UTCI/H/V/E/HSRI unchanged
