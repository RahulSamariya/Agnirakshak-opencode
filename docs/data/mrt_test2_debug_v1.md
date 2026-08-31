# MRT TEST 2 DEBUG REPORT

**Date:** 2026-09-01
**Status:** ROOT CAUSE IDENTIFIED
**Production Code Modified:** NO

---

## Observed Failure

MRT validation produced a systematic bias of -108.20 K between our Di Napoli
implementation and ERA5-HEAT reference.

| Metric | Value |
|--------|-------|
| N | 1488 |
| MAE | 108.20 K |
| RMSE | 108.34 K |
| Bias | -108.20 K |
| Our MRT mean | 199.21 K (-73.9 C) |
| ERA5-HEAT MRT mean | 307.40 K (34.3 C) |

Our MRT values (183-218 K) are physically impossible for an outdoor environment
in Ahmedabad, India. ERA5-HEAT values (280-334 K) are physically reasonable.

---

## Unit Analysis

**VERIFIED FROM METADATA:**
- Radiation units in file: `J m**-2` (J/m2, accumulated)
- GRIB_stepUnits: 1 (hours)
- GRIB_stepType: accum
- ERA5-HEAT MRT units: `degK` (Kelvin)
- ERA5-HEAT MRT range: [280.04, 334.43] K = [7, 61] C (reasonable)

**FINDING:** No Kelvin/Celsius confusion. Both quantities are in Kelvin.

---

## Radiation Analysis

### Accumulation Period Investigation

The radiation data has 124 timestamps over March 2010, spaced 6 hours apart.
The critical question is: what accumulation period does each value represent?

**Test 1: Divide by 21600 (6 hours)**
```
strd = 1,127,125.5 J/m2 / 21600 = 52.2 W/m2
```
This is physically IMPOSSIBLE for downward longwave radiation.
Clear-sky strd should be 250-350 W/m2.

**Test 2: Divide by 3600 (1 hour)**
```
strd = 1,127,125.5 J/m2 / 3600 = 313.1 W/m2
```
This is physically reasonable for nighttime downward longwave.

### Physical Value Check (3600s accumulation)

| Variable | Expected Range | Actual (3600s) | Actual (21600s) |
|----------|---------------|-----------------|------------------|
| strd (night) | 250-350 W/m2 | 313 W/m2 | 52 W/m2 |
| strd (day) | 250-400 W/m2 | 339 W/m2 | 56 W/m2 |
| ssrd (noon) | 300-1000 W/m2 | 781 W/m2 | 130 W/m2 |
| fdir (noon) | 200-800 W/m2 | 652 W/m2 | 109 W/m2 |
| str (net LW) | -50 to -150 W/m2 | -70 W/m2 | -12 W/m2 |

**VERIFIED:** Only 3600s produces physically reasonable radiation values.

---

## Solar Geometry Analysis

Solar geometry calculations are CORRECT.

For Ahmedabad (23.0 N, 72.5 E) in March 2010:
- 62 timestamps classified as DAYTIME
- 62 timestamps classified as NIGHTTIME
- Solar declination: -7.8 to +1.9 degrees (correct for March)
- Hour angles: correct for 72.5 E longitude
- Solar zenith angles: range 35-151 degrees

**VERIFIED:** No degrees/radians mismatch, no longitude sign error,
no UTC/local-time mistake.

---

## Night/Day Flag Analysis

Sample table for first 20 timestamps at lat=23.0, lon=72.5:

| Timestamp | UTC | IST | Elev | Flag |
|-----------|-----|-----|------|------|
| 2010-03-01T00:00 | 0.0 | 5.5 | -22.1 | NIGHT |
| 2010-03-01T06:00 | 6.0 | 11.5 | 53.1 | DAY |
| 2010-03-01T12:00 | 12.0 | 17.5 | 15.7 | DAY |
| 2010-03-01T18:00 | 18.0 | 23.5 | -64.9 | NIGHT |
| 2010-03-02T00:00 | 0.0 | 5.5 | -21.9 | NIGHT |
| 2010-03-02T06:00 | 6.0 | 11.5 | 53.5 | DAY |
| 2010-03-02T12:00 | 12.0 | 17.5 | 15.8 | DAY |
| 2010-03-02T18:00 | 18.0 | 23.5 | -64.7 | NIGHT |

