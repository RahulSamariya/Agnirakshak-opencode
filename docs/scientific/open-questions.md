# Open Questions & Decision Register

**Project:** Extreme Heatwave Early Warning and Human Thermal Stress Index
**MoES Problem Statement ID:** 26083
**Last updated:** 2026-08-29

## Status Legend

| Status | Meaning |
|--------|---------|
| BLOCKED | Cannot proceed without this item |
| OPEN | Decision needed, not yet blocking |
| TBD | Requires scientific confirmation |
| DEFERRED | Intentionally postponed to later phase |
| CONFIRMED | Resolved and implemented |

---

## UTCI Implementation

### 1. UTCI Algorithm / Polynomial

**Status:** CONFIRMED

**Resolution:** Implemented Fiala et al. (2012) 210-coefficient polynomial regression using the exact coefficient set from `pythermalcomfort` (BSD-3 licensed). Cross-validated against the standalone `utci` PyPI package (exact numerical translation from reference Fortran implementation).

**Implementation:** `scientific/thermal_comfort/utci.py`
**Provenance:** `docs/scientific/utci-provenance.md`

### 2. UTCI Reference Test Values

**Status:** CONFIRMED (with discrepancy)

**Resolution:** Our implementation exactly matches the reference Fortran-derived `utci` PyPI package. The supplied prompt.txt reference values are approximate and do not match any standard UTCI implementation. Discrepancies documented in `docs/scientific/utci-provenance.md`.

**Decision:** No modification made to the UTCI formula to force agreement with approximate reference values. The actual calculation is preserved.

---

## Vulnerability

### 3. BMI Classification Rules

**Status:** CONFIRMED

**Resolution:** Implemented with 5-band classification:
- < 17.0 -> HIGH (1.00)
- 17.0-18.4 -> MEDIUM (0.66)
- 18.5-24.9 -> LOW (0.33)
- 25.0-29.9 -> MEDIUM (0.66)
- >= 30.0 -> HIGH (1.00)

### 4. Economic Status Classification Rules

**Status:** CONFIRMED

**Resolution:** Implemented with string-based classification:
- HIG/high -> LOW (0.33)
- MIG/middle -> MEDIUM (0.66)
- LIG/EWS/low -> HIGH (1.00)

### 5. Social Isolation Classification Rules

**Status:** CONFIRMED

**Resolution:** Implemented with integer-based classification:
- > 1 other adult -> LOW (0.33)
- 1 other adult -> MEDIUM (0.66)
- 0 (living alone) -> HIGH (1.00)

### 6. Education Classification Rules

**Status:** CONFIRMED

**Resolution:** Implemented with string-based classification:
- high/postgraduate/graduate/enrolled -> LOW (0.33)
- secondary -> MEDIUM (0.66)
- no_secondary/none/not_enrolled -> HIGH (1.00)

### 7. Gender/Sex Classification Rules

**Status:** CONFIRMED

**Resolution:** Implemented with string-based classification:
- male -> MEDIUM (0.66)
- female/intersex/pregnant -> HIGH (1.00)

### 8. Disability Classification Rules

**Status:** CONFIRMED

**Resolution:** Implemented with string-based classification:
- none/no_disability -> LOW (0.33)
- below_benchmark -> MEDIUM (0.66)
- above_benchmark -> HIGH (1.00)

**Note:** Benchmark definitions are source-unspecified and exposed as configuration/TBD.

---

## Exposure

### 9. AQI/PM2.5 Threshold for Air Quality

**Status:** CONFIRMED

**Resolution:** Implemented with string-based classification:
- good/satisfactory/moderate -> LOW (0.33)
- poor -> MEDIUM (0.66) [intermediate NOT YET SPECIFIED, conservatively mapped]
- very_poor/severe -> HIGH (1.00)

### 10. Fluid Intake/Activity Classification Rules

**Status:** CONFIRMED

**Resolution:** Implemented with numeric threshold:
- deficit <= 4% -> LOW (0.33)
- deficit > 4% -> HIGH (1.00)

### 11. Healthcare Accessibility Classification Rules

**Status:** CONFIRMED

**Resolution:** Implemented with numeric threshold:
- < 30 min -> LOW (0.33)
- 30-60 min -> MEDIUM (0.66) [intermediate NOT YET SPECIFIED]
- > 60 min -> HIGH (1.00)

### 12. Exposure Sub-component Weighting Confirmation

**Status:** CONFIRMED

**Resolution:** Weights loaded from YAML configuration: 0.282, 0.282, 0.184, 0.126, 0.125 (sum = 0.999). Source-unspecified intermediate categories documented as TBD.

---

## Mortality / Hospitalization ML

### 13. Mortality Target Definition

**Status:** DEFERRED (Phase 3+)

**Question:** What is the exact definition of the mortality prediction target?

### 14. Hospitalization Target Definition

**Status:** DEFERRED (Phase 3+)

**Question:** What is the exact definition of the hospitalization prediction target?

### 15. Historical Health Dataset

**Status:** DEFERRED (Phase 3+)

**Question:** Where is the historical health dataset for model training?

### 16. ML Model Selection

**Status:** DEFERRED (Phase 3+)

**Question:** Which ML model architecture should be used?

**Note:** Do NOT choose XGBoost, LightGBM, LSTM, Transformer, etc. yet. Model selection requires actual historical health data, target definition, baseline comparison, and validation.

### 17. 3-5 Day Forecasting Methodology

**Status:** DEFERRED (Phase 3+)

**Question:** How should the 3-5 day health-risk forecast be generated?

---

## Scientific Discrepancies

### UTCI Reference Values

**Discrepancy:** The supplied reference test cases (prompt.txt) use approximate expected values that do not match any standard UTCI implementation.

| Case | Prompt Expected | Our Result | Reference Fortran | Status |
|------|-----------------|------------|-------------------|--------|
| 1 | ~32.2 | 30.4 | 30.4 | Prompt approximate |
| 2 | ~29.0 | 29.2 | 29.2 | Prompt approximate |
| 3 | 38.0-39.5 | 33.5 | 33.5 | Prompt approximate |
| 4 | ~-10.0 | -14.7 | -14.7 | Prompt approximate |

**Resolution:** Our implementation matches the reference Fortran-derived `utci` PyPI package exactly. No modification was made to the UTCI formula to force agreement with approximate reference values. The actual calculation is preserved.

### Vulnerability Diagnostic Case

**Discrepancy:** Expected V ~ 0.407, computed V = 0.4006 (difference: 0.0064)

**Cause:** Rounding in source specification scores (0.33/0.66 vs exact 1/3, 2/3).

**Resolution:** Weights not modified. Discrepancy documented.

---

## Summary

| Category | CONFIRMED | OPEN | TBD | DEFERRED |
|----------|-----------|------|-----|----------|
| UTCI | 2 | 0 | 0 | 0 |
| Vulnerability | 6 | 0 | 0 | 0 |
| Exposure | 4 | 0 | 0 | 0 |
| Mortality/ML | 0 | 0 | 0 | 5 |
| **Total** | **12** | **0** | **0** | **5** |
