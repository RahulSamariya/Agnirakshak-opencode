# Phase 2 Scientific Specification

**Project:** Extreme Heatwave Early Warning and Human Thermal Stress Index
**MoES Problem Statement ID:** 26083
**Status:** Scientific specification — not yet implemented

## Core Risk Equation

```
HSRI = H × V × E
```

[SOURCE-DERIVED]

Where:
- **H** = Hazard (UTCI-derived thermal stress, normalized to 0–1)
- **V** = Vulnerability (population susceptibility, BBWM-weighted, 0.33–1.0)
- **E** = Exposure (population exposure, BBWM-weighted, 0.33–1.0)

HSRI is NOT mortality probability. It is a normalized risk index.

## Pipeline Architecture

```
Weather Forecast
    ↓
Temperature + Humidity + Wind + Radiation
    ↓
Thermal Comfort Metric (UTCI)
    ↓
Hazard H
    ↓
Vulnerability V
    ↓
Exposure E
    ↓
HSRI = H × V × E
    ↓
Historical Health + Weather Lags + HSRI
    ↓
Mortality / Hospitalization Prediction Model
    ↓
3–5 day health-risk forecast
    ↓
GIS + Alerts + Heat Action Plan triggers
```

[SOURCE-DERIVED — Phase 2 implements up to HSRI; mortality ML is deferred]

## Scientific Scope

### Implemented in Phase 2

- UTCI → Hazard normalization (H)
- Vulnerability scoring (V) using BBWM weights
- Exposure scoring (E) using BBWM weights
- HSRI = H × V × E
- Risk classification (LOW / MEDIUM / HIGH)

### NOT Implemented in Phase 2

- UTCI calculation from meteorological inputs (blocked — no authoritative algorithm in repo)
- Mortality / hospitalization ML
- 3–5 day health-risk prediction
- Ward-level aggregation

## Numerical Scoring Scale

| Score | Label |
|-------|-------|
| 0.33 | LOW |
| 0.66 | MEDIUM |
| 1.00 | HIGH |

[SOURCE-DERIVED]

## Residual Risk Floor

Vulnerability and Exposure maintain a minimum floor of 0.33 to ensure baseline risk is always represented.

[SOURCE-DERIVED]

## Determinism Requirements

For identical inputs and identical configuration:
- Identical outputs
- No random state
- No current-time dependence
- No hidden global mutable state

[PROJECT IMPLEMENTATION CONVENTION]

## Configuration Source of Truth

All scientific constants are loaded from `scientific/configuration/*.yaml` and validated by Pydantic models in `scientific/configuration/models.py`.

[PROJECT IMPLEMENTATION CONVENTION]