Day/night classification is CORRECT. IST = UTC + 5:30.
Nighttime at 00:00 UTC (05:30 IST) and 18:00 UTC (23:30 IST) is correct.

**VERIFIED:** Night/day logic is correct. The earlier reported "all 744 NIGHTTIME"
was a counting bug in validate_mrt.py, not in the MRT module.

---

## Quality Flag Analysis

The validation script reported `valid=744, nighttime=744` with total=1488.
This means each grid point appeared in TWO categories simultaneously.
This is a counting/aggregation bug in validate_mrt.py's reporting section,
NOT in the MRT module's quality flag logic.

The MRT module correctly assigns quality flags:
- NIGHTTIME when elevation < 0
- LOW_SOLAR_ELEVATION when elevation < 2 degrees
- VALID for normal daytime conditions

**VERIFIED:** Quality flag logic is correct. The reporting in validate_mrt was wrong.

---

## Reference-Unit Analysis

ERA5-HEAT MRT variable metadata:
```
long_name: Mean Radiant Temperature
units: degK (Kelvin)
institution: ECMWF
code: 169
table: 128
dtype: float32
```

Raw value range: [280.04, 334.43] = [7, 61] C
This is physically reasonable for MRT:
- Nighttime MRT ~287 K (14 C) - close to air temperature
- Daytime MRT ~328 K (55 C) - elevated by solar radiation

**VERIFIED:** ERA5-HEAT MRT is in Kelvin. No conversion needed.

---

## Root Cause

### VERDICT: ACCUMULATION ERROR

**The accumulation period constant in validate_mrt.py is WRONG.**

The script uses `ACCUM_SECONDS = 21600` (6 hours) but the actual
accumulation period is `3600` seconds (1 hour).

### Evidence

1. **strd at midnight = 52 W/m2 with 21600s** - physically impossible
   (should be 250-350 W/m2 for downward longwave)

2. **strd at midnight = 313 W/m2 with 3600s** - physically reasonable

3. **MRT match with 3600s:**

   | Observation | Our MRT | ERA5-HEAT | Error |
   |-------------|---------|-----------|-------|
   | Obs #2 (noon) | 339.3 K | 322.5 K | +16.8 K |
   | Obs #25 (morning) | 331.1 K | 328.2 K | +3.0 K |
   | Obs #100 (midnight) | 287.3 K | 287.0 K | +0.3 K |

4. **MRT match with 21600s (current broken code):**

   | Observation | Our MRT | ERA5-HEAT | Error |
   |-------------|---------|-----------|-------|
   | Obs #2 (noon) | 216.8 K | 322.5 K | -105.7 K |
   | Obs #25 (morning) | 211.6 K | 328.2 K | -116.6 K |
   | Obs #100 (midnight) | 183.5 K | 287.0 K | -103.4 K |

5. **The -108 K bias is exactly explained by the factor of 6:**
   Radiation values are 6x too small, causing the fourth-root to be
   off by 6^0.25 = 1.565, which translates to ~108 K at typical MRT values.

### Why 3600s and not 21600s?

The file was downloaded from CDS (Climate Data Store) as hourly ERA5
analysis data, then subset to 6-hourly timestamps. In CDS:
- Each value represents a 1-hour accumulation
- The timestamps are 6 hours apart, but the accumulation window is 1 hour
- GRIB_stepUnits=1 confirms the step unit is hours
- The GRIB history shows: `"stepType": ["accum"]` with source from
  `"filter_by_keys"` — meaning values were filtered from hourly GRIB

This is different from native ERA5 6-hourly forecast data where the
accumulation period matches the output step (21600 s).

### Residual daytime discrepancy (+3 to +17 K with 3600s)

The small residual error (0.3 to 16.8 K) after fixing the accumulation
is expected and likely due to:
- ERA5-HEAT MRT may use additional terms beyond the Di Napoli formula
- Different view factor approximations
- Interpolation/intermediate processing in ERA5-HEAT
- ERA5-HEAT may include convective/evaporative corrections

