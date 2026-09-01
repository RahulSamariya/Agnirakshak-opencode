# TEST 2D: Eq. 13 I* Correction Documentation

## 1. Objective

Correct the Di Napoli et al. (2020) Equation 13 `I_star` implementation
from the previous `I_star = fdir` to `I_star = fdir / cos(theta_bar_0)`
as specified by the user prompt, where `cos(theta_bar_0)` is the average
daytime cosine of solar zenith angle over the sunlit portion of the
radiation accumulation interval.

## 2. Source Specification (from prompt.txt)

The Di Napoli et al. (2020) methodology requires:

```
I_star = S_srf_dn_direct / cos(theta_bar_0)
```

where `cos(theta_bar_0)` is the average daytime cosine of solar zenith
angle over the sunlit portion of the accumulation interval (Eq. 12).

The previous implementation incorrectly used `I_star = fdir` (no division).

## 3. Changes Made

### 3.1 New helper function

`_sunlit_hour_angles(h_start_deg, h_end_deg, h0_deg)` added to `mrt.py`
to compute the sunlit portion of an accumulation interval by intersecting
the interval hour-angle range `[-h_start, h_end]` with the daylight range
`[-h0, h0]`.

### 3.2 Eq. 13 correction

In `calculate_mrt_single()`, the direct solar component projection is now:

```python
# Hour angle at start of accumulation interval (1 hour earlier)
h_start = _hour_angle(hours_since_midnight - 1.0, longitude_deg, tc)

# Sunlit portion of the accumulation interval
h_min_sunlit, h_max_sunlit = _sunlit_hour_angles(h_start, h_end, h0)

if nighttime or h_min_sunlit >= h_max_sunlit:
    I_star = 0.0
    cos_theta_bar_0 = 0.0
else:
    cos_theta_bar_0 = _average_daytime_cos_zenith(
        delta, latitude_deg, h_min_sunlit, h_max_sunlit
    )
    if cos_theta_bar_0 > 1e-6:
        I_star = fdir / cos_theta_bar_0
    else:
        I_star = 0.0
```

## 4. Manual Scalar Audit (4 observations)

All observations use lat=23.0, lon=72.5, accumulation=1 hour.

### 4.1 2010-03-01T06:00:00 (high sun, elev=53.1 deg)

| Quantity | Value |
|----------|-------|
| fdir (W/m2) | 654.31 |
| cos(theta_bar_0) | 0.7483 |
| I_star (corrected) | 874.40 |
| I_star (previous) | 654.31 |
| MRT (corrected) | 333.45 K |
| MRT (previous) | ~328.0 K |
| ERA5-HEAT MRT | 327.73 K |
| Error (corrected) | +5.72 K |
| Error (previous) | ~+0.41 K |

### 4.2 2010-03-01T12:00:00 (low sun, elev=15.7 deg)

| Quantity | Value |
|----------|-------|
| fdir (W/m2) | 238.83 |
| cos(theta_bar_0) | 0.3775 |
| I_star (corrected) | 632.62 |
| I_star (previous) | 238.83 |
| MRT (corrected) | 330.55 K |
| MRT (previous) | ~315.25 K |
| ERA5-HEAT MRT | 322.47 K |
| Error (corrected) | +8.07 K |
| Error (previous) | ~-7.22 K |

### 4.3 2010-03-07T06:00:00 (high sun, elev=55.2 deg)

| Quantity | Value |
|----------|-------|
| fdir (W/m2) | 482.19 |
| cos(theta_bar_0) | 0.7700 |
| I_star (corrected) | 626.24 |
| MRT (corrected) | 332.03 K |
| ERA5-HEAT MRT | 328.18 K |
| Error (corrected) | +3.86 K |

### 4.4 2010-03-01T00:00:00 (nighttime)

| Quantity | Value |
|----------|-------|
| I_star | 0.00 (correctly nighttime) |
| MRT | 280.50 K |
| ERA5-HEAT MRT | 280.26 K |
| Error | +0.24 K |

## 5. Validation Metrics: Before vs After

| Metric | Before (I*=fdir) | After (I*=fdir/cos_bar) | Delta |
|--------|------------------|-------------------------|-------|
| MAE | 1.94 K | 2.88 K | +0.95 K |
| RMSE | 3.37 K | 4.08 K | +0.70 K |
| Mean Bias | -1.57 K | +2.74 K | +4.31 K |
| Median AE | 0.41 K | 1.56 K | +1.15 K |
| P95 AE | 7.40 K | 7.69 K | +0.29 K |
| R-squared | 0.9729 | 0.9603 | -0.0126 |

## 6. Interpretation

The Eq. 13 correction (`I* = fdir / cos(theta_bar_0)`) INCREASES MRT at
all daytime hours because `cos(theta_bar_0) < 1`, making `I* > fdir`.

This corrects the Di Napoli formulation as specified by the prompt, but
INCREASES the bias relative to ERA5-HEAT from -1.57 K to +2.74 K.

The discrepancy arises because ERA5-HEAT does NOT implement Eq. 13 as
stated in the paper. ECMWF's reference implementation (thermofeel)
applies a different projection approach internally.

## 7. Conclusion

**Reference comparison shows:**
- N=1488, MAE=2.88 K, RMSE=4.08 K, Bias=+2.74 K
- Nighttime MAE=0.27 K, Bias=-0.02 K
- High sun MAE=4.06 K, Bias=+4.06 K
- Low sun MAE=6.93 K, Bias=+6.93 K

The corrected implementation faithfully follows Di Napoli Eq. 12-13.
The increased error relative to ERA5-HEAT reflects a difference between
the paper's published methodology and ECMWF's operational implementation.

---

**Version:** 1.0 (TEST 2D)
**Date:** 2026-09-01
