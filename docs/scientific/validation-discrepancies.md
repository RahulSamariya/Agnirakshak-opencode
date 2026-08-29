# Scientific Validation Discrepancies

**Project:** Extreme Heatwave Early Warning and Human Thermal Stress Index
**MoES Problem Statement ID:** 26083
**Date:** 2026-08-29
**Status:** All discrepancies documented. No code modifications made to force agreement.

---

## Discrepancy 1: UTCI Reference Test Values

### Issue
The supplied reference test cases (prompt.txt) use approximate expected UTCI values that do not match any standard UTCI implementation.

### Supplied Reference vs Actual

| Case | Inputs | Prompt Expected | Our Result | Reference Fortran | Abs Diff |
|------|--------|-----------------|------------|-------------------|----------|
| 1 | Ta=30, Tmrt=30, v=0.5, RH=50% | ~32.2 | 30.4 | 30.4 | 1.8 |
| 2 | Ta=29, Tmrt=29, v=0.5, VP=20hPa | ~29.0 | 29.2 | 29.2 | 0.2 |
| 3 | Ta=30, Tmrt=35, v=1.0, RH=70% | 38.0-39.5 | 33.5 | 33.5 | 5.0 |
| 4 | Ta=0, Tmrt=0, v=5.0, RH=50% | ~-10.0 | -14.7 | -14.7 | 4.7 |

### Analysis

**Our implementation:** Fiala et al. (2012) 210-coefficient polynomial regression using exact coefficients from `pythermalcomfort` (BSD-3 licensed).

**Cross-validation:** Our results exactly match the standalone `utci` PyPI package (version 1.0.0), which is described as "exact numerical translation from the reference Fortran implementation."

**Conclusion:** The prompt reference values appear to be approximate estimates, not outputs from a validated UTCI implementation. The discrepancies are:

- **CASE 1:** 1.8C difference - likely approximate value
- **CASE 2:** 0.2C difference - close match (within rounding)
- **CASE 3:** 5.0C difference - significant; prompt value 38.0-39.5 does not match any standard UTCI calculation for these inputs
- **CASE 4:** 4.7C difference - prompt value -10.0 does not match; our -14.7 matches reference Fortran

### Resolution
**No modification made to the UTCI formula.** The actual calculation is preserved. The discrepancies are documented here.

---

## Discrepancy 2: Vulnerability Diagnostic Case

### Issue
The supplied diagnostic example expects V ~ 0.407, but our calculation yields V = 0.4006.

### Calculation

```
Weights:  age=0.160, bmi=0.117, es=0.142, si=0.092, ed=0.094, g=0.097, hi=0.198, di=0.100
Scores:   age=0.33,  bmi=0.66,  es=0.33,  si=0.33,  ed=0.33,  g=0.66, hi=0.33,  di=0.33

V = 0.160*0.33 + 0.117*0.66 + 0.142*0.33 + 0.092*0.33 + 0.094*0.33 + 0.097*0.66 + 0.198*0.33 + 0.100*0.33
  = 0.0528 + 0.0772 + 0.0469 + 0.0304 + 0.0310 + 0.0640 + 0.0653 + 0.0330
  = 0.4006
```

### Difference
0.407 - 0.4006 = 0.0064 (0.64%)

### Likely Cause
The source specification uses 0.33 and 0.66 as rounded scores. If the source used exact fractions (1/3 and 2/3), the result would be 0.4047, which is closer to 0.407 but still not exact.

### Resolution
**No modification made to the formula or weights.** The discrepancy is documented. The mathematical result is preserved.

---

## Summary

| # | Discrepancy | Severity | Resolution |
|---|-------------|----------|------------|
| 1 | UTCI reference values are approximate | Medium | Documented; no code change |
| 2 | V diagnostic 0.4006 vs 0.407 | Low | Documented; no code change |

**All discrepancies are in externally supplied reference values, not in the implementation.**
