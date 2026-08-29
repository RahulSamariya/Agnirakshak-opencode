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

---

## UTCI Implementation

### 1. UTCI Algorithm / Polynomial

**Status:** BLOCKED

**Question:** Which authoritative UTCI algorithm or polynomial should be used?

**What is needed:**
- Closed-form UTCI polynomial with regression coefficients, OR
- Reference to an established Python library (e.g., pythermalcomfort), OR
- Documented algorithm with provenance

**Current state:** The supplied sources do not contain a closed-form UTCI polynomial, regression coefficients, or library reference.

**Impact:** Without this, the `PlaceholderUTCIModel` raises `NotImplementedError`. The full chain (meteorological inputs → UTCI → H) cannot be completed.

### 2. UTCI Reference Test Values

**Status:** BLOCKED

**Question:** What are the authoritative reference values for UTCI validation?

**What is needed:**
- Known input→output pairs (e.g., Temp=40°C, RH=50%, Wind=2m/s, MRT=45°C → UTCI=XX.X°C)
- Source/publication identifier for each reference value

**Current state:** No reference test values found in the repository.

**Impact:** Cannot validate UTCI implementation correctness.

---

## Vulnerability

### 3. BMI Classification Rules

**Status:** NOT YET SPECIFIED

**Question:** What are the exact BMI thresholds for LOW/MEDIUM/HIGH vulnerability?

**What is known:**
- Normal BMI 18.5–24.9 is LOW risk
- BMI below 17 or at least 30 is HIGH risk

**What is missing:**
- Exact boundary values for MEDIUM
- Non-overlapping boundary convention

### 4. Economic Status Classification Rules

**Status:** NOT YET SPECIFIED

**Question:** What are the exact economic status thresholds?

### 5. Social Isolation Classification Rules

**Status:** NOT YET SPECIFIED

**Question:** What are the exact social isolation thresholds?

### 6. Education Classification Rules

**Status:** NOT YET SPECIFIED

**Question:** What are the exact education level thresholds?

### 7. Gender/Sex Classification Rules

**Status:** NOT YET SPECIFIED

**Question:** How does gender factor into vulnerability scoring?

### 8. Disability Classification Rules

**Status:** NOT YET SPECIFIED

**Question:** What are the exact disability thresholds?

---

## Exposure

### 9. AQI/PM2.5 Threshold for Air Quality

**Status:** NOT YET SPECIFIED

**Question:** What is the exact AQI or PM2.5 threshold for high air quality exposure?

**What is known:** Joint heat + air pollution co-exposure is HIGH.

**What is missing:** Numerical threshold.

**Impact:** Cannot implement air quality scoring without this.

### 10. Fluid Intake/Activity Classification Rules

**Status:** NOT YET SPECIFIED

**Question:** What are the exact thresholds for fluid intake and physical activity?

### 11. Healthcare Accessibility Classification Rules

**Status:** NOT YET SPECIFIED

**Question:** What are the exact healthcare accessibility thresholds?

### 12. Exposure Sub-component Weighting Confirmation

**Status:** OPEN

**Question:** Are the BBWM-derived exposure weights (0.282, 0.282, 0.184, 0.126, 0.125) confirmed by IIT Roorkee?

**Note:** The source does NOT provide official numerical weights for Commuting + Lifestyle + Air Quality as a combined equation. Do NOT claim equal weighting is an official IIT Roorkee equation.

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

### 17. 3–5 Day Forecasting Methodology

**Status:** DEFERRED (Phase 3+)

**Question:** How should the 3–5 day health-risk forecast be generated?

---

## Summary

| Category | BLOCKED | OPEN | NOT YET SPECIFIED | DEFERRED |
|----------|---------|------|-------------------|----------|
| UTCI | 2 | 0 | 0 | 0 |
| Vulnerability | 0 | 0 | 6 | 0 |
| Exposure | 0 | 1 | 3 | 0 |
| Mortality/ML | 0 | 0 | 0 | 5 |
| **Total** | **2** | **1** | **9** | **5** |