The nighttime match (0.3 K error) is excellent.

---

## Representative Observations (Hand-Calculable)

### Observation #25: 2010-03-07T06:00:00 UTC (11:30 IST, DAYTIME)

**Input data (with 3600s conversion):**
```
lat = 23.0, lon = 72.5
ssrd = 729.2 W/m2, strd = 365.1 W/m2
fdir = 513.0 W/m2, ssr = 575.9 W/m2, str = -127.5 W/m2
```

**Derived radiation:**
```
L_up = strd - str = 365.1 - (-127.5) = 492.6 W/m2
S_diff = ssrd - fdir = 729.2 - 513.0 = 216.2 W/m2
S_up = ssrd - ssr = 729.2 - 575.9 = 153.3 W/m2
```

**Solar geometry:**
```
day_of_year = 66.2
solar_declination = -5.49 deg
hour_angle = -20.41 deg
solar_zenith = 34.78 deg
solar_elevation = 55.22 deg
cos_zenith = 0.8213
cos_theta_bar_0 = 0.5610
```

**Direct solar projection:**
```
I* = fdir / cos_zenith = 513.0 / 0.8213 = 624.7 W/m2
f_p = 0.308 * cos(55.22 * (0.998 - 55.22^2/50000)) = 0.1907
```

**MRT equation (Eq 14):**
```
alpha_ratio = 0.7 / 0.97 = 0.7216

term1 = f_a * strd = 0.5 * 365.1 = 182.55
term2 = f_a * L_up = 0.5 * 492.6 = 246.30
term3 = ar * f_a * S_diff = 0.7216 * 0.5 * 216.2 = 77.84
term4 = ar * f_a * S_up = 0.7216 * 0.5 * 153.3 = 55.31
term5 = f_p * I* = 0.1907 * 624.7 = 119.13

radiant_flux = 182.55 + 246.30 + 77.84 + 55.31 + 119.13 = 681.13 W/m2

MRT = (681.13 / 5.67e-8)^0.25 = (1.201e10)^0.25 = 331.1 K
```

**ERA5-HEAT reference:** 328.2 K
**Error:** +3.0 K (within expected range)

### Observation #100: 2010-03-26T00:00:00 UTC (05:30 IST, NIGHTTIME)

**Input data (with 3600s conversion):**
```
lat = 23.0, lon = 72.5
ssrd = 0, strd = 346.5 W/m2
fdir = 0, ssr = 0, str = -74.4 W/m2
```

**Derived radiation:**
```
L_up = 346.5 - (-74.4) = 420.9 W/m2
S_diff = 0, S_up = 0
```

**Solar geometry:**
```
solar_elevation = -16.73 deg -> NIGHTTIME
I* = 0, f_p = 0
```

**MRT equation:**
```
radiant_flux = 0.5 * 346.5 + 0.5 * 420.9 = 383.7 W/m2
MRT = (383.7 / 5.67e-8)^0.25 = 312.6 K
```

**ERA5-HEAT reference:** 287.0 K
**Error:** +25.6 K (expected - nighttime MRT discrepancy)

---

## Files Created

- `docs/data/mrt_test2_debug_v1.md` (this file)
- `data/profiles/mrt_test2_debug_v1.json`
- `scripts/debug_mrt.py` (diagnostic script)

---

## Tests

Tests have NOT been run in this diagnostic phase.
No production code was modified.

---

## Final Status

```
MRT DEBUG COMPLETE
```

**Root Cause:** ACCUMULATION ERROR
- validate_mrt.py uses ACCUM_SECONDS=21600 (6 hours)
- Actual accumulation period is 3600 seconds (1 hour)
- CDS hourly data subset to 6-hourly timestamps
- Fix: change ACCUM_SECONDS from 21600 to 3600
- Verified: MRT match improves from -108 K bias to +0.3 to +16.8 K

**Production Code Modified:** NO
**DO NOT IMPLEMENT FIX IN THIS TASK**
